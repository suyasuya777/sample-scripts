# 🛒 フリーマーケットアプリ（FastAPI + PostgreSQL）

FastAPI / SQLAlchemy 2.0（非同期）/ PostgreSQL による学習用フリマAPI。JWT認証、Argon2によるパスワード管理、画像アップロードを備える。

## 🧰 前提バージョン

| | バージョン |
|---|---|
| Python | 3.11 |
| FastAPI | 0.141.x |
| pydantic / pydantic-settings | 2.13.x / 2.15.x |
| SQLAlchemy | 2.0.51 |
| Alembic | 1.x |
| PostgreSQL | 16（Docker） |

---

## 📁 ディレクトリ・ファイル構成

```
python-12-fastapi-fleamarket/
│
├── docker-compose.yml # 開発用DB環境（PostgreSQL + pgAdmin）
├── alembic.ini        # Alembic設定（sqlalchemy.url は空・env.pyから注入）
├── .env               # 環境変数（Git管理外）
│
├── main.py            # エントリーポイント・CORS・ミドルウェア・静的配信
├── config.py          # 環境変数管理（pydantic-settings）
├── enums.py           # 共通Enum定義（ItemStatusEnum）
├── database.py        # DB接続・非同期セッション管理
├── models.py          # SQLAlchemy ORMモデル
├── schemas.py         # Pydanticスキーマ・型エイリアス
├── security.py        # パスワードハッシュ（Argon2）
├── storage.py         # 画像のローカル保存層（将来S3へ差し替え可）
│
├── routers/           # エンドポイント定義
│   ├── auth.py        # /auth エンドポイント
│   └── item.py        # /items エンドポイント
│
├── cruds/             # DB操作ロジック
│   ├── auth.py        # 認証・ユーザーのDB操作・JWT
│   └── item.py        # items テーブルのDB操作
│
├── migrations/        # Alembicマイグレーション（alembic init -t async migrations で生成）
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── docker/
│   └── postgres/
│       └── init.d/    # 初回起動時の初期化SQL/スクリプト（DB実データは名前付きボリューム）
│
├── uploads/           # アップロード画像の保存先（起動時に自動生成）
│   └── items/
│
├── pytest.ini         # pytest設定（asyncio_mode = auto）
│
└── tests/             # pytestテスト
    ├── __init__.py         # helpers を tests パッケージとして import するため
    ├── conftest.py         # 非同期フィクスチャ・DIオーバーライド定義
    ├── helpers.py          # テスト用の画像バイト列生成ヘルパー
    ├── test_item.py        # items の基本CRUD
    ├── test_item_authz.py  # 所有者チェック・認証
    ├── test_item_image.py  # 画像アップロード
    └── test_auth.py        # signup / login
```

## 📋 ファイル一覧

