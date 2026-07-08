#!/usr/bin/env python3
"""
import_to_anki.py
AnkiConnect経由で Git / 数学 / Emacs デッキを自動インポートするスクリプト。

- git_deck.csv   → Basic ノート（Front + Back + 画像）
- math_deck.csv  → Cloze ノート（Text + MathJax + Back Extra）
- emacs_deck.csv → Basic ノート（Front + Back + カテゴリタグ）
"""

import argparse
import base64
import csv
import os
import sys
from pathlib import Path

import requests

ANKI_CONNECT_URL = "http://localhost:8765"

GIT_DECK_NAME = "Git学習"
GIT_CSV = "git_deck.csv"
IMAGES_DIR = Path("assets/images/git-deck")

MATH_DECK_NAME = "高校数学・基礎解析"
MATH_CSV = "math_deck.csv"

EMACS_DECK_NAME = "Emacsキー操作"
EMACS_CSV = "emacs_deck.csv"
EMACS_EXPECTED_COUNT = 77

PROJECT_TAG = "anki-mydeck-make"


def to_mathjax(text: str) -> str:
    """Anki MathJax 記法 \\(...\\) に統一（[$]...[/]$] や $...$ を変換）"""
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("[$$]", i):
            end = text.find("[/$$]", i)
            if end == -1:
                out.append(text[i:])
                break
            content = text[i + 4 : end]
            out.append(f"\\[{content}\\]")
            i = end + 5
        elif text.startswith("[$]", i):
            end = text.find("[/$]", i)
            if end == -1:
                out.append(text[i:])
                break
            content = text[i + 3 : end]
            out.append(f"\\({content}\\)")
            i = end + 4
        elif text[i] == "$":
            end = text.find("$", i + 1)
            if end == -1:
                out.append(text[i])
                i += 1
                continue
            content = text[i + 1 : end]
            out.append(f"\\({content}\\)")
            i = end + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def invoke(action, params=None):
    """AnkiConnectにリクエストを送る"""
    payload = {"action": action, "version": 6, "params": params or {}}
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result.get("error"):
            print(f"[AnkiConnect Error] {action}: {result['error']}")
            return None
        return result.get("result")
    except requests.RequestException as e:
        print(f"[接続エラー] Ankiが起動しているか、AnkiConnectアドオンが有効か確認してください: {e}")
        return None


def check_connection() -> bool:
    """AnkiConnect への接続確認（必要なら権限リクエスト）"""
    perm = invoke(
        "requestPermission",
        {"permission": "granted", "origin": "http://localhost"},
    )
    if perm and perm.get("permission") == "granted":
        print(f"AnkiConnect 権限: granted (API version {perm.get('version')})")

    result = invoke("version")
    if result is None:
        return False
    print(f"AnkiConnect 接続OK (version {result})")
    return True


def ensure_deck_exists(deck_name: str):
    """デッキが存在しなければ作成"""
    decks = invoke("deckNames") or []
    if deck_name not in decks:
        invoke("createDeck", {"deck": deck_name})
        print(f"デッキを作成しました: {deck_name}")


def ensure_model_exists(model_name: str) -> bool:
    """必要なノートタイプが存在するか確認"""
    models = invoke("modelNames") or []
    if model_name not in models:
        print(f"エラー: ノートタイプ '{model_name}' が見つかりません。Ankiの標準モデルを確認してください。")
        return False
    return True


