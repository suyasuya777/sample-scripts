"""
yaml_file_read_write.py - YAML形式ファイルの読み書き

依存ライブラリ:
    pip install pyyaml
"""

import yaml
import tempfile
import os

# サンプルデータ
CONFIG = {
    "server": {
        "host": "localhost",
        "port": 8080,
        "debug": True,
    },
    "database": {
        "host": "db.example.com",
        "port": 5432,
        "name": "mydb",
    },
}

USERS = [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob",   "role": "user"},
]

MULTI_DOCS = [
    {"env": "dev",  "host": "localhost"},
    {"env": "stg",  "host": "stg.example.com"},
    {"env": "prod", "host": "prod.example.com"},
]

# 作業用の一時ファイルパス
_TMP_DIR  = tempfile.gettempdir()
YAML_FILE = os.path.join(_TMP_DIR, "config.yaml")
MULTI_FILE = os.path.join(_TMP_DIR, "multi.yaml")


# ============================================================
# 1. YAMLファイルへの書き込み（yaml.dump）
# ============================================================
def write_yaml():
    with open(YAML_FILE, "w", encoding="utf-8") as f:
        yaml.dump(CONFIG, f, allow_unicode=True, default_flow_style=False, indent=2)


# ============================================================
# 2. YAMLファイルの読み込み（yaml.safe_load）
# ============================================================
def read_yaml():
    with open(YAML_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print("port:", data["server"]["port"])


# ============================================================
# 3. 複数ドキュメントの書き込み・読み込み（yaml.safe_load_all）
# ============================================================
def read_write_multi_docs():
    # 書き込み（--- で区切られた複数ドキュメント）
    with open(MULTI_FILE, "w", encoding="utf-8") as f:
        yaml.dump_all(MULTI_DOCS, f, allow_unicode=True, default_flow_style=False)

    # 読み込み
    with open(MULTI_FILE, encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))

    for doc in docs:
        print(f"  {doc['env']}: {doc['host']}")


# ============================================================
# 4. PythonオブジェクトとYAMLの相互変換（文字列）
# ============================================================
def convert_object_yaml():
    # Python → YAML文字列
    yaml_str = yaml.dump(USERS, allow_unicode=True, default_flow_style=False)

    # YAML文字列 → Python
    loaded = yaml.safe_load(yaml_str)
      print("type:", type(loaded), "| 件数:", len(loaded))

# ============================================================
# 5. 日本語（マルチバイト）の扱い
# ============================================================
def japanese_yaml():
    jp_data = {
        "名前": "田中 太郎",
        "部署": "エンジニアリング",
        "スコア": 95,
    }

    # allow_unicode=True で日本語をそのまま出力
    yaml_str = yaml.dump(jp_data, allow_unicode=True, default_flow_style=False)
    print("【allow_unicode=True】\n", yaml_str)

    # allow_unicode=False（デフォルト）だとエスケープされる
    yaml_escaped = yaml.dump(jp_data, allow_unicode=False, default_flow_style=False)
    print("【allow_unicode=False】\n", yaml_escaped)

    # 読み込みは共通
    loaded = yaml.safe_load(yaml_str)
    print("読み込み:", loaded)