| ディレクトリ | ソース | 説明 |
|---|---|---|
| ルート | [config.py](#configpy) | 環境変数管理（pydantic-settings・SecretStr・cache） |
| ルート | [enums.py](#enumspy) | 共通Enum定義（ItemStatusEnum） |
| ルート | [database.py](#databasepy) | 非同期DBエンジン・セッション管理 |
| ルート | [models.py](#modelspy) | SQLAlchemy ORMモデル定義（Item・User） |
| ルート | [schemas.py](#schemaspy) | Pydanticスキーマ・型エイリアス定義 |
| ルート | [security.py](#securitypy) | パスワードのハッシュ化・検証（Argon2） |
| ルート | [storage.py](#storagepy) | 画像のローカル保存・削除（`/images` 配信と対応） |
| `cruds/` | [auth.py](#crudsauthpy) | 認証・ユーザーのDB操作・JWT生成 |
| `cruds/` | [item.py](#crudsitempy) | itemsテーブルのDB操作 |
| `routers/` | [auth.py](#routersauthpy) | /auth エンドポイント定義 |
| `routers/` | [item.py](#routersitempy) | /items エンドポイント定義 |
| ルート | [main.py](#mainpy) | エントリーポイント・CORS・ミドルウェア設定 |
| `tests/` | [conftest.py](#testsconftestpy) | 非同期pytestフィクスチャ・DIオーバーライド定義 |
| `tests/` | [helpers.py](#testshelperspy) | テスト用の画像バイト列生成ヘルパー |
| `tests/` | [test_item.py](#teststest_itempy) | items の基本CRUDテスト |
| `tests/` | [test_item_authz.py](#teststest_item_authzpy) | 所有者チェック・認証のテスト |
| `tests/` | [test_item_image.py](#teststest_item_imagepy) | 画像アップロードのテスト |
| `tests/` | [test_auth.py](#teststest_authpy) | signup / login のテスト |
| ルート | [pytest.ini](#pytestini) | pytest設定（`asyncio_mode = auto`） |
| ルート | [docker-compose.yml](#docker-composeyml) | 開発用DB環境（PostgreSQL + pgAdmin） |

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
python -m pip install -r requirements.txt

# DB環境を起動（バックグラウンド）
docker compose up -d

# STATUS が (healthy) になったことを確認
docker compose ps

# マイグレーション適用（後述）
alembic upgrade head

# サーバーの起動
python -m uvicorn main:app --reload

# ブラウザを起動
http://localhost:8000/docs
```

### 📦 主な依存パッケージ

```
fastapi[standard]
sqlalchemy[asyncio]
asyncpg
alembic
pydantic-settings
pyjwt
argon2-cffi
Pillow            # 画像検証・再エンコード
python-multipart  # multipart/form-data の受け取り
```

テスト用は `pytest` / `pytest-asyncio` / `aiosqlite` / `httpx`。

### 🐘 pgAdmin

```bash
# pgAdminにアクセス
http://127.0.0.1:81
# → メール: fastapi@example.com / パスワード: password でログイン
# → 接続先ホストは postgres、ユーザー fastapiuser、DB fleamarket を指定

# DB環境を停止
docker compose down
```

### 🗃️ DB初期化（マイグレーション）

非同期エンジンを使うため、Alembicのテンプレートは **async 版**を指定する。

```bash
# 初回のみ：非同期テンプレートで初期化
alembic init -t async migrations

# 現行モデルから初期マイグレーションを生成
alembic revision --autogenerate -m "initial schema"

# DBへ適用（users / items / alembic_version テーブルが作られる）
alembic upgrade head
```

`migrations/env.py` には以下を設定する。

```python
from config import get_settings
from database import Base
import models  # noqa: F401  ← モデルを読み込ませる（これがないと空のマイグレーションになる）

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

**生成されたマイグレーションの確認ポイント**

- `users` テーブルが `items` より先に作られている（外部キーの依存順）
- `status` 列が `VARCHAR(20)`（`native_enum=False` が効いている証拠。ネイティブENUM型ではない）
- `ix_items_user_id` インデックスが作られている
- FK制約に `ondelete='CASCADE'` が含まれている

> `.env` の `DATABASE_URL` は非同期ドライバ付きで、compose の `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` と一致させる：
> `postgresql+asyncpg://fastapiuser:fastapipass@localhost:5432/fleamarket`
> `POSTGRES_*` 環境変数はデータが空の初回起動時のみ適用されるため、ユーザー/DBを作り直したいときは `docker compose down -v` でボリュームごと削除してから起動する（DB実データは名前付きボリュームにあり、プロジェクトフォルダには存在しない）。
>
> `.env` の例（`SECRET_KEY` は `python -c "import secrets; print(secrets.token_hex(32))"` で生成）：
> ```
> SECRET_KEY=<ランダムな16進文字列>
> DATABASE_URL=postgresql+asyncpg://fastapiuser:fastapipass@localhost:5432/fleamarket
> ECHO_SQL=false
> ACCESS_TOKEN_EXPIRE_MINUTES=20
> ```
> `ECHO_SQL` と `ACCESS_TOKEN_EXPIRE_MINUTES` は省略可（既定 `false` / `20`）。認証情報は `alembic.ini` に直書きせず（`sqlalchemy.url = ` を空にする）、`migrations/env.py` が `get_settings().database_url` から注入する。`.env` は `.gitignore` で追跡対象外にする。

### 🧪 テスト実行

```bash
# テストは非同期（httpx.AsyncClient + aiosqlite インメモリDB）
python -m pytest

# ファイル単位で実行
python -m pytest tests/test_item_image.py -v
```

現在 **46件**（基本CRUD 9 / 所有者チェック・認証 13 / 画像 13 / 認証エンドポイント 11）。

| ファイル | 件数 | 検証範囲 |
|---|---|---|
| `test_item.py` | 9 | 一覧・詳細・検索・作成・更新・削除の基本動作 |
| `test_item_authz.py` | 13 | 他人のアイテムへの操作が404、認証なしが401、閲覧系は認証不要 |
| `test_item_image.py` | 13 | 形式判定・サイズ制限・再エンコード・ファイルの後始末 |
| `test_auth.py` | 11 | signup（201/409/422）・login（200/401）・発行トークンでの出品 |

> `test_auth.py` は Argon2 のハッシュ計算を伴うため、全体の実行時間は4秒程度になる（他は1秒未満）。Argon2は意図的に低速な設計のため、本番と同じパラメータで検証する以上は避けられない。

> **⚠️ 補足**：`main.py` は import 時に `ensure_dirs()` を実行してから `StaticFiles` をマウントするため、`uploads/items/` は自動生成される。ただし `alembic` など `main.py` を経由しないコマンドを先に実行する場合は影響しない。

---

## 🖼 画像アップロード（ローカル保存・最小構成）

アイテムに商品画像を1枚添付できる。**まずはローカルディスク保存**の最小構成で、保存層（`storage.py`）を差し替えれば S3 等へ移行できる設計。

**フロー**

1. 出品時（`POST /items`）に画像を同時送信、または後から `POST /items/{item_id}/image` で追加・差し替え。いずれも `multipart/form-data`。
2. バックエンドは所有者を確認し、**Pillowで再エンコードして** `uploads/items/<item_id>_<uuid>.<ext>` に保存、`items.image_url` を更新。
3. `app.mount("/images", StaticFiles(...))` により `GET /images/items/...` で配信。

**仕様・制約**

- **形式判定**: `content_type` ヘッダやファイル名の拡張子に依存せず、実データを **Pillow で開いて `format` を判定**する。`evil.php` という名前のPNGは `.png` として保存される。
- **再エンコード**: 受け取ったバイト列をそのまま書かず、Pillowで開き直して保存する。これにより
  - 画像末尾に付加されたスクリプト等のデータ（polyglotファイル）が除去される
  - **EXIF（GPS座標・端末情報など）が除去される**
  - アニメーションGIFは1コマ目のみになる
- **サイズ制限**: 5MB。`file.size` で読み込み前に判定し、読み込み後にも再確認する（大容量ファイルをメモリに載せる前に弾く）。
- **エラー**: 空は `400`、対応外形式・画像として開けないものは `415`、5MB超は `413`。
- **認可**: 所有者（`user_id` 一致）のアイテムのみ許可（他人のアイテムは `404`）。
- **後始末**:
  - 再アップロード時は commit 後に旧ファイルを削除
  - commit 失敗時は新規保存したファイルを削除（孤児ファイルを残さない）
  - **アイテム削除時も画像ファイルを削除する**（`delete_item` が削除前の `image_url` を返し、router が commit 後に削除）
- **配信**: `X-Content-Type-Options: nosniff` を全レスポンスに付与し、ブラウザによるMIME推測を抑止する。

> **未対応**：ユーザー削除APIは未実装。実装する場合、CASCADEで消えるアイテムの画像ファイルを別途削除する必要がある。

---

## 🔐 セキュリティ設計のまとめ

| 対策 | 実装箇所 |
|---|---|
| パスワードはArgon2id（salt・パラメータ埋め込み） | `security.py` |
| ハッシュ照合の例外を漏らさない（不一致・破損の両方を `False`） | `security.py` |
| ユーザー名の存在をタイミングで推測させない（ダミーハッシュ照合） | `cruds/auth.py` |
| ログイン失敗メッセージを一本化（存在の有無を区別しない） | `routers/auth.py` |
| JWTの `algorithms` 明示（alg=none攻撃の防止） | `cruds/auth.py` |
| JWTに `exp` / `sub` を必須化 | `cruds/auth.py` |
| 秘密鍵を `SecretStr` で保持（ログ・reprに出さない） | `config.py` |
| LIKE検索の `%` `_` `\` エスケープ | `cruds/item.py` |
| 所有者チェックをSQLのWHERE句に埋め込み | `cruds/item.py` |
| 他人のリソースは403ではなく404（存在を漏らさない） | `routers/item.py` |
| 画像の実データ検証・再エンコード | `storage.py` |
| `X-Content-Type-Options: nosniff` | `main.py` |

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

`BaseSettings` を継承した `Settings` クラスで環境変数を管理する。

| 項目 | 型 | 既定値 |
|---|---|---|
| `secret_key` | `SecretStr` | **必須** |
| `database_url` | `str` | **必須** |
| `echo_sql` | `bool` | `False` |
| `access_token_expire_minutes` | `int` | `20` |
| `cors_origins` | `list[str]` | `http://127.0.0.1:5500` / `http://localhost:5500` |

`model_config = SettingsConfigDict(env_file=".env", extra="ignore")` で `.env` を読み込む。`extra="ignore"` により、`.env` に `Settings` で未定義のキー（docker-compose用の変数など）があってもバリデーションエラーにならない。

環境変数名は大文字小文字を区別しないため、`.env` の `SECRET_KEY` が `secret_key` に対応する。値の優先順位は **環境変数 > `.env`** で、本番ではコンテナの環境変数で上書きできる。

`get_settings()` に `@cache` を付与し、アプリ全体で同一インスタンスを共有する。

---

<a id="enumspy"></a>
### 🏷️ [enums.py](enums.py)　―　共通Enum定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `enum.StrEnum` | 文字列ベースの列挙型（Python 3.11+） |

**📝 処理概要**

アプリ全体で共有する列挙型を定義する最下層モジュール（他のどのモジュールにも依存しない）。`ItemStatusEnum(StrEnum)` に `ON_SALE` / `SOLD_OUT` を定義する。`schemas.py`（Pydantic層）と `models.py`（ORM層）の双方がここを参照することで、両者の間に直接の依存を作らず、循環importを避ける。

`StrEnum`（3.11で追加）は `str` のサブクラスであり、`(str, Enum)` の多重継承と異なり f-string や `str()` の結果が**値そのもの**になる。JSONシリアライズもそのまま通るため、APIレスポンスで `"ON_SALE"` として出力される。

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

非同期対応の `engine` / `async_session` / `Base` を生成・公開する。`engine` は `create_async_engine(settings.database_url, echo=settings.echo_sql)` で生成する（SQLログ出力は `.env` の `ECHO_SQL` で切り替え）。

`async_session` は `async_sessionmaker` で生成する。**`expire_on_commit=False` は非同期では実質必須**で、これがないと commit 後のオブジェクト属性アクセスで `MissingGreenlet` が発生する。

`Base` は SQLAlchemy 2.0スタイルの `DeclarativeBase` を継承して定義する（`declarative_base()` は旧スタイル）。

`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに独立した非同期DBセッションを払い出し、`async with` により終了後に確実にクローズする。戻り値型は `AsyncGenerator[AsyncSession, None]`。

データベースURLには非同期ドライバ（PostgreSQLの場合 `postgresql+asyncpg`）を使用する。

> **トランザクション方針**：`commit` はエンドポイント側（`routers/`）に集約し、各CRUD（`cruds/`）は `commit` せず `flush` に留める。これにより「1リクエスト＝1トランザクション」を担保し、画像保存など後続処理が失敗した際にDB操作ごとロールバックできる。

---

<a id="modelspy"></a>
### 🧱 [models.py](models.py)　―　SQLAlchemy ORMモデル定義（Item・User）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 前方参照（`Mapped[User]` 等）をクォートなしで記述 |
| `datetime.UTC`, `datetime` | タイムスタンプのデフォルト値生成（UTC） |
| `sqlalchemy.DateTime`, `String`, `ForeignKey` | カラム型・外部キー定義 |
| `sqlalchemy.Enum as SAEnum` | `status` を文字列カラムとして定義 |
| `sqlalchemy.orm.Mapped` | カラム・リレーションの型アノテーション |
| `sqlalchemy.orm.mapped_column` | 型付きカラム定義（SQLAlchemy 2.0スタイル） |
| `sqlalchemy.orm.relationship` | テーブル間リレーション定義 |
| `database.Base` | ORMモデルの基底クラス |
| `enums.ItemStatusEnum` | `status` カラムの型 |

**📝 処理概要**

`items` / `users` テーブルに対応するORMモデルを定義する。SQLAlchemy 2.0スタイルの `Mapped` + `mapped_column` を使用し、`price: Mapped[int]` のように推論可能なカラムは `mapped_column()` を省略する。型アノテーションからNULL可否が決まる（`Mapped[str]` は `NOT NULL`、`Mapped[str | None]` は NULL可）ため、`nullable=` の明示は不要。

`TimestampMixin` で `created_at` / `updated_at`（いずれも `DateTime(timezone=True)`・デフォルトは `datetime.now(UTC)`、更新時は `onupdate`）を共通化する。値はPython側で決まるため、`flush` の時点でオブジェクトに反映される。

**Item モデル**

| カラム | 定義 |
|---|---|
| `id` | 主キー |
| `name` | `String(50)` |
| `price` | `int` |
| `description` | `String(255)`・nullable |
| `image_url` | `String(255)`・nullable（商品画像の公開URL） |
| `status` | `SAEnum(ItemStatusEnum, native_enum=False, length=20)`・既定 `ON_SALE` |
| `user_id` | `ForeignKey("users.id", ondelete="CASCADE")`・`index=True` |

- `status` は **`native_enum=False`** により PostgreSQL のネイティブENUM型ではなく `VARCHAR(20)` として作られる。ネイティブENUMだと選択肢追加時にAlembicが差分を検出できず、手書きの `ALTER TYPE` が必要になるため。なおSQLAlchemyはEnumの `.value` ではなく **`.name`** を保存する（本プロジェクトは両者が同一）。
- `user_id` に **`index=True`** を付与。PostgreSQLは外部キー列に自動でインデックスを作らないため、「あるユーザーの商品一覧」の検索が全件走査になるのを防ぐ。
- `user: Mapped[User]` で多対1の逆参照を構成。**`lazy="raise_on_sql"`** を指定し、未ロードのリレーションにアクセスした際に分かりやすい例外を出す（非同期では暗黙の遅延ロードができず、放置すると `MissingGreenlet` やN+1問題として遠回りに表面化するため）。

**User モデル**

| カラム | 定義 |
|---|---|
| `id` | 主キー |
| `username` | `String(50)`・`unique=True`（一意制約により索引も作られる） |
| `password_hash` | `String(255)` |

- **パスワードは Argon2 ハッシュ文字列に salt が埋め込まれるため、独立した `salt` カラムは持たない**（Argon2idのハッシュは97文字程度）。
- `items: Mapped[list[Item]]` で1対多を構成。**`cascade="all, delete-orphan"` + `passive_deletes=True`** を指定し、ユーザー削除時の子レコード削除をDBの `ON DELETE CASCADE` に委ねる。これがないとSQLAlchemyが子を全件読み込んで `user_id = NULL` にしようとし、NOT NULL違反になる。

---

<a id="schemaspy"></a>
### 📐 [schemas.py](schemas.py)　―　Pydanticスキーマ・型エイリアス定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `datetime.datetime` | レスポンスの日時フィールド型 |
| `typing.Annotated` | 型エイリアス（`ItemName`・`ItemPrice` 等）への制約付与 |
| `fastapi.Form`, `HTTPException` | フォーム受け取り・バリデーションエラー応答 |
| `pydantic.BaseModel` | スキーマ基底クラス |
| `pydantic.Field` | バリデーション制約・サンプル値の付与 |
| `pydantic.ConfigDict` | ORM連携・空白トリム設定 |
| `pydantic.ValidationError` | フォーム変換失敗時の捕捉 |
| `enums.ItemStatusEnum` | ステータス型エイリアスの元となる列挙型 |

**📝 処理概要**

アプリ全体のPydanticスキーマを一元管理する。`Annotated` による型エイリアス（`ItemName`, `ItemPrice`, `ItemOptionalName` 等）で `Field` の制約とサンプル値を共通化し、各スキーマで再利用する。制約の変更が1箇所で済み、`ItemCreate` と `ItemUpdate` で二重管理にならない。

`StrippedBaseModel`（`ConfigDict(str_strip_whitespace=True)`）を**入力スキーマの**共通基底とし、前後空白を自動除去する。

> **設計方針：制約は入力側にのみ置く**
> レスポンススキーマ（`ItemResponse` / `UserResponse`）は `BaseModel` を直接継承し、`min_length` 等の制約を持たない。出力はDBから取り出した値であり検証しても意味がなく、万一制約を外れたデータがあるとレスポンス生成時に **500エラー**になるため。`str_strip_whitespace` も出力には不要。

`item_create_form()` はフォーム（`multipart/form-data`）の各値を受け取り `ItemCreate` へ変換する依存関数。`ValidationError` を捕捉して `HTTPException(422)` に変換する。

> `Annotated[ItemCreate, Form()]`（FastAPI 0.113+）でモデルを直接フォーム引数にする方法もあるが、同一エンドポイントに `UploadFile` を別引数として並べるとボディが埋め込みモードになりフォームがフラットに受け取れない。ファイルをモデル内に含める構成に変える必要があるため、本プロジェクトでは依存関数方式を採用している。

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `StrippedBaseModel` | 入力スキーマ共通の基底（`str_strip_whitespace=True`） |
| `ItemBase` | アイテム共通フィールド（`name` / `price` / `description`）の基底 |
| `ItemCreate` | アイテム作成リクエスト（`ItemBase` を継承） |
| `ItemUpdate` | アイテム更新リクエスト（全フィールド省略可・`status` を含む） |
| `ItemResponse` | アイテムレスポンス（`from_attributes=True`・制約なし） |
| `UserCreate` | ユーザー作成リクエスト（`username` / `password`） |
| `UserResponse` | ユーザーレスポンス（`password_hash` を含まない・`from_attributes=True`） |
| `Token` | JWTトークンレスポンス |
| `DecodedToken` | JWTデコード結果（`username` / `user_id`） |

---

<a id="securitypy"></a>
### 🔒 [security.py](security.py)　―　パスワードのハッシュ化・検証（Argon2）

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `argon2.PasswordHasher` | Argon2 によるハッシュ生成・検証 |
| `argon2.exceptions.VerificationError` | パスワード不一致（`VerifyMismatchError` を含む） |
| `argon2.exceptions.InvalidHashError` | ハッシュ文字列が不正・破損している場合 |

**📝 処理概要**

パスワードのハッシュ化と検証を担う独立モジュール。`argon2-cffi` の `PasswordHasher` をモジュールレベルで1つ生成（`_ph`）し、使い回す。引数なしの既定で **argon2id**（RFC 9106の推奨バリアント）と推奨パラメータが適用されるため、明示指定はしない（ライブラリ更新時に自動追随できる）。

| 関数 | 処理 |
|---|---|
| `hash_password` | 平文パスワードを Argon2 でハッシュ化して返す。返り値（`$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>`）に salt・パラメータが埋め込まれる。**同じパスワードでも毎回異なる値**になる（saltがランダム生成されるため） |
| `verify_password` | 平文パスワードと保存済みハッシュを照合し `bool` を返す |

`argon2` の `verify()` は不一致時に `False` を返すのではなく**例外を投げる**設計のため、`verify_password` はこれを `bool` に包み直す。捕捉する例外は2種類必要で、両者は継承関係にない。

| 例外 | 発生条件 | 継承 |
|---|---|---|
| `VerificationError` | パスワード不一致 | `Argon2Error` |
| `InvalidHashError` | ハッシュが空・不正形式・破損 | `ValueError` |

`InvalidHashError` を捕捉しないと、DBに壊れた `password_hash` が混入した場合にログイン失敗（401）ではなく **500エラー**になる。

> **引数順に注意**：`argon2` の `_ph.verify(hash, password)` はハッシュが第1引数。自作の `verify_password(password, password_hash)` とは順序が逆。

---

<a id="storagepy"></a>
### 🗂️ [storage.py](storage.py)　―　画像のローカル保存層

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 型アノテーションの遅延評価 |
| `io` | バイト列を `Pillow` に渡すためのバッファ |
| `logging` | 削除失敗時の警告出力 |
| `uuid` | 保存ファイル名の一意化 |
| `pathlib.Path` | 保存パスの組み立て・ファイル操作 |
| `fastapi.UploadFile`, `HTTPException`, `status` | アップロード受け取り・検証エラー応答 |
| `PIL.Image` | 画像データの読み込み・形式判定・検証・再エンコード |

**📝 処理概要**

アイテム画像をローカル（`uploads/items/`）に保存し、公開URL（`/images/items/<item_id>_<uuid>.<ext>`）を返す層。`routers` / `cruds` は文字列の `image_url` だけを扱うため、将来 S3（presigned URL）へ移行する場合はこの層のみ差し替えればよい。

保存先パス（`uploads/`）と公開URL（`/images/`）を分けており、ディレクトリ構造をそのままURLに晒さない。

| 関数 | 処理 |
|---|---|
| `ensure_dirs` | 保存先 `uploads/items/` を作成（`main.py` が import 時に呼ぶ） |
| `save_item_image` | 検証してから再エンコード保存し、公開URLを返す |
| `delete_item_image` | 公開URLに対応するローカルファイルを削除（`None` を渡しても安全） |

**`save_item_image` の処理順**

1. `file.size` が5MB超なら `413`（読み込み前に弾き、大容量ファイルをメモリに載せない）
2. 読み込み後、空なら `400`、5MB超なら `413`（`file.size` が `None` の場合の最終防衛）
3. `Image.open()` + `verify()` で形式判定。開けなければ `415`。巨大画像を宣言する圧縮爆弾は Pillow の `DecompressionBombError` で弾かれる
4. `ALLOWED_FORMATS`（JPEG/PNG/WEBP/GIF）以外なら `415`
5. `<item_id>_<uuid>.<ext>` の名前で **`Image.open()` → `save()` により再エンコード**して保存。元のファイル名は一切使わない（パストラバーサル対策）
6. 保存に失敗したら書きかけのファイルを削除して `415`

**ファイル名の生成**

```
uploads/items/1_56d4a2993aba4272a3a904b1812149f6.png
              ^item_id ^uuid4.hex               ^検出した形式に対応する拡張子
```

ユーザー由来の文字列を含まないため、`../../etc/passwd` のようなファイル名を送られても影響しない。

**`delete_item_image` のパス組み立て**

`ITEMS_DIR / Path(image_url).name` としてディレクトリ部分を捨てるため、`/images/items/../../secret` のような値が来ても `uploads/items/` の外には出ない。削除失敗（権限エラー等）は `logger.warning` に記録し、例外は投げない（画像が残ってもAPI処理自体は成功しているため）。

---

<a id="crudsauthpy"></a>
### 🔐 [cruds/auth.py](cruds/auth.py)　―　認証・ユーザーのDB操作・JWT生成

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `datetime.UTC`, `datetime`, `timedelta` | JWT有効期限の計算 |
| `typing.Annotated` | DI（`Depends`）の型付与 |
| `jwt`（PyJWT）, `jwt.exceptions.InvalidTokenError` | JWTエンコード・デコード |
| `fastapi.Depends`, `HTTPException`, `status` | DI・認証/重複エラー応答 |
| `fastapi.security.OAuth2PasswordBearer` | OAuth2トークン取得スキーム |
| `pydantic.ValidationError` | デコード結果の検証失敗捕捉 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `sqlalchemy.exc.IntegrityError` | username重複時の例外捕捉 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `config.get_settings` | `secret_key` の取得 |
| `models.User` | usersテーブルのORMモデル |
| `schemas.UserCreate`, `DecodedToken` | 入力・出力スキーマ |
| `security.hash_password`, `verify_password` | パスワードのハッシュ化・検証（Argon2） |

**📝 処理概要**

認証・ユーザー管理に関するDB操作と認証ロジックを提供する。パスワードのハッシュ化・検証は `security.py`（Argon2）に委譲し、このモジュール自身はハッシュアルゴリズムを持たない。

JWTの署名鍵は `get_settings().secret_key.get_secret_value()` で `SecretStr` から文字列を取り出して保持する（`SecretStr` のまま `jwt.encode`/`decode` に渡すと `TypeError` になるため）。

| 関数 | 種別 | 処理 |
|---|---|---|
| `create_user` | `async def` | `hash_password()` でハッシュ化して `User` を作成し `flush`。username重複（`IntegrityError`）は `rollback` のうえ **`409 Conflict`** に変換 |
| `authenticate_user` | `async def` | `select(User)` で取得し `verify_password()` で検証。**ユーザー不在時もダミーハッシュとの照合を実行**して応答時間を揃える |
| `create_access_token` | `def` | JWTトークンを生成（DB不使用・`HS256`・`sub` / `id` / `exp`） |
| `get_current_user` | `def` | JWTをデコードして `DecodedToken` を返す（DB不使用） |

**タイミング攻撃対策**

Argon2は意図的に低速なため、ユーザーが見つからず即座に返すと応答時間に桁違いの差が生じ、**ユーザー名の存在が推測できてしまう**。モジュールレベルで生成した `_DUMMY_HASH` と照合することで、不在時も同等の処理時間になる。

```
（対策前）存在するユーザー名+誤パスワード: 約172ms / 存在しないユーザー名: 約0ms
（対策後）約202ms / 約205ms
```

**JWTデコードの設定**

```python
jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub"]})
```

- `algorithms=[...]` の明示により、ヘッダで `alg: none` を宣言した署名なしトークンが `InvalidAlgorithmError` で拒否される
- `require` により `exp` / `sub` を持たないトークンを `MissingRequiredClaimError` で拒否する

いずれも `InvalidTokenError` のサブクラスなので、`ExpiredSignatureError`（期限切れ）・`InvalidSignatureError`（鍵不一致）とまとめて `401` に変換される。

> **既知の割り切り**：`get_current_user` はDBを参照しないため、ユーザー削除後もトークンの有効期限までリクエストが通る。DB照会を足すと全リクエストにSELECTが増えるトレードオフがあり、有効期限を短く保つ方針としている。

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

`items` テーブルに対する非同期DB操作関数を提供する。全関数は `async def` で定義し、レガシーな `session.query()` ではなく `select()` + `scalars()` を使う。コミットは `routers` 側に集約し、各関数は `await db.flush()` に留める。

| 関数 | 処理 |
|---|---|
| `get_items` | 全アイテムを `id` 降順で取得 |
| `get_items_by_name` | `name` の部分一致（`ILIKE`）で検索し `id` 降順で返す |
| `get_item` | `id` と `user_id` で絞り込んで1件取得（**所有者チェック用**） |
| `get_item_public` | `id` のみで1件取得（**公開参照用**） |
| `create_item` | 新規アイテムを作成・`flush` / `refresh` |
| `update_item` | `get_item` で取得後 `exclude_unset=True` のフィールドのみ更新・`flush` / `refresh` |
| `delete_item` | `get_item` で取得後削除・`flush`。**`(成功可否, 削除前のimage_url)` のタプルを返す** |
| `set_item_image` | `image_url` を設定し `flush` / `refresh`（画像アップロード用） |

**LIKE検索のエスケープ**

```python
escaped = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
select(Item).where(Item.name.ilike(f"%{escaped}%", escape="\\"))
```

`%` と `_` はLIKEのワイルドカードのため、エスケープしないと「`%` で検索すると全件ヒット」する。バックスラッシュを最初に置換する順序が重要（逆だと二重エスケープになる）。

**`order_by` の必要性**

`ORDER BY` を指定しないとDBが返す行順序は保証されず、更新・削除のたびに一覧の並びが変わりうる。`Item.id.desc()`（新しい出品が先頭）を明示する。

**`delete_item` がタプルを返す理由**

削除後は `item.image_url` を読めないため、削除前に取り出して呼び出し側へ渡す。router はこれを使い、commit 成功後に画像ファイルを削除する。

> `refresh()` は現行モデル（全てPython側の `default` / `onupdate`）では必須ではないが、将来 `server_default` へ移行した際にそのまま動くよう残している。

---

<a id="routersauthpy"></a>
### 🔑 [routers/auth.py](routers/auth.py)　―　/auth エンドポイント定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `datetime.timedelta` | JWT有効期限の指定 |
| `typing.Annotated` | DIの型付与 |
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends`, `HTTPException`, `status` | DI・認証エラー応答 |
| `fastapi.security.OAuth2PasswordRequestForm` | ログインフォームデータ取得 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `config.get_settings` | トークン有効期限の取得 |
| `cruds.auth` | 認証・ユーザーのDB操作関数 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `schemas.Token`, `UserCreate`, `UserResponse` | リクエスト・レスポンスのスキーマ |

**📝 処理概要**

`/auth` プレフィックスの認証エンドポイントを定義する。コミットはこのルーター層で行う（`await db.commit()`）。

| エンドポイント | メソッド | 処理 |
|---|---|---|
| `/auth/signup` | POST | ユーザーを作成し、**そのままログイン済みにするトークンを返す**（成功時 `201`） |
| `/auth/login` | POST | `OAuth2PasswordRequestForm` で受け取り認証、JWTを返す（失敗時 `401`） |

**signup がトークンを返す理由**

登録直後にクライアントが `/auth/login` を呼び直す必要をなくすため。`response_model` は `UserResponse` ではなく `Token` で、login と同じ形のレスポンスになる。

```python
def _issue_token(user: User) -> Token:
    token = auth_cruds.create_access_token(
        user.username,
        user.id,
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=token, token_type="bearer")
```

トークン発行を `_issue_token()` に切り出し、signup / login の双方から呼ぶ。有効期限の指定漏れや `token_type` の書き間違いが1箇所に集約される。

副次的に、従来は登録時のハッシュ化（Argon2）とログイン時の照合（Argon2）で2回かかっていた計算が1回で済み、**登録の体感時間がおよそ半分**になる。

ユーザー名・IDはJWTのペイロード（`sub` / `id`）に含まれるため、クライアントはトークンをデコードすれば表示に必要な情報を得られる。`UserResponse` はこのエンドポイントでは使わなくなるが、将来 `GET /auth/me` などを追加する際に必要なので `schemas.py` には残している。

**その他**

- username重複の `409` 変換は `cruds/auth.py` 側で行うため、router に `except IntegrityError` は置かない。
- トークン有効期限は `settings.access_token_expire_minutes`（既定20分）から取得し、`.env` で変更できる。
- レスポンスは辞書リテラルではなく `Token(...)` を返す（キー名の誤りを型チェッカーが検出できる）。
- ログイン失敗のメッセージは `"Incorrect username or password"` に一本化し、ユーザー名の存在有無を区別しない。

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
| `schemas.ItemCreate`, `ItemUpdate`, `ItemResponse`, `DecodedToken`, `item_create_form` | スキーマ・フォーム変換 |
| `storage.save_item_image`, `delete_item_image` | 画像の保存・削除 |

**📝 処理概要**

`/items` プレフィックスのエンドポイントを定義する。`UserDependency`（`Depends(auth_cruds.get_current_user)`）を付けたエンドポイントのみ認証を要求する。

**認可方針：閲覧は誰でも、変更は本人のみ**

| エンドポイント | メソッド | 認証 | 所有者チェック | 処理 |
|---|---|---|---|---|
| `/items` | GET | 不要 | — | 全アイテム一覧（`id` 降順）。`?name=` （1〜20文字）で部分一致検索 |
| `/items/{item_id}` | GET | 不要 | — | IDで1件取得（`get_item_public`・該当なしは `404`） |
| `/items` | POST | 必要 | — | アイテム作成（`multipart/form-data`・`201`・`user_id` はトークンから付与・画像同時アップロード可） |
| `/items/{item_id}` | PATCH | 必要 | あり | 部分更新（`exclude_unset` により送信されたフィールドのみ反映） |
| `/items/{item_id}` | DELETE | 必要 | あり | 削除（`204 No Content`・画像ファイルも削除） |
| `/items/{item_id}/image` | POST | 必要 | あり | 画像アップロード・差し替え（旧ファイルは削除） |

- 404のメッセージは全て **`"Item not found"`** に統一。
- 他人のリソースへの操作も `403` ではなく `404` を返す。`403` だと「そのIDの商品は存在するが自分のものではない」と伝わり、他人の出品IDを推測する手がかりになるため。
- 名前検索は独立エンドポイントではなく `GET /items` の `name` クエリパラメータで処理する（ハンドラ内で `get_items` / `get_items_by_name` を切り替え）。

**画像とDBの整合性**

作成・画像アップロード・削除のいずれも、DBのコミットとファイル操作の順序を制御して孤児ファイルや参照切れを防ぐ。

| 処理 | 順序 |
|---|---|
| 作成（画像あり） | 画像保存 → `commit` → 失敗時は保存した画像を削除 |
| 画像差し替え | 新画像保存 → `commit`（失敗時は新画像を削除）→ 成功後に旧画像を削除 |
| 削除 | 削除前の `image_url` を受け取る → `commit` → 成功後に画像を削除 |

いずれも「commit成功後に旧ファイルを消す」「commit失敗時は新ファイルを消す」という方針で統一している。逆順にすると、失敗時に「DBは参照しているのに実体がない」という復旧困難な状態になる。

---

<a id="mainpy"></a>
### 🚪 [main.py](main.py)　―　エントリーポイント・CORS・ミドルウェア設定

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `time` | 処理時間計測（`X-Process-Time`） |
| `fastapi.FastAPI`, `Request` | アプリ生成・ミドルウェアのリクエスト処理 |
| `fastapi.middleware.cors.CORSMiddleware` | CORS設定 |
| `fastapi.staticfiles.StaticFiles` | アップロード画像の静的配信 |
| `config.get_settings` | CORS許可オリジン等の取得 |
| `routers.auth`, `routers.item` | ルーター登録 |
| `storage.UPLOAD_ROOT`, `ensure_dirs` | 保存先ディレクトリの用意・配信元 |

**📝 処理概要**

アプリケーションのエントリーポイント。

**`ensure_dirs()` はモジュールレベルで実行する**（`lifespan` ではない）。`StaticFiles(directory=...)` は**インスタンス生成時**にディレクトリの存在を確認するため、`lifespan` に置くと実行が間に合わず、`uploads/` が無い環境（Gitからクローンした直後など。空ディレクトリはGit管理されない）で以下のエラーが出て起動できない。

```
RuntimeError: Directory 'uploads' does not exist
```

`CORSMiddleware` で `settings.cors_origins` からのアクセスを許可する。`allow_credentials=True` と併用するため、オリジンはワイルドカードではなく具体的に列挙する（ブラウザ仕様上、`*` との併用ではCookieが送られない）。

`@app.middleware("http")` の `add_process_time_header` は各レスポンスに以下を付与する。

| ヘッダ | 内容 |
|---|---|
| `X-Process-Time` | 処理時間（`time.perf_counter()` で計測・小数第4位まで） |
| `X-Content-Type-Options` | `nosniff`（ブラウザのMIME推測を抑止） |

`time.time()` ではなく `perf_counter()` を使うのは、システム時刻の補正（NTP等）で経過時間が負になるのを避けるため。

`app.mount("/images", StaticFiles(directory=str(UPLOAD_ROOT)), name="images")` でアップロード画像を静的配信し、`item` / `auth` の各ルーターを登録する。

> **本番向けメモ**：`X-Process-Time` は応答時間から内部処理を推測される可能性があるため、本番では外すことが多い。`config.py` に `debug` フラグを足して切り替える構成も検討できる。

---

<a id="testsconftestpy"></a>
### 🧪 [tests/conftest.py](tests/conftest.py)　―　非同期pytestフィクスチャ・DIオーバーライド定義

**📥 インポート**

| モジュール | 用途 |
|---|---|
| `os`, `sys` | アプリのルートを `sys.path` に追加 |
| `pytest` | 同期フィクスチャ（`image_dir`）の定義 |
| `pytest_asyncio` | 非同期フィクスチャ定義（`@pytest_asyncio.fixture`） |
| `httpx.ASGITransport`, `AsyncClient` | ASGIアプリを直接叩く非同期テストクライアント |
| `sqlalchemy.ext.asyncio.create_async_engine`, `async_sessionmaker` | テスト用インメモリ非同期SQLiteエンジン・セッション |
| `sqlalchemy.pool.StaticPool` | 単一接続を使い回すテスト用プール（インメモリDB共有） |
| `storage` | 画像保存先（`ITEMS_DIR`）の差し替え対象 |
| `database.Base`, `get_db` | テーブル定義メタデータ・DIオーバーライド対象 |
| `models.Item` | テーブル登録・テストデータ投入 |
| `schemas.DecodedToken` | 認証オーバーライドの戻り値 |
| `main.app` | テスト対象アプリ |
| `cruds.auth.get_current_user` | 認証DIオーバーライド対象 |

**📝 処理概要**

アプリ本体が完全に非同期（`async def` のCRUD・`AsyncSession`）であるため、テストも**非同期**で実装する。同期の `TestClient` ではなく `httpx.AsyncClient` + `ASGITransport` でアプリを直接叩き、DBには `aiosqlite` によるインメモリ非同期SQLiteを注入する。

| フィクスチャ | 処理 |
|---|---|
| `session_fixture` | `create_async_engine("sqlite+aiosqlite://")` でインメモリDBを作り、`Base.metadata.create_all` でテーブル作成、テストデータ（`PC1`（user_id=1）/ `PC2`（user_id=2）の Item×2件）を投入して `yield`。終了後 `await engine.dispose()` |
| `client_fixture` | `get_current_user` を `DecodedToken(username="user1", user_id=1)` にオーバーライド。**PC1 の所有者** |
| `other_client_fixture` | `get_current_user` を `user_id=2` にオーバーライド。**PC1 の所有者ではない**（所有者チェックの検証用） |
| `unauth_client_fixture` | `get_current_user` を**オーバーライドしない**。401 の検証と、signup / login で発行された実トークンを使う検証に用いる |
| `image_dir` | `monkeypatch` で `storage.ITEMS_DIR` を `tmp_path` に差し替える |

クライアント系フィクスチャはいずれも `get_db` を `session_fixture` にオーバーライドし、終了時に `app.dependency_overrides.clear()` する。1つのテストで複数のクライアントフィクスチャを併用しないこと（オーバーライドが競合するため）。

`StaticPool` によりインメモリDBの単一接続が全操作で共有されるため、シード投入とリクエスト処理が同じDB状態を参照する。

**`image_dir` の役割**

```python
monkeypatch.setattr(storage, "ITEMS_DIR", items_dir)
```

`save_item_image` / `delete_item_image` は呼び出し時にモジュールグローバルの `ITEMS_DIR` を参照するため、この差し替えで保存先が一時ディレクトリに向く。**実際の `uploads/` を汚さず**、テストごとに空の状態から始まるので「ファイルが1件だけ存在すること」といった検証が安全にできる。

> **SQLiteでのテストに関する注意**：SQLiteは既定で外部キー制約を強制しないため、`ON DELETE CASCADE`（ユーザー削除時のアイテム連鎖削除）の挙動は本番のPostgreSQLと異なる。この部分の検証はPostgreSQLで行う必要がある。

---

<a id="testshelperspy"></a>
### 🧰 [tests/helpers.py](tests/helpers.py)　―　テスト用の画像バイト列生成

**📝 処理概要**

画像アップロードのテストで使うバイト列を Pillow で組み立てる。ダミー画像ファイルをリポジトリに置かずに済み、「何を検証したいか」が関数名で分かる。

| 関数 | 生成物 |
|---|---|
| `png_bytes(size)` | 正常なPNG |
| `bmp_bytes()` | 許可されていない形式（`415` の検証用） |
| `jpeg_with_exif_bytes()` | Exif（Makeタグに `MyPhone`）を含むJPEG |
| `polyglot_png_bytes()` | 正常なPNGの末尾に `<script>` を連結したファイル |

`jpeg_with_exif_bytes()` は手組みのTIFFブロックを `Image.save(..., exif=...)` に渡してExifを埋め込む。再エンコードによってExifが消えることを、実際に埋め込んだタグ文字列の有無で判定するため。

---

<a id="teststest_itempy"></a>
### ✅ [tests/test_item.py](tests/test_item.py)　―　items の基本CRUD

全テストは `async def` + `@pytest.mark.asyncio` で定義し、`client_fixture`（`user_id=1`）を受け取る。

| テスト | 検証内容 |
|---|---|
| `test_find_all` | 一覧取得で2件返ること |
| `test_find_by_id_正常系` | `GET /items/1` が `id=1` を返すこと |
| `test_find_by_id_異常系` | `GET /items/10` が `404` かつ `detail == "Item not found"` |
| `test_find_by_name` | `GET /items?name=PC1` で1件（`PC1`）に絞れること |
| `test_create` | `POST /items` にフォームデータで作成し `201`、一覧が3件に増えること |
| `test_update_正常系` | `PATCH /items/1` が `200` かつ内容が反映されること |
| `test_update_異常系` | `PATCH /items/10` が `404` かつ `detail == "Item not found"` |
| `test_delete_正常系` | `DELETE /items/1` が `204` かつ一覧が1件に減ること |
| `test_delete_異常系` | `DELETE /items/10` が `404` かつ `detail == "Item not found"` |

**補足**

- 作成テストは `json=` ではなく `data=`（フォーム）で送る。作成エンドポイントが `item_create_form`（`Form`）経由で受け取るため。
- 更新は `PUT` ではなく `PATCH`、削除の成功は `204 No Content`。
- `GET /items` は末尾スラッシュ無しで定義されているため、`AsyncClient`（リダイレクト非追従）では `/items?name=` と書く。

---

<a id="teststest_item_authzpy"></a>
### 🛡️ [tests/test_item_authz.py](tests/test_item_authz.py)　―　所有者チェック・認証

`other_client_fixture`（`user_id=2`）と `unauth_client_fixture`（未認証）を使い、認可の境界を検証する。

**他人のアイテムへの操作は404**

| テスト | 検証内容 |
|---|---|
| `test_patch_他人のアイテムは404` | `user_id=2` が PC1 を更新すると `404 Item not found` |
| `test_patch_他人のアイテムは変更されない` | 上記のあと PC1 の `price` が元のままであること |
| `test_delete_他人のアイテムは404` | `user_id=2` が PC1 を削除すると `404` |
| `test_delete_他人のアイテムは削除されない` | 上記のあと一覧が2件のままであること |
| `test_image_他人のアイテムは404` | 他人のアイテムへの画像アップロードが `404`、ファイルも作られないこと |
| `test_自分のアイテムは操作できる` | `user_id=2` が PC2 を更新でき `200` |

エラーを返すことだけでなく **実際に変更・削除されていないこと** まで確認する。ステータスコードだけの検証では「404を返しつつ更新は通っている」取りこぼしを検出できないため。最後の1件は、所有者チェックが単に全件404にしているわけではないことの裏付け。

**認証なしアクセスは401**

| テスト | 検証内容 |
|---|---|
| `test_create_認証なしは401` | `POST /items` |
| `test_patch_認証なしは401` | `PATCH /items/1` |
| `test_delete_認証なしは401` | `DELETE /items/1` |
| `test_image_認証なしは401` | `POST /items/1/image` |
| `test_不正なトークンは401` | でたらめな Bearer トークンで `401 Could not validate credentials` |

**閲覧系は認証不要**

| テスト | 検証内容 |
|---|---|
| `test_一覧は認証不要` | 未認証で `GET /items` が `200` |
| `test_詳細は認証不要かつ他人のものも見られる` | 未認証で `GET /items/2`（他人の出品）が `200` |

---

<a id="teststest_item_imagepy"></a>
### 🖼️ [tests/test_item_image.py](tests/test_item_image.py)　―　画像アップロード

`image_dir` フィクスチャで保存先を一時ディレクトリに差し替えたうえで検証する。

**正常系**

| テスト | 検証内容 |
|---|---|
| `test_png_をアップロードできる` | `200`・`image_url` が `/images/items/....png`・実ファイルと名前が一致 |
| `test_ファイル名は元の名前を含まない` | `secret.png` を送ってもファイル名に `secret` が含まれず `1_` で始まること |
| `test_出品と同時に画像を送れる` | `POST /items` に画像を添えて `201`、ファイルが1件作られること |

**形式判定（拡張子・Content-Type を信用しない）**

| テスト | 検証内容 |
|---|---|
| `test_拡張子偽装は実データの形式で保存される` | `evil.php`（中身はPNG）が `.png` として保存される |
| `test_対応外の画像形式は415` | BMPは `415`、ファイルも作られない |
| `test_画像でないファイルは415` | テキストは `415`、ファイルも作られない |

**サイズ制限**

| テスト | 検証内容 |
|---|---|
| `test_空ファイルは400` | 空は `400` |
| `test_5MB超は413` | 5MB+1バイトは `413` |

**再エンコード**

| テスト | 検証内容 |
|---|---|
| `test_末尾に埋め込まれたスクリプトが除去される` | polyglotファイルの `<script>` が保存後のファイルに残らない |
| `test_exifが除去される` | Exif（`MyPhone`）が保存後のファイルに残らない |

いずれも **送信前のバイト列に対象が含まれていることを先に assert** してから、保存後に消えていることを確認する。生成側の不備でテストが「たまたま通る」状態を避けるため。

**ファイルの後始末**

| テスト | 検証内容 |
|---|---|
| `test_差し替え時に旧ファイルが削除される` | 2回アップロードすると旧ファイルが消え、新ファイルだけ残る |
| `test_アイテム削除で画像ファイルも削除される` | `DELETE /items/1` 後にディレクトリが空になる |
| `test_画像なしのアイテム削除でも例外にならない` | `image_url` が `None` でも `204` |

---

<a id="teststest_authpy"></a>
### 🔑 [tests/test_auth.py](tests/test_auth.py)　―　signup / login

`unauth_client_fixture` を使い、認証をオーバーライドしない実際のフローを検証する。

| テスト | 検証内容 |
|---|---|
| `test_signup_正常系` | `201` で `token_type` が `bearer`・JWTが3パート構成 |
| `test_signup_パスワードを返さない` | レスポンスに `password` / `password_hash` が含まれないこと |
| `test_signup_のトークンでそのまま出品できる` | **ログインし直さずに** 認証つきリクエストが通ること |
| `test_signup_重複は409` | 同じ `username` の2回目が `409 Conflict` |
| `test_signup_短いパスワードは422` | 8文字未満は `422` |
| `test_signup_短いユーザー名は422` | 2文字未満は `422` |
| `test_login_正常系` | `200`・`token_type` が `bearer`・JWTが3パート構成 |
| `test_login_パスワード誤りは401` | `401 Incorrect username or password` |
| `test_login_存在しないユーザーは401` | `401` |
| `test_login_失敗メッセージはユーザーの有無で変わらない` | パスワード誤りとユーザー不在で、ステータスと**レスポンスボディが完全一致**すること |
| `test_発行したトークンで出品できる` | signup → login → `Authorization: Bearer` 付きで `POST /items` が `201` |

`test_signup_のトークンでそのまま出品できる` と `test_発行したトークンで出品できる` は、JWTの生成（`create_access_token`）と検証（`get_current_user`）が実際に噛み合っているかを通しで確認するE2E。前者は signup で発行したトークン、後者は login で発行したトークンを使い、**2つの発行経路の両方**を押さえている。ユニットテストでは気づけない設定の食い違い（アルゴリズム・クレーム名の不一致など）を検出できる。

`test_login_失敗メッセージ...` はステータスコードだけでなくボディの一致まで見るため、片方だけ文言を変えてしまう改修を防げる。

---


<a id="pytestini"></a>
### ⚙️ [pytest.ini](pytest.ini)　―　pytest設定

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

`docker compose up -d` 一発で、アプリの接続先となる **PostgreSQL 16** と、その GUI 管理ツール **pgAdmin 4** をまとめて起動する。DB名 `fleamarket`（フリマアプリ）はこのプロジェクトのデータベース。

### 📄 ファイル全体

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    ports:
      - 5432:5432
    volumes:
      - ./docker/postgres/init.d:/docker-entrypoint-initdb.d
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: fastapiuser
      POSTGRES_PASSWORD: fastapipass
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
      POSTGRES_DB: fleamarket
    hostname: postgres
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fastapiuser -d fleamarket"]
      interval: 5s
      timeout: 3s
      retries: 10

  pgadmin:
    image: dpage/pgadmin4
    container_name: pgadmin
    restart: always
    ports:
      - 81:80
    environment:
      PGADMIN_DEFAULT_EMAIL: fastapi@example.com
      PGADMIN_DEFAULT_PASSWORD: password
    volumes:
      - pgadmin:/var/lib/pgadmin
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  pgdata:
  pgadmin:
```

### 🧩 サービス一覧

| サービス | イメージ | 役割 |
|---|---|---|
| `postgres` | `postgres:16-alpine` | アプリの接続先となるPostgreSQL本体（軽量Alpineベース） |
| `pgadmin` | `dpage/pgadmin4` | ブラウザからDBを操作・確認するWeb管理UI |

### 💾 ボリューム設計

DBの実データ（`pgdata`）と pgAdmin の設定（`pgadmin`）は、**名前付きボリューム**で Docker の管理領域に置く。プロジェクトフォルダ配下へのバインドマウント（`./docker/postgres/pgdata` など）は使わない。

| 用途 | 方式 | 理由 |
|---|---|---|
| `init.d`（初期化SQL置き場） | バインドマウント | 自分で置いたファイルをコンテナに渡すため。DBは書き込まない |
| `pgdata`（DB実データ） | **名前付きボリューム** | 下記の副作用を避けるため |
| `pgadmin`（設定・接続情報） | **名前付きボリューム** | 同上 |

**バインドマウントで起きる問題**

PostgreSQL は数百のファイルを高頻度に書き換える。これがプロジェクトフォルダ内にあると、フォルダを監視している他のツールを巻き込む。

- **エディタのライブリロード**が「ファイルが変わった」と誤検知してページを再読み込みする。ユーザー登録や出品のたびにDBが書き込むため、**登録直後に画面がリロードされてログイン状態が反映されない**、といった一見無関係な不具合として現れる
- **クラウドストレージの同期フォルダ**上だと `fsync` が極端に遅くなる。実測でチェックポイントの同期に12秒かかり、コンテナ起動に67秒を要した（名前付きボリュームでは約7秒）
- 同期処理とDBの書き込みが競合すると**データ破損**の恐れがある
- `.gitignore` への追加を忘れると、DBの内部ファイルが大量にコミットされる

名前付きボリュームにすると実データがWSL2側（Dockerの管理領域）に移るため、これらの影響を受けない。

**データを作り直す場合**

保存場所が変わると既存データは引き継がれない。切り替え時やDBをリセットしたいときは以下を実行する。

```powershell
docker compose down -v          # -v でボリュームも削除
docker compose up -d
alembic upgrade head            # テーブルを作り直す
```

残したいデータがあれば、先にダンプを取る。

```powershell
docker compose exec postgres pg_dump -U fastapiuser fleamarket > backup.sql
```

### 🐘 postgres サービス

| 項目 | 値 | 説明 |
|---|---|---|
| image | `postgres:16-alpine` | PostgreSQL 16（軽量Alpineベース） |
| container_name | `postgres` | コンテナ名を `postgres` に固定 |
| ports | `5432:5432` | ホストの5432番を公開。ローカルのFastAPIから接続可能 |
| volumes | `./docker/postgres/init.d → /docker-entrypoint-initdb.d` | 初回起動時に実行される初期化SQL/スクリプト置き場 |
| volumes | `pgdata → /var/lib/postgresql/data` | DB実データ（名前付きボリューム） |
| environment | `POSTGRES_USER=fastapiuser` | DBユーザー |
| environment | `POSTGRES_PASSWORD=fastapipass` | DBパスワード |
| environment | `POSTGRES_DB=fleamarket` | 初期作成されるDB名 |
| environment | `POSTGRES_INITDB_ARGS=--encoding=UTF-8` | エンコーディングをUTF-8に指定 |
| hostname | `postgres` | コンテナ間通信用ホスト名。pgAdminからの接続先ホストに指定する |
| restart | `always` | クラッシュ・再起動時に自動復帰 |
| healthcheck | `pg_isready` | 接続受付が完了したかを判定（後述） |

> `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` は**データが空の初回起動時のみ**適用される。既存データがある状態でこれらを変えても反映されないため、認証情報を変更したいときは `docker compose down -v` でボリュームごと削除してから起動する。

接続URL（`.env` の `DATABASE_URL`）は非同期ドライバを使い、以下の形式になる：

```
postgresql+asyncpg://fastapiuser:fastapipass@localhost:5432/fleamarket
```

### 🩺 healthcheck

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U fastapiuser -d fleamarket"]
  interval: 5s
  timeout: 3s
  retries: 10
```

`docker compose up -d` はコンテナを起動した時点で完了を返すが、PostgreSQL 本体はその後も初期化処理を続けている。この間に接続すると `ConnectionRefusedError` になり、「設定が悪いのか、まだ起動途中なのか」の切り分けに手間がかかる。

healthcheck を入れると `docker compose ps` の `STATUS` に状態が出る。

| 表示 | 意味 |
|---|---|
| `Up 3 seconds (health: starting)` | 初期化中。まだ接続できない |
| `Up 10 seconds (healthy)` | 接続受付済み。`alembic upgrade head` に進んでよい |

### 🖥️ pgadmin サービス

| 項目 | 値 | 説明 |
|---|---|---|
| image | `dpage/pgadmin4` | pgAdmin 4（Web版DB管理ツール） |
| container_name | `pgadmin` | 自動生成名ではなく `pgadmin` に固定 |
| ports | `81:80` | ブラウザで `http://localhost:81` からアクセス |
| environment | `PGADMIN_DEFAULT_EMAIL=fastapi@example.com` | ログイン用メールアドレス |
| environment | `PGADMIN_DEFAULT_PASSWORD=password` | ログイン用パスワード |
| volumes | `pgadmin → /var/lib/pgadmin` | pgAdminの設定・接続情報（名前付きボリューム） |
| depends_on | `postgres` が `service_healthy` | **DBが接続可能になってから**起動 |

`depends_on` は単に列挙するだけだと起動順序を制御するのみで、接続受付の完了までは待たない。`condition: service_healthy` を指定することで、上記の healthcheck が通るまで pgAdmin の起動を待たせている。

> **補足**：`version:` は Compose V2 では無視され警告が出るため記載しない。`user: root` もバインドマウント時のパーミッション対策として使われることがあるが、名前付きボリュームでは不要なので指定しない。
