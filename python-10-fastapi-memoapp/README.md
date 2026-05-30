# メモ管理アプリ（FastAPI + SQLite）

FastAPI と SQLAlchemy（非同期）を使ったメモ管理 REST API のサンプルプロジェクトです。  
フロントエンド（HTML / CSS / JavaScript）も同梱しており、ブラウザから CRUD 操作を行えます。

---

## 🚀 セットアップ

```bash

# Ptyon 3.11にする
conda activate py311

# 仮想環境を作成
python -m venv .venv

# アクティブ化
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

### データベースの初期化

```bash
python init_database.py
```

### サーバーの起動

```bash
uvicorn main:app --reload
```

起動後、Swagger UI は `http://127.0.0.1:8000/docs` で確認できます。  
フロントエンドは `frontapp/index.html` を Live Server 等で開いてください（オリジン: `http://127.0.0.1:5500`）。

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

---

## 📄 Python ソース詳細

### [main.py](main.py)

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

### [db.py](db.py)

| import モジュール | 用途 |
|---|---|
| `os` | データベースファイルの絶対パス生成 |
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期 DB エンジンの作成 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッションクラス |
| `sqlalchemy.orm.sessionmaker` | セッションファクトリの生成 |
| `sqlalchemy.orm.declarative_base` | ORM ベースクラスの定義 |

非同期 SQLAlchemy の基盤設定ファイル。以下を定義します。

- `Base`：全 ORM モデルが継承するベースクラス
- `DATABASE_URL`：`sqlite+aiosqlite:///<絶対パス>/memodb.sqlite`
- `engine`：非同期エンジン（`echo=True` でSQLログを出力）
- `async_session`：`sessionmaker` で生成した非同期セッションファクトリ
- `get_dbsession()`：FastAPI の `Depends` で使用するセッションジェネレーター（`yield` で自動クローズ）

---

### [init_database.py](init_database.py)

| import モジュール | 用途 |
|---|---|
| `os` | データベースファイルの絶対パス生成 |
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期 DB エンジンの作成 |
| `models.memo.Base` | ORM メタデータ（テーブル定義情報） |
| `asyncio` | 非同期処理の実行（`asyncio.run`） |

DB の初期化（テーブル削除＆再作成）を行うスクリプト。以下の処理を実行します。

- `Base.metadata.drop_all`：既存テーブルをすべて削除
- `Base.metadata.create_all`：ORM モデルをもとにテーブルを新規作成
- `if __name__ == "__main__"` ブロックで `asyncio.run(init_db())` を呼び出し、直接実行時のみ動作

---

### [models/memo.py](models/memo.py)

| import モジュール | 用途 |
|---|---|
| `sqlalchemy.Column` | テーブルカラムの定義 |
| `sqlalchemy.Integer` | 整数型カラム（`memo_id`） |
| `sqlalchemy.String` | 文字列型カラム（`title`、`description`、`priority`） |
| `sqlalchemy.DateTime` | 日時型カラム（`created_at`、`updated_at`、`due_date`） |
| `sqlalchemy.Boolean` | 真偽値型カラム（`is_completed`） |
| `db.Base` | ORM ベースクラス |
| `datetime.datetime` | `created_at` のデフォルト値設定 |

`memos` テーブルの ORM モデル定義。各カラムの構成は以下のとおりです。

| カラム名 | 型 | 説明 |
|---|---|---|
| `memo_id` | Integer（PK） | メモ ID（自動インクリメント） |
| `title` | String(50) | タイトル（必須） |
| `description` | String(255) | 詳細説明（任意） |
| `created_at` | DateTime | 作成日時（自動設定） |
| `updated_at` | DateTime | 更新日時 |
| `priority` | String(10) | 優先度（必須） |
| `due_date` | DateTime | 期限日（任意） |
| `is_completed` | Boolean | 完了フラグ（デフォルト: `False`） |

---

### [schemas/memo.py](schemas/memo.py)

| import モジュール | 用途 |
|---|---|
| `pydantic.BaseModel` | スキーマの基底クラス |
| `pydantic.Field` | バリデーションルール・説明・例示値の定義 |
| `datetime.datetime` | 期限日フィールドの型定義 |

リクエスト・レスポンスの Pydantic スキーマ定義。4 つのスキーマで構成されます。

