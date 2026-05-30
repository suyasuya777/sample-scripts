# project_structure

FastAPIの推奨フォルダ構成サンプルです。

```
project_structure/
│
├── main.py            # エントリーポイント
├── config.py          # 環境変数管理（pydantic-settings）
├── database.py        # DB接続・非同期セッション管理
├── models.py          # SQLAlchemy ORMモデル
├── schemas.py         # Pydanticスキーマ
│
├── routers/           # エンドポイント定義
│   ├── auth.py        # /auth エンドポイント
│   └── item.py        # /items エンドポイント
│
├── cruds/             # DB操作ロジック
│   ├── auth.py        # 認証・ユーザーのDB操作
│   └── item.py        # items テーブルのDB操作
│
├── migrations/        # Alembicマイグレーション
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
└── tests/             # pytestテスト
    ├── conftest.py    # フィクスチャ定義
    ├── test_example.py
    └── test_item.py   # items エンドポイントのテスト
```

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

# 依存関係をインストール
pip install -r requirements.txt
```

各サンプルは単体で `uvicorn ファイル名:app --reload` で起動できます。

```bash
# ブラウザを起動
http://localhost:8000/docs
```

---

## ファイル一覧

### [main.py](main.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | アプリケーションインスタンス生成 |
| `fastapi.Request` | ミドルウェアでのリクエスト処理 |
| `fastapi.middleware.cors.CORSMiddleware` | CORS設定 |
| `routers.item`, `routers.auth` | ルーター登録 |

**処理概要**

アプリケーションのエントリーポイント。CORSMiddleware でフロントエンド（`http://localhost:3000`）からのアクセスを許可する。HTTPミドルウェアでレスポンスヘッダーに処理時間（`X-Process-Time`）を付与する。`item` / `auth` の各ルーターを `FastAPI` インスタンスに登録する。

---

### [config.py](config.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `pydantic_settings.BaseSettings` | 環境変数を型安全に管理するベースクラス |
| `pydantic_settings.SettingsConfigDict` | `.env` ファイル読み込み設定 |
| `functools.lru_cache` | `Settings` インスタンスをキャッシュし再生成を防ぐ |

**処理概要**

`BaseSettings` を継承した `Settings` クラスで環境変数（`secret_key`・`sqlalchemy_database_url`）を管理する。`get_settings()` に `@lru_cache` を付与し、アプリ全体で同一インスタンスを共有する。

---

### [database.py](database.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期DBエンジン生成 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッションクラス |
| `sqlalchemy.orm.sessionmaker` | セッションファクトリ生成 |
| `sqlalchemy.orm.declarative_base` | ORMモデルの基底クラス生成 |
| `config.get_settings` | `sqlalchemy_database_url` の取得 |

**処理概要**

非同期対応の `engine` / `async_session` / `Base` を生成・公開する。`expire_on_commit=False` により commit 後もオブジェクトの属性にアクセス可能にする。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出し、`async with` により終了後に確実にクローズする。データベースURLには非同期ドライバ（PostgreSQLの場合 `postgresql+asyncpg`）を使用する。

---

### [models.py](models.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.orm.Mapped` | カラム・リレーションの型アノテーション |
| `sqlalchemy.orm.mapped_column` | 型付きカラム定義（SQLAlchemy 2.0スタイル） |
| `sqlalchemy.orm.relationship` | テーブル間リレーション定義 |
| `sqlalchemy.String`, `Enum`, `ForeignKey` | カラム型・外部キー定義 |
| `database.Base` | ORMモデルの基底クラス |
| `schemas.ItemStatus` | ItemStatusのEnumをカラム型に使用 |

**処理概要**

`items` / `users` テーブルに対応するORMモデルを定義する。SQLAlchemy 2.0スタイルの `Mapped` + `mapped_column` を使用する。

`Item` モデルは `id` / `name` / `price` / `description` / `status` / `created_at` / `updated_at` / `user_id` のカラムを持ち、`user_id` は `ForeignKey("users.id", ondelete="CASCADE")` で `users` テーブルを参照する。`user: Mapped["User"]` により多対1の逆参照を構成する。

`User` モデルは `id` / `username` / `password` / `salt` / `created_at` / `updated_at` のカラムを持ち、`items: Mapped[list["Item"]]` により1人のUserが複数のItemを所有する1対多リレーションを構成する。

---

### [schemas.py](schemas.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `pydantic.BaseModel` | スキーマ基底クラス |
| `pydantic.Field` | バリデーション制約・サンプル値の付与 |
| `pydantic.ConfigDict` | ORM連携設定（`from_attributes=True`） |
| `enum.Enum` | `ItemStatus` の列挙型定義 |

**処理概要**

アプリ全体のPydanticスキーマを一元管理する。`ItemStatus` Enumで `ON_SALE` / `SOLD_OUT` を定義する。型エイリアス（`ItemId`, `ItemName`, `ItemPrice` 等）でバリデーション制約を共通化し、各スキーマクラスで再利用する。

スキーマ一覧：

| クラス | 用途 |
|---|---|
| `ItemCreate` | アイテム作成リクエスト |
| `ItemUpdate` | アイテム更新リクエスト（全フィールド省略可） |
| `ItemResponse` | アイテムレスポンス（`from_attributes=True`） |
| `UserCreate` | ユーザー作成リクエスト |
| `UserResponse` | ユーザーレスポンス（`from_attributes=True`） |
| `Token` | JWTトークンレスポンス |
| `DecodedToken` | JWTデコード結果（`username` / `user_id`） |

