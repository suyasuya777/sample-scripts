"""
zip_file_compress_extract.py - ZIPファイルの圧縮・展開
"""

import io
import os
import zipfile

# サンプルデータ（テキストファイルの内容）
SAMPLE_FILES = {
    "alice.txt":  "Hello, I am Alice.\n",
    "bob.txt":    "Hello, I am Bob.\n",
    "carol.txt":  "Hello, I am Carol.\n",
}

WORK_DIR = "/tmp/zip_sample"
ZIP_PATH = "/tmp/zip_sample/sample.zip"


def _setup():
    """作業ディレクトリとサンプルファイルを準備する。"""
    os.makedirs(WORK_DIR, exist_ok=True)
    for name, content in SAMPLE_FILES.items():
        with open(os.path.join(WORK_DIR, name), "w") as f:
            f.write(content)


# ============================================================
# 1. ZIPファイルの作成・圧縮（ZipFile, write）
# ============================================================
def create_zip():
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in SAMPLE_FILES:
            zf.write(os.path.join(WORK_DIR, name), arcname=name)


# ============================================================
# 2. ZIPファイルの展開（extractall, extract）
# ============================================================
def extract_zip():
    out_dir = os.path.join(WORK_DIR, "extracted")

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        # 全ファイルを展開
        zf.extractall(out_dir)

        # 1ファイルだけ展開
        zf.extract("alice.txt", os.path.join(WORK_DIR, "single"))


# ============================================================
# 3. ZIP内のファイル一覧取得（namelist, infolist）
# ============================================================
def list_zip():
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        # ファイル名一覧
        print("namelist:", zf.namelist())

        # 詳細情報
        for info in zf.infolist():
            print(f"  {info.filename:<12} "
                  f"size:{info.file_size:>6}B  "
                  f"compressed:{info.compress_size:>6}B")


# ============================================================
# 4. ZIPファイルへのファイル追加
# ============================================================
def add_to_zip():
    new_file = os.path.join(WORK_DIR, "dave.txt")
    with open(new_file, "w") as f:
        f.write("Hello, I am Dave.\n")

    # "a" モードで既存ZIPに追記
    with zipfile.ZipFile(ZIP_PATH, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(new_file, arcname="dave.txt")

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        print("追加後:", zf.namelist())


# ============================================================
# 5. パスワード付きZIPの展開（pwd）
# ============================================================
def extract_with_password():
    """
    注意: Pythonの zipfile はパスワード付きZIPの【読み込み】のみ対応。
          パスワード付きZIPの作成には pyminizip 等の外部ライブラリが必要。
    ここでは読み込み方法のみ示す。
    """
    pwd_zip = os.path.join(WORK_DIR, "password_protected.zip")

    if not os.path.exists(pwd_zip):
        print("パスワード付きZIPが存在しないためスキップ")
        return

    password = b"secret123"
    out_dir  = os.path.join(WORK_DIR, "pwd_extracted")

    with zipfile.ZipFile(pwd_zip, "r") as zf:
        # 全ファイルをパスワード付きで展開
        zf.extractall(out_dir, pwd=password)

        # 1ファイルだけ展開
        zf.extract("alice.txt", out_dir, pwd=password)

    print("パスワード付きZIP展開完了:", os.listdir(out_dir))
