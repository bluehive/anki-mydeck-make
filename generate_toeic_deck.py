#!/usr/bin/env python3
"""
generate_toeic_deck.py
抽出済み TOEIC データから「1問5秒」向けの2種類の CSV を生成する。

パターンA（英→日）: 表面=英単語+音声 / 裏面=和訳+画像+英英辞典+例文
パターンB（Cloze）:  表面=和訳+例文穴埋め / 裏面=単語+和訳+音声+画像
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

INPUT_JSON = Path("assets/toeic/toeic_words.json")
OUTPUT_A = Path("toeic_deck_meaning.csv")
OUTPUT_B = Path("toeic_deck_cloze.csv")


def sound_tag(filename: str) -> str:
    return f"[sound:{filename}]" if filename else ""


def image_tag(filename: str) -> str:
    return f'<img src="{filename}">' if filename else ""


def normalize_for_match(text: str) -> str:
    return re.sub(r"[\s\-_]+", "", text.lower())


def make_cloze_sentence(word: str, example: str) -> str | None:
    """例文内の対象語を {{c1::...}} に置換。失敗時は None。"""
    if not example:
        return None

    def wrap(match: re.Match[str]) -> str:
        return "{{c1::" + match.group(0) + "}}"

    if " " in word:
        match = re.search(re.escape(word), example, re.I)
        if match:
            return (
                example[: match.start()]
                + "{{c1::" + example[match.start() : match.end()] + "}}"
                + example[match.end() :]
            )

    pattern = r"(?<![A-Za-z])" + re.escape(word) + r"(?![A-Za-z])"
    match = re.search(pattern, example, re.I)
    if match:
        return example[: match.start()] + wrap(match) + example[match.end() :]

    stem = word[: max(4, len(word) // 2)]
    stem_pattern = r"(?<![A-Za-z])" + re.escape(stem) + r"[A-Za-z]*(?![A-Za-z])"
    match = re.search(stem_pattern, example, re.I)
    if match:
        return example[: match.start()] + wrap(match) + example[match.end() :]

    word_norm = normalize_for_match(word)
    for token_match in re.finditer(r"[A-Za-z][A-Za-z\-]*", example):
        token = token_match.group(0)
        if normalize_for_match(token) == word_norm:
            return (
                example[: token_match.start()]
                + "{{c1::" + token + "}}"
                + example[token_match.end() :]
            )

    return None


def build_pattern_a(word: dict) -> tuple[str, str]:
    """パターンA: 表面 / 裏面"""
    surface_parts = [word["word"]]
    if word["audio"]:
        surface_parts.append(sound_tag(word["audio"]))

    back_parts = []
    if word["translation_ja"]:
        back_parts.append(word["translation_ja"])
    if word["image"]:
        back_parts.append(image_tag(word["image"]))
    if word["definition_en"]:
        back_parts.append(f"<i>{word['definition_en']}</i>")
    if word["example"]:
        back_parts.append(word["example"])

    return "<br>".join(surface_parts), "<br>".join(back_parts)


def build_pattern_b(word: dict) -> tuple[str, str] | None:
    """パターンB: Cloze 表面 / 裏面。穴埋め不可なら None。"""
    cloze = make_cloze_sentence(word["word"], word["example"])
    if not cloze:
        return None

    front_parts = []
    if word["translation_ja"]:
        front_parts.append(word["translation_ja"])
    front_parts.append(cloze)

    back_parts = [word["word"]]
    if word["translation_ja"]:
        back_parts.append(word["translation_ja"])
    if word["audio"]:
        back_parts.append(sound_tag(word["audio"]))
    if word["image"]:
        back_parts.append(image_tag(word["image"]))

    return "<br>".join(front_parts), "<br>".join(back_parts)


def generate_decks(
    input_json: Path = INPUT_JSON,
    output_a: Path = OUTPUT_A,
    output_b: Path = OUTPUT_B,
) -> dict:
    if not input_json.exists():
        raise FileNotFoundError(
            f"{input_json} がありません。先に extract_toeic_apkg.py を実行してください。"
        )

    data = json.loads(input_json.read_text(encoding="utf-8"))
    words = data["words"]

    rows_a: list[dict[str, str]] = []
    rows_b: list[dict[str, str]] = []
    skipped_b = 0

    for word in words:
        front_a, back_a = build_pattern_a(word)
        rows_a.append(
            {
                "表面": front_a,
                "裏面": back_a,
                "Word": word["word"],
                "Audio": word["audio"],
                "Image": word["image"],
            }
        )

        pattern_b = build_pattern_b(word)
        if pattern_b:
            front_b, back_b = pattern_b
            rows_b.append(
                {
                    "Text": front_b,
                    "Back Extra": back_b,
                    "Word": word["word"],
                    "TranslationJa": word["translation_ja"],
                    "Audio": word["audio"],
                    "Image": word["image"],
                }
            )
        else:
            skipped_b += 1

    with open(output_a, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["表面", "裏面", "Word", "Audio", "Image"]
        )
        writer.writeheader()
        writer.writerows(rows_a)

    with open(output_b, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Text", "Back Extra", "Word", "TranslationJa", "Audio", "Image"],
        )
        writer.writeheader()
        writer.writerows(rows_b)

    print("=== TOEIC デッキ CSV 生成 ===")
    print(f"入力: {input_json} ({len(words)} 語)")
    print(f"パターンA（意味）: {output_a} — {len(rows_a)} カード")
    print(f"パターンB（Cloze）: {output_b} — {len(rows_b)} カード")
    if skipped_b:
        print(f"  パターンBスキップ: {skipped_b} 件（例文なし or 穴埋め不可）")

    return {
        "pattern_a_count": len(rows_a),
        "pattern_b_count": len(rows_b),
        "skipped_b": skipped_b,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TOEIC 1問5秒デッキ CSV を生成")
    parser.add_argument("--input", type=Path, default=INPUT_JSON)
    parser.add_argument("--output-a", type=Path, default=OUTPUT_A)
    parser.add_argument("--output-b", type=Path, default=OUTPUT_B)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_decks(args.input, args.output_a, args.output_b)


if __name__ == "__main__":
    main()