class MediaCache:
    """同一画像の重複アップロードを防ぐ"""

    def __init__(self, images_dir: Path):
        self.images_dir = images_dir
        self.uploaded: set[str] = set()

    def store(self, filename: str) -> bool:
        if not filename:
            return False
        if filename in self.uploaded:
            return True

        image_path = self.images_dir / filename
        if not image_path.exists():
            print(f"  ⚠ 画像が見つかりません: {filename}")
            return False

        with open(image_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        result = invoke("storeMediaFile", {"filename": filename, "data": b64_data})
        if result is not None:
            self.uploaded.add(filename)
            print(f"  ✓ 画像アップロード: {filename}")
            return True
        return False


def add_git_note(front: str, back: str, image: str = "") -> bool:
    """Gitカードを追加（画像がある場合はFrontに埋め込む）"""
    front_html = f'{front}<br><br><img src="{image}">' if image else front

    note = {
        "deckName": GIT_DECK_NAME,
        "modelName": "Basic",
        "fields": {
            "Front": front_html,
            "Back": back,
        },
        "tags": ["git", PROJECT_TAG],
    }
    return invoke("addNote", {"note": note}) is not None


def add_math_note(text: str, tag: str = "", extra: str = "") -> bool:
    """数学Clozeカードを追加"""
    tags = ["math", "基礎解析", PROJECT_TAG]
    if tag:
        tags.append(tag)

    note = {
        "deckName": MATH_DECK_NAME,
        "modelName": "Cloze",
        "fields": {
            "Text": text,
            "Back Extra": extra.replace("\n", "<br>"),
        },
        "tags": tags,
    }
    return invoke("addNote", {"note": note}) is not None


def add_emacs_note(front: str, back: str, category: str = "") -> bool:
    """Emacsキー操作カードを追加"""
    tags = ["emacs", PROJECT_TAG]
    if category:
        tags.append(category)

    note = {
        "deckName": EMACS_DECK_NAME,
        "modelName": "Basic",
        "fields": {
            "Front": front,
            "Back": back,
        },
        "tags": tags,
    }
    return invoke("addNote", {"note": note}) is not None


def import_git_deck() -> tuple[int, int]:
    """git_deck.csv をインポート。戻り値: (成功数, 総数)"""
    if not os.path.exists(GIT_CSV):
        print(f"エラー: {GIT_CSV} が見つかりません")
        return 0, 0

    if not ensure_model_exists("Basic"):
        return 0, 0

    ensure_deck_exists(GIT_DECK_NAME)
    media = MediaCache(IMAGES_DIR)

    print(f"\n=== Gitデッキのインポート開始 ===")
    print(f"CSV: {GIT_CSV}")
    print(f"画像フォルダ: {IMAGES_DIR}")

    with open(GIT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    success = 0

    for i, row in enumerate(rows, 1):
        surface = row["表面"]
        back = row["裏面"]
        image = row.get("Image", "").strip()

        print(f"\n[{i}/{total}] {surface[:50]}...")

        if image:
            media.store(image)

        if add_git_note(surface, back, image):
            success += 1
            print("  ✓ カード追加成功")
        else:
            print("  ✗ カード追加失敗")

    print(f"\n--- Gitデッキ完了: {success}/{total} カード ---")
    print(f"画像アップロード: {len(media.uploaded)} 枚")
    return success, total


def import_math_deck() -> tuple[int, int]:
    """math_deck.csv をインポート。戻り値: (成功数, 総数)"""
    if not os.path.exists(MATH_CSV):
        print(f"エラー: {MATH_CSV} が見つかりません")
        return 0, 0

    if not ensure_model_exists("Cloze"):
        return 0, 0

    ensure_deck_exists(MATH_DECK_NAME)

    print(f"\n=== 数学デッキのインポート開始 ===")
    print(f"CSV: {MATH_CSV}")

    with open(MATH_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    success = 0

    for i, row in enumerate(rows, 1):
        text = row["Text"]
        tag = row.get("Tag", "").strip()
        extra = row.get("Extra", "").strip()
        preview = text.replace("\n", " ")[:50]

        print(f"\n[{i}/{total}] {preview}...")

        if add_math_note(text, tag, extra):
            success += 1
            print("  ✓ カード追加成功")
        else:
            print("  ✗ カード追加失敗")

    print(f"\n--- 数学デッキ完了: {success}/{total} カード ---")
    return success, total


def import_emacs_deck() -> tuple[int, int]:
    """emacs_deck.csv をインポート。戻り値: (成功数, 総数)"""
    if not os.path.exists(EMACS_CSV):
        print(f"エラー: {EMACS_CSV} が見つかりません")
        return 0, 0

    if not ensure_model_exists("Basic"):
        return 0, 0

    ensure_deck_exists(EMACS_DECK_NAME)

    print(f"\n=== Emacsデッキのインポート開始 ===")
    print(f"CSV: {EMACS_CSV}")

    with open(EMACS_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    success = 0

    for i, row in enumerate(rows, 1):
        front = row["表面"]
        back = row["裏面"]
        category = row.get("カテゴリ", "").strip()
        preview = front[:50]

        print(f"\n[{i}/{total}] {preview}...")

        if add_emacs_note(front, back, category):
            success += 1
            print("  ✓ カード追加成功")
        else:
            print("  ✗ カード追加失敗")

    print(f"\n--- Emacsデッキ完了: {success}/{total} カード ---")
    return success, total


def fix_mathjax_in_anki() -> tuple[int, int]:
    """数学デッキの既存ノートを CSV から同期（Text + Back Extra）"""
    if not os.path.exists(MATH_CSV):
        print(f"エラー: {MATH_CSV} が見つかりません")
        return 0, 0

    with open(MATH_CSV, "r", encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))

    note_ids = sorted(invoke("findNotes", {"query": f'deck:"{MATH_DECK_NAME}"'}) or [])
    if not note_ids:
        print(f"数学デッキ ({MATH_DECK_NAME}) にノートがありません")
        return 0, 0

    if len(note_ids) != len(csv_rows):
        print(
            f"警告: ノート数 ({len(note_ids)}) と CSV行数 ({len(csv_rows)}) が一致しません"
        )

    notes = sorted(
        invoke("notesInfo", {"notes": note_ids}) or [],
        key=lambda n: n["noteId"],
    )
    updated = 0
    total = len(notes)

    print(f"\n=== 数学デッキ同期 ({total} ノート) ===")

    for i, note in enumerate(notes, 1):
        note_id = note["noteId"]
        fields = note.get("fields", {})
        text = fields.get("Text", {}).get("value", "")
        extra = fields.get("Back Extra", {}).get("value", "")
        row = csv_rows[i - 1] if i <= len(csv_rows) else {}
        fixed_text = row.get("Text", to_mathjax(text))
        fixed_extra = row.get("Extra", "").replace("\n", "<br>")

        if fixed_text == text and fixed_extra == extra:
            continue

        preview = text.replace("\n", " ")[:50]
        print(f"\n[{i}/{total}] 更新: {preview}...")

        payload = {
            "action": "updateNoteFields",
            "version": 6,
            "params": {
                "note": {
                    "id": note_id,
                    "fields": {"Text": fixed_text, "Back Extra": fixed_extra},
                }
            },
        }
        try:
            response = requests.post(ANKI_CONNECT_URL, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            print(f"  ✗ 接続エラー: {e}")
            continue

        if result.get("error"):
            print(f"  ✗ 更新失敗: {result['error']}")
        else:
            updated += 1
            print("  ✓ 同期完了")

    print(f"\n--- 同期完了: {updated}/{total} ノートを更新 ---")
    return updated, total


def print_usage_guide():
    """インポート後の使い方ガイド"""
    print("\n" + "=" * 50)
    print("使い方ガイド")
    print("=" * 50)
    print("1. Ankiアプリでデッキを確認:")
    print(f"   - {GIT_DECK_NAME}")
    print(f"   - {MATH_DECK_NAME}")
    print(f"   - {EMACS_DECK_NAME}")
    print("2. 数学デッキの数式は \\(...\\)（MathJax）記法です。")
    print("   答え側に「Back Extra」フィールドで解説が表示されます。")
    print("3. 再実行するとカードが重複追加されます。")
    print("   初回インポート前に空のデッキで実行するか、")
    print("   重複分は Anki 上で手動削除してください。")
    print("=" * 50)


def preflight_check(
    check_git: bool = True,
    check_math: bool = True,
    check_emacs: bool = True,
) -> bool:
    """CSV・画像の存在確認（Anki不要）"""
    print("\n=== 事前チェック ===")
    ok = True

    targets = []
    if check_git:
        targets.append((GIT_CSV, "Git CSV"))
    if check_math:
        targets.append((MATH_CSV, "数学 CSV"))
    if check_emacs:
        targets.append((EMACS_CSV, "Emacs CSV"))

    for path, label in targets:
        if os.path.exists(path):
            print(f"  ✓ {label}: {path}")
        else:
            print(f"  ✗ {label} が見つかりません: {path}")
            ok = False

    if check_git and os.path.exists(GIT_CSV):
        with open(GIT_CSV, "r", encoding="utf-8") as f:
            git_rows = list(csv.DictReader(f))
        missing_images = []
        for row in git_rows:
            img = row.get("Image", "").strip()
            if img and not (IMAGES_DIR / img).exists():
                missing_images.append(img)
        print(f"  Gitカード数: {len(git_rows)}")
        if missing_images:
            print(f"  ✗ 不足画像: {len(missing_images)} 枚")
            ok = False
        else:
            print(f"  ✓ Git画像: {len(git_rows)} 枚すべて存在")

    if check_math and os.path.exists(MATH_CSV):
        with open(MATH_CSV, "r", encoding="utf-8") as f:
            math_rows = list(csv.DictReader(f))
        bad_cloze = [r for r in math_rows if "{{c1::" not in r.get("Text", "")]
        missing_extra = [r for r in math_rows if not r.get("Extra", "").strip()]
        print(f"  数学カード数: {len(math_rows)}")
        if bad_cloze:
            print(f"  ✗ Cloze記法なし: {len(bad_cloze)} 件")
            ok = False
        else:
            print("  ✓ Cloze記法: 全カードOK")
        if missing_extra:
            print(f"  ✗ 解説なし: {len(missing_extra)} 件")
            ok = False
        else:
            print(f"  ✓ 解説(Extra): {len(math_rows)} 件すべてあり")

    if check_emacs and os.path.exists(EMACS_CSV):
        with open(EMACS_CSV, "r", encoding="utf-8") as f:
            emacs_rows = list(csv.DictReader(f))
        missing_cat = [r for r in emacs_rows if not r.get("カテゴリ", "").strip()]
        print(f"  Emacsカード数: {len(emacs_rows)}")
        if len(emacs_rows) != EMACS_EXPECTED_COUNT:
            print(
                f"  ✗ 件数不一致（期待: {EMACS_EXPECTED_COUNT}, 実際: {len(emacs_rows)}）"
            )
            ok = False
        else:
            print(f"  ✓ 件数: {EMACS_EXPECTED_COUNT}問")
        if missing_cat:
            print(f"  ✗ カテゴリなし: {len(missing_cat)} 件")
            ok = False
        else:
            print("  ✓ カテゴリ: 全カードOK")

    print("=== 事前チェック完了 ===\n")
    return ok


def verify_imported(
    check_git: bool = True,
    check_math: bool = True,
    check_emacs: bool = True,
) -> bool:
    """インポート後の件数確認"""
    print("\n=== インポート結果の検証 ===")
    all_ok = True

    if check_git:
        git_count = invoke("findNotes", {"query": f'deck:"{GIT_DECK_NAME}"'})
        if git_count is None:
            print("  検証APIの呼び出しに失敗しました（Git）")
            return False
        print(f"  Gitデッキ ({GIT_DECK_NAME}): {len(git_count)} ノート")
        if len(git_count) < 50:
            print(f"  ⚠ Gitデッキが不足しています（期待: 50, 実際: {len(git_count)}）")
            all_ok = False

    if check_math:
        math_count = invoke("findNotes", {"query": f'deck:"{MATH_DECK_NAME}"'})
        if math_count is None:
            print("  検証APIの呼び出しに失敗しました（数学）")
            return False
        print(f"  数学デッキ ({MATH_DECK_NAME}): {len(math_count)} ノート")
        if len(math_count) < 100:
            print(
                f"  ⚠ 数学デッキが不足しています（期待: 100, 実際: {len(math_count)}）"
            )
            all_ok = False

    if check_emacs:
        emacs_count = invoke("findNotes", {"query": f'deck:"{EMACS_DECK_NAME}"'})
        if emacs_count is None:
            print("  検証APIの呼び出しに失敗しました（Emacs）")
            return False
        print(f"  Emacsデッキ ({EMACS_DECK_NAME}): {len(emacs_count)} ノート")
        if len(emacs_count) < EMACS_EXPECTED_COUNT:
            print(
                f"  ⚠ Emacsデッキが不足しています"
                f"（期待: {EMACS_EXPECTED_COUNT}, 実際: {len(emacs_count)}）"
            )
            all_ok = False

    if all_ok:
        print("  ✓ インポート対象デッキの想定件数を満たしています")
    return all_ok


def parse_args():
    parser = argparse.ArgumentParser(
        description="AnkiConnect経由で Git / 数学 / Emacs デッキをインポート"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--git-only", action="store_true", help="Gitデッキのみ")
    group.add_argument("--math-only", action="store_true", help="数学デッキのみ")
    group.add_argument("--emacs-only", action="store_true", help="Emacsデッキのみ")
    parser.add_argument(
        "--preflight", action="store_true", help="CSV/画像の事前チェックのみ（Anki不要）"
    )
    parser.add_argument(
        "--fix-mathjax",
        action="store_true",
        help="数学デッキの既存ノートを CSV から同期（Text + 解説）",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("AnkiConnect 自動インポートツール")
    print("前提: Ankiを起動 + AnkiConnectアドオン有効 (ポート8765)")

    if args.preflight:
        sys.exit(0 if preflight_check() else 1)

    if args.fix_mathjax:
        if not check_connection():
            sys.exit(1)
        fix_mathjax_in_anki()
        sys.exit(0)

    if args.git_only:
        import_git, import_math, import_emacs = True, False, False
    elif args.math_only:
        import_git, import_math, import_emacs = False, True, False
    elif args.emacs_only:
        import_git, import_math, import_emacs = False, False, True
    else:
        import_git = import_math = import_emacs = True

    if not preflight_check(import_git, import_math, import_emacs):
        sys.exit(1)

    if not check_connection():
        print("\n対処法:")
        print("  1. Ankiアプリを起動する")
        print("  2. ツール → アドオン → AnkiConnect (コード: 2055492159) を有効化")
        print("  3. Ankiを再起動してから、再度このスクリプトを実行する")
        sys.exit(1)

    git_result = (0, 0)
    math_result = (0, 0)
    emacs_result = (0, 0)

    if import_git:
        git_result = import_git_deck()
    if import_math:
        math_result = import_math_deck()
    if import_emacs:
        emacs_result = import_emacs_deck()

    print("\n" + "=" * 50)
    print("インポート結果サマリー")
    print("=" * 50)
    if import_git:
        print(f"Gitデッキ ({GIT_DECK_NAME}): {git_result[0]}/{git_result[1]}")
    if import_math:
        print(f"数学デッキ ({MATH_DECK_NAME}): {math_result[0]}/{math_result[1]}")
    if import_emacs:
        print(f"Emacsデッキ ({EMACS_DECK_NAME}): {emacs_result[0]}/{emacs_result[1]}")

    total_ok = git_result[0] + math_result[0] + emacs_result[0]
    total_all = git_result[1] + math_result[1] + emacs_result[1]
    print(f"合計: {total_ok}/{total_all} カード")

    if total_ok < total_all:
        sys.exit(1)

    verify_imported(import_git, import_math, import_emacs)
    print_usage_guide()


if __name__ == "__main__":
    main()