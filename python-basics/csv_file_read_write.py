"""
csv_file_read_write.py - CSVファイルの読み書き
"""

import csv
import os

# サンプルデータ
FIELDNAMES = ["name", "dept", "score"]
ROWS = [
    ["Alice", "Engineering", 88],
    ["Bob",   "Sales",       72],
    ["Carol", "Engineering", 95],
]
DICT_ROWS = [
    {"name": "Alice", "dept": "Engineering", "score": 88},
    {"name": "Bob",   "dept": "Sales",       "score": 72},
    {"name": "Carol", "dept": "Engineering", "score": 95},
]

CSV_FILE  = "sample.csv"
TSV_FILE  = "sample.tsv"


# ============================================================
# 1. CSVファイルの書き込み（csv.writer）
# ============================================================
def write_csv():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDNAMES)   # ヘッダー行
        writer.writerows(ROWS)        # データ行（一括）


# ============================================================
# 2. CSVファイルの読み込み（csv.reader）
# ============================================================
def read_csv():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)         # ヘッダー行を取得
        for row in reader:
            print(f"  {row}")


# ============================================================
# 3. 辞書形式での書き込み（csv.DictWriter）
# ============================================================
def write_csv_dict():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()          # ヘッダー行（自動）
        writer.writerows(DICT_ROWS)   # 辞書リストを一括書き込み


# ============================================================
# 4. 辞書形式での読み込み（csv.DictReader）
# ============================================================
def read_csv_dict():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"  {dict(row)}")


# ============================================================
# 5. 区切り文字・クォートの設定（delimiter, quotechar）
# ============================================================
def write_tsv():
    """TSV形式（タブ区切り）で書き込む"""
    with open(TSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(FIELDNAMES)
        writer.writerows(ROWS)


def read_tsv():
    """TSV形式（タブ区切り）で読み込む"""
    with open(TSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        for row in reader:
            print(f"  {row}")


def write_csv_quote():
    """クォート設定あり（カンマを含む値を扱う場合）"""
    rows = [
        ["Alice",       "Engineering, AI", 88],
        ["Bob",         "Sales, Retail",   72],
    ]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(
            f,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,  # 必要な場合のみクォート
        )
        writer.writerow(FIELDNAMES)
        writer.writerows(rows)


# ============================================================
# 6. エンコーディングの指定（UTF-8 / UTF-8 BOM / CP932）
# ============================================================
def write_csv_encoding():
    """Excel で開くために UTF-8 BOM で書き込む"""
    rows_jp = [
        {"name": "山田太郎", "dept": "営業",   "score": 88},
        {"name": "鈴木花子", "dept": "開発",   "score": 95},
    ]
    fields = ["name", "dept", "score"]

    # UTF-8 BOM（Excel対応）
    bom_file = "sample_bom.csv"
    with open(bom_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_jp)

    # CP932（Shift-JIS / Windows標準）
    cp932_file = "sample_cp932.csv"
    with open(cp932_file, "w", newline="", encoding="cp932") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_jp)
  
