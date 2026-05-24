"""
dict_operations.py - dictの操作
"""

# サンプルデータ
USER = {"name": "Alice", "age": 30, "dept": "Engineering"}

USERS = {
    "alice": {"name": "Alice", "age": 30, "score": 88},
    "bob":   {"name": "Bob",   "age": 25, "score": 72},
    "carol": {"name": "Carol", "age": 28, "score": 95},
}


# ============================================================
# 1. 辞書の作成・初期化
# ============================================================
def create_dict():
    empty    = {}                                      # 空辞書
    literal  = {"name": "Alice", "age": 30}            # リテラル
    from_kv  = dict(name="Bob", age=25)                # dict()
    from_list = dict([("name", "Carol"), ("age", 28)]) # キーと値のリストから
    keys     = ["a", "b", "c"]
    fixed    = dict.fromkeys(keys, 0)                  # 初期値0で初期化

 
# ============================================================
# 2. 要素の追加・更新（dict[key] = value）
# ============================================================
def add_update():
    user = USER.copy()
    user["email"] = "alice@example.com"   # 追加
    user["age"]   = 31                    # 更新


# ============================================================
# 3. 要素の削除（del, pop）
# ============================================================
def remove_elements():
    user = USER.copy()
    del user["dept"]                      # キーで削除
    age = user.pop("age")                 # 取り出し（戻り値あり）
    removed = user.pop("email", None)     # 存在しないキーも安全に削除


# ============================================================
# 4. キー・値の取得（keys, values, items）
# ============================================================
def get_keys_values():
    user = USER.copy()
    print(list(user.keys()))              # キー一覧
    print(list(user.values()))            # 値一覧
    print(list(user.items()))             # キーと値のペア一覧

    # items() でループ
    for key, val in user.items():
        print(f"  {key}: {val}")


# ============================================================
# 5. 安全な取得（get, setdefault）
# ============================================================
def safe_get():
    user = USER.copy()

    # get: キーが存在しない場合にデフォルト値を返す
    print(user.get("name"))               # Alice
    print(user.get("email"))              # None
    print(user.get("email", "N/A"))       # N/A

    # setdefault: キーが存在しない場合のみセット
    user.setdefault("score", 0)           # scoreがなければ0をセット
    user.setdefault("name", "Unknown")    # nameは上書きしない


# ============================================================
# 6. 辞書のマージ（update, |）
# ============================================================
def merge_dicts():
    base    = {"name": "Alice", "age": 30}
    updates = {"age": 31, "email": "alice@example.com"}

    # update: 破壊的マージ（元の辞書を変更）
    merged = base.copy()
    merged.update(updates)

    # | 演算子: 非破壊的マージ（Python 3.9+）
    merged2 = base | updates

    # |= 演算子: インプレースマージ（Python 3.9+）
    base |= updates


# ============================================================
# 7. 辞書内包表記（{k: v for k, v in dict.items()}）
# ============================================================
def dict_comprehension():
    user = USER.copy()

    # 値を変換（全値を文字列に）
    str_vals = {k: str(v) for k, v in user.items()}

    # フィルタ（値が文字列のキーのみ抽出）
    str_only = {k: v for k, v in user.items() if isinstance(v, str)}


# ============================================================
# 8. ネストした辞書の操作
# ============================================================
def nested_dict():
    users = {k: v.copy() for k, v in USERS.items()}  # 1階層コピー

    # 値の取得
    print(users["alice"]["name"])                    # Alice

    # 安全な取得（存在しないキー）
    print(users.get("dave", {}).get("name", "N/A"))  # N/A

    # 値の更新
    users["alice"]["score"] = 99
    print(users["alice"])

    # 新規キーの追加
    users["dave"] = {"name": "Dave", "age": 35, "score": 60}
    print(list(users.keys()))

    # 全ユーザーのスコア一覧
    scores = {k: v["score"] for k, v in users.items()}

    # スコアの平均
    avg = sum(scores.values()) / len(scores)

