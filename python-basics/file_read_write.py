"""
file_read_write.py - ファイルの読み書き
"""

import os
import shutil
from pathlib import Path

# 作業ディレクトリ
WORK_DIR = Path("work")
WORK_DIR.mkdir(exist_ok=True)

TEXT_FILE   = WORK_DIR / "sample.txt"
COPY_FILE   = WORK_DIR / "sample_copy.txt"
MOVE_FILE   = WORK_DIR / "sample_moved.txt"
BINARY_FILE = WORK_DIR / "sample.bin"


# ============================================================
# 1. ファイルのオープン・クローズ（open, with）
# ============================================================
def open_close():
    # with を使うと自動でクローズされる（推奨）
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("Hello, World!\n")

    # with を使うと自動でクローズされる（推奨）
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print(content)


# ============================================================
# 2. テキストファイルの読み込み（read, readline, readlines）
# ============================================================
def read_text():
    # 事前にファイルを準備
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("line1\nline2\nline3\n")

    # read: ファイル全体を1つの文字列で読み込む
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    print("[read]", repr(content))

    # readline: 1行ずつ読み込む
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        line = f.readline()
    print("[readline]", repr(line))

    # readlines: 全行をリストで読み込む
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print("[readlines]", lines)

    # イテレータで1行ずつ処理（大きなファイルに有効）
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            print("[iter]", line.strip())


# ============================================================
# 3. テキストファイルの書き込み（write, writelines）
# ============================================================
def write_text():
    # write: 文字列を書き込む（上書き）
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("line1\n")
        f.write("line2\n")

    # writelines: リストを書き込む（改行は自分で付与）
    lines = ["line3\n", "line4\n", "line5\n"]
    with open(TEXT_FILE, "a", encoding="utf-8") as f:
        f.writelines(lines)

 
 # ============================================================
# 4. ファイルの存在確認（os.path.exists, pathlib.Path.exists）
# ============================================================
def check_exists():
    # pathlib.Path.exists（推奨）
    path = Path(TEXT_FILE)
    if path.exists():
        print(f"[pathlib]  {path} は存在します")

    # ファイル / ディレクトリの判別
    print(f"[is_file] {path.is_file()}")
    print(f"[is_dir]  {path.is_dir()}")

    # 存在しないファイルの確認
    missing = Path("not_found.txt")
    print(f"[missing] {missing.exists()}")


# ============================================================
# 5. ファイルのコピー・移動・削除（shutil）
# ============================================================
def copy_move_delete():
    # コピー（内容のみ）
    shutil.copy(TEXT_FILE, COPY_FILE)
    print(f"[copy]   {COPY_FILE.exists()}")

    # コピー（メタデータも含む）
    shutil.copy2(TEXT_FILE, WORK_DIR / "sample_copy2.txt")
    print(f"[copy2]  {(WORK_DIR / 'sample_copy2.txt').exists()}")

    # 移動（リネームにも使える）
    shutil.move(str(COPY_FILE), str(MOVE_FILE))
    print(f"[move]   コピー元:{COPY_FILE.exists()}  移動先:{MOVE_FILE.exists()}")

    # ファイルの削除
    MOVE_FILE.unlink()
    print(f"[unlink] {MOVE_FILE.exists()}")

    # ディレクトリごと削除
    sub_dir = WORK_DIR / "subdir"
    sub_dir.mkdir(exist_ok=True)
    (sub_dir / "temp.txt").write_text("temp")
    shutil.rmtree(sub_dir)
    print(f"[rmtree] {sub_dir.exists()}")

