# 🛒 フリーマーケットアプリ（PostgreSQL + pgAdmin）

## 📁 ディレクトリ・ファイル構成

```
python-12-fastapi-fleamarket/
│
├── docker-compose.yml # 開発用DB環境（PostgreSQL + pgAdmin）
│
├── main.py            # エントリーポイント
├── config.py          # 環境変数管理（pydantic-settings）
├── enums.py           # 共通Enum定義（ItemStatusEnum）
├── database.py        # DB接続・非同期セッション管理
├── models.py          # SQLAlchemy ORMモデル
├── schemas.py         # Pydanticスキーマ・型エイリアス
├── security.py        # パスワードハッシュ（Argon2）
├── storage.py         # 画像のローカル保存層（将来S3へ差し替え可）
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
├── frontapp/          # フロントエンド（index.htmlにJS埋め込み・app.jsは旧コピー）
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── uploads/           # アップロード画像の保存先（実行時に自動生成）
│   └── items/
│
├── pytest.ini         # pytest設定（asyncio_mode = auto）
│
└── tests/             # pytestテスト
    ├── conftest.py    # 非同期フィクスチャ・DIオーバーライド定義
    └── test_item.py   # items エンドポイントのテスト（async）
```

## 📋 ファイル一覧

| ディレクトリ | ソース | 説明 |
|---|---|---|
| ルート | [config.py](#configpy) | 環境変数管理（pydantic-settings・SecretStr・cache） |
| ルート | [enums.py](#enumspy) | 共通Enum定義（ItemStatusEnum） |
| ルート | [database.py](#databasepy) | 非同期DBエンジン・セッション管理 |
| ルート | [schemas.py](#schemaspy) | Pydanticスキーマ・型エイリアス定義 |
| ルート | [models.py](#modelspy) | SQLAlchemy ORMモデル定義（Item・User） |
| ルート | [security.py](#securitypy) | パスワードのハッシュ化・検証（Argon2） |
| ルート | [storage.py](#storagepy) | 画像のローカル保存・削除（`/images` 配信と対応） |
| `cruds/` | [auth.py](#crudsauthpy) | 認証・ユーザーのDB操作・JWT生成 |
| `cruds/` | [item.py](#crudsitempy) | itemsテーブルのDB操作 |
| `routers/` | [auth.py](#routersauthpy) | /auth エンドポイント定義 |
| `routers/` | [item.py](#routersitempy) | /items エンドポイント定義 |
| ルート | [main.py](#mainpy) | エントリーポイント・CORS・ミドルウェア設定 |
| `tests/` | [conftest.py](#testsconftestpy) | 非同期pytestフィクスチャ・DIオーバーライド定義 |
| `tests/` | [test_item.py](#teststest_itempy) | items エンドポイントのテスト（async） |
| ルート | pytest.ini | pytest設定（`asyncio_mode = auto`） |
| ルート | [docker-compose.yml](#docker-composeyml) | 開発用DB環境（PostgreSQL + pgAdmin） |
| `frontapp/` | index.html / app.js / styles.css | フロントエンド（画像アップロード対応） |

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

# 依存関係をインストール（argon2-cffi を含む）
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

### 🗃️ DB初期化（マイグレーション）

DB環境を起動したら、Alembicでテーブルを作成する。

```bash
# 現行モデルから初期マイグレーションを生成
alembic revision --autogenerate -m "initial schema"

# DBへ適用（users / items / alembic_version テーブルが作られる）
alembic upgrade head
```

> `.env` の `DATABASE_URL` は非同期ドライバ付きで、compose の `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` と一致させる：
> `postgresql+asyncpg://fastapiuser:fastapipass@localhost:5432/fleamarket`
> `POSTGRES_*` 環境変数はデータが空の初回起動時のみ適用されるため、ユーザー/DBを作り直したいときは `docker compose down -v` でボリュームごと削除してから起動する。
>
> `.env` の例（`SECRET_KEY` は `python -c "import secrets; print(secrets.token_hex(32))"` で生成）：
> ```
> SECRET_KEY=<ランダムな16進文字列>
> DATABASE_URL=postgresql+asyncpg://fastapiuser:fastapipass@localhost:5432/fleamarket
> ECHO_SQL=false
> ```
> 認証情報は `alembic.ini` に直書きせず（`sqlalchemy.url = ` を空にする）、`migrations/env.py` が `get_settings().database_url` から注入する。`.env` は `.gitignore` で追跡対象外にする。

### 🧪 テスト実行

```bash
# テストは非同期（httpx.AsyncClient + aiosqlite インメモリDB）
python -m pytest

# 依存: pytest / pytest-asyncio / aiosqlite / httpx（requirements.txt に含める）
```

> **⚠️ 補足**：`uvicorn` 起動・テスト実行の前に `uploads/items/` が存在する必要がある（`main.py` の `StaticFiles` マウントが import 時にディレクトリを要求する）。無い場合は `mkdir -p uploads/items`（PowerShell: `New-Item -ItemType Directory -Force -Path uploads/items`）で作成する。

---

## 🖼 画像アップロード（ローカル保存・最小構成）

アイテムに商品画像を1枚添付できる。**まずはローカルディスク保存**の最小構成で、保存層（`storage.py`）を差し替えれば S3 等へ移行できる設計。

**フロー**

1. フロントの出品/編集ダイアログで画像を選択（任意）。クライアント側で形式（jpeg/png/webp/gif）とサイズ（5MB）を事前チェックしプレビュー表示。
2. アイテムを作成/更新（JSON）した後、画像が選択されていれば `POST /items/{item_id}/image` に `multipart/form-data` で送信。
3. バックエンドは所有者を確認し `uploads/items/<item_id>_<uuid>.<ext>` に保存、`items.image_url` を更新。
4. `app.mount("/images", StaticFiles(...))` により `GET /images/items/...` で配信。フロントは `API_BASE + image_url` を `<img>` に表示。

**仕様・制約**

- 検証: 実データを **Pillow で読み込み** `format` を判定する（`content_type` ヘッダに依存しない）。jpeg/png/webp/gif 以外は `415`、5MB超は `413`、空は `400`。
- 認可: 所有者（`user_id` 一致）のアイテムのみ許可（他人のアイテムは `404`）。
- 置き換え: 再アップロード時は旧ファイルを削除。
- 依存: `UploadFile`（multipart）の受け取りに **`python-multipart`**、画像検証に **`Pillow`** が必要。
- 既知の割り切り: アイテム削除時に画像ファイルは削除していない（孤児ファイルが残る）。運用では削除フックか定期GCで対応する。

> **フロントエンド**：実体は `frontapp/index.html`（JSを埋め込み）。`app.js` は読み込まれない旧コピーだが同じ変更を反映済み。出品ダイアログに写真フィールドとプレビューを追加し、カードに画像サムネイルを表示する。

---

## 📄 Python ソース詳細

<a id="configpy"></a>
### ⚙️ [config.py](config.py)　―　環境変数管理（pydantic-settings・SecretStr・cache）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `functools.cache` | `Settings` インスタンスをキャッシュし再生成を防ぐ |
| `pydantic.SecretStr` | `secret_key` をログ・`repr` に出さない秘匿型として保持 |
| `pydantic_settings.BaseSettings` | 環境変数を型安全に管理するベースクラス |
| `pydantic_settings.SettingsConfigDict` | `.env` ファイル読み込み設定 |

**📝 処理概要**

`BaseSettings` を継承した `Settings` クラスで環境変数を管理する。`secret_key`（`SecretStr`）・`database_url` を必須項目とし、`echo_sql`（`bool`・デフォルト `False`）でSQLログ出力を切り替え、`cors_origins` は `http://127.0.0.1:5500` / `http://localhost:5500` をデフォルト値に持つ。`model_config = SettingsConfigDict(env_file=".env")` で `.env` を読み込む。`get_settings()` に `@cache` を付与し、アプリ全体で同一インスタンスを共有する。

---

<a id="enumspy"></a>
### 🏷️ [enums.py](enums.py)　―　共通Enum定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `enum.StrEnum` | 文字列ベースの列挙型（Python 3.11+） |

**📝 処理概要**

アプリ全体で共有する列挙型を定義する最下層モジュール（他のどのモジュールにも依存しない）。`ItemStatusEnum(StrEnum)` に `ON_SALE` / `SOLD_OUT` を定義する。`schemas.py`（Pydantic層）と `models.py`（ORM層）の双方がここを参照することで、両者の間に直接の依存を作らず、循環importを避ける。

---

<a id="databasepy"></a>
### 🗄️ [database.py](database.py)　―　非同期DBエンジン・セッション管理

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `collections.abc.AsyncGenerator` | `get_db` の戻り値型アノテーション |
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期DBエンジン生成 |
| `sqlalchemy.ext.asyncio.async_sessionmaker` | 非同期セッションファクトリ生成 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッション型 |
| `sqlalchemy.orm.DeclarativeBase` | ORMモデルの基底クラス（SQLAlchemy 2.0スタイル） |
| `config.get_settings` | `database_url` の取得 |

**📝 処理概要**

非同期対応の `engine` / `async_session` / `Base` を生成・公開する。冒頭で `settings = get_settings()` を一度受け、`engine` は `create_async_engine(settings.database_url, echo=settings.echo_sql)` で生成する（SQLログ出力は `.env` の `ECHO_SQL` で切り替え可能・既定は無効）。`async_session` は `async_sessionmaker` で生成する。`expire_on_commit=False` により commit 後もオブジェクトの属性にアクセス可能にする（async では実質必須）。`Base` は SQLAlchemy 2.0スタイルの `DeclarativeBase` を継承して定義する。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出し、`async with` により終了後に確実にクローズする。戻り値型は Python 3.11 に合わせ `AsyncGenerator[AsyncSession, None]`（2引数表記）とする。データベースURLには非同期ドライバ（PostgreSQLの場合 `postgresql+asyncpg`）を使用する。

> **トランザクション方針**：`commit` はエンドポイント側（`routers/`）に集約し、各CRUD（`cruds/`）は `commit` せず `flush` に留める。これにより「1リクエスト＝1トランザクション」を担保する。

---

<a id="schemaspy"></a>
### 📐 [schemas.py](schemas.py)　―　Pydanticスキーマ・型エイリアス定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `datetime.datetime` | レスポンスの日時フィールド型 |
| `typing.Annotated` | 型エイリアス（`ItemId`・`ItemName` 等）への制約付与 |
| `fastapi.Form`, `HTTPException` | フォーム受け取り・バリデーションエラー応答 |
| `pydantic.BaseModel` | スキーマ基底クラス |
| `pydantic.Field` | バリデーション制約・サンプル値の付与 |
| `pydantic.ConfigDict` | ORM連携・空白トリム設定 |
| `pydantic.ValidationError` | フォーム変換失敗時の捕捉 |
| `enums.ItemStatusEnum` | ステータス型エイリアスの元となる列挙型 |

**📝 処理概要**

アプリ全体のPydanticスキーマを一元管理する。`ItemStatusEnum` 自体の定義は `enums.py` に移設済みで、ここでは import して使う。型エイリアス（`ItemId`, `ItemName`, `ItemPrice`, `ItemStatus` 等）で `Field` によるバリデーション制約とサンプル値を共通化し、各スキーマクラスで再利用する。`StrippedBaseModel`（`ConfigDict(str_strip_whitespace=True)`）を共通の基底とし、全スキーマで前後空白を自動除去する。

また `item_create_form()` はフォーム（`multipart/form-data`）の各値を受け取り、`ItemCreate` へ変換する依存関数。変換時の `ValidationError` を捕捉して `HTTPException(422)` に変換する。

スキーマ一覧：

| クラス | 用途 |
|---|---|
| `StrippedBaseModel` | 全スキーマ共通の基底（`str_strip_whitespace=True`） |
| `ItemBase` | アイテム共通フィールド（`name` / `price` / `description`）の基底スキーマ |
| `ItemCreate` | アイテム作成リクエスト（`ItemBase` を継承） |
| `ItemUpdate` | アイテム更新リクエスト（全フィールド省略可） |
| `ItemResponse` | アイテムレスポンス（`ItemBase` を継承・`image_url` を含む・`from_attributes=True`） |
| `UserCreate` | ユーザー作成リクエスト（`username` / `password`） |
| `UserResponse` | ユーザーレスポンス（`password_hash` を含まない・`from_attributes=True`） |
| `Token` | JWTトークンレスポンス |
| `DecodedToken` | JWTデコード結果（`username` / `user_id`） |

---

<a id="modelspy"></a>
### 🧱 [models.py](models.py)　―　SQLAlchemy ORMモデル定義（Item・User）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 前方参照（`Mapped[User]` 等）をクォートなしで記述 |
| `datetime.UTC`, `datetime` | タイムスタンプのデフォルト値生成（UTC） |
| `sqlalchemy.DateTime`, `String`, `ForeignKey` | カラム型・外部キー定義 |
| `sqlalchemy.orm.Mapped` | カラム・リレーションの型アノテーション |
| `sqlalchemy.orm.mapped_column` | 型付きカラム定義（SQLAlchemy 2.0スタイル） |
| `sqlalchemy.orm.relationship` | テーブル間リレーション定義 |
| `database.Base` | ORMモデルの基底クラス |
| `enums.ItemStatusEnum` | `status` カラムの型 |

**📝 処理概要**

`items` / `users` テーブルに対応するORMモデルを定義する。SQLAlchemy 2.0スタイルの `Mapped` + `mapped_column` を使用し、`price: Mapped[int]` のように推論可能なカラムは `mapped_column()` を省略する。`TimestampMixin` で `created_at` / `updated_at`（いずれも `DateTime(timezone=True)`・デフォルトは `datetime.now(UTC)`、更新時は `onupdate`）を共通化する。

`Item` モデルは `id` / `name` / `price` / `description` / `image_url` / `status` / `created_at` / `updated_at` / `user_id` のカラムを持つ。`image_url` は商品画像の公開URLを保持する任意カラム（nullable）。`status` は `Mapped[ItemStatusEnum]` の型アノテーションだけで DB Enum 型が自動生成される（`Enum(...)` の明示は不要）。デフォルトは `ItemStatusEnum.ON_SALE`。`user_id` は `ForeignKey("users.id", ondelete="CASCADE")` で `users` テーブルを参照し、`user: Mapped[User]` で多対1の逆参照を構成する。

`User` モデルは `id` / `username`（`unique=True`）/ `password_hash` / `created_at` / `updated_at` のカラムを持つ。**パスワードは Argon2 ハッシュ文字列に salt が埋め込まれるため、独立した `salt` カラムは持たない**（`password_hash` のみ）。`items: Mapped[list[Item]]` により1人のUserが複数のItemを所有する1対多リレーションを構成する。

---

<a id="securitypy"></a>
### 🔒 [security.py](security.py)　―　パスワードのハッシュ化・検証（Argon2）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `argon2.PasswordHasher` | Argon2 によるハッシュ生成・検証 |
| `argon2.exceptions.VerifyMismatchError` | パスワード不一致時の例外 |

**📝 処理概要**

パスワードのハッシュ化と検証を担う独立モジュール。`argon2-cffi` の `PasswordHasher` をモジュールレベルで1つ生成（`_ph`）し、使い回す。

| 関数 | 処理 |
|---|---|
| `hash_password` | 平文パスワードを Argon2 でハッシュ化して返す。返り値の文字列（`$argon2id$v=19$m=...`）に salt・パラメータが埋め込まれる |
| `verify_password` | 平文パスワードと保存済みハッシュを照合。一致すれば `True`、不一致は `VerifyMismatchError` を捕捉して `False` を返す |

salt がハッシュ文字列に内包されるため、検証時に salt を別途渡す必要がなく、DB側に独立の `salt` カラムを持たない設計を可能にしている。

---

<a id="storagepy"></a>
### 🗂️ [storage.py](storage.py)　―　画像のローカル保存層

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 型アノテーションの遅延評価 |
| `io` | バイト列を `Pillow` に渡すためのバッファ |
| `uuid` | 保存ファイル名の一意化 |
| `pathlib.Path` | 保存パスの組み立て・ファイル操作 |
| `fastapi.UploadFile`, `HTTPException`, `status` | アップロード受け取り・検証エラー応答 |
| `PIL.Image` | 画像データの読み込み・形式判定・検証 |

**📝 処理概要**

アイテム画像をローカル（`uploads/items/`）に保存し、公開URL（`/images/items/<item_id>_<uuid>.<ext>`）を返す層。`routers` / `cruds` は文字列の `image_url` だけを扱うため、将来 S3（presigned URL）へ移行する場合はこの層のみ差し替えればよい。形式の判定は `content_type` ヘッダに頼らず、**実データを `Pillow` で開いて `format` を確認**する（`ALLOWED_FORMATS` は JPEG/PNG/WEBP/GIF）。

| 関数 | 処理 |
|---|---|
| `ensure_dirs` | 保存先 `uploads/items/` を作成（起動時に呼ぶ） |
| `save_item_image` | 空ファイルは `400`、5MB超は `413`、`Pillow` で開けない/対応外形式は `415` を返して検証し、保存して公開URLを返す |
| `delete_item_image` | 公開URLに対応するローカルファイルを削除（置き換え時に使用・ベストエフォート） |

---

<a id="crudsauthpy"></a>
### 🔐 [cruds/auth.py](cruds/auth.py)　―　認証・ユーザーのDB操作・JWT生成

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `datetime.datetime`, `timedelta`, `timezone` | JWT有効期限の計算 |
| `typing.Annotated` | DI（`Depends`）の型付与 |
| `jwt`（PyJWT）, `jwt.exceptions.InvalidTokenError` | JWTエンコード・デコード |
| `fastapi.Depends`, `HTTPException`, `status` | DI・認証エラー応答 |
| `fastapi.security.OAuth2PasswordBearer` | OAuth2トークン取得スキーマ |
| `pydantic.ValidationError` | デコード結果の検証失敗捕捉 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `sqlalchemy.exc.IntegrityError` | username重複時の例外捕捉 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `config.get_settings` | `secret_key` の取得 |
| `models.User` | usersテーブルのORMモデル |
| `schemas.UserCreate`, `DecodedToken` | 入力・出力スキーマ |
| `security.hash_password`, `verify_password` | パスワードのハッシュ化・検証（Argon2） |

**📝 処理概要**

認証・ユーザー管理に関するDB操作と認証ロジックを提供する。パスワードのハッシュ化・検証は `security.py`（Argon2）に委譲し、このモジュール自身はハッシュアルゴリズムを持たない。JWTの署名鍵は `get_settings().secret_key.get_secret_value()` で `SecretStr` から文字列を取り出して保持する（`SecretStr` のまま `jwt.encode`/`decode` に渡すと `TypeError` になるため）。

| 関数 | 種別 | 処理 |
|---|---|---|
| `create_user` | `async def` | `hash_password()` でハッシュ化して `User` を作成し `await db.flush()`（username重複は `IntegrityError` を送出） |
| `authenticate_user` | `async def` | `select(User)` で取得し `verify_password()` でパスワード検証 |
| `create_access_token` | `def` | JWTトークンを生成（DB不使用・`HS256`） |
| `get_current_user` | `def` | JWTをデコードして `DecodedToken` を返す（DB不使用） |

---

<a id="crudsitempy"></a>
### 📦 [cruds/item.py](cruds/item.py)　―　itemsテーブルのDB操作

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `models.Item` | itemsテーブルのORMモデル |
| `schemas.ItemCreate`, `ItemUpdate` | 入力スキーマ |

**📝 処理概要**

`items` テーブルに対する非同期DB操作関数を提供する。全関数は `async def` で定義し、DB操作には `await` を使用する。コミットは `routers` 側に集約し、各関数は `await db.flush()` に留める。

| 関数 | 処理 |
|---|---|
| `get_items` | 全アイテムを取得 |
| `get_items_by_name` | `name` の部分一致（`ILIKE`）で検索。`%` `_` `\` をエスケープして安全に部分一致 |
| `get_item` | `id` と `user_id` で絞り込んで1件取得 |
| `create_item` | 新規アイテムを作成・`await db.flush()` / `refresh` |
| `update_item` | `await get_item` で取得後 `exclude_unset=True` のフィールドのみ更新・`await db.flush()` |
| `delete_item` | `await get_item` で取得後削除・`await db.flush()`（成功時 `True` を返す） |
| `set_item_image` | `image_url` を設定し `await db.flush()` / `refresh`（画像アップロード用） |

---

<a id="routersauthpy"></a>
### 🔑 [routers/auth.py](routers/auth.py)　―　/auth エンドポイント定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `datetime.timedelta` | JWT有効期限の指定 |
| `typing.Annotated` | DIの型付与 |
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends`, `HTTPException`, `status` | DI・認証/重複エラー応答 |
| `fastapi.security.OAuth2PasswordRequestForm` | ログインフォームデータ取得 |
| `sqlalchemy.exc.IntegrityError` | username重複（409）の判定 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `cruds.auth` | 認証・ユーザーのDB操作関数 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `schemas.Token`, `UserCreate`, `UserResponse` | リクエスト・レスポンスのスキーマ |

**📝 処理概要**

`/auth` プレフィックスの認証エンドポイントを定義する。コミットはこのルーター層で行う（`await db.commit()`）。

| エンドポイント | メソッド | 処理 |
|---|---|---|
| `/auth/signup` | POST | `await auth_cruds.create_user()` でユーザー作成（成功時 `201`。username重複時は `IntegrityError` を捕捉して `409 Conflict`） |
| `/auth/login` | POST | `OAuth2PasswordRequestForm` で受け取り `await auth_cruds.authenticate_user()` で認証後、有効期限20分のJWTを返す（失敗時 `401`） |

---

<a id="routersitempy"></a>
### 🛣️ [routers/item.py](routers/item.py)　―　/items エンドポイント定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `typing.Annotated` | DI・パス/クエリパラメータの型付与 |
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends`, `Path`, `Query`, `HTTPException`, `status` | DI・パス/クエリパラメータ・エラー応答 |
| `fastapi.UploadFile`, `File` | 画像アップロード（multipart）の受け取り |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `cruds.item`, `cruds.auth` | DB操作・認証関数 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `schemas.ItemCreate`, `ItemUpdate`, `ItemResponse`, `DecodedToken`, `item_create_form` | リクエスト・レスポンスのスキーマ・フォーム変換 |
| `storage.save_item_image`, `delete_item_image` | 画像の保存・削除 |

**📝 処理概要**

`/items` プレフィックスのエンドポイントを定義する。`UserDependency`（`Depends(auth_cruds.get_current_user)`）により認証済みユーザーのみアクセス可能なエンドポイントを制御する。

| エンドポイント | メソッド | 認証 | 処理 |
|---|---|---|---|
| `/items` | GET | 不要 | 全アイテム一覧取得。`?name=` クエリパラメータ（1〜20文字）を付けると名前で部分一致検索 |
| `/items/{item_id}` | GET | 必要 | IDで1件取得（自分のアイテムのみ・該当なしは `404 Item not found`） |
| `/items` | POST | 必要 | アイテム作成（`multipart/form-data`／`item_create_form` 経由・`201`・`user_id` はトークンから付与・画像同時アップロード可） |
| `/items/{item_id}` | PATCH | 必要 | アイテム部分更新（該当なしは `404 Item not updated`） |
| `/items/{item_id}` | DELETE | 必要 | アイテム削除（成功時 `204 No Content`・該当なしは `404 Item not deleted`） |
| `/items/{item_id}/image` | POST | 必要 | 画像アップロード（`multipart/form-data`・所有者のみ・成功時 `ItemResponse`。該当なしは `404 Item not found`。置き換え時は旧ファイル削除） |

> **補足**：名前検索は独立したエンドポイントではなく、`GET /items` の `name` クエリパラメータで処理される（`get_items` ハンドラ内で `name` の有無により `item_cruds.get_items` / `get_items_by_name` を切り替える）。

---

<a id="mainpy"></a>
### 🚪 [main.py](main.py)　―　エントリーポイント・CORS・ミドルウェア設定

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `time` | 処理時間計測（`X-Process-Time`） |
| `contextlib.asynccontextmanager` | `lifespan` の定義 |
| `fastapi.FastAPI`, `Request` | アプリ生成・ミドルウェアのリクエスト処理 |
| `fastapi.middleware.cors.CORSMiddleware` | CORS設定 |
| `fastapi.staticfiles.StaticFiles` | アップロード画像の静的配信 |
| `config.get_settings` | CORS許可オリジン等の取得 |
| `routers.auth`, `routers.item` | ルーター登録 |
| `storage.UPLOAD_ROOT`, `ensure_dirs` | 保存先ディレクトリの用意・配信元 |

**📝 処理概要**

アプリケーションのエントリーポイント。`lifespan`（`@asynccontextmanager`）で起動時に `ensure_dirs()` を呼び、`uploads/items/` を用意する。`CORSMiddleware` で `settings.cors_origins`（`http://127.0.0.1:5500` / `http://localhost:5500`）からのアクセスを許可する。`@app.middleware("http")` の `add_process_time_header` は各レスポンスに処理時間 `X-Process-Time` ヘッダを付与する（有効）。`app.mount("/images", StaticFiles(...))` でアップロード画像を静的配信し、`item` / `auth` の各ルーターを登録する。

---

<a id="testsconftestpy"></a>
### 🧪 [tests/conftest.py](tests/conftest.py)　―　非同期pytestフィクスチャ・DIオーバーライド定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `os`, `sys` | アプリのルートを `sys.path` に追加 |
| `pytest_asyncio` | 非同期フィクスチャ定義（`@pytest_asyncio.fixture`） |
| `httpx.ASGITransport`, `AsyncClient` | ASGIアプリを直接叩く非同期テストクライアント |
| `sqlalchemy.ext.asyncio.create_async_engine`, `async_sessionmaker` | テスト用インメモリ非同期SQLiteエンジン・セッション |
| `sqlalchemy.pool.StaticPool` | 単一接続を使い回すテスト用プール（インメモリDB共有） |
| `database.Base`, `get_db` | テーブル定義メタデータ・DIオーバーライド対象 |
| `models.Item` | テーブル登録・テストデータ投入 |
| `schemas.DecodedToken` | 認証オーバーライドの戻り値 |
| `main.app` | テスト対象アプリ |
| `cruds.auth.get_current_user` | 認証DIオーバーライド対象 |

**📝 処理概要**

アプリ本体が完全に非同期（`async def` のCRUD・`AsyncSession`）であるため、テストも**非同期**で実装する。同期の `TestClient` ではなく `httpx.AsyncClient` + `ASGITransport` でアプリを直接叩き、DBには `aiosqlite` によるインメモリ非同期SQLiteを注入する。

| フィクスチャ | 処理 |
|---|---|
| `session_fixture` | `create_async_engine("sqlite+aiosqlite://")` でインメモリDBを作り、`Base.metadata.create_all` でテーブル作成、テストデータ（`PC1` / `PC2` の Item×2件）を `await session.commit()` で投入して `yield`。終了後 `await engine.dispose()` |
| `client_fixture` | `get_db`（→ `session_fixture` を `yield` する非同期ジェネレータ）と `get_current_user`（→ `DecodedToken(username="user1", user_id=1)`）をオーバーライドし、`AsyncClient` を生成。終了後に `app.dependency_overrides.clear()` |

`StaticPool` によりインメモリDBの単一接続が全操作で共有されるため、シード投入とリクエスト処理が同じDB状態を参照する。

---

<a id="teststest_itempy"></a>
### ✅ [tests/test_item.py](tests/test_item.py)　―　items エンドポイントのテスト

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `pytest` | `@pytest.mark.asyncio` マーカー付与 |
| `httpx.AsyncClient` | `client_fixture` の型注釈 |

**📝 処理概要**

`/items` 系エンドポイントの正常系・異常系を検証する。全テストは `async def` + `@pytest.mark.asyncio` で定義し、`conftest.py` の `client_fixture`（`AsyncClient`）を受け取って `await client_fixture.get(...)` のように非同期で呼ぶ。

| テスト | 検証内容 |
|---|---|
| `test_find_all` | 一覧取得で2件返ること |
| `test_find_by_id_正常系` | `GET /items/1` が `id=1` を返すこと |
| `test_find_by_id_異常系` | `GET /items/10` が `404` かつ `detail == "Item not found"` |
| `test_find_by_name` | `GET /items?name=PC1`（末尾スラッシュ無し）で1件（`PC1`）に絞れること |
| `test_create` | `POST /items` にフォームデータ（`data={...}`）で作成し `201`、一覧が3件に増えること |
| `test_update_正常系` | `PATCH /items/1` が `200` かつ内容が反映されること |
| `test_update_異常系` | `PATCH /items/10` が `404` かつ `detail == "Item not updated"` |
| `test_delete_正常系` | `DELETE /items/1` が `204` かつ一覧が1件に減ること |
| `test_delete_異常系` | `DELETE /items/10` が `404` かつ `detail == "Item not deleted"` |

> **メモ**：以前あった「テストの期待メッセージと `routers/item.py` の返す `detail` の不整合」は、`routers/item.py` 側を `Item not found` / `Item not updated` / `Item not deleted` に統一したことで解消済み。全9テストがパスする。
>
> **補足**：作成テストは `json=` ではなく `data=`（フォーム）で送る。作成エンドポイントが `item_create_form`（`Form`）経由で受け取るため。更新は `PUT` ではなく `PATCH`、削除の成功は `204 No Content`。`GET /items` は末尾スラッシュ無しで定義されているため、`AsyncClient`（リダイレクト非追従）では `/items?name=` と書く。

---

<a id="pytestini"></a>
### ⚙️ pytest.ini　―　pytest設定

```ini
[pytest]
asyncio_mode = auto
```

`asyncio_mode = auto` により、`@pytest.mark.asyncio` を付けなくても `async def test_*` が自動的に非同期テストとして実行される（本プロジェクトのテストは明示マーカーも付けているため、どちらでも動作する）。

> **配置・命名**
> 設定が有効になるには、ファイル名が **`pytest.ini`（スペース無し）** で、かつ **プロジェクト直下** に置かれている必要がある。正しく配置すると `pytest` 実行時のヘッダに `configfile: pytest.ini` と `asyncio: mode=Mode.AUTO` が表示される。`tests/` 配下や `pytest .ini`（スペース入り）では設定ファイルとして認識されず `Mode.STRICT` のままになるので注意。

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
