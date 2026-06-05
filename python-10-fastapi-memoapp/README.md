# メモ管理アプリ（FastAPI + SQLite）

FastAPI と SQLAlchemy（非同期）を使ったメモ管理 REST API のサンプルプロジェクトです。  
フロントエンド（HTML / CSS / JavaScript）も同梱しており、ブラウザから CRUD 操作を行えます。

---

## 📁 ディレクトリ・ファイル構成

```
memo_project/
├── main.py                  # FastAPI エントリーポイント・CORS・ルーター登録
├── db.py                    # 非同期 DB エンジン・セッション管理
├── init_database.py         # DB 初期化スクリプト（テーブル作成）
├── memodb.sqlite            # SQLite データベースファイル
├── models/
│   └── memo.py              # SQLAlchemy ORM モデル（memos テーブル定義）
├── schemas/
│   └── memo.py              # Pydantic スキーマ定義（リクエスト・レスポンス）
├── cruds/
│   └── memo.py              # 非同期 CRUD 処理（DB 操作ロジック）
├── routers/
│   └── memo.py              # FastAPI ルーター・エンドポイント定義
└── frontapp/
    ├── index.html           # フロントエンド HTML
    ├── styles.css           # スタイルシート
    └── app.js               # フロントエンド JavaScript（API 呼び出し）
```

## 📋 ファイル一覧

