#!/usr/bin/env python3
"""
Task 5: emacs_deck.csv generator
Emacsキー操作 77問の Basic カードを生成する。

- 3列: 表面, 裏面, カテゴリ
- 一次資料: plan.md §4.3
"""

import csv
from collections import Counter

OUTPUT = "emacs_deck.csv"
EXPECTED_TOTAL = 77

EXPECTED_COUNTS = {
    "基本・移動": 10,
    "基本・編集": 8,
    "基本・検索": 2,
    "基本・ウィンドウ": 3,
    "基本・ファイル": 3,
    "基本・その他": 2,
    "Org-mode": 20,
    "Magit": 16,
    "Avy": 5,
    "Avy/Embark": 1,
    "Embark": 4,
    "Paredit": 3,
}

# (表面, 裏面, カテゴリ)
CARDS = [
    # ── 基本・移動（10問） ──
    ("1文字左に移動する", "C-b", "基本・移動"),
    ("1文字右に移動する", "C-f", "基本・移動"),
    ("1行上に移動する", "C-p", "基本・移動"),
    ("1行下に移動する", "C-n", "基本・移動"),
    ("行頭に移動する", "C-a", "基本・移動"),
    ("行末に移動する", "C-e", "基本・移動"),
    ("1ページ戻る", "M-v", "基本・移動"),
    ("1ページ進む", "C-v", "基本・移動"),
    ("ファイル先頭に移動する", "M-<", "基本・移動"),
    ("ファイル末尾に移動する", "M->", "基本・移動"),
    # ── 基本・編集（8問） ──
    ("テキスト全選択", "C-x h", "基本・編集"),
    ("選択範囲をコピーする（キルリングに保存）", "M-w", "基本・編集"),
    ("選択範囲を切り取る（キル）", "C-w", "基本・編集"),
    ("貼り付け（ヤンク）", "C-y", "基本・編集"),
    ("履歴から貼り付ける（ヤンクポップ）", "M-y", "基本・編集"),
    ("1行切り取る", "C-k", "基本・編集"),
    ("1文字削除する（デリート）", "C-d", "基本・編集"),
    ("操作を元に戻す（Undo）", "C-/ または C-_", "基本・編集"),
    # ── 基本・検索（2問） ──
    ("カーソルより下の範囲で検索（インクリメンタル検索）", "C-s", "基本・検索"),
    ("カーソルより上の範囲で検索", "C-r", "基本・検索"),
    # ── 基本・ウィンドウ（3問） ──
    ("ウィンドウを上下に分割する", "C-x 2", "基本・ウィンドウ"),
    ("ウィンドウを左右に分割する", "C-x 3", "基本・ウィンドウ"),
    ("分割されたウィンドウを現在の1つだけにする", "C-x 1", "基本・ウィンドウ"),
    # ── 基本・ファイル（3問） ──
    ("ファイルを開く", "C-x C-f", "基本・ファイル"),
    ("ファイルを保存する", "C-x C-s", "基本・ファイル"),
    ("バッファを変更・切り替える", "C-x b", "基本・ファイル"),
    # ── 基本・その他（2問） ──
    ("実行途中のコマンドを中断（アボート）する", "C-g", "基本・その他"),
    ("Emacsを終了する", "C-x C-c", "基本・その他"),
    # ── Org-mode（20問） ──
    ("【Org】見出しを隠す / 展開する", "TAB", "Org-mode"),
    ("【Org】すべてを展開して表示する", "C-u C-u C-u TAB", "Org-mode"),
    ("【Org】新しい見出しを追加する", "M-RET", "Org-mode"),
    ("【Org】見出しのレベルを減らす（昇格）", "M-LEFT", "Org-mode"),
    ("【Org】見出しのレベルを増やす（降格）", "M-RIGHT", "Org-mode"),
    ("【Org】サブツリー全体を上に移動する", "M-UP", "Org-mode"),
    ("【Org】サブツリー全体を下に移動する", "M-DOWN", "Org-mode"),
    ("【Org】TODOの状態を切り替える", "C-c C-t", "Org-mode"),
    ("【Org】優先度を設定する", "C-c ,", "Org-mode"),
    ("【Org】チェックボックスの状態をトグルする", "C-c C-c", "Org-mode"),
    ("【Org】スケジュール（作業予定日）を設定する", "C-c C-s", "Org-mode"),
    ("【Org】締め切り（DEADLINE）を設定する", "C-c C-d", "Org-mode"),
    ("【Org】タイムスタンプを挿入する", "C-c .", "Org-mode"),
    ("【Org】タグを設定する", "C-c C-q", "Org-mode"),
    ("【Org】プロパティを設定する", "C-c C-x p", "Org-mode"),
    ("【Org】クロッキング（作業時間記録）を開始する", "C-c C-x C-i", "Org-mode"),
    ("【Org】クロッキングを停止する", "C-c C-x C-o", "Org-mode"),
    ("【Org】条件に合う見出しのスパースツリーを作成する", "C-c /", "Org-mode"),
    ("【Org】表を再フォーマット（アライメント）する", "C-c C-c または TAB", "Org-mode"),
    ("【Org】アジェンダディスパッチャ（一覧）を開く", "C-c a (一般的な割当)", "Org-mode"),
    # ── Magit（16問） ──
    ("【Magit】ステータス画面を開く", "magit-status", "Magit"),
    ("【Magit】カーソル位置のファイルをステージングする", "s", "Magit"),
    ("【Magit】カーソル位置のファイルのステージングを解除する", "u", "Magit"),
    ("【Magit】すべてのファイルをステージングする", "S", "Magit"),
    ("【Magit】すべてのファイルのステージングを解除する", "U", "Magit"),
    ("【Magit】ファイルの差分をインラインで展開/折りたたみする", "TAB", "Magit"),
    ("【Magit】カーソル位置のファイルの変更を取り消す（破棄する）", "k", "Magit"),
    ("【Magit】ワーキングツリーの差分を表示する", "d d", "Magit"),
    ("【Magit】コミットメニューを開く/コミットを作成する", "c c", "Magit"),
    ("【Magit】直前のコミットを修正する（amend）", "c a", "Magit"),
    ("【Magit】ブランチを切り替える（checkout）", "b b", "Magit"),
    ("【Magit】新しいブランチを作成して切り替える", "b c", "Magit"),
    ("【Magit】ブランチを削除する", "b d", "Magit"),
    ("【Magit】現在のブランチのログを確認する", "l l", "Magit"),
    ("【Magit】リモートリポジトリにプッシュする", "P p", "Magit"),
    ("【Magit】リモートリポジトリからプルする", "F p", "Magit"),
    # ── Avy（5問）+ Avy/Embark（1問） ──
    ("【Avy】画面上の文字列にタイマーベースでジャンプする", "avy-goto-char-timer", "Avy"),
    ("【Avy】実行可能なアクション(ディスパッチ)の一覧を表示する", "?", "Avy"),
    ("【Avyディスパッチ】対象の単語やsexpを削除(Kill)する", "k", "Avy"),
    ("【Avyディスパッチ】対象の単語やsexpをコピー(Copy)する", "w", "Avy"),
    ("【Avyディスパッチ】現在のカーソル位置から対象までを削除(Zap)する", "z", "Avy"),
    ("【Avyディスパッチ】対象に対してEmbarkのアクションを呼び出す", "o", "Avy/Embark"),
    # ── Embark（4問） ──
    ("【Embark】選択した対象に対してアクションを選択・実行する", "embark-act", "Embark"),
    ("【Embark】ミニバッファーの候補リストから永続的なコレクションを作成", "embark-export", "Embark"),
    ("【Embarkアクション】ファイルのオープン時に別の場所へコピーする", "c", "Embark"),
    ("【Embarkアクション】root権限(sudo)でファイルをオープンする", "S", "Embark"),
    # ── Paredit（3問） ──
    ("【Paredit】S式を削除(Kill)し、括弧の構造を保持する", "C-k", "Paredit"),
    ("【Paredit】次のS式を現在のリストの中に取り込む(Slurp)", "C-) または C-<right>", "Paredit"),
    ("【Paredit】現在のリストの最後のS式を外に出す(Barf)", "C-} または C-<left>", "Paredit"),
]


