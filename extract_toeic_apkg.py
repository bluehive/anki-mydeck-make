#!/usr/bin/env python3
"""
extract_toeic_apkg.py
Anki .apkg（7 TOEIC for Japanese Speakers）から英単語データとメディアを抽出する。

対応形式: Anki 2.1.50+（collection.anki21b + zstd 圧縮メディア）
出力:
  assets/toeic/toeic_words.json  — 構造化データ
  assets/toeic/media/            — 音声・画像ファイル
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sqlite3
import tempfile
import zipfile
from pathlib import Path

import zstandard as zstd

DEFAULT_APKG = Path(r"C:\Users\mevius\Downloads\7 TOEIC for Japanese Speakers.apkg")
TOEIC_MODEL_ID = 1414069242838
OUTPUT_JSON = Path("assets/toeic/toeic_words.json")
MEDIA_DIR = Path("assets/toeic/media")

FIELD_WORD = 0
FIELD_POS = 1
FIELD_EN_EN = 2
FIELD_EXAMPLE = 3
FIELD_JA = 4
FIELD_AUDIO = 5
FIELD_IMAGE = 6


def zstd_decompress(data: bytes, max_size: int = 100 * 1024 * 1024) -> bytes:
    dctx = zstd.ZstdDecompressor()
    try:
        return dctx.decompress(data, max_output_size=max_size)
    except zstd.ZstdError:
        with dctx.stream_reader(io.BytesIO(data)) as reader:
            return reader.read()


def parse_varint(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while index < len(data):
        byte = data[index]
        index += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return value, index


def parse_entry_name(chunk: bytes) -> str:
    index = 0
    while index < len(chunk):
        tag = chunk[index]
        index += 1
        field_num = tag >> 3
        wire_type = tag & 7
        if wire_type == 2:
            length, index = parse_varint(chunk, index)
            value = chunk[index : index + length]
            index += length
            if field_num == 1:
                return value.decode("utf-8")
    return ""


def parse_media_entries(data: bytes) -> dict[int, str]:
    """MediaEntries protobuf を簡易パースして index -> ファイル名 を返す。"""
    entries: dict[int, str] = {}
    entry_idx = 0
    index = 0
    while index < len(data):
        tag = data[index]
        index += 1
        field_num = tag >> 3
        wire_type = tag & 7
        if wire_type == 2:
            length, index = parse_varint(data, index)
            chunk = data[index : index + length]
            index += length
            if field_num == 1:
                entries[entry_idx] = parse_entry_name(chunk)
                entry_idx += 1
    return entries


def extract_media_files(apkg_path: Path, media_dir: Path) -> dict[str, str]:
    """番号付きメディアを展開し、ファイル名 -> ローカルパス の辞書を返す。"""
    media_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}

    with zipfile.ZipFile(apkg_path) as zf:
        media_index = parse_media_entries(zstd_decompress(zf.read("media")))
        for idx, filename in media_index.items():
            key = str(idx)
            if key not in zf.namelist():
                continue
            raw = zf.read(key)
            try:
                data = zstd_decompress(raw)
            except zstd.ZstdError:
                data = raw
            dest = media_dir / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            mapping[filename] = str(dest).replace("\\", "/")

    return mapping


def open_collection_db(apkg_path: Path) -> tuple[sqlite3.Connection, tempfile.TemporaryDirectory]:
    """collection.anki21b を展開して SQLite 接続を返す。"""
    tmp = tempfile.TemporaryDirectory()
    with zipfile.ZipFile(apkg_path) as zf:
        db_bytes = zstd_decompress(zf.read("collection.anki21b"))
    db_path = Path(tmp.name) / "collection.anki2"
    db_path.write_bytes(db_bytes)
    return sqlite3.connect(db_path), tmp


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def extract_sound_filename(field: str) -> str:
    match = re.search(r"\[sound:([^\]]+)\]", field)
    return match.group(1) if match else ""


def extract_image_filename(field: str) -> str:
    match = re.search(r"""<img[^>]+src=['"]([^'"]+)['"]""", field, re.I)
    return match.group(1) if match else ""


def parse_toeic_notes(conn: sqlite3.Connection) -> list[dict]:
    """TOEIC ノートタイプ（7フィールド）のノートを抽出。"""
    cur = conn.cursor()
    cur.execute(
        "SELECT flds, tags FROM notes WHERE mid = ? ORDER BY id",
        (TOEIC_MODEL_ID,),
    )
    words: list[dict] = []
    for flds, tags in cur.fetchall():
        parts = (flds or "").split("\x1f")
        while len(parts) < 7:
            parts.append("")

        word = strip_html(parts[FIELD_WORD])
        if not word:
            continue

        words.append(
            {
                "word": word,
                "pos": strip_html(parts[FIELD_POS]),
                "definition_en": strip_html(parts[FIELD_EN_EN]),
                "example": strip_html(parts[FIELD_EXAMPLE]),
                "translation_ja": strip_html(parts[FIELD_JA]),
                "audio": extract_sound_filename(parts[FIELD_AUDIO]),
                "image": extract_image_filename(parts[FIELD_IMAGE]),
                "tags": (tags or "").strip(),
            }
        )
    return words


def extract_apkg(
    apkg_path: Path,
    output_json: Path = OUTPUT_JSON,
    media_dir: Path = MEDIA_DIR,
) -> dict:
    """apkg を解析して JSON とメディアを出力。"""
    if not apkg_path.exists():
        raise FileNotFoundError(f"apkg が見つかりません: {apkg_path}")

    print(f"=== TOEIC apkg 抽出 ===")
    print(f"入力: {apkg_path}")

    media_map = extract_media_files(apkg_path, media_dir)
    print(f"メディア: {len(media_map)} ファイル -> {media_dir}")

    conn, tmp = open_collection_db(apkg_path)
    try:
        words = parse_toeic_notes(conn)
    finally:
        conn.close()
        tmp.cleanup()

    output_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_apkg": str(apkg_path),
        "model_id": TOEIC_MODEL_ID,
        "count": len(words),
        "words": words,
    }
    output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with_audio = sum(1 for w in words if w["audio"])
    with_image = sum(1 for w in words if w["image"])
    with_example = sum(1 for w in words if w["example"])

    print(f"単語: {len(words)} 件")
    print(f"  音声あり: {with_audio}")
    print(f"  画像あり: {with_image}")
    print(f"  例文あり: {with_example}")
    print(f"JSON: {output_json}")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TOEIC apkg から単語データとメディアを抽出")
    parser.add_argument(
        "--apkg",
        type=Path,
        default=DEFAULT_APKG,
        help="入力 .apkg パス",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_JSON,
        help="出力 JSON パス",
    )
    parser.add_argument(
        "--media-dir",
        type=Path,
        default=MEDIA_DIR,
        help="メディア出力ディレクトリ",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extract_apkg(args.apkg, args.output, args.media_dir)


if __name__ == "__main__":
    main()