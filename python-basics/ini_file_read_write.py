"""
ini_file_read_write.py - INI形式ファイルの読み書き
"""

import configparser
import io

# サンプルINI文字列（ファイルの代わりに使用）
SAMPLE_INI = """
[DEFAULT]
env     = production
timeout = 30
base_dir = /opt/myapp

[database]
host = localhost
port = 5432
name = mydb
user = admin
pool_size = 5
ssl = true
log_dir = %(base_dir)s/logs

[server]
host = 0.0.0.0
port = 8080
debug = false
workers = 4

[cache]
host = localhost
port = 6379
ttl  = 300
"""

SAMPLE_FILE = "sample.ini"


# ============================================================
# 1. configparser モジュールの基本
# ============================================================
def basic_usage():
    config = configparser.ConfigParser()
    config.read_string(SAMPLE_INI)
    print(config.sections())           # ['database', 'server', 'cache']
    print(config.defaults())           # DEFAULT セクションの内容


# ============================================================
# 2. INIファイルの読み込み（read, read_string）
# ============================================================
def read_ini():
    config = configparser.ConfigParser()

    # 文字列から読み込み
    config.read_string(SAMPLE_INI)
    print("[read_string]", config["database"]["host"])

    # ファイルに書き出してから read で読み込み
    with open(SAMPLE_FILE, "w", encoding="utf-8") as f:
        config.write(f)

    config2 = configparser.ConfigParser()
    config2.read(SAMPLE_FILE, encoding="utf-8")
    print("[read file] ", config2["server"]["port"])

    # ファイルが存在しない場合は空のまま（例外は発生しない）
    config3 = configparser.ConfigParser()
    result = config3.read("not_found.ini")
    print("[not found]", result)       # [] （空リスト）


# ============================================================
# 3. セクション・キーの取得（sections, options, get）
# ============================================================
def get_sections_keys():
    config = configparser.ConfigParser()
    config.read_string(SAMPLE_INI)

    # セクション一覧（DEFAULT は含まれない）
    print(config.sections())

    # セクション内のキー一覧（DEFAULT のキーも含まれる）
    print(config.options("database"))

    # 値の取得
    print(config.get("database", "host"))

    # 存在しないキーのデフォルト値
    print(config.get("database", "charset", fallback="utf8"))

    # セクションを辞書として取得
    db = dict(config["database"])
    print(db)


# ============================================================
# 4. 型変換（getint, getfloat, getboolean）
# ============================================================
def type_conversion():
    config = configparser.ConfigParser()
    config.read_string(SAMPLE_INI)

    port      = config.getint    ("database", "port")       # int
    pool_size = config.getint    ("database", "pool_size")  # int
    ttl       = config.getfloat  ("cache",    "ttl")        # float
    ssl       = config.getboolean("database", "ssl")        # bool
    debug     = config.getboolean("server",   "debug")      # bool

    print(f"port={port}({type(port).__name__}), pool={pool_size}, "
          f"ttl={ttl}({type(ttl).__name__}), ssl={ssl}, debug={debug}")


# ============================================================
# 5. INIファイルへの書き込み（set, write）
# ============================================================
def write_ini():
    config = configparser.ConfigParser()
    config.read_string(SAMPLE_INI)

    # 既存キーの値を更新
    config.set("database", "host", "db.example.com")
    config.set("server",   "port", "443")

    # ファイルに書き込み
    with open(SAMPLE_FILE, "w", encoding="utf-8") as f:
        config.write(f)

    # 書き込み結果を確認
    config2 = configparser.ConfigParser()
    config2.read(SAMPLE_FILE, encoding="utf-8")
    print(config2.get("database", "host"))   # db.example.com
    print(config2.get("server",   "port"))   # 443


# ============================================================
# 6. セクションの追加・削除（add_section, remove_section）
# ============================================================
def add_remove_section():
    config = configparser.ConfigParser()
    config.read_string(SAMPLE_INI)

    # セクションの追加
    config.add_section("mail")
    config.set("mail", "host", "smtp.example.com")
    config.set("mail", "port", "587")
    config.set("mail", "tls",  "true")
    print("追加後:", config.sections())

    # セクションの削除
    config.remove_section("cache")
    print("削除後:", config.sections())

    # キーの削除
    config.remove_option("database", "pool_size")
    print("pool_size 削除後:", config.options("database"))


# ============================================================
# 7. DEFAULT セクションの活用
# ============================================================
def use_default_section():
    config = configparser.ConfigParser()
    config.read_string(SAMPLE_INI)

    # DEFAULT の値は全セクションで参照できる
    print(config.get("database", "env"))     # production（DEFAULTから）
    print(config.get("server",   "timeout")) # 30（DEFAULTから）

    # DEFAULT に新しい値を追加
    config.defaults()["version"] = "1.0"
    print(config.get("database", "version")) # 1.0
    print(config.get("cache",    "version")) # 1.0