def validate_cards(cards: list[tuple[str, str, str]]) -> None:
    assert len(cards) == EXPECTED_TOTAL, (
        f"カード数が{EXPECTED_TOTAL}ではありません: {len(cards)}"
    )

    fronts = [c[0] for c in cards]
    assert len(fronts) == len(set(fronts)), "表面（問題文）に重複があります"

    counts = Counter(c[2] for c in cards)
    assert counts == Counter(EXPECTED_COUNTS), (
        f"カテゴリ別件数が仕様と一致しません\n"
        f"期待: {EXPECTED_COUNTS}\n実際: {dict(counts)}"
    )

    for front, back, category in cards:
        assert front.strip(), "表面が空です"
        assert back.strip(), f"裏面が空です: {front[:40]}"
        assert category.strip(), f"カテゴリが空です: {front[:40]}"

    print("カテゴリ別内訳:")
    for tag, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {tag}: {count}問")
    print(f"\n合計: {sum(counts.values())}問")


def main() -> None:
    validate_cards(CARDS)

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["表面", "裏面", "カテゴリ"])
        for front, back, category in CARDS:
            writer.writerow([front, back, category])

    print(f"\n✓ {OUTPUT} を生成しました（{len(CARDS)}問）")


if __name__ == "__main__":
    main()