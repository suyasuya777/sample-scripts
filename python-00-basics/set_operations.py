"""
set_operations.py - setの操作
"""

# サンプルデータ
SKILLS_A = {"python", "aws", "docker", "linux"}
SKILLS_B = {"aws", "terraform", "docker", "go"}

NAMES = ["Alice", "Bob", "Carol", "Alice", "Bob", "Dave"]  # 重複あり


# ============================================================
# 1. セットの作成・初期化
# ============================================================
def create_set():
    empty     = set()                          # 空セット（{} はdictになるので注意）
    literal   = {"python", "aws", "docker"}    # リテラル
    from_list = set(NAMES)                     # リストから（重複は自動的に排除）
    from_str  = set("hello")                   # {'h', 'e', 'l', 'o'}
    frozen    = frozenset({"a", "b"})          # イミュータブルなセット（変更不可）

    # セットは「重複なし・順序なし」のコレクション
    print(len(from_list))                      # 4（Alice, Bob, Carol, Dave）


# ============================================================
# 2. 要素の追加（add, update）
# ============================================================
def add_elements():
    skills = SKILLS_A.copy()
    skills.add("git")                          # 1件追加
    skills.add("aws")                          # 既存の値は無視される（エラーにならない）
    skills.update(["k8s", "ansible"])          # 複数を追加
    skills |= {"bash"}                         # |= 演算子でも追加できる


# ============================================================
# 3. 要素の削除（remove, discard, pop, clear）
# ============================================================
def remove_elements():
    skills = SKILLS_A.copy()
    skills.remove("linux")                     # 値で削除（存在しないとKeyError）
    skills.discard("perl")                     # 存在しなくてもエラーにならない
    item = skills.pop()                        # 任意の1件を取り出し（順序は不定）
    skills.clear()                             # 全削除


# ============================================================
# 4. 要素の検索・判定（in, len）
# ============================================================
def search_elements():
    skills = SKILLS_A.copy()
    print("aws" in skills)                     # True
    print("java" not in skills)                # True
    print(len(skills))                         # 4

    # listのinはO(n)、setのinはO(1) → 大量データの存在チェックはsetが速い
    names = set(NAMES)
    print("Eve" in names)                      # False


# ============================================================
# 5. 集合演算（和・積・差・対称差）
# ============================================================
def set_operations():
    a, b = SKILLS_A, SKILLS_B

    # 和集合: どちらかに含まれる
    print(a | b)                               # a.union(b)
    # 積集合: 両方に含まれる
    print(a & b)                               # a.intersection(b)     -> {'aws', 'docker'}
    # 差集合: aにだけ含まれる
    print(a - b)                               # a.difference(b)       -> {'python', 'linux'}
    # 対称差: どちらか一方にだけ含まれる
    print(a ^ b)                               # a.symmetric_difference(b)

    # メソッド版はlistなどのiterableも引数に取れる
    print(a.union(["git", "aws"]))
    print(a.intersection(NAMES))               # set()

    # インプレース版（破壊的）
    c = a.copy()
    c |= b                                     # c.update(b)
    c &= b                                     # c.intersection_update(b)
    c -= b                                     # c.difference_update(b)


# ============================================================
# 6. 包含関係の判定（issubset, issuperset, isdisjoint）
# ============================================================
def compare_sets():
    a     = SKILLS_A.copy()
    small = {"aws", "docker"}

    print(small.issubset(a))                   # True   （small <= a）
    print(a.issuperset(small))                 # True   （a >= small）
    print(small < a)                           # True   （真部分集合）
    print(a.isdisjoint({"java", "ruby"}))      # True   （共通要素なし）
    print(a == SKILLS_A)                       # True   （要素が同じなら等しい）


# ============================================================
# 7. セット内包表記（{x for x in iterable}）
# ============================================================
def set_comprehension():
    # 変換（重複は自動的に排除される）
    upper  = {n.upper() for n in NAMES}

    # フィルタ
    short  = {n for n in NAMES if len(n) <= 3}         # {'Bob'}

    # 変換 + フィルタ
    initials = {n[0] for n in NAMES if n.startswith(("A", "B"))}


# ============================================================
# 8. list / dict との連携
# ============================================================
def with_list_and_dict():
    # 重複排除（順序は保証されない）
    unique = list(set(NAMES))

    # 重複排除（順序を保ちたい場合はdictを使う）
    unique_ordered = list(dict.fromkeys(NAMES))

    # 2つのリストの差分を取る
    before = ["a", "b", "c"]
    after  = ["b", "c", "d"]
    added   = set(after) - set(before)          # {'d'}  追加されたもの
    removed = set(before) - set(after)          # {'a'}  削除されたもの
    kept    = set(before) & set(after)          # {'b', 'c'}

    # dictのkeys()は集合演算に対応している
    d1 = {"name": "Alice", "age": 30}
    d2 = {"name": "Bob", "email": "bob@example.com"}
    print(d1.keys() & d2.keys())                # {'name'}  共通キー
    print(d1.keys() - d2.keys())                # {'age'}   d1にだけあるキー

    # ソートしてlistに戻す（setは順序を持たないため）
    print(sorted(set(NAMES)))