---

### [cruds/auth.py](cruds/auth.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `fastapi.security.OAuth2PasswordBearer` | OAuth2トークン取得スキーマ |
| `jose.jwt` | JWTエンコード・デコード |
| `schemas.UserCreate`, `DecodedToken` | 入力・出力スキーマ |
| `models.User` | usersテーブルのORMモデル |
| `config.get_settings` | `secret_key` の取得 |

**処理概要**

認証・ユーザー管理に関するDB操作と認証ロジックを提供する。

| 関数 | 種別 | 処理 |
|---|---|---|
| `create_user` | `async def` | saltを生成しPBKDF2でパスワードをハッシュ化してUserを作成・保存 |
| `authenticate_user` | `async def` | `select(User)` でユーザーを取得しパスワード検証 |
| `create_access_token` | `def` | JWTトークンを生成（DB不使用） |
| `get_current_user` | `def` | JWTをデコードして `DecodedToken` を返す（DB不使用） |

---

### [cruds/item.py](cruds/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `schemas.ItemCreate`, `ItemUpdate` | 入力スキーマ |
| `models.Item` | itemsテーブルのORMモデル |

**処理概要**

`items` テーブルに対する非同期DB操作関数を提供する。全関数は `async def` で定義し、DB操作には `await` を使用する。

| 関数 | 処理 |
|---|---|
| `find_all` | 全アイテムを取得 |
| `find_by_id` | `id` と `user_id` で絞り込んで1件取得 |
| `find_by_name` | `name` の部分一致で検索 |
| `create` | 新規アイテムを作成・`await db.commit()` |
| `update` | `await find_by_id` で取得後フィールドを更新・`await db.commit()` |
| `delete` | `await find_by_id` で取得後削除・`await db.commit()` |

---

### [routers/auth.py](routers/auth.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends` | DIコンテナ（DBセッション注入） |
| `fastapi.security.OAuth2PasswordRequestForm` | ログインフォームデータ取得 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `cruds.auth` | 認証・ユーザーのDB操作関数 |
| `schemas.UserCreate`, `UserResponse`, `Token` | リクエスト・レスポンスのスキーマ |

**処理概要**

`/auth` プレフィックスの認証エンドポイントを定義する。

| エンドポイント | メソッド | 処理 |
|---|---|---|
| `/auth/signup` | POST | `await auth_cruds.create_user()` でユーザー作成 |
| `/auth/login` | POST | `await auth_cruds.authenticate_user()` で認証後JWTを返す |

---

### [routers/item.py](routers/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends`, `Path`, `Query` | DI・パスパラメータ・クエリパラメータ |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `cruds.item`, `cruds.auth` | DB操作・認証関数 |
| `schemas.ItemCreate`, `ItemUpdate`, `ItemResponse`, `DecodedToken` | リクエスト・レスポンスのスキーマ |

**処理概要**

`/items` プレフィックスのエンドポイントを定義する。`UserDependency` により認証済みユーザーのみアクセス可能なエンドポイントを制御する。

| エンドポイント | メソッド | 認証 | 処理 |
|---|---|---|---|
| `/items` | GET | 不要 | 全アイテム一覧取得 |
| `/items/{id}` | GET | 必要 | IDで1件取得 |
| `/items/` | GET | 不要 | 名前で部分一致検索 |
| `/items` | POST | 必要 | アイテム作成 |
| `/items/{id}` | PUT | 必要 | アイテム更新 |
| `/items/{id}` | DELETE | 必要 | アイテム削除 |

---

### [migrations/env.py](migrations/env.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `asyncio` | 非同期処理の実行 |
| `sqlalchemy.ext.asyncio.async_engine_from_config` | 非同期エンジン生成 |
| `sqlalchemy.pool` | NullPool指定（マイグレーション時の接続管理） |
| `alembic.context` | Alembic設定・マイグレーション実行 |
| `models.Base` | autogenerateのためのメタデータ参照 |

**処理概要**

Alembicの非同期マイグレーション設定。`run_migrations_offline()` はDBに接続せずSQLをファイル出力するオフラインモード（同期）。`run_migrations_online()` は `async_engine_from_config` で非同期エンジンを生成し、`connection.run_sync(do_run_migrations)` で同期的にマイグレーションを実行する。`asyncio.run()` で非同期関数をエントリーポイントから呼び出す。

---

### [tests/conftest.py](tests/conftest.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.testclient.TestClient` | 同期テストクライアント |
| `sqlalchemy.create_engine` | テスト用インメモリSQLiteエンジン生成 |
| `sqlalchemy.pool.StaticPool` | 接続を使い回すテスト用プール |
| `sqlalchemy.orm.sessionmaker` | テスト用同期セッションファクトリ |
| `models.Base`, `Item` | テーブル作成・テストデータ投入 |
| `database.get_db` | DIオーバーライド対象 |
| `cruds.auth.get_current_user` | 認証DIオーバーライド対象 |

**処理概要**

pytestフィクスチャを定義する。アプリ本体は非同期だが `TestClient` による同期テストパターンで実装する。

| フィクスチャ | 処理 |
|---|---|
| `session_fixture` | インメモリSQLiteでテーブル作成・テストデータ（Item×2件）投入 |
| `user_fixture` | テスト用 `DecodedToken` を返す |
| `client_fixture` | `get_db` / `get_current_user` をオーバーライドして `TestClient` を生成 |

`override_get_db` は `yield session_fixture` でDI互換のジェネレータとして定義する。