| スキーマ名 | 用途 |
|---|---|
| `MemoStatusSchema` | メモのステータス情報（`priority`・`due_date`・`is_completed`） |
| `InsertAndUpdateMemoSchema` | 新規登録・更新リクエストのスキーマ（`title`・`description`・`status`） |
| `MemoSchema` | メモ情報レスポンス用スキーマ（`InsertAndUpdateMemoSchema` に `memo_id` を追加） |
| `ResponseSchema` | 登録・更新・削除の結果メッセージ返却用スキーマ（`message` フィールドのみ） |

---

### [cruds/memo.py](cruds/memo.py)

| import モジュール | 用途 |
|---|---|
| `sqlalchemy.select` | SELECT クエリの構築 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期 DB セッションの型ヒント |
| `schemas.memo` | リクエストスキーマ（`InsertAndUpdateMemoSchema`） |
| `models.memo` | ORM モデル（`Memo`） |
| `datetime.datetime` | 更新日時の現在時刻設定 |

DB 操作ロジック層。以下の 4 つの非同期関数を実装します。

| 関数名 | HTTP | 処理内容 |
|---|---|---|
| `insert_memo(db_session, memo_data)` | POST | `Memo` モデルを生成して `add` → `commit` → `refresh` で新規登録 |
| `get_memos(db_session)` | GET | `select(Memo)` で全件取得し `scalars().all()` でリスト返却 |
| `get_memo_by_id(db_session, memo_id)` | GET | `where(Memo.memo_id == memo_id)` で 1 件取得（存在しない場合は `None`） |
| `update_memo(db_session, memo_id, target_data)` | PUT | ID で取得後、各フィールドを上書きして `commit` → `refresh` |
| `delete_memo(db_session, memo_id)` | DELETE | ID で取得後、`db_session.delete` → `commit` で削除 |

---

### [routers/memo.py](routers/memo.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーターの生成（`prefix="/memos"`、`tags=["Memos"]`） |
| `fastapi.HTTPException` | 404 / 400 エラーのレスポンス |
| `fastapi.Depends` | DB セッションの依存注入 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッションの型ヒント |
| `schemas.memo.*` | リクエスト・レスポンス用 Pydantic スキーマ |
| `cruds.memo` | CRUD 処理関数の呼び出し |
| `db` | `get_dbsession` の依存注入元 |

メモ用 REST API のエンドポイント定義。`/memos` プレフィックスで以下の 5 つのエンドポイントを提供します。

| メソッド | パス | 処理内容 |
|---|---|---|
| `POST` | `/memos/` | メモ新規登録。成功時に `ResponseSchema`（登録完了メッセージ）を返却 |
| `GET` | `/memos/` | メモ全件取得。ORM オブジェクトを `MemoSchema` リストに変換して返却 |
| `GET` | `/memos/{memo_id}` | 指定 ID のメモ 1 件取得。存在しない場合は 404 |
| `PUT` | `/memos/{memo_id}` | 指定 ID のメモを更新。存在しない場合は 404 |
| `DELETE` | `/memos/{memo_id}` | 指定 ID のメモを削除。存在しない場合は 404 |

---

## 🌐 フロントエンド（frontapp/）

| ファイル | 説明 |
|---|---|
| [`frontapp/index.html`](frontapp/index.html) | メモ一覧・登録・編集フォームの HTML |
| [`frontapp/styles.css`](frontapp/styles.css) | レイアウト・デザインのスタイルシート |
| [`frontapp/app.js`](frontapp/app.js) | fetch API を使った REST API 呼び出しと DOM 操作 |

フロントエンドは `http://127.0.0.1:5500` で Live Server 等を使って開きます（CORS 許可済みオリジン）。

---

## 🔄 API エンドポイント一覧

| メソッド | URL | 説明 |
|---|---|---|
| `POST` | `/memos/` | メモ新規登録 |
| `GET` | `/memos/` | メモ全件取得 |
| `GET` | `/memos/{memo_id}` | メモ 1 件取得 |
| `PUT` | `/memos/{memo_id}` | メモ更新 |
| `DELETE` | `/memos/{memo_id}` | メモ削除 |

Swagger UI：`http://127.0.0.1:8000/docs`
