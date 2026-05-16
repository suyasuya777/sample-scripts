"""
template_file_read_write.py - テンプレートファイルの読み書き
"""

import string
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, BaseLoader

# 出力ディレクトリ
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# サンプルデータ
USER = {"name": "Alice", "role": "Admin", "score": 95}
ITEMS = [
    {"name": "Apple",  "price": 100, "stock": True},
    {"name": "Banana", "price":  80, "stock": False},
    {"name": "Cherry", "price": 200, "stock": True},
]


# ============================================================
# 1. string.Template による変数の埋め込み（$変数名）
# ============================================================
def string_template():
    tmpl = string.Template("Hello, $name! Your role is $role.")
    result = tmpl.substitute(name=USER["name"], role=USER["role"])
    print(result)

    # safe_substitute: 未定義キーをそのまま残す（KeyError を回避）
    tmpl2  = string.Template("Hello, $name! Score: $score, Rank: $rank")
    result2 = tmpl2.safe_substitute(name=USER["name"], score=USER["score"])
    print(result2)   # $rank はそのまま残る


# ============================================================
# 2. str.format / f-string によるテンプレート処理
# ============================================================
def format_template():
    # str.format
    tmpl = "Hello, {name}! Role: {role}, Score: {score}"
    result = tmpl.format(**USER)
    print(result)

    # 数値フォーマット
    price = 1234567
    print(f"Price: {price:,}")          # 1,234,567
    print(f"Score: {score:05.1f}")      # 095.0


# ============================================================
# 3. テンプレートファイルの読み込み・書き出し（string.Template）
# ============================================================
def template_file_read_write():
    # テンプレートファイルを作成
    tmpl_path = OUTPUT_DIR / "report.txt.tmpl"
    tmpl_path.write_text(
        "Report\n"
        "------\n"
        "Name : $name\n"
        "Role : $role\n"
        "Score: $score\n",
        encoding="utf-8"
    )

    # テンプレートファイルを読み込んで変数を埋め込む
    tmpl   = string.Template(tmpl_path.read_text(encoding="utf-8"))
    result = tmpl.substitute(**USER)

    # 結果をファイルに書き出し
    out_path = OUTPUT_DIR / "report.txt"
    out_path.write_text(result, encoding="utf-8")
    print(out_path.read_text(encoding="utf-8"))


# ============================================================
# 4. Jinja2 による文字列テンプレートのレンダリング
# ============================================================
def jinja2_string_template():
    tmpl_str = "Hello, {{ name }}! Role: {{ role }}, Score: {{ score }}"
    env      = Environment(loader=BaseLoader())
    tmpl     = env.from_string(tmpl_str)
    result   = tmpl.render(**USER)
    print(result)


# ============================================================
# 5. Jinja2 テンプレートのループ・条件分岐
# ============================================================
def jinja2_loop_condition():
    tmpl_str = """\
Item List
---------
{% for item in items -%}
- {{ item.name }}: {{ item.price }}円
  {% if item.stock %}[在庫あり]{% else %}[在庫なし]{% endif %}
{% endfor %}
High price items (>= 150円):
{% for item in items if item.price >= 150 -%}
  * {{ item.name }}
{% endfor %}"""

    env    = Environment(loader=BaseLoader(), keep_trailing_newline=True)
    tmpl   = env.from_string(tmpl_str)
    result = tmpl.render(items=ITEMS)
    print(result)


# ============================================================
# 6. Jinja2 テンプレートファイルの読み込み・書き出し
# ============================================================
def jinja2_file_template():
    # テンプレートファイルを作成
    tmpl_path = OUTPUT_DIR / "invoice.html.j2"
    tmpl_path.write_text(
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<body>\n"
        "<h1>Invoice</h1>\n"
        "<p>Customer: {{ user.name }} ({{ user.role }})</p>\n"
        "<table border='1'>\n"
        "  <tr><th>Item</th><th>Price</th><th>Stock</th></tr>\n"
        "  {% for item in items %}\n"
        "  <tr>\n"
        "    <td>{{ item.name }}</td>\n"
        "    <td>{{ item.price }}円</td>\n"
        "    <td>{% if item.stock %}○{% else %}×{% endif %}</td>\n"
        "  </tr>\n"
        "  {% endfor %}\n"
        "</table>\n"
        "<p>Total: {{ items | selectattr('stock') | list | length }} items available</p>\n"
        "</body>\n"
        "</html>\n",
        encoding="utf-8"
    )

    # テンプレートファイルを読み込んでレンダリング
    env    = Environment(loader=FileSystemLoader(OUTPUT_DIR))
    tmpl   = env.get_template("invoice.html.j2")
    result = tmpl.render(user=USER, items=ITEMS)

    # 結果をファイルに書き出し
    out_path = OUTPUT_DIR / "invoice.html"
    out_path.write_text(result, encoding="utf-8")
    print(out_path.read_text(encoding="utf-8"))
