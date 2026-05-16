"""
loop_operations.py - ループの操作
"""

import itertools

# サンプルデータ
NAMES  = ["Alice", "Bob", "Carol", "Dave", "Eve"]
SCORES = [88, 72, 95, 60, 81]
DEPT   = ["Engineering", "Sales", "Engineering", "HR", "Sales"]


# ============================================================
# 1. for ループの基本
# ============================================================
def for_basic():
    for name in NAMES:
        print(name, end=" ")

    # インデックスアクセス
    for i in range(len(NAMES)):
        print(f"{i}: {NAMES[i]}", end=" ")


# ============================================================
# 2. while ループの基本
# ============================================================
def while_basic():
    # カウントアップ
    count = 0
    while count < 3:
        print(count, end=" ")
        count += 1
    print()

    # リストが空になるまで処理
    queue = NAMES.copy()
    while queue:
        print(queue.pop(0), end=" ")
    print()


# ============================================================
# 3. range を使ったループ
# ============================================================
def range_loop():
    print(list(range(5)))           # [0, 1, 2, 3, 4]
    print(list(range(1, 6)))        # [1, 2, 3, 4, 5]
    print(list(range(0, 10, 2)))    # [0, 2, 4, 6, 8]
    print(list(range(5, 0, -1)))    # [5, 4, 3, 2, 1]


# ============================================================
# 4. enumerate によるインデックス付きループ
# ============================================================
def enumerate_loop():
    # 基本（0始まり）
    for i, name in enumerate(NAMES):
        print(f"{i}: {name}", end="  ")

    # 1始まり
    for i, name in enumerate(NAMES, start=1):
        print(f"{i}: {name}", end="  ")

 
# ============================================================
# 5. zip による複数リストの同時ループ
# ============================================================
def zip_loop():
    # 2リストを同時にループ
    for name, score in zip(NAMES, SCORES):
        print(f"{name}: {score}", end="  ")

    # zip でリストを辞書に変換
    score_map = dict(zip(NAMES, SCORES))


# ============================================================
# 6. ネストしたループ
# ============================================================
def nested_loop():
    # 掛け算テーブル（3x3）
    for i in range(1, 4):
        for j in range(1, 4):
            print(f"{i*j:2}", end=" ")
        print()

    # 部署ごとに集計
    depts = set(DEPT)
    for dept in sorted(depts):
        members = [n for n, d in zip(NAMES, DEPT) if d == dept]
        print(f"{dept}: {members}")


# ============================================================
# 7. ループ内包表記（list / dict / set）
# ============================================================
def comprehension_loop():
    # list内包表記
    high_scores = [s for s in SCORES if s >= 80]

    # dict内包表記
    score_map = {n: s for n, s in zip(NAMES, SCORES) if s >= 80}

    # set内包表記（重複排除）
    unique_depts = {d for d in DEPT}

    # ネスト内包表記（行列の転置）
    matrix    = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    transposed = [[row[i] for row in matrix] for i in range(3)]


# ============================================================
# 8. itertools を使った高度なループ
# ============================================================
def itertools_loop():
    # chain: 複数のイテラブルを連結
    a = ["Alice", "Bob"]
    b = ["Carol", "Dave"]
    print("chain    :", list(itertools.chain(a, b)))

    # combinations: 組み合わせ（順序なし）
    print("combinations:", list(itertools.combinations(["A", "B", "C"], 2)))

    # permutations: 順列（順序あり）
    print("permutations:", list(itertools.permutations(["A", "B", "C"], 2)))

    # product: デカルト積（全組み合わせ）
    sizes   = ["S", "M"]
    colors  = ["Red", "Blue"]
    print("product  :", list(itertools.product(sizes, colors)))

    # groupby: キーでグループ化
    data = sorted(zip(NAMES, DEPT), key=lambda x: x[1])
    for dept, members in itertools.groupby(data, key=lambda x: x[1]):
        print(f"groupby  {dept}: {[m[0] for m in members]}")

    # islice: イテラブルを途中で切り取り
    print("islice   :", list(itertools.islice(range(100), 3, 8)))

    # cycle: 無限ループ（先頭n件だけ取得）
    cycled = list(itertools.islice(itertools.cycle(["A", "B", "C"]), 7))
    print("cycle    :", cycled)

