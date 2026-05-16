"""
memory_file_read_write.py - メモリファイルの読み書き
"""

import io
import csv
import zipfile
from pathlib import Path

# サンプルデータ
EMPLOYEES = [
    {"name": "Alice", "dept": "Engineering", "score": 88},
    {"name": "Bob",   "dept": "Sales",        "score": 72},
    {"name": "Carol", "dept": "Engineering",  "score": 95},
]
TEXT_DATA   = "Hello, World!\nLine 2\nLine 3\n"
BINARY_DATA = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"  # PNG ヘッダー模擬


# ============================================================
# 1. io.StringIO によるテキストのメモリ上読み書き
# ============================================================
def stringio_basic():
    buf = io.StringIO()

    # 書き込み
    buf.write("Line 1\n")
    buf.write("Line 2\n")
    buf.write("Line 3\n")

    # 先頭に戻って読み込み
    buf.seek(0)
    print(buf.read())

    # getvalue: seek 位置に関わらず全内容取得
    print(repr(buf.getvalue()))


# ============================================================
# 2. io.BytesIO によるバイナリのメモリ上読み書き
# ============================================================
def bytesio_basic():
    buf = io.BytesIO()

    # 書き込み
    buf.write(BINARY_DATA)
    buf.write(b"\x00" * 8)

    # 先頭に戻って読み込み
    buf.seek(0)
    data = buf.read()
    print(f"size: {len(data)} bytes")
    print(f"hex : {data.hex()}")


# ============================================================
# 3. read / write / seek / getvalue の基本操作
# ============================================================
def seek_operations():
    buf = io.StringIO(TEXT_DATA)

    print(buf.read(5))          # 先頭5文字を読む
    print(buf.tell())           # 現在位置: 5
    buf.seek(0)                 # 先頭に戻る
    print(buf.readline())       # 1行読む
    buf.seek(0, 2)              # 末尾に移動（whence=2）
    print("end pos:", buf.tell())
    buf.seek(0)
    print("getvalue:", repr(buf.getvalue()[:20]))


# ============================================================
# 4. メモリ上での CSV 生成・パース
# ============================================================
def csv_on_memory():
    # --- CSV 生成（メモリ上に書き込み）---
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["name", "dept", "score"])
    writer.writeheader()
    writer.writerows(EMPLOYEES)

    csv_text = buf.getvalue()
    print("--- generated CSV ---")
    print(csv_text)

    # --- CSV パース（メモリ上から読み込み）---
    buf.seek(0)
    reader = csv.DictReader(buf)
    rows = list(reader)
    print("--- parsed rows ---")
    for row in rows:
        print(dict(row))


# ============================================================
# 5. メモリ上での ZIP ファイル操作
# ============================================================
def zip_on_memory():
    # --- メモリ上に ZIP を作成 ---
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt",  "This is readme.")
        zf.writestr("data/a.txt", "Content of A.")
        zf.writestr("data/b.txt", "Content of B.")

    print(f"ZIP size: {zip_buf.tell()} bytes")

    # --- メモリ上の ZIP を読み込み ---
    zip_buf.seek(0)
    with zipfile.ZipFile(zip_buf, mode="r") as zf:
        print("ZIP contents:", zf.namelist())
        print(zf.read("readme.txt").decode())


# ============================================================
# 6. ファイルと同じインターフェース（csv + zipfile との組み合わせ）
# ============================================================
def unified_interface():
    """
    CSV をメモリ上で生成し、そのまま ZIP に格納する。
    実ファイルへの一時書き出しが不要になる。
    """
    # Step1: CSV をメモリ上で生成
    csv_buf = io.StringIO()
    writer = csv.DictWriter(csv_buf, fieldnames=["name", "dept", "score"])
    writer.writeheader()
    writer.writerows(EMPLOYEES)
    csv_bytes = csv_buf.getvalue().encode("utf-8")

    # Step2: ZIP をメモリ上で生成（CSV を格納）
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("employees.csv", csv_bytes)

    print(f"CSV+ZIP on memory: {zip_buf.tell()} bytes")
    return zip_buf


# ============================================================
# 7. メモリファイルを実ファイルに書き出す
# ============================================================
def write_to_file():
    output_dir = Path("/tmp/memory_sample")
    output_dir.mkdir(exist_ok=True)

    # StringIO → テキストファイル
    text_buf = io.StringIO(TEXT_DATA)
    text_path = output_dir / "output.txt"
    text_path.write_text(text_buf.getvalue(), encoding="utf-8")
    print(f"text written: {text_path}")

    # BytesIO（ZIP）→ バイナリファイル
    zip_buf = unified_interface()
    zip_buf.seek(0)
    zip_path = output_dir / "output.zip"
    zip_path.write_bytes(zip_buf.read())
    print(f"zip  written: {zip_path}")

    # 検証：書き出した ZIP を開いて確認
    with zipfile.ZipFile(zip_path) as zf:
        print("zip contents:", zf.namelist())
        print(zf.read("employees.csv").decode("utf-8")[:80])