| ディレクトリ | ソース名 | 説明 |
|---|---|---|
| memo_project/ | [main.py](#mainpy--fastapi-エントリーポイントcorsルーター登録) | FastAPI エントリーポイント・CORS・ルーター登録 |
| | [db.py](#dbpy--非同期-db-エンジンセッション管理) | 非同期 DB エンジン・セッション管理 |
| | [init_database.py](#init_databasepy--db-初期化スクリプトテーブル作成) | DB 初期化スクリプト（テーブル作成） |
| | memodb.sqlite | SQLite データベースファイル |
| models/ | [memo.py](#modelsmemopy--sqlalchemy-orm-モデルmemos-テーブル定義) | SQLAlchemy ORM モデル（memos テーブル定義） |
| schemas/ | [memo.py](#schemasmemopy--pydantic-スキーマ定義リクエストレスポンス) | Pydantic スキーマ定義（リクエスト・レスポンス） |
| cruds/ | [memo.py](#crudsmemopy--非同期-crud-処理db-操作ロジック) | 非同期 CRUD 処理（DB 操作ロジック） |
| routers/ | [memo.py](#routersmemopy--fastapi-ルーターエンドポイント定義) | FastAPI ルーター・エンドポイント定義 |
| frontapp/ | index.html | フロントエンド HTML |
| | styles.css | スタイルシート |
| | app.js | フロントエンド JavaScript（API 呼び出し） |

---

## 🚀 セットアップ

```bash
# Python 3.11 にする
conda activate py311

# 仮想環境を作成
python -m venv .venv

# アクティブ化
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

# インストール
pip install -r requirements.txt

# データベースの初期化
python init_database.py

# サーバーの起動
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

起動後、Swagger UI は `http://127.0.0.1:8000/docs` で確認できます。

フロントエンドは `frontapp/index.html` を Live Server 等で開いてください（オリジン: `http://127.0.0.1:5500`）。

---

## 📄 Python ソース詳細

### main.py ─ FastAPI エントリーポイント・CORS・ルーター登録

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | FastAPI アプリ本体の生成 |
| `fastapi.middleware.cors.CORSMiddleware` | CORS ミドルウェア設定 |
| `fastapi.responses.JSONResponse` | カスタムエラーレスポンスの生成 |
| `pydantic.ValidationError` | バリデーションエラーのキャッチ |
| `routers.memo.router` | メモ用ルーターのインポート |

FastAPI アプリのエントリーポイント。以下の処理を担当します。

- `CORSMiddleware` でフロントエンド（`http://127.0.0.1:5500`）からのリクエストを許可
- `memo_router` をアプリに登録（`include_router`）
- `ValidationError` 発生時にステータスコード 422 とエラー詳細を返すカスタムハンドラーを定義

---

### db.py ─ 非同期 DB エンジン・セッション管理

| import モジュール | 用途 |
|---|---|
| `os` | データベースファイルの絶対パス生成 |
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期 DB エンジンの作成 |
| `sqlalchemy.ext.asyncio.async_sessionmaker` | 非同期セッションファクトリの生成 |
| `sqlalchemy.orm.DeclarativeBase` | ORM ベースクラスの定義 |

非同期 SQLAlchemy の基盤設定ファイル。以下を定義します。

- `Base`：`DeclarativeBase` を継承した全 ORM モデルの基底クラス
- `DATABASE_URL`：`sqlite+aiosqlite:///<絶対パス>/memodb.sqlite`
- `engine`：非同期エンジン（`echo=True` で SQL ログを出力）
- `async_session`：`async_sessionmaker` で生成した非同期セッションファクトリ（`expire_on_commit=False`）
- `get_db()`：FastAPI の `Depends` で使用するセッションジェネレーター（`yield` で自動クローズ）

---

### init_database.py ─ DB 初期化スクリプト（テーブル作成）

| import モジュール | 用途 |
|---|---|
| `asyncio` | 非同期処理の実行（`asyncio.run`） |
| `db.engine` | `db.py` で定義した非同期エンジン（一元管理） |
| `db.Base` | ORM メタデータ（テーブル定義情報） |
| `models.memo` | `Base` へのモデル登録（テーブル作成に必要） |

DB の初期化（テーブル削除＆再作成）を行うスクリプト。`engine` と `Base` は `db.py` から直接インポートして使用するため、接続設定の重複定義がありません。以下の処理を実行します。

- `import models.memo`：`Memo` モデルを `Base` に登録し、`create_all` でテーブルが作成されるようにする
- `Base.metadata.drop_all`：既存テーブルをすべて削除
- `Base.metadata.create_all`：ORM モデルをもとにテーブルを新規作成
- `if __name__ == "__main__"` ブロックで `asyncio.run(init_db())` を呼び出し、直接実行時のみ動作

---

### models/memo.py ─ SQLAlchemy ORM モデル（memos テーブル定義）

| import モジュール | 用途 |
|---|---|
| `sqlalchemy.String` | 文字列型カラム（`title`・`description`・`priority`） |
| `sqlalchemy.orm.Mapped` | カラムの型アノテーション（SQLAlchemy 2.0 スタイル） |
| `sqlalchemy.orm.mapped_column` | カラム定義（SQLAlchemy 2.0 スタイル） |
| `db.Base` | ORM ベースクラス |
| `datetime.datetime` | `created_at` のデフォルト値設定 |
| `datetime.timezone` | UTC タイムゾーン指定 |

`memos` テーブルの ORM モデル定義。SQLAlchemy 2.0 の `Mapped` / `mapped_column` スタイルで記述しています。各カラムの構成は以下のとおりです。

| カラム名 | 型 | 説明 |
|---|---|---|
| `memo_id` | Integer（PK） | メモ ID（自動インクリメント） |
| `title` | String(50) | タイトル（必須） |
| `description` | String(255) | 詳細説明（任意） |
| `created_at` | DateTime | 作成日時（自動設定・UTC） |
| `updated_at` | DateTime | 更新日時（任意） |
| `priority` | String(10) | 優先度（必須） |
| `due_date` | DateTime | 期限日（任意） |
| `is_completed` | Boolean | 完了フラグ |

---

### schemas/memo.py ─ Pydantic スキーマ定義（リクエスト・レスポンス）

| import モジュール | 用途 |
|---|---|
| `typing.Annotated` | フィールドの型エイリアス定義 |
| `pydantic.BaseModel` | スキーマの基底クラス |
| `pydantic.Field` | バリデーションルール・説明・例示値の定義 |
| `pydantic.ConfigDict` | ORM モード設定（`from_attributes=True`） |
| `datetime.datetime` | 期限日・作成日時・更新日時フィールドの型定義 |

リクエスト・レスポンスの Pydantic スキーマ定義。`Annotated` を使った型エイリアスでフィールド定義を一元管理しています。

**型エイリアス一覧**

| エイリアス名 | 型 | 説明 |
|---|---|---|
| `MemoId` | `int` | メモ ID（DB 自動採番） |
| `MemoTitle` | `str` | タイトル（1 文字以上必須） |
| `MemoDesc` | `str \| None` | 詳細説明（任意・デフォルト: `None`） |
| `Priority` | `str` | 優先度（例: `"高"`） |
| `DueDate` | `datetime \| None` | 期限日（デフォルト: `None`） |
| `IsCompleted` | `bool` | 完了フラグ（デフォルト: `False`） |
| `ResponseMsg` | `str` | API 操作結果メッセージ |

**スキーマ一覧**

| スキーマ名 | 用途 |
|---|---|
| `CreateAndUpdateMemoSchema` | 新規登録・更新リクエストのスキーマ（`title`・`description`・`priority`・`due_date`・`is_completed` をフラットに定義） |
| `MemoSchema` | メモ情報レスポンス用スキーマ（`CreateAndUpdateMemoSchema` に `memo_id`・`created_at`・`updated_at` を追加） |
| `ResponseSchema` | 登録・更新・削除の結果メッセージ返却用スキーマ（`message` フィールドのみ） |

---

### cruds/memo.py ─ 非同期 CRUD 処理（DB 操作ロジック）

| import モジュール | 用途 |
|---|---|
| `sqlalchemy.select` | SELECT クエリの構築 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期 DB セッションの型ヒント |
| `schemas.memo` | リクエストスキーマ（`CreateAndUpdateMemoSchema`） |
| `models.memo` | ORM モデル（`Memo`） |
| `datetime.datetime` | 更新日時の現在時刻設定 |
| `datetime.timezone` | UTC タイムゾーン指定 |

DB 操作ロジック層。以下の 5 つの非同期関数を実装します。

| 関数名 | HTTP | 処理内容 |
|---|---|---|
| `create_memo(db_session, memo_data)` | POST | `Memo` モデルを生成して `add` → `commit` → `refresh` で新規登録 |
| `get_memos(db_session)` | GET | `select(Memo)` で全件取得し `scalars().all()` でリスト返却 |
| `get_memo_by_id(db_session, memo_id)` | GET | `where(Memo.memo_id == memo_id)` で 1 件取得（存在しない場合は `None`） |
| `update_memo(db_session, memo_id, target_data)` | PUT | ID で取得後、各フィールドを上書きして `commit` → `refresh` |
| `delete_memo(db_session, memo_id)` | DELETE | ID で取得後、`db_session.delete` → `commit` で削除 |

---

### routers/memo.py ─ FastAPI ルーター・エンドポイント定義

| import モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーターの生成（`prefix="/memos"`、`tags=["Memos"]`） |
| `fastapi.HTTPException` | 404 / 400 エラーのレスポンス |
| `fastapi.Depends` | DB セッションの依存注入 |
| `typing.Annotated` | `DbSession` 型エイリアスの定義 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッションの型ヒント |
| `schemas.memo.*` | リクエスト・レスポンス用 Pydantic スキーマ |
| `cruds.memo` | CRUD 処理関数の呼び出し |
| `db` | `get_db` の依存注入元 |

メモ用 REST API のエンドポイント定義。`DbSession = Annotated[AsyncSession, Depends(db.get_db)]` で型エイリアスを定義し、各エンドポイントの引数名を `db_session` で統一しています（`import db` のモジュール名との衝突を回避）。

`/memos` プレフィックスで以下の 5 つのエンドポイントを提供します。

| メソッド | パス | 処理内容 |
|---|---|---|
| `POST` | `/memos/` | メモ新規登録。成功時に `ResponseSchema`（登録完了メッセージ）を返却 |
| `GET` | `/memos/` | メモ全件取得。ORM オブジェクトを `MemoSchema` リストに変換して返却 |
| `GET` | `/memos/{memo_id}` | 指定 ID のメモ 1 件取得。存在しない場合は 404 |
| `PUT` | `/memos/{memo_id}` | 指定 ID のメモを更新。存在しない場合は 404 |
| `DELETE` | `/memos/{memo_id}` | 指定 ID のメモを削除。存在しない場合は 404 |

Swagger UI：`http://127.0.0.1:8000/docs`

---

## 🌐 フロントエンド（frontapp/）

| ファイル | 説明 |
|---|---|
| [`frontapp/index.html`](frontapp/index.html) | メモ一覧・登録・編集フォームの HTML（優先度・期限日・完了チェックボックス対応） |
| [`frontapp/styles.css`](frontapp/styles.css) | レイアウト・デザインのスタイルシート |
| [`frontapp/app.js`](frontapp/app.js) | fetch API を使った REST API 呼び出しと DOM 操作 |

フロントエンドは `http://127.0.0.1:5500` で Live Server 等を使って開きます（CORS 許可済みオリジン）。

---
