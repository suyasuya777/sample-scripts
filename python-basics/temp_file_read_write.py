"""
temp_file_read_write.py - 一時ファイルの読み書き
"""

import tempfile
import os
import json
import csv

SAMPLE_TEXT = "Hello, Tempfile!\n日本語テキスト\n"
SAMPLE_JSON = {"name": "Alice", "score": 88}
SAMPLE_ROWS = [["name", "score"], ["Alice", "88"], ["Bob", "72"]]


# ============================================================
# 1. TemporaryFile - 無名一時ファイル（パス不要な場合）
# ============================================================
def use_temporary_file():
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as f:
        f.write(SAMPLE_TEXT)
        f.seek(0)                          # 先頭に戻す
        content = f.read()
        print(content)
    # with を抜けると自動削除（パス取得不可）


# ============================================================
# 2. NamedTemporaryFile - 名前付き一時ファイル（パスが必要な場合）
# ============================================================
def use_named_temporary_file():
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        prefix="app_",
        encoding="utf-8",
        delete=True,                       # with を抜けると自動削除
    ) as f:
        print("path:", f.name)             # パスを取得

        f.write(SAMPLE_TEXT)
        f.flush()                          # バッファをディスクに書き出す

        # 同じファイルを別途開いて読み込み
        with open(f.name, encoding="utf-8") as rf:
            content = rf.read()
            print(content)

    print("exists:", os.path.exists(f.name))   # False（削除済み）


# ============================================================
# 3. TemporaryDirectory - 一時ディレクトリ
# ============================================================
def use_temporary_directory():
    with tempfile.TemporaryDirectory(prefix="workdir_") as tmpdir:
        print("tmpdir:", tmpdir)

        # 一時ディレクトリ内にファイルを作成
        filepath = os.path.join(tmpdir, "data.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(SAMPLE_JSON, f, ensure_ascii=False, indent=2)

        # 読み込み
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            print(data)

    print("exists:", os.path.exists(tmpdir))   # False（削除済み）
