# 🛒 フリーマーケットアプリ（PostgreSQL + pgAdmin）

## 📁 ディレクトリ・ファイル構成

```
python-12-fastapi-fleamarket/
│
├── docker-compose.yml # 開発用DB環境（PostgreSQL + pgAdmin）
│
├── main.py            # エントリーポイント
├── config.py          # 環境変数管理（pydantic-settings）
├── database.py        # DB接続・非同期セッション管理
├── models.py          # SQLAlchemy ORMモデル
├── schemas.py         # Pydanticスキーマ
│
├── docker/            # Dockerボリュームマウント先
│   ├── postgres/
│   │   ├── init.d/    # 初回起動時の初期化SQL/スクリプト
│   │   └── pgdata/    # PostgreSQL実データ（永続化）
│   └── pgadmin/       # pgAdmin設定・接続情報（永続化）
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
    ├── conftest.py    # フィクスチャ・DIオーバーライド定義
    └── test_item.py   # items エンドポイントのテスト
```

## 📋 ファイル一覧

| ディレクトリ | ソース | 説明 |
|---|---|---|
| ルート | [docker-compose.yml](#docker-composeyml) | 開発用DB環境（PostgreSQL + pgAdmin） |
| ルート | [main.py](#mainpy) | エントリーポイント・CORS・ミドルウェア設定 |
| ルート | [config.py](#configpy) | 環境変数管理（pydantic-settings・lru_cache） |
| ルート | [database.py](#databasepy) | 非同期DBエンジン・セッション管理 |
| ルート | [models.py](#modelspy) | SQLAlchemy ORMモデル定義（Item・User） |
| ルート | [schemas.py](#schemaspy) | Pydanticスキーマ・Enum・型エイリアス定義 |
| `cruds/` | [auth.py](#crudsauthpy) | 認証・ユーザーのDB操作・JWT生成 |
| `cruds/` | [item.py](#crudsitempy) | itemsテーブルのDB操作 |
| `routers/` | [auth.py](#routersauthpy) | /auth エンドポイント定義 |
| `routers/` | [item.py](#routersitempy) | /items エンドポイント定義 |
| `migrations/` | [env.py](#migrationsenvpy) | Alembic非同期マイグレーション設定 |
| `tests/` | [conftest.py](#testsconftestpy) | pytestフィクスチャ・DIオーバーライド定義 |

---

## 🚀 セットアップ

```bash
# Python 3.11にする
conda activate py311

# 仮想環境を作成
python -m venv .venv

# アクティブ化
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

# 依存関係をインストール
pip install -r requirements.txt

# サーバーの起動
python -m uvicorn main:app --reload

# ブラウザを起動
http://localhost:8000/docs



# DB環境を起動（バックグラウンド）
docker compose up -d

# pgAdminにアクセス
http://127.0.0.1:81
# → メール: fastapi@example.com / パスワード: password でログイン
# → 接続先ホストは postgres、ユーザー fastapiuser、DB fleamarket を指定

# DB環境を停止
docker compose down
```

---

## 📄 Python ソース詳細

<a id="mainpy"></a>
### 🚪 [main.py](main.py)　―　エントリーポイント・CORS・ミドルウェア設定

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | アプリケーションインスタンス生成 |
| `fastapi.Request` | ミドルウェアでのリクエスト処理 |
| `fastapi.middleware.cors.CORSMiddleware` | CORS設定 |
| `routers.item`, `routers.auth` | ルーター登録 |

**📝 処理概要**

アプリケーションのエントリーポイント。CORSMiddleware でフロントエンド（`http://localhost:3000`）からのアクセスを許可する。HTTPミドルウェアでレスポンスヘッダーに処理時間（`X-Process-Time`）を付与する。`item` / `auth` の各ルーターを `FastAPI` インスタンスに登録する。

---

<a id="configpy"></a>
### ⚙️ [config.py](config.py)　―　環境変数管理（pydantic-settings・lru_cache）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `pydantic_settings.BaseSettings` | 環境変数を型安全に管理するベースクラス |
| `pydantic_settings.SettingsConfigDict` | `.env` ファイル読み込み設定 |
| `functools.lru_cache` | `Settings` インスタンスをキャッシュし再生成を防ぐ |

**📝 処理概要**

`BaseSettings` を継承した `Settings` クラスで環境変数（`secret_key`・`database_url`）を管理する。`get_settings()` に `@lru_cache` を付与し、アプリ全体で同一インスタンスを共有する。

---

<a id="databasepy"></a>
### 🗄️ [database.py](database.py)　―　非同期DBエンジン・セッション管理

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期DBエンジン生成 |
| `sqlalchemy.ext.asyncio.async_sessionmaker` | 非同期セッションファクトリ生成 |
| `sqlalchemy.orm.DeclarativeBase` | ORMモデルの基底クラス（SQLAlchemy 2.0スタイル） |
| `config.get_settings` | `database_url` の取得 |

**📝 処理概要**

非同期対応の `engine` / `async_session` / `Base` を生成・公開する。`engine` は `create_async_engine` で生成し、`async_session` は `async_sessionmaker` で生成する。`expire_on_commit=False` により commit 後もオブジェクトの属性にアクセス可能にする。`Base` は SQLAlchemy 2.0スタイルの `DeclarativeBase` を継承して定義する。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出し、`async with` により終了後に確実にクローズする。データベースURLには非同期ドライバ（PostgreSQLの場合 `postgresql+asyncpg`）を使用する。

---

<a id="modelspy"></a>
### 🧱 [models.py](models.py)　―　SQLAlchemy ORMモデル定義（Item・User）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.orm.Mapped` | カラム・リレーションの型アノテーション |
| `sqlalchemy.orm.mapped_column` | 型付きカラム定義（SQLAlchemy 2.0スタイル） |
| `sqlalchemy.orm.relationship` | テーブル間リレーション定義 |
| `sqlalchemy.String`, `Enum`, `ForeignKey` | カラム型・外部キー定義 |
| `database.Base` | ORMモデルの基底クラス |
| `schemas.ItemStatus` | ItemStatusのEnumをカラム型に使用 |

**📝 処理概要**

`items` / `users` テーブルに対応するORMモデルを定義する。SQLAlchemy 2.0スタイルの `Mapped` + `mapped_column` を使用する。

`Item` モデルは `id` / `name` / `price` / `description` / `status` / `created_at` / `updated_at` / `user_id` のカラムを持ち、`user_id` は `ForeignKey("users.id", ondelete="CASCADE")` で `users` テーブルを参照する。`user: Mapped["User"]` により多対1の逆参照を構成する。

`User` モデルは `id` / `username` / `password` / `salt` / `created_at` / `updated_at` のカラムを持ち、`items: Mapped[list["Item"]]` により1人のUserが複数のItemを所有する1対多リレーションを構成する。

---

<a id="schemaspy"></a>
### 📐 [schemas.py](schemas.py)　―　Pydanticスキーマ・Enum・型エイリアス定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `pydantic.BaseModel` | スキーマ基底クラス |
| `pydantic.Field` | バリデーション制約・サンプル値の付与 |
| `pydantic.ConfigDict` | ORM連携設定（`from_attributes=True`） |
| `enum.Enum` | `ItemStatus` の列挙型定義 |
| `typing.Annotated` | 型エイリアス（`ItemId`・`ItemName` 等）への制約付与 |

**📝 処理概要**

アプリ全体のPydanticスキーマを一元管理する。`ItemStatus` Enumで `ON_SALE` / `SOLD_OUT` を定義する。型エイリアス（`ItemId`, `ItemName`, `ItemPrice` 等）でバリデーション制約を共通化し、各スキーマクラスで再利用する。

スキーマ一覧：

| クラス | 用途 |
|---|---|
| `ItemBase` | アイテム共通フィールド（`name` / `price` / `description`）の基底スキーマ |
| `ItemCreate` | アイテム作成リクエスト（`ItemBase` を継承） |
| `ItemUpdate` | アイテム更新リクエスト（全フィールド省略可） |
| `ItemResponse` | アイテムレスポンス（`ItemBase` を継承・`from_attributes=True`） |
| `UserCreate` | ユーザー作成リクエスト |
| `UserResponse` | ユーザーレスポンス（`from_attributes=True`） |
| `Token` | JWTトークンレスポンス |
| `DecodedToken` | JWTデコード結果（`username` / `user_id`） |

---

<a id="crudsauthpy"></a>
### 🔐 [cruds/auth.py](cruds/auth.py)　―　認証・ユーザーのDB操作・JWT生成

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `base64`, `hashlib`, `os` | salt生成・PBKDF2によるパスワードハッシュ化 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `sqlalchemy.exc.IntegrityError` | username重複時の例外捕捉 |
| `fastapi.Depends`, `HTTPException`, `status` | DI・認証エラー応答 |
| `fastapi.security.OAuth2PasswordBearer` | OAuth2トークン取得スキーマ |
| `jose.jwt`, `JWTError` | JWTエンコード・デコード |
| `schemas.UserCreate`, `DecodedToken` | 入力・出力スキーマ |
| `models.User` | usersテーブルのORMモデル |
| `config.get_settings` | `secret_key` の取得 |

**📝 処理概要**

認証・ユーザー管理に関するDB操作と認証ロジックを提供する。

| 関数 | 種別 | 処理 |
|---|---|---|
| `create_user` | `async def` | saltを生成しPBKDF2でパスワードをハッシュ化してUserを作成・保存 |
| `authenticate_user` | `async def` | `select(User)` でユーザーを取得しパスワード検証 |
| `create_access_token` | `def` | JWTトークンを生成（DB不使用） |
| `get_current_user` | `def` | JWTをデコードして `DecodedToken` を返す（DB不使用） |

---

<a id="crudsitempy"></a>
### 📦 [cruds/item.py](cruds/item.py)　―　itemsテーブルのDB操作

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `schemas.ItemCreate`, `ItemUpdate` | 入力スキーマ |
| `models.Item` | itemsテーブルのORMモデル |

**📝 処理概要**

`items` テーブルに対する非同期DB操作関数を提供する。全関数は `async def` で定義し、DB操作には `await` を使用する。

| 関数 | 処理 |
|---|---|
| `get_items` | 全アイテムを取得 |
| `get_items_by_name` | `name` の部分一致（`LIKE`）で検索 |
| `get_item` | `id` と `user_id` で絞り込んで1件取得 |
| `create_item` | 新規アイテムを作成・`await db.commit()` |
| `update_item` | `await get_item` で取得後 `exclude_unset=True` のフィールドのみ更新・`await db.commit()` |
| `delete_item` | `await get_item` で取得後削除・`await db.commit()`（成功時 `True` を返す） |

---

<a id="routersauthpy"></a>
### 🔑 [routers/auth.py](routers/auth.py)　―　/auth エンドポイント定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends`, `HTTPException`, `status` | DI・認証/重複エラー応答 |
| `fastapi.security.OAuth2PasswordRequestForm` | ログインフォームデータ取得 |
| `sqlalchemy.exc.IntegrityError` | username重複（409）の判定 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `cruds.auth` | 認証・ユーザーのDB操作関数 |
| `schemas.UserCreate`, `UserResponse`, `Token` | リクエスト・レスポンスのスキーマ |

**📝 処理概要**

`/auth` プレフィックスの認証エンドポイントを定義する。

| エンドポイント | メソッド | 処理 |
|---|---|---|
| `/auth/signup` | POST | `await auth_cruds.create_user()` でユーザー作成（成功時 `201`、username重複時は `IntegrityError` を捕捉して `409 Conflict`） |
| `/auth/login` | POST | `OAuth2PasswordRequestForm` で受け取り `await auth_cruds.authenticate_user()` で認証後、有効期限20分のJWTを返す（失敗時 `401`） |

---

<a id="routersitempy"></a>
### 🛣️ [routers/item.py](routers/item.py)　―　/items エンドポイント定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends`, `Path`, `Query`, `HTTPException`, `status` | DI・パスパラメータ・クエリパラメータ・エラー応答 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `cruds.item`, `cruds.auth` | DB操作・認証関数 |
| `schemas.ItemCreate`, `ItemUpdate`, `ItemResponse`, `DecodedToken` | リクエスト・レスポンスのスキーマ |

**📝 処理概要**

`/items` プレフィックスのエンドポイントを定義する。`UserDependency`（`Depends(auth_cruds.get_current_user)`）により認証済みユーザーのみアクセス可能なエンドポイントを制御する。

| エンドポイント | メソッド | 認証 | 処理 |
|---|---|---|---|
| `/items` | GET | 不要 | 全アイテム一覧取得。`?name=` クエリパラメータ（2〜20文字）を付けると名前で部分一致検索 |
| `/items/{item_id}` | GET | 必要 | IDで1件取得（自分のアイテムのみ・該当なしは `404`） |
| `/items` | POST | 必要 | アイテム作成（`201`・`user_id` はトークンから付与） |
| `/items/{item_id}` | PUT | 必要 | アイテム更新（該当なしは `404`） |
| `/items/{item_id}` | DELETE | 必要 | アイテム削除（成功時 `bool` を返す・該当なしは `404`） |

> **補足**：名前検索は独立したエンドポイントではなく、`GET /items` の `name` クエリパラメータで処理される（`get_items` ハンドラ内で `name` の有無により `item_cruds.get_items` / `get_items_by_name` を切り替える）。

---

<a id="migrationsenvpy"></a>
### 🔄 [migrations/env.py](migrations/env.py)　―　Alembic非同期マイグレーション設定

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `asyncio` | 非同期処理の実行 |
| `sqlalchemy.ext.asyncio.async_engine_from_config` | 非同期エンジン生成 |
| `sqlalchemy.pool` | NullPool指定（マイグレーション時の接続管理） |
| `alembic.context` | Alembic設定・マイグレーション実行 |
| `models.Base` | autogenerateのためのメタデータ参照 |

**📝 処理概要**

Alembicの非同期マイグレーション設定。`run_migrations_offline()` はDBに接続せずSQLをファイル出力するオフラインモード（同期）。`run_migrations_online()` は `async_engine_from_config` で非同期エンジンを生成し、`connection.run_sync(do_run_migrations)` で同期的にマイグレーションを実行する。`asyncio.run()` で非同期関数をエントリーポイントから呼び出す。

---

<a id="testsconftestpy"></a>
### 🧪 [tests/conftest.py](tests/conftest.py)　―　pytestフィクスチャ・DIオーバーライド定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.testclient.TestClient` | 同期テストクライアント |
| `sqlalchemy.create_engine` | テスト用インメモリSQLiteエンジン生成 |
| `sqlalchemy.pool.StaticPool` | 接続を使い回すテスト用プール |
| `sqlalchemy.orm.sessionmaker` | テスト用同期セッションファクトリ |
| `models.Base`, `Item` | テーブル作成・テストデータ投入 |
| `database.get_db` | DIオーバーライド対象 |
| `cruds.auth.get_current_user` | 認証DIオーバーライド対象 |

**📝 処理概要**

pytestフィクスチャを定義する。アプリ本体は非同期だが `TestClient` による同期テストパターンで実装する。

| フィクスチャ | 処理 |
|---|---|
| `session_fixture` | インメモリSQLiteでテーブル作成・テストデータ（Item×2件）投入 |
| `user_fixture` | テスト用 `DecodedToken` を返す |
| `client_fixture` | `get_db` / `get_current_user` をオーバーライドして `TestClient` を生成 |

`override_get_db` は `yield session_fixture` でDI互換のジェネレータとして定義する。

> **⚠️ ソース上の不整合（要修正）**
> `tests/test_item.py` は `detail` に `"Item not found"` / `"Item not updated"` / `"Item not deleted"` を期待しているが、`routers/item.py` は全て `detail="not found"` を返すため、該当の異常系テストは現状失敗する。テスト側か `routers/item.py` 側のいずれかでメッセージを揃える必要がある。

---

<a id="docker-composeyml"></a>
## 🐳 [docker-compose.yml](docker-compose.yml)　―　開発用DB環境（PostgreSQL + pgAdmin）

`docker compose up` 一発で、アプリの接続先となる **PostgreSQL 16** と、その GUI 管理ツール **pgAdmin 4** をまとめて起動する。DB名 `fleamarket`（フリマアプリ）はこのプロジェクトのデータベース。

### 📄 ファイル全体

```yaml
version: "3.7"
services:
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    ports:
      - 5432:5432
    volumes:
      - ./docker/postgres/init.d:/docker-entrypoint-initdb.d
      - ./docker/postgres/pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: fastapiuser
      POSTGRES_PASSWORD: fastapipass
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
      POSTGRES_DB: fleamarket
    hostname: postgres
    restart: always
    user: root

  pgadmin:
    image: dpage/pgadmin4
    restart: always
    ports:
      - 81:80
    environment:
      PGADMIN_DEFAULT_EMAIL: fastapi@example.com
      PGADMIN_DEFAULT_PASSWORD: password
    volumes:
      - ./docker/pgadmin:/var/lib/pgadmin
    depends_on:
      - postgres
```

### 🧩 サービス一覧

| サービス | イメージ | 役割 |
|---|---|---|
| `postgres` | `postgres:16-alpine` | アプリの接続先となるPostgreSQL本体（軽量Alpineベース） |
| `pgadmin` | `dpage/pgadmin4` | ブラウザからDBを操作・確認するWeb管理UI |

### 🐘 postgres サービス

| 項目 | 値 | 説明 |
|---|---|---|
| image | `postgres:16-alpine` | PostgreSQL 16（軽量Alpineベース） |
| container_name | `postgres` | コンテナ名を `postgres` に固定 |
| ports | `5432:5432` | ホストの5432番を公開。ローカルのFastAPIから接続可能 |
| volumes | `init.d → /docker-entrypoint-initdb.d` | 初回起動時に実行される初期化SQL/スクリプト置き場 |
| volumes | `pgdata → /var/lib/postgresql/data` | DB実データを永続化（コンテナ削除後もデータが残る） |
| environment | `POSTGRES_USER=fastapiuser` | DBユーザー |
| environment | `POSTGRES_PASSWORD=fastapipass` | DBパスワード |
| environment | `POSTGRES_DB=fleamarket` | 初期作成されるDB名 |
| environment | `POSTGRES_INITDB_ARGS=--encoding=UTF-8` | エンコーディングをUTF-8に指定 |
| hostname | `postgres` | コンテナ間通信用ホスト名。pgAdminからの接続先ホストに指定する |
| restart | `always` | クラッシュ・再起動時に自動復帰 |
| user | `root` | コンテナを root 実行（権限上は非推奨・後述の補足参照） |

接続URL（`config.py` の `database_url` / `.env` の `DATABASE_URL`）は非同期ドライバを使い、以下の形式になる：

```
postgresql+asyncpg://fastapiuser:fastapipass@0.0.0.0:5432/fleamarket
```

> ※ ホストは `localhost` でも同義。本リポジトリの `.env` では `0.0.0.0` を指定している。

### 🖥️ pgadmin サービス

| 項目 | 値 | 説明 |
|---|---|---|
| image | `dpage/pgadmin4` | pgAdmin 4（Web版DB管理ツール） |
| ports | `81:80` | ブラウザで `http://localhost:81` からアクセス |
| environment | `PGADMIN_DEFAULT_EMAIL=fastapi@example.com` | ログイン用メールアドレス |
| environment | `PGADMIN_DEFAULT_PASSWORD=password` | ログイン用パスワード |
| volumes | `pgadmin → /var/lib/pgadmin` | pgAdminの設定・接続情報を永続化 |
| depends_on | `postgres` | postgres起動後に立ち上げ |

> **補足**
> - `depends_on` は起動順序を制御するだけで、PostgreSQLの接続受付完了までは保証しない。確実を期すなら `healthcheck` + `condition: service_healthy` の併用を推奨。
> - `version: "3.7"` は Compose V2 では無視される属性のため省略可。
> - `user: root` は権限整合性の観点から非推奨。ボリュームのパーミッション問題が出ていなければ外してよい。
