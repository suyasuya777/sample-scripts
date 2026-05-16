"""
list_operations.py - listの操作
"""

# サンプルデータ
SCORES = [88, 72, 95, 60, 81, 77]
NAMES  = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]


# ============================================================
# 1. リストの作成・初期化
# ============================================================
def create_list():
    empty      = []                    # 空リスト
    from_range = list(range(5))        # [0, 1, 2, 3, 4]
    from_str   = list("abc")           # ['a', 'b', 'c']
    fixed      = [0] * 5               # [0, 0, 0, 0, 0]


# ============================================================
# 2. 要素の追加（append, insert, extend）
# ============================================================
def add_elements():
    names = NAMES.copy()
    names.append("Grace")             # 末尾に追加
    names.insert(0, "Heidi")          # 先頭に挿入
    names.extend(["Ivan", "Judy"])    # 複数を末尾に追加


# ============================================================
# 3. 要素の削除（remove, pop, del）
# ============================================================
def remove_elements():
    names  = NAMES.copy()
    names.remove("Dave")              # 値で削除
    popped = names.pop()              # 末尾を取り出し
    del names[0]                      # インデックスで削除


# ============================================================
# 4. 要素の検索（index, in）
# ============================================================
def search_elements():
    names = NAMES.copy()
    print("Bob" in names)             # True
    print(names.index("Carol"))       # 2

    # 安全な検索（存在しない場合 -1）
    def find(lst, val):
        return lst.index(val) if val in lst else -1

    print(find(names, "Eve"))         # 4
    print(find(names, "ZZZ"))         # -1


# ============================================================
# 5. ソート（sort, sorted, reverse）
# ============================================================
def sort_elements():
    scores = SCORES.copy()
    scores.sort()                         # 昇順（破壊的）

    scores.sort(reverse=True)             # 降順（破壊的）
  
    print("sorted   :", sorted(SCORES))   # 元リストを変更しない

    names = NAMES.copy()
    names.reverse()                       # 逆順（破壊的）


# ============================================================
# 6. スライス（list[start:end:step]）
# ============================================================
def slice_elements():
    names = NAMES.copy()
    print(names[:3])                  # 先頭3件
    print(names[-2:])                 # 末尾2件
    print(names[::2])                 # 1つおき
    print(names[1:4])                 # インデックス1〜3


# ============================================================
# 7. リスト内包表記（[x for x in list]）
# ============================================================
def list_comprehension():
    # 変換
    upper  = [n.upper() for n in NAMES]

    # フィルタ
    high   = [s for s in SCORES if s >= 80]

    # 変換 + フィルタ
    result = [(n, s) for n, s in zip(NAMES, SCORES) if s >= 80]


# ============================================================
# 8. リストの結合・コピー
# ============================================================
def combine_copy():
    a = NAMES[:3]
    b = NAMES[3:]

    merged = a + b                    # 結合

    copy1 = a.copy()                  # Shallow Copy（copy）
    copy2 = list(a)                   # Shallow Copy（list）
    copy3 = a[:]                      # Shallow Copy（スライス）

    # 重複排除して結合
    unique = list(set(a + b))
  
