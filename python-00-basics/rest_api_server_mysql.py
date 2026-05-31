"""
rest_api_server_mysql.py - サーバ側のREST API処理（MySQL）

事前準備:
    pip install flask PyMySQL

    # MySQLでDBとテーブルを作成
    # mysql -u root -p で接続後:
    # CREATE DATABASE itemsdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

起動方法:
    python rest_api_server_mysql.py

動作確認:
    curl http://localhost:5000/items
    curl http://localhost:5000/items/1
    curl -X POST   http://localhost:5000/items -d "name=ノートPC&price=98000"
    curl -X PUT    http://localhost:5000/items/1 -d "name=PC&price=80000"
    curl -X DELETE http://localhost:5000/items/1
"""

import pymysql
import pymysql.cursors
from flask import Flask, request, g

app = Flask(__name__)

# ============================================================
# DB接続設定
# ============================================================
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "db":       "itemsdb",
    "user":     "root",
    "password": "root",
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.Cursor,
}

# ============================================================
# DBの接続・切断
# ============================================================
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = pymysql.connect(**DB_CONFIG)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db(db):
    """テーブルの作成"""
    with db.cursor() as curs:
        curs.execute(
            "CREATE TABLE IF NOT EXISTS items ("
            "id    INT          NOT NULL AUTO_INCREMENT PRIMARY KEY, "
            "name  VARCHAR(255) NOT NULL, "
            "price FLOAT        NOT NULL)"
        )
    db.commit()

# ============================================================
# ルーティングの定義
# ============================================================

# GET /items - 一覧取得（クエリパラメータ: min_price）
@app.route("/items", methods=["GET"])
def get_items():
    db = get_db()
    init_db(db)

    min_price = request.args.get("min_price", type=float)

    with db.cursor() as curs:
        if min_price is not None:
            curs.execute("SELECT * FROM items WHERE price >= %s", (min_price,))
        else:
            curs.execute("SELECT * FROM items")
        rows = curs.fetchall()

    if not rows:
        return "No items", 404

    result = "\n".join(f"{r[0]}: {r[1]} ({r[2]}円)" for r in rows)
    return result, 200


# GET /items/<item_id> - 1件取得（パスパラメータ）
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    db = get_db()
    init_db(db)

    with db.cursor() as curs:
        curs.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        row = curs.fetchone()

    if not row:
        return f"Item {item_id} not found", 404

    return f"{row[0]}: {row[1]} ({row[2]}円)", 200


# POST /items - 新規作成
@app.route("/items", methods=["POST"])
def create_item():
    db = get_db()
    init_db(db)

    name  = request.values.get("name")
    price = request.values.get("price", type=float)

    if not name or price is None:
        return "name and price are required", 400
    if price <= 0:
        return "price must be greater than 0", 400

    with db.cursor() as curs:
        curs.execute("INSERT INTO items(name, price) VALUES(%s, %s)", (name, price))
    db.commit()
    return f"created: {name} ({price}円)", 201


# PUT /items/<item_id> - 更新
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    db = get_db()
    init_db(db)

    with db.cursor() as curs:
        curs.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        if not curs.fetchone():
            return f"Item {item_id} not found", 404

    name  = request.values.get("name")
    price = request.values.get("price", type=float)

    if not name and price is None:
        return "name or price is required", 400

    with db.cursor() as curs:
        if name and price is not None:
            curs.execute("UPDATE items SET name = %s, price = %s WHERE id = %s", (name, price, item_id))
        elif name:
            curs.execute("UPDATE items SET name = %s WHERE id = %s", (name, item_id))
        else:
            curs.execute("UPDATE items SET price = %s WHERE id = %s", (price, item_id))

    db.commit()
    return f"updated item {item_id}", 200


# DELETE /items/<item_id> - 削除
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    db = get_db()
    init_db(db)

    with db.cursor() as curs:
        curs.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        if not curs.fetchone():
            return f"Item {item_id} not found", 404

        curs.execute("DELETE FROM items WHERE id = %s", (item_id,))
    db.commit()
    return f"deleted item {item_id}", 200


# ============================================================
# サーバの起動
# ============================================================
def main():
    app.debug = True
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
