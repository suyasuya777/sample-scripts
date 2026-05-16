# Python 基礎処理 一覧

---

## [list_operations.py](list_operations.py)　listの操作

- リストの作成・初期化
- 要素の追加（`append`, `insert`, `extend`）
- 要素の削除（`remove`, `pop`, `del`）
- 要素の検索（`index`, `in`）
- ソート（`sort`, `sorted`, `reverse`）
- スライス（`list[start:end:step]`）
- リスト内包表記（`[x for x in list]`）
- リストの結合・コピー

---

## [dict_operations.py](dict_operations.py)　dictの操作

- 辞書の作成・初期化
- 要素の追加・更新（`dict[key] = value`）
- 要素の削除（`del`, `pop`）
- キー・値の取得（`keys`, `values`, `items`）
- 安全な取得（`get`, `setdefault`）
- 辞書のマージ（`update`, `|`）
- 辞書内包表記（`{k: v for k, v in dict.items()}`）
- ネストした辞書の操作

---

## [set_operations.py](set_operations.py)　setの操作

- セットの作成・初期化
- 要素の追加・削除（`add`, `remove`, `discard`）
- 集合演算（和集合 `|`, 積集合 `&`, 差集合 `-`, 対称差 `^`）
- 包含関係の確認（`issubset`, `issuperset`）
- 重複排除（`list` → `set` → `list`）
- セット内包表記（`{x for x in iterable}`）

---

## [loop_operations.py](loop_operations.py)　ループの操作

- `for` ループの基本
- `while` ループの基本
- `range` を使ったループ
- `enumerate` によるインデックス付きループ
- `zip` による複数リストの同時ループ
- ネストしたループ
- ループ内包表記（list / dict / set）
- `itertools` を使った高度なループ

---

## [file_read_write.py](file_read_write.py)　ファイルの読み書き

- ファイルのオープン・クローズ（`open`, `with`）
- テキストファイルの読み込み（`read`, `readline`, `readlines`）
- テキストファイルの書き込み（`write`, `writelines`）
- ファイルの存在確認（`os.path.exists`, `pathlib.Path.exists`）
- ファイルのコピー・移動・削除（`shutil`）

---

## [template_file_read_write.py](template_file_read_write.py)　テンプレートファイルの読み書き

- テンプレートファイルの読み込み
- `string.Template` による変数の埋め込み（`$変数名`）
- `str.format` / f-string によるテンプレート処理
- テンプレートレンダリング（jinja2）
- テンプレートファイルへの書き出し（jinja2）
- テンプレートのループ・条件分岐（jinja2）

---

## [temp_file_read_write.py](temp_file_read_write.py)　一時ファイルの読み書き

- `tempfile` モジュールの基本
- 一時ファイルの作成（`NamedTemporaryFile`, `TemporaryFile`）
- 一時ディレクトリの作成（`TemporaryDirectory`）
-
---

## [memory_file_read_write.py](memory_file_read_write.py)　メモリファイルの読み書き

- `io.StringIO` によるテキストのメモリ上読み書き
- `io.BytesIO` によるバイナリのメモリ上読み書き
- `read`, `write`, `seek`, `getvalue` の基本操作
- ファイルと同じインターフェースでの利用（`csv`, `zipfile` との組み合わせ）
- メモリ上でのCSV生成・パース
- メモリ上でのZIPファイル操作
- メモリファイルを実ファイルに書き出す

---

## [csv_file_read_write.py](csv_file_read_write.py)　CSVファイルの読み書き

- `csv` モジュールの基本
- CSVファイルの読み込み（`csv.reader`）
- 辞書形式での読み込み（`csv.DictReader`）
- CSVファイルの書き込み（`csv.writer`）
- 辞書形式での書き込み（`csv.DictWriter`）
- 区切り文字・クォートの設定（`delimiter`, `quotechar`）
- ヘッダー行の処理
- エンコーディングの指定

---

## [zip_file_compress_extract.py](zip_file_compress_extract.py)　ZIPファイルの圧縮・展開

- `zipfile` モジュールの基本
- ZIPファイルの作成・圧縮（`ZipFile`, `write`）
- ZIPファイルの展開（`extractall`, `extract`）
- ZIP内のファイル一覧取得（`namelist`, `infolist`）
- ZIPファイルへのファイル追加
- パスワード付きZIPの展開（`pwd`）

---

## [ini_file_read_write.py](ini_file_read_write.py)　INI形式ファイルの読み書き

- `configparser` モジュールの基本
- INIファイルの読み込み（`read`, `read_string`）
- セクション・キーの取得（`sections`, `options`, `get`）
- 型変換（`getint`, `getfloat`, `getboolean`）
- INIファイルへの書き込み（`set`, `write`）
- セクションの追加・削除（`add_section`, `remove_section`）
- `DEFAULT` セクションの活用

---

## [yaml_file_read_write.py](yaml_file_read_write.py)　YAML形式ファイルの読み書き

- `pyyaml` モジュールの基本（`import yaml`）
- YAMLファイルの読み込み（`yaml.safe_load`）
- 複数ドキュメントの読み込み（`yaml.safe_load_all`）
- YAMLファイルへの書き込み（`yaml.dump`）
- Pythonオブジェクト ↔ YAML の変換
- 日本語（マルチバイト）の扱い（`allow_unicode=True`）

---

## [json_file_read_write.py](json_file_read_write.py)　JSONファイルの読み書き

- `json` モジュールの基本
- JSONファイルの読み込み（`json.load`）
- JSON文字列のパース（`json.loads`）
- JSONファイルへの書き込み（`json.dump`）
- JSON文字列への変換（`json.dumps`）
- インデント・ソートの設定（`indent`, `sort_keys`）
- 日本語の扱い（`ensure_ascii=False`）

---

## [log_file_config_write.py](log_file_config_write.py)　ログファイルの設定・書き込み

- `logging` モジュールの基本
- ログレベルの設定（`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`）
- ファイルへのログ出力（`FileHandler`）
- コンソールへのログ出力（`StreamHandler`）
- ログフォーマットの設定（`Formatter`）
- ロガーの作成（`getLogger`）
- ログのローテーション（`RotatingFileHandler`, `TimedRotatingFileHandler`）
- `logging.config` による設定ファイルからの読み込み

---

## [rest_api_client.py](rest_api_client.py)　クライアント側のREST API処理

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

markdown## [rest_api_server.py](rest_api_server.py)　サーバ側のREST API処理

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
