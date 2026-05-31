# Python 基礎処理

## 📋 ファイル一覧

| ソース名 | 説明 |
|---|---|
| [list_operations.py](#list_operationspy-listの操作) | listの操作 |
| [dict_operations.py](#dict_operationspy-dictの操作) | dictの操作 |
| [set_operations.py](#set_operationspy-setの操作) | setの操作 |
| [loop_operations.py](#loop_operationspy-ループの操作) | ループの操作 |
| [file_read_write.py](#file_read_writepy-ファイルの読み書き) | ファイルの読み書き |
| [template_file_read_write.py](#template_file_read_writepy-テンプレートファイルの読み書き) | テンプレートファイルの読み書き |
| [temp_file_read_write.py](#temp_file_read_writepy-一時ファイルの読み書き) | 一時ファイルの読み書き |
| [memory_file_read_write.py](#memory_file_read_writepy-メモリファイルの読み書き) | メモリファイルの読み書き |
| [csv_file_read_write.py](#csv_file_read_writepy-csvファイルの読み書き) | CSVファイルの読み書き |
| [zip_file_compress_extract.py](#zip_file_compress_extractpy-zipファイルの圧縮展開) | ZIPファイルの圧縮・展開 |
| [ini_file_read_write.py](#ini_file_read_writepy-ini形式ファイルの読み書き) | INI形式ファイルの読み書き |
| [yaml_file_read_write.py](#yaml_file_read_writepy-yaml形式ファイルの読み書き) | YAML形式ファイルの読み書き |
| [json_file_read_write.py](#json_file_read_writepy-jsonファイルの読み書き) | JSONファイルの読み書き |
| [log_file_config_write.py](#log_file_config_writepy-ログファイルの設定書き込み) | ログファイルの設定・書き込み |
| [rest_api_client.py](#rest_api_clientpy-クライアント側のrest-api処理) | クライアント側のREST API処理 |
| [rest_api_server.py](#rest_api_serverpy-サーバ側のrest-api処理) | サーバ側のREST API処理 |

---

## 📄 Python ソース詳細

## [list_operations.py](list_operations.py) listの操作

**インポートするモジュール**
```python
import copy  # deepcopy によるリストのコピー
```


- リストの作成・初期化
- 要素の追加（`append`, `insert`, `extend`）
- 要素の削除（`remove`, `pop`, `del`）
- 要素の検索（`index`, `in`）
- ソート（`sort`, `sorted`, `reverse`）
- スライス（`list[start:end:step]`）
- リスト内包表記（`[x for x in list]`）
- リストの結合・コピー

---

## [dict_operations.py](dict_operations.py) dictの操作

**インポートするモジュール**
```python
import copy  # deepcopy によるネスト辞書のコピー
```


- 辞書の作成・初期化
- 要素の追加・更新（`dict[key] = value`）
- 要素の削除（`del`, `pop`）
- キー・値の取得（`keys`, `values`, `items`）
- 安全な取得（`get`, `setdefault`）
- 辞書のマージ（`update`, `|`）
- 辞書内包表記（`{k: v for k, v in dict.items()}`）
- ネストした辞書の操作

---

## [set_operations.py](set_operations.py) setの操作

**インポートするモジュール**
```python
# 標準のset操作のみ使用（追加インポート不要）
```


- セットの作成・初期化
- 要素の追加・削除（`add`, `remove`, `discard`）
- 集合演算（和集合 `|`, 積集合 `&`, 差集合 `-`, 対称差 `^`）
- 包含関係の確認（`issubset`, `issuperset`）
- 重複排除（`list` → `set` → `list`）
- セット内包表記（`{x for x in iterable}`）

---

## [loop_operations.py](loop_operations.py) ループの操作

**インポートするモジュール**
```python
import itertools  # count, cycle, chain, product, combinations, permutations 等
```


- `for` ループの基本
- `while` ループの基本
- `range` を使ったループ
- `enumerate` によるインデックス付きループ
- `zip` による複数リストの同時ループ
- ネストしたループ
- ループ内包表記（list / dict / set）
- `itertools` を使った高度なループ

---

## [file_read_write.py](file_read_write.py) ファイルの読み書き

**インポートするモジュール**
```python
import os                    # os.path.exists, os.path.join 等
from pathlib import Path     # Path.exists, Path.read_text 等
import shutil                # copy, move, rmtree 等
```


- ファイルのオープン・クローズ（`open`, `with`）
- テキストファイルの読み込み（`read`, `readline`, `readlines`）
- テキストファイルの書き込み（`write`, `writelines`）
- ファイルの存在確認（`os.path.exists`, `pathlib.Path.exists`）
- ファイルのコピー・移動・削除（`shutil`）

---

## [template_file_read_write.py](template_file_read_write.py) テンプレートファイルの読み書き

**インポートするモジュール**
```python
import string                                        # string.Template
from jinja2 import Environment, FileSystemLoader     # テンプレートレンダリング
```


- テンプレートファイルの読み込み
- `string.Template` による変数の埋め込み（`$変数名`）
- `str.format` / f-string によるテンプレート処理
- テンプレートレンダリング（jinja2）
- テンプレートファイルへの書き出し（jinja2）
- テンプレートのループ・条件分岐（jinja2）

---

## [temp_file_read_write.py](temp_file_read_write.py) 一時ファイルの読み書き

**インポートするモジュール**
```python
import tempfile  # NamedTemporaryFile, TemporaryFile, TemporaryDirectory
```


- `tempfile` モジュールの基本
- 一時ファイルの作成（`NamedTemporaryFile`, `TemporaryFile`）
- 一時ディレクトリの作成（`TemporaryDirectory`）

---

## [memory_file_read_write.py](memory_file_read_write.py) メモリファイルの読み書き

**インポートするモジュール**
```python
import io       # StringIO, BytesIO
import csv      # メモリ上でのCSV生成・パース
import zipfile  # メモリ上でのZIPファイル操作
```


- `io.StringIO` によるテキストのメモリ上読み書き
- `io.BytesIO` によるバイナリのメモリ上読み書き
- `read`, `write`, `seek`, `getvalue` の基本操作
- ファイルと同じインターフェースでの利用（`csv`, `zipfile` との組み合わせ）
- メモリ上でのCSV生成・パース
- メモリ上でのZIPファイル操作
- メモリファイルを実ファイルに書き出す

---

## [csv_file_read_write.py](csv_file_read_write.py) CSVファイルの読み書き

**インポートするモジュール**
```python
import csv  # reader, DictReader, writer, DictWriter
```


- `csv` モジュールの基本
- CSVファイルの読み込み（`csv.reader`）
- 辞書形式での読み込み（`csv.DictReader`）
- CSVファイルの書き込み（`csv.writer`）
- 辞書形式での書き込み（`csv.DictWriter`）
- 区切り文字・クォートの設定（`delimiter`, `quotechar`）
- ヘッダー行の処理
- エンコーディングの指定

---

## [zip_file_compress_extract.py](zip_file_compress_extract.py) ZIPファイルの圧縮・展開

**インポートするモジュール**
```python
import zipfile  # ZipFile, ZipInfo, namelist, infolist
```


- `zipfile` モジュールの基本
- ZIPファイルの作成・圧縮（`ZipFile`, `write`）
- ZIPファイルの展開（`extractall`, `extract`）
- ZIP内のファイル一覧取得（`namelist`, `infolist`）
- ZIPファイルへのファイル追加
- パスワード付きZIPの展開（`pwd`）

---

## [ini_file_read_write.py](ini_file_read_write.py) INI形式ファイルの読み書き

**インポートするモジュール**
```python
import configparser  # ConfigParser, read, sections, options, get, set, write
```


- `configparser` モジュールの基本
- INIファイルの読み込み（`read`, `read_string`）
- セクション・キーの取得（`sections`, `options`, `get`）
- 型変換（`getint`, `getfloat`, `getboolean`）
- INIファイルへの書き込み（`set`, `write`）
- セクションの追加・削除（`add_section`, `remove_section`）
- `DEFAULT` セクションの活用

---

## [yaml_file_read_write.py](yaml_file_read_write.py) YAML形式ファイルの読み書き

**インポートするモジュール**
```python
import yaml  # safe_load, safe_load_all, dump（pip install pyyaml）
```


- `pyyaml` モジュールの基本（`import yaml`）
- YAMLファイルの読み込み（`yaml.safe_load`）
- 複数ドキュメントの読み込み（`yaml.safe_load_all`）
- YAMLファイルへの書き込み（`yaml.dump`）
- Pythonオブジェクト ↔ YAML の変換
- 日本語（マルチバイト）の扱い（`allow_unicode=True`）

---

## [json_file_read_write.py](json_file_read_write.py) JSONファイルの読み書き

**インポートするモジュール**
```python
import json  # load, loads, dump, dumps
```


- `json` モジュールの基本
- JSONファイルの読み込み（`json.load`）
- JSON文字列のパース（`json.loads`）
- JSONファイルへの書き込み（`json.dump`）
- JSON文字列への変換（`json.dumps`）
- インデント・ソートの設定（`indent`, `sort_keys`）
- 日本語の扱い（`ensure_ascii=False`）

---

## [log_file_config_write.py](log_file_config_write.py) ログファイルの設定・書き込み

**インポートするモジュール**
```python
import logging                                                              # 基本ロガー
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler  # ローテーション
import logging.config                                                       # 設定ファイルからの読み込み
```


- `logging` モジュールの基本
- ログレベルの設定（`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`）
- ファイルへのログ出力（`FileHandler`）
- コンソールへのログ出力（`StreamHandler`）
- ログフォーマットの設定（`Formatter`）
- ロガーの作成（`getLogger`）
- ログのローテーション（`RotatingFileHandler`, `TimedRotatingFileHandler`）
- `logging.config` による設定ファイルからの読み込み

---

## [rest_api_client.py](rest_api_client.py) クライアント側のREST API処理

**インポートするモジュール**
```python
import requests  # get, post, put, delete（pip install requests）
```


- `requests` ライブラリの基本
- GETリクエスト（`requests.get`）
- POSTリクエスト（`requests.post`）
- PUTリクエスト（`requests.put`）
- DELETEリクエスト（`requests.delete`）
- リクエストヘッダーの設定
- クエリパラメータの設定（`params`）
- リクエストボディの送信（`json`, `data`）
- レスポンスの処理（`status_code`, `json()`, `text`）
- 認証（Basic認証, Bearer Token）
- タイムアウト・エラーハンドリング

---

## [rest_api_server.py](rest_api_server.py) サーバ側のREST API処理

**インポートするモジュール**
```python
from flask import Flask, request, jsonify, g  # pip install flask
import sqlite3                                # DB接続管理
```


- `Flask` の基本セットアップ
- ルーティングの定義（`@app.route`, `methods=["GET", "POST", ...]`）
- パスパラメータの受け取り（`/items/<int:item_id>`）
- クエリパラメータの受け取り（`request.args.get`）
- リクエストボディの受け取り（`request.values.get`）
- レスポンスの返却（文字列 + ステータスコード）
- ステータスコードの設定（`200`, `201`, `400`, `404`）
- エラーハンドリング（条件チェック + 直接 `return`）
- DB接続管理（`sqlite3`, `g`, `@app.teardown_appcontext`）
- サーバの起動（`app.run`）
