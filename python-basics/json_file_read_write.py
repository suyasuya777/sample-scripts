"""
json_file_read_write.py - JSONファイルの読み書き
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

# サンプルデータ
SAMPLE = {
    "name": "Alice",
    "age": 30,
    "dept": "開発部",
    "joined": "2020-04-01",
    "scores": [88, 72, 95],
    "active": True,
}

JSON_FILE = Path("sample.json")


# ============================================================
# 1. JSONファイルへの書き込み（json.dump）
# ============================================================
def write_json():
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(SAMPLE, f, indent=2, ensure_ascii=False)
    print(JSON_FILE.read_text(encoding="utf-8"))


# ============================================================
# 2. JSONファイルの読み込み（json.load）
# ============================================================
def read_json():
    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)
    print(data["dept"])          # 開発部
    print(data["scores"][0])     # 88


# ============================================================
# 3. JSON文字列への変換（json.dumps）
# ============================================================
def to_json_string():
    # 基本
    s = json.dumps(SAMPLE)
  
    # インデント・ソート・日本語
    s = json.dumps(SAMPLE, indent=2, sort_keys=True, ensure_ascii=False)


# ============================================================
# 4. JSON文字列のパース（json.loads）
# ============================================================
def parse_json_string():
    s = '{"name": "Bob", "age": 25, "dept": "営業部"}'
    data = json.loads(s)
    print(data["dept"])          # 営業部


# ============================================================
# 5. インデント・ソートの設定（indent, sort_keys）
# ============================================================
def indent_sort():
    data = {"z_key": 1, "a_key": 2, "m_key": 3}

    print(json.dumps(data, indent=4))                  # インデント4
    print(json.dumps(data, indent=4, sort_keys=True))  # キーをソート


# ============================================================
# 6. 日本語の扱い（ensure_ascii=False）
# ============================================================
def japanese_handling():
    data = {"部署": "開発部", "氏名": "山田 太郎", "役職": "リーダー"}

    # ensure_ascii=True（デフォルト）→ 日本語がエスケープされる
    print(json.dumps(data))

    # ensure_ascii=False → 日本語がそのまま出力される
    print(json.dumps(data, ensure_ascii=False, indent=2))

