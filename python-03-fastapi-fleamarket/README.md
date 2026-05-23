# 🛍️ Fleamarket API

FastAPI + PostgreSQL で構築したフリーマーケット向け REST API です。  
ユーザー認証（JWT）と出品アイテムの CRUD 操作を提供します。

---

## 📁 ディレクトリ構成

```
fleamarket/
├── main.py                      # アプリケーションエントリーポイント
├── config.py                    # 環境変数・設定管理
├── database.py                  # DB接続・セッション管理
├── models.py                    # SQLAlchemy ORMモデル定義
├── schemas.py                   # Pydantic スキーマ定義
├── requirements.txt             # 依存パッケージ一覧
├── .env                         # 環境変数ファイル（要秘匿）
├── .gitignore                   # Git除外設定
├── alembic.ini                  # Alembicマイグレーション設定ファイル
├── docker-compose.yml           # PostgreSQL / pgAdmin コンテナ定義
├── __init__.py                  # ルートパッケージ初期化
├── cruds/
│   ├── __init__.py              # パッケージ初期化
│   ├── auth.py                  # 認証関連のCRUD処理
│   └── item.py                  # アイテム関連のCRUD処理
├── routers/
│   ├── __init__.py              # パッケージ初期化
│   ├── auth.py                  # 認証エンドポイント定義
│   └── item.py                  # アイテムエンドポイント定義
├── migrations/
│   ├── env.py                   # Alembicマイグレーション実行環境
│   ├── script.py.mako           # マイグレーションスクリプトテンプレート
│   └── versions/
│       ├── f3d5adf85e9a_create_items_table.py   # itemsテーブル作成
│       ├── b8ca17099c7d_create_users_table.py   # usersテーブル作成
│       ├── ff676fae4f35_add_salt_column.py      # saltカラム追加
│       └── 5f1777586dbe_add_foreign_key.py      # 外部キー追加
└── tests/
    ├── conftest.py              # pytestフィクスチャ定義
    ├── test_example.py          # サンプルテスト
    └── test_item.py             # アイテムAPIテスト
```

---

## 🔧 各ファイルの説明

---

### [`main.py`](./main.py) — アプリケーションエントリーポイント

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `time` | 標準ライブラリ | リクエスト処理時間の計測に使用 |
| `FastAPI` | `fastapi` | FastAPI アプリケーションインスタンスの生成 |
| `Request` | `fastapi` | ミドルウェア内でHTTPリクエストオブジェクトを受け取る |
| `item` | `routers`（ローカル） | アイテム系エンドポイントを定義したルーターモジュール |
| `auth` | `routers`（ローカル） | 認証系エンドポイントを定義したルーターモジュール |
| `CORSMiddleware` | `fastapi.middleware.cors` | クロスオリジンリソース共有（CORS）の制御 |

#### 処理内容

**FastAPI インスタンスの生成**

```python
app = FastAPI()
```

アプリケーション全体のエントリーポイントとなる FastAPI インスタンスを生成します。

**CORS ミドルウェアの設定**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

フロントエンド（`http://localhost:3000`）からのクロスオリジンリクエストを許可します。`allow_methods=["*"]`・`allow_headers=["*"]` により、すべての HTTP メソッドとリクエストヘッダーを許可しています。

**処理時間計測ミドルウェア**

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

全 HTTP リクエストに対して処理時間（秒）を計測し、レスポンスヘッダー `X-Process-Time` に付与します。パフォーマンス監視や遅延調査に活用できます。

**ルーターの登録**

```python
app.include_router(item.router)
app.include_router(auth.router)
```

アイテム・認証それぞれのルーターをアプリに組み込みます。各ルーターはプレフィックスとタグを持ち、エンドポイントが `/items`・`/auth` 以下に展開されます。

---

### [`config.py`](./config.py) — 環境変数・設定管理

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `BaseSettings` | `pydantic_settings` | `.env` ファイルや OS 環境変数から設定値を自動読み込みする基底クラス |
| `SettingsConfigDict` | `pydantic_settings` | 設定クラスのメタ情報（読み込むファイル名等）を定義する辞書型 |
| `lru_cache` | `functools`（標準ライブラリ） | 関数の戻り値をキャッシュし、同一引数での再実行コストをゼロにするデコレータ |

#### 処理内容

**Settings クラス**

```python
class Settings(BaseSettings):
    secret_key: str
    sqlalchemy_database_url: str
    model_config = SettingsConfigDict(env_file=".env")
```

`BaseSettings` を継承した設定クラスです。`model_config` に `env_file=".env"` を指定することで、プロジェクトルートの `.env` ファイルから以下の値を自動的に読み込みます。Pydantic による型検証も行われ、値が不足している場合は起動時にエラーになります。

| フィールド | 対応する環境変数 | 説明 |
|---|---|---|
| `secret_key` | `SECRET_KEY` | JWT トークンの署名・検証に使用するシークレットキー |
| `sqlalchemy_database_url` | `SQLALCHEMY_DATABASE_URL` | SQLAlchemy が使用する DB 接続 URL |

**get_settings 関数**

```python
@lru_cache()
def get_settings():
    return Settings()
```

`@lru_cache()` により `Settings()` のインスタンス生成はアプリ起動中に一度だけ実行され、以降は同じオブジェクトを返します。`.env` の I/O やバリデーション処理を毎回行わないためのパフォーマンス最適化です。

---

### [`database.py`](./database.py) — DB接続・セッション管理

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `create_engine` | `sqlalchemy` | DB 接続エンジンの生成 |
| `sessionmaker` | `sqlalchemy.orm` | DB セッションのファクトリクラス生成 |
| `declarative_base` | `sqlalchemy.orm` | ORM モデルの宣言的ベースクラス生成 |
| `get_settings` | `config`（ローカル） | DB 接続 URL の取得 |

#### 処理内容

**エンジンの生成**

```python
SQLALCHEMY_DATABASE_URL = get_settings().sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

`config.py` から PostgreSQL 接続 URL を取得し、SQLAlchemy のエンジンを生成します。

**セッションファクトリ**

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

DB セッションのファクトリを生成します。`autocommit=False` によりトランザクションは明示的なコミットが必要、`autoflush=False` により自動フラッシュを無効にしています。

**宣言的ベースクラス**

```python
Base = declarative_base()
```

`models.py` の全 ORM モデルが継承するベースクラスです。`migrations/env.py` から `Base.metadata` を参照することで、Alembic による自動マイグレーション生成が有効になります。

**get_db 関数**

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI の依存性注入（`Depends`）で使用するジェネレーター関数です。リクエストごとにセッションを生成して `yield` し、処理終了後（例外発生時も含む）に `finally` ブロックで必ずセッションをクローズします。

---

### [`models.py`](./models.py) — SQLAlchemy ORMモデル定義

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `datetime` | `datetime`（標準ライブラリ） | `created_at`・`updated_at` カラムのデフォルト値に使用 |
| `Column` | `sqlalchemy` | テーブルカラムの定義 |
| `Integer` | `sqlalchemy` | 整数型カラム（`id`・`price`・`user_id`） |
| `String` | `sqlalchemy` | 文字列型カラム（`name`・`username`・`password`・`salt`・`description`） |
| `Enum` | `sqlalchemy` | 列挙型カラム（`status`）。`schemas.ItemStatus` と連動 |
| `DateTime` | `sqlalchemy` | 日時型カラム（`created_at`・`updated_at`） |
| `ForeignKey` | `sqlalchemy` | 外部キー制約の定義（`items.user_id → users.id`） |
| `relationship` | `sqlalchemy.orm` | モデル間のリレーションシップ（ORM レベルの JOIN 定義） |
| `Base` | `database`（ローカル） | 全モデルが継承する宣言的ベースクラス |
| `ItemStatus` | `schemas`（ローカル） | `Enum` 型カラムに使用するステータス列挙型 |

#### 処理内容

**Item モデル（`items` テーブル）**

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | Integer | PK | アイテムID（自動採番） |
| `name` | String | NOT NULL | アイテム名 |
| `price` | Integer | NOT NULL | 価格 |
| `description` | String | NULL可 | 説明文 |
| `status` | Enum(ItemStatus) | NOT NULL, default=ON_SALE | 出品状態 |
| `created_at` | DateTime | default=now | 作成日時 |
| `updated_at` | DateTime | default=now, onupdate=now | 更新日時 |
| `user_id` | Integer | FK→users.id, NOT NULL, CASCADE | 出品者ユーザーID |

`user = relationship("User", back_populates="items")` により `item.user` で出品者の `User` オブジェクトへアクセスできます。ユーザー削除時は `ondelete="CASCADE"` によりアイテムも連動削除されます。

**User モデル（`users` テーブル）**

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | Integer | PK | ユーザーID（自動採番） |
| `username` | String | NOT NULL, UNIQUE | ユーザー名（重複不可） |
| `password` | String | NOT NULL | PBKDF2ハッシュ済みパスワード |
| `salt` | String | NOT NULL | パスワードハッシュ用ソルト |
| `created_at` | DateTime | default=now | 作成日時 |
| `updated_at` | DateTime | default=now, onupdate=now | 更新日時 |

`items = relationship("Item", back_populates="user")` により `user.items` でそのユーザーの出品アイテム一覧へアクセスできます。

---

### [`schemas.py`](./schemas.py) — Pydantic スキーマ定義

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `datetime` | `datetime`（標準ライブラリ） | `ItemResponse`・`UserResponse` の日時フィールドの型ヒント |
| `Enum` | `enum`（標準ライブラリ） | `ItemStatus` 列挙型の基底クラス |
| `Optional` | `typing`（標準ライブラリ） | 任意フィールドの型ヒント（`Optional[str]` 等） |
| `BaseModel` | `pydantic` | 全スキーマが継承する Pydantic 基底クラス |
| `Field` | `pydantic` | フィールドごとのバリデーションルールと Swagger 例示値の定義 |
| `ConfigDict` | `pydantic` | スキーマのモデル設定（`from_attributes=True` で ORM 変換を有効化） |

#### 処理内容

**ItemStatus** — 出品状態の列挙型

```python
class ItemStatus(Enum):
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"
```

アイテムの出品状態を表す列挙型です。`models.py` の `Enum(ItemStatus)` カラムと連動します。

**ItemCreate** — アイテム出品リクエスト

| フィールド | 型 | バリデーション | 説明 |
|---|---|---|---|
| `name` | `str` | 2〜20文字 | アイテム名 |
| `price` | `int` | 1以上（`gt=0`） | 価格 |
| `description` | `Optional[str]` | なし | 説明文（省略可） |

`status` は含まれておらず、`models.py` 側のデフォルト値 `ON_SALE` が適用されます。

**ItemUpdate** — アイテム更新リクエスト（全フィールドが任意）

| フィールド | 型 | バリデーション | 説明 |
|---|---|---|---|
| `name` | `Optional[str]` | 2〜20文字 | アイテム名 |
| `price` | `Optional[int]` | 1以上 | 価格 |
| `description` | `Optional[str]` | なし | 説明文 |
| `status` | `Optional[ItemStatus]` | 列挙値 | 出品状態（販売中→売切済みへの変更等） |

全フィールドが `Optional` なので、更新したいフィールドのみ送信するパーシャルアップデートが可能です。

**ItemResponse** — アイテム取得レスポンス

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | `int` | アイテムID |
| `name` | `str` | アイテム名 |
| `price` | `int` | 価格 |
| `description` | `Optional[str]` | 説明文 |
| `status` | `ItemStatus` | 出品状態 |
| `created_at` | `datetime` | 作成日時 |
| `updated_at` | `datetime` | 更新日時 |
| `user_id` | `int` | 出品者ユーザーID |

`model_config = ConfigDict(from_attributes=True)` により、SQLAlchemy の ORM オブジェクトをこのスキーマへ直接変換できます（旧 `orm_mode=True` に相当）。

**UserCreate** — ユーザー登録リクエスト

| フィールド | 型 | バリデーション | 説明 |
|---|---|---|---|
| `username` | `str` | 2文字以上 | ユーザー名 |
| `password` | `str` | 8文字以上 | 平文パスワード（サーバー側でハッシュ化） |

**UserResponse** — ユーザー取得レスポンス

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | `int` | ユーザーID |
| `username` | `str` | ユーザー名 |
| `created_at` | `datetime` | 作成日時 |
| `updated_at` | `datetime` | 更新日時 |

`password`・`salt` はレスポンスに含まれず、セキュリティ上安全な設計になっています。

**Token** — ログインレスポンス

| フィールド | 型 | 説明 |
|---|---|---|
| `access_token` | `str` | 発行された JWT アクセストークン |
| `token_type` | `str` | トークン種別（常に `"bearer"`） |

**DecodedToken** — JWT デコード結果の格納

| フィールド | 型 | 説明 |
|---|---|---|
| `username` | `str` | ユーザー名（JWT の `sub` クレームから取得） |
| `user_id` | `int` | ユーザーID（JWT の `id` クレームから取得） |

---

### [`cruds/auth.py`](./cruds/auth.py) — 認証CRUD処理

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `datetime` | `datetime`（標準ライブラリ） | JWT の有効期限（`exp`）を現在時刻ベースで算出 |
| `timedelta` | `datetime`（標準ライブラリ） | トークン有効期間の差分表現（例: `timedelta(minutes=20)`） |
| `hashlib` | 標準ライブラリ | `pbkdf2_hmac` によるパスワードの PBKDF2-SHA256 ハッシュ化 |
| `base64` | 標準ライブラリ | ランダムバイト列をBase64文字列にエンコード（ソルトの保存形式） |
| `os` | 標準ライブラリ | `os.urandom(32)` による暗号論的乱数生成（ソルト生成） |
| `Annotated` | `typing`（標準ライブラリ） | 型ヒントへのメタ情報付与（`Depends` との組み合わせ） |
| `Depends` | `fastapi` | FastAPI の依存性注入。`oauth2_schema` の自動注入に使用 |
| `OAuth2PasswordBearer` | `fastapi.security` | `Authorization: Bearer <token>` ヘッダーからトークンを自動抽出するスキーム |
| `jwt` | `jose` | JWT トークンのエンコード（`jwt.encode`）・デコード（`jwt.decode`） |
| `JWTError` | `jose` | JWT の署名検証失敗・期限切れ等で発生する例外クラス |
| `Session` | `sqlalchemy.orm` | DB セッションの型ヒント |
| `UserCreate`, `DecodedToken` | `schemas`（ローカル） | ユーザー登録リクエストおよびJWTデコード結果のスキーマ |
| `User` | `models`（ローカル） | SQLAlchemy の User ORM モデル |
| `get_settings` | `config`（ローカル） | `SECRET_KEY` の取得 |

#### 処理内容

**定数・スキーマの初期化**

```python
ALGORITHM = "HS256"
SECRET_KEY = get_settings().secret_key
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")
```

JWT の署名アルゴリズムとシークレットキーを設定します。`OAuth2PasswordBearer` はリクエストヘッダー `Authorization: Bearer <token>` からトークンを自動抽出するスキームで、`tokenUrl="/auth/login"` は Swagger UI でのログインエンドポイントの指定です。

**`create_user(db, user_create)`** — ユーザー登録

1. `os.urandom(32)` で 32 バイトの暗号論的乱数を生成し、Base64 エンコードしてソルトとする
2. `hashlib.pbkdf2_hmac("sha256", password, salt, 1000)` でパスワードをハッシュ化（PBKDF2-HMAC-SHA256、1000 回ストレッチング）
3. `User` モデルにユーザー名・ハッシュ済みパスワード・ソルトをセットして DB に保存し返却

**`authenticate_user(db, username, password)`** — ログイン認証

1. DB からユーザー名でレコードを検索し、存在しない場合は `None` を返す
2. DB に保存されているソルトを使って入力パスワードを同じ手順で再ハッシュ化
3. ハッシュが一致すれば `User` オブジェクトを返却。不一致の場合は `None` を返す

**`create_access_token(username, user_id, expires_delta)`** — JWT 生成

1. 現在時刻に `expires_delta` を加算して有効期限 `exp` を算出
2. ペイロード `{"sub": username, "id": user_id, "exp": expires}` を HS256 で署名した JWT 文字列を返却

**`get_current_user(token)`** — 認証済みユーザー取得

1. `OAuth2PasswordBearer` により `Authorization: Bearer` ヘッダーからトークンが自動注入される
2. `jwt.decode()` で署名検証・有効期限チェックを行い、クレームを取得
3. `username`・`user_id` を `DecodedToken` スキーマに詰めて返却。検証失敗時は `JWTError` を送出

#### セキュリティポイント

- パスワードは **PBKDF2-HMAC-SHA256**（イテレーション数 1000）でハッシュ化
- ユーザーごとに **ランダムな 32 バイトのソルト** を生成（レインボーテーブル攻撃対策）
- JWT は **HS256** アルゴリズムで署名し、有効期限（`exp`）を設定（ルーターで 20 分に設定）

---

### [`cruds/item.py`](./cruds/item.py) — アイテムCRUD処理

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `Session` | `sqlalchemy.orm` | DB セッションの型ヒント |
| `ItemCreate`, `ItemUpdate` | `schemas`（ローカル） | アイテム作成・更新リクエストの Pydantic スキーマ |
| `Item` | `models`（ローカル） | SQLAlchemy の Item ORM モデル |

#### 処理内容

**`find_all(db)`** — 全件取得

`db.query(Item).all()` で `items` テーブルの全レコードをリストで返します。

**`find_by_id(db, id, user_id)`** — ID・ユーザーIDで1件取得

`Item.id` と `Item.user_id` の両方でフィルタリングすることで、**自分が出品したアイテムのみ**を取得する所有者確認を行います。他ユーザーのアイテムは取得できません。

**`find_by_name(db, name)`** — アイテム名で部分一致検索

`Item.name.like(f"%{name}%")` による LIKE 検索でアイテム名に部分一致するレコードをリストで返します。

**`create(db, item_create, user_id)`** — アイテム新規作成

`item_create.model_dump()` で Pydantic スキーマを辞書に展開し、`user_id` を追加して `Item` インスタンスを生成し DB に保存します。

**`update(db, id, item_update, user_id)`** — アイテム更新

`find_by_id()` で所有者確認後、各フィールドを `None` チェックしてから上書きします。`None` のフィールドは既存値を維持するため、送信されたフィールドのみを更新する**パーシャルアップデート**を実現しています。

**`delete(db, id, user_id)`** — アイテム削除

`find_by_id()` で所有者確認後、`db.delete()` でレコードを削除します。削除対象が存在しない、または他ユーザーの所有の場合は `None` を返します。

---

### [`cruds/__init__.py`](./cruds/__init__.py) — パッケージ初期化

空ファイルです。`cruds/` ディレクトリを Python パッケージとして認識させます。`routers/item.py` では `from cruds import item as item_cruds` のようにインポートされます。

---

### [`routers/auth.py`](./routers/auth.py) — 認証エンドポイント定義

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `timedelta` | `datetime`（標準ライブラリ） | JWT の有効期間指定（20 分） |
| `Annotated` | `typing`（標準ライブラリ） | 依存性注入の型エイリアス定義 |
| `APIRouter` | `fastapi` | ルーターインスタンスの生成 |
| `Depends` | `fastapi` | DB セッション・フォームデータの依存性注入 |
| `HTTPException` | `fastapi` | 認証失敗時の 401 エラーレスポンス送出 |
| `OAuth2PasswordRequestForm` | `fastapi.security` | `username`・`password` を `application/x-www-form-urlencoded` 形式で受け取るフォームクラス |
| `Session` | `sqlalchemy.orm` | DB セッションの型ヒント |
| `status` | `starlette` | HTTP ステータスコード定数（`201 CREATED`・`200 OK` 等） |
| `auth_cruds` | `cruds`（ローカル） | `cruds/auth.py` の認証CRUD関数群 |
| `UserCreate`, `UserResponse`, `Token` | `schemas`（ローカル） | 登録リクエスト・レスポンス・トークンスキーマ |
| `get_db` | `database`（ローカル） | DB セッション取得の依存関数 |

#### 処理内容

**ルーターの設定**

```python
router = APIRouter(prefix="/auth", tags=["Auth"])
DbDependency = Annotated[Session, Depends(get_db)]
FormDependency = Annotated[OAuth2PasswordRequestForm, Depends()]
```

プレフィックス `/auth` で Swagger UI の "Auth" タグにまとめます。型エイリアスにより依存性注入をシンプルに記述できます。

**`POST /auth/signup`** — ユーザー登録

`UserCreate` スキーマ（`username` 2文字以上、`password` 8文字以上）を受け取り、`cruds/auth.py` の `create_user()` を呼び出してユーザーを作成します。成功時に `UserResponse`（パスワード・ソルトを除いた情報）を `HTTP 201` で返します。

**`POST /auth/login`** — ログイン・JWT発行

`OAuth2PasswordRequestForm` でフォームデータを受け取り、`authenticate_user()` で認証します。認証失敗時は `401 Unauthorized` を送出します。認証成功時は有効期限 **20 分** の JWT を生成し `Token` スキーマで返します。

---

### [`routers/item.py`](./routers/item.py) — アイテムエンドポイント定義

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `Annotated` | `typing`（標準ライブラリ） | 依存性注入の型エイリアス定義 |
| `APIRouter` | `fastapi` | ルーターインスタンスの生成 |
| `Path` | `fastapi` | パスパラメータのバリデーション（`gt=0` でID正数チェック） |
| `Query` | `fastapi` | クエリパラメータのバリデーション（`name` の文字数制限） |
| `HTTPException` | `fastapi` | 404 エラーレスポンスの送出 |
| `Depends` | `fastapi` | DB セッション・認証ユーザーの依存性注入 |
| `Session` | `sqlalchemy.orm` | DB セッションの型ヒント |
| `status` | `starlette` | HTTP ステータスコード定数 |
| `item_cruds` | `cruds`（ローカル） | `cruds/item.py` のアイテムCRUD関数群 |
| `auth_cruds` | `cruds`（ローカル） | `cruds/auth.py` の `get_current_user` 関数 |
| `ItemCreate`, `ItemUpdate`, `ItemResponse`, `DecodedToken` | `schemas`（ローカル） | アイテム操作・認証ユーザーのスキーマ |
| `get_db` | `database`（ローカル） | DB セッション取得の依存関数 |

#### 処理内容

**ルーターの設定**

```python
router = APIRouter(prefix="/items", tags=["Items"])
DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[DecodedToken, Depends(auth_cruds.get_current_user)]
```

プレフィックス `/items` で Swagger UI の "Items" タグにまとめます。`UserDependency` により認証が必要なエンドポイントでは JWT が自動検証され、`DecodedToken`（`username`・`user_id`）が注入されます。

**`GET /items`** — 全件取得（認証不要）

全アイテムをリストで返します。

**`GET /items/{id}`** — ID指定で1件取得（認証必要）

`Path(gt=0)` でIDが正の整数であることをバリデーション。認証ユーザー自身の出品アイテムのみ取得可能。存在しない場合は `404 Not Found` を返します。

**`GET /items/?name=xxx`** — 名前で検索（認証不要）

`Query(min_length=2, max_length=20)` でパラメータ `name` の文字数を制限。部分一致（LIKE 検索）でヒットしたアイテムをリストで返します。

**`POST /items`** — アイテム出品（認証必要）

JWT から取得した `user.user_id` を `user_id` として紐付けてアイテムを作成します。成功時は `HTTP 201` を返します。

**`PUT /items/{id}`** — アイテム更新（認証必要）

認証ユーザー自身の出品アイテムのみ更新可能。更新対象が存在しない場合は `404 Not Found` を返します。

**`DELETE /items/{id}`** — アイテム削除（認証必要）

認証ユーザー自身の出品アイテムのみ削除可能。削除対象が存在しない場合は `404 Not Found` を返します。

---

### [`routers/__init__.py`](./routers/__init__.py) — パッケージ初期化

空ファイルです。`routers/` ディレクトリを Python パッケージとして認識させます。`main.py` での `from routers import item, auth` が可能になります。

---

### [`migrations/env.py`](./migrations/env.py) — Alembicマイグレーション実行環境

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `fileConfig` | `logging.config`（標準ライブラリ） | `alembic.ini` 記載のログ設定を Python の logging に適用 |
| `engine_from_config` | `sqlalchemy` | `.ini` ファイルの `sqlalchemy.url` からエンジンを生成 |
| `pool` | `sqlalchemy` | コネクションプール戦略の指定（`NullPool` で接続の即時解放） |
| `context` | `alembic` | マイグレーション実行コンテキストの管理 |
| `Base` | `models`（ローカル） | 全モデルのメタデータ（自動マイグレーション生成に使用） |

#### 処理内容

```python
target_metadata = Base.metadata
```

`models.py` の `Base.metadata` を設定することで、`alembic revision --autogenerate` 実行時にモデル定義と DB の差分から**マイグレーションスクリプトを自動生成**できます。

**`run_migrations_offline()`** — オフラインモード

DB エンジンへの実接続なしで SQL スクリプトを出力するモードです。DB が利用できない環境でスクリプトを事前生成し、後から手動適用する用途に使います。

**`run_migrations_online()`** — オンラインモード

`engine_from_config()` で DB エンジンを生成し実際に接続してマイグレーションを適用します。通常の `alembic upgrade head` 実行時に使われます。`NullPool` を使用して、マイグレーション完了後に接続が即座に解放されます。

---

### [`migrations/script.py.mako`](./migrations/script.py.mako) — マイグレーションスクリプトテンプレート

#### テンプレート内インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `Sequence`, `Union` | `typing`（標準ライブラリ） | `branch_labels`・`depends_on` の型ヒント |
| `op` | `alembic` | DDL 操作（`create_table`・`add_column`・`drop_table` 等）の実行 |
| `sa` | `sqlalchemy` | カラム型定義（`sa.String()`・`sa.Integer()`・`sa.DateTime()` 等） |

#### 処理内容

`alembic revision` コマンド実行時にこのテンプレートから新しいマイグレーションファイルが生成されます。Mako テンプレート構文（`${...}`）で以下の変数が埋め込まれます。

| 変数 | 説明 |
|---|---|
| `up_revision` | 新規生成されるリビジョン ID |
| `down_revision` | 1つ前のリビジョン ID（ロールバック先） |
| `create_date` | ファイル生成日時 |
| `upgrades` / `downgrades` | `--autogenerate` 時に差分から自動生成される DDL |

---

### マイグレーション履歴（[`migrations/versions/`](./migrations/versions/)）

マイグレーションは以下の順序で適用されます（`down_revision` チェーンで管理）。

#### [`f3d5adf85e9a_create_items_table.py`](./migrations/versions/f3d5adf85e9a_create_items_table.py) — itemsテーブル作成（起点）

`down_revision = None`（チェーンの起点）。

| 操作 | 内容 |
|---|---|
| upgrade | `items` テーブルを作成（`id`・`name`・`price`・`description`・`status`・`created_at`・`updated_at`） |
| downgrade | `items` テーブルを削除 |

#### [`b8ca17099c7d_create_users_table.py`](./migrations/versions/b8ca17099c7d_create_users_table.py) — usersテーブル作成

`down_revision = 'f3d5adf85e9a'`

| 操作 | 内容 |
|---|---|
| upgrade | `users` テーブルを作成（`id`・`username`(UNIQUE)・`password`・`created_at`・`updated_at`） |
| downgrade | `users` テーブルを削除 |

#### [`ff676fae4f35_add_salt_column.py`](./migrations/versions/ff676fae4f35_add_salt_column.py) — saltカラム追加

`down_revision = 'b8ca17099c7d'`

| 操作 | 内容 |
|---|---|
| upgrade | `users.salt`（String, NOT NULL）カラムを追加 |
| downgrade | `users.salt` カラムを削除 |

#### [`5f1777586dbe_add_foreign_key.py`](./migrations/versions/5f1777586dbe_add_foreign_key.py) — 外部キー追加（最新）

`down_revision = 'ff676fae4f35'`

| 操作 | 内容 |
|---|---|
| upgrade | `items.user_id`（Integer, NOT NULL）カラムを追加し、`users.id` への外部キー（`ondelete=CASCADE`）を設定 |
| downgrade | 外部キー制約と `items.user_id` カラムを削除 |

---

### [`tests/conftest.py`](./tests/conftest.py) — pytestフィクスチャ定義

#### インポートモジュール

| モジュール | パッケージ | 用途 |
|---|---|---|
| `os` | 標準ライブラリ | アプリルートのパス解決（`sys.path` への追加） |
| `sys` | 標準ライブラリ | `sys.path.append()` でインポートパスを調整 |
| `pytest` | `pytest` | フィクスチャ（`@pytest.fixture`）の定義 |
| `TestClient` | `fastapi.testclient` | FastAPI アプリへの HTTP リクエストをテスト内で送信するクライアント |
| `create_engine` | `sqlalchemy` | テスト用インメモリ SQLite エンジンの生成 |
| `StaticPool` | `sqlalchemy.pool` | テスト用に接続を使い回す固定プール（SQLite インメモリ DB の接続維持に必要） |
| `Session` | `sqlalchemy.orm` | DB セッションの型ヒント |
| `sessionmaker` | `sqlalchemy.orm` | テスト用セッションファクトリの生成 |
| `Base`, `Item` | `models`（ローカル） | テスト DB のスキーマ作成・フィクスチャデータ投入 |
| `DecodedToken` | `schemas`（ローカル） | 認証ユーザーのモックデータ生成 |
| `app` | `main`（ローカル） | テスト対象の FastAPI アプリ |
| `get_db` | `database`（ローカル） | DB 依存関係のオーバーライド対象 |
| `get_current_user` | `cruds.auth`（ローカル） | 認証依存関係のオーバーライド対象 |

#### 処理内容

**`session_fixture`** — テスト用 DB セッション

PostgreSQL の代わりにインメモリ SQLite を使用してテスト用 DB を構築します。`StaticPool` により接続が維持され、複数リクエスト間でデータが共有されます。フィクスチャデータとして `PC1`（user_id=1）・`PC2`（user_id=2）の 2 アイテムを事前に投入します。

**`user_fixture`** — 認証済みユーザーのモック

テスト中の認証ユーザーとして `DecodedToken(username="user1", user_id=1)` を返します。

**`client_fixture`** — テスト用 HTTP クライアント

FastAPI の `dependency_overrides` 機能を使い、`get_db` をテスト用 SQLite セッション、`get_current_user` をモックユーザーに差し替えます。テスト終了後に `app.dependency_overrides.clear()` でオーバーライドを解除します。

---

### [`tests/test_example.py`](./tests/test_example.py) — サンプルテスト

pytest の動作確認用のシンプルなサンプルファイルです。`add()` 関数を定義し、`1 + 2 = 3` であることを確認するだけのテストです。

---

### [`tests/test_item.py`](./tests/test_item.py) — アイテムAPIテスト

`client_fixture` を使ってアイテム API の各エンドポイントを正常系・異常系に分けてテストします。

| テスト関数 | 検証内容 |
|---|---|
| `test_find_all` | `GET /items` で 2 件返ること |
| `test_find_by_id_正常系` | `GET /items/1` で `id=1` のアイテムが返ること |
| `test_find_by_id_異常系` | `GET /items/10`（存在しない）で `404` が返ること |
| `test_find_by_name` | `GET /items/?name=PC1` で 1 件・`name=PC1` のアイテムが返ること |
| `test_create` | `POST /items` でアイテムを作成し全件数が 3 件になること |
| `test_update_正常系` | `PUT /items/1` で `name`・`price` が更新されること |
| `test_update_異常系` | `PUT /items/10`（存在しない）で `404` が返ること |
| `test_delete_正常系` | `DELETE /items/1` 後に全件数が 1 件になること |
| `test_delete_異常系` | `DELETE /items/10`（存在しない）で `404` が返ること |

---

## 🐳 インフラ構成（[docker-compose.yml](./docker-compose.yml)）

| サービス | イメージ | ポート | 説明 |
|---|---|---|---|
| `postgres` | `postgres:16-alpine` | `5432:5432` | アプリケーション用 PostgreSQL |
| `pgadmin` | `dpage/pgadmin4` | `81:80` | DB 管理 GUI ツール |

- PostgreSQL のデータは `./docker/postgres/pgdata` にボリュームマウントされ永続化
- `./docker/postgres/init.d` に SQL ファイルを配置すると初回起動時に自動実行
- pgAdmin アクセス: `http://localhost:81` / `fastapi@example.com` / `password`

---

## 🔑 環境変数（[.env](./.env)）

| 変数名 | 説明 |
|---|---|
| `SECRET_KEY` | JWT トークンの署名・検証に使用するシークレットキー |
| `SQLALCHEMY_DATABASE_URL` | PostgreSQL 接続 URL（`postgresql://user:pass@host:port/dbname` 形式） |

> ⚠️ `.env` は `.gitignore` に記載されており Git 管理対象外です。サンプル値を本番環境でそのまま使用しないでください。

---

## 🚀 セットアップ手順

### 1. データベースの起動

```bash
docker compose up -d
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. マイグレーションの実行

```bash
alembic upgrade head
```

### 4. アプリケーションの起動

```bash
uvicorn main:app --reload
```

起動後、Swagger UI は `http://localhost:8000/docs` で確認できます。

### 5. テストの実行

```bash
pytest tests/
```

---

## 🔌 API エンドポイント一覧

### 認証 `/auth`

| メソッド | パス | 認証 | ステータス | 説明 |
|---|---|---|---|---|
| `POST` | `/auth/signup` | 不要 | 201 | ユーザー登録 |
| `POST` | `/auth/login` | 不要 | 200 | ログイン・JWTトークン発行 |

### アイテム `/items`

| メソッド | パス | 認証 | ステータス | 説明 |
|---|---|---|---|---|
| `GET` | `/items` | 不要 | 200 | 全アイテム取得 |
| `GET` | `/items/{id}` | 必要 | 200 / 404 | ID指定で1件取得（自分の出品のみ） |
| `GET` | `/items/?name=xxx` | 不要 | 200 | アイテム名で部分一致検索 |
| `POST` | `/items` | 必要 | 201 | アイテム出品 |
| `PUT` | `/items/{id}` | 必要 | 200 / 404 | アイテム更新 |
| `DELETE` | `/items/{id}` | 必要 | 200 / 404 | アイテム削除 |

---

## 🏗️ アーキテクチャ概要

```
クライアント（React等 / http://localhost:3000）
    │  HTTP リクエスト
    ▼
[main.py] FastAPI アプリ
    │  ① CORSMiddleware（オリジン制御）
    │  ② add_process_time_header（処理時間計測 → X-Process-Time ヘッダー）
    ▼
[routers/auth.py | routers/item.py] ルーター層
    │  エンドポイント定義・Path/Query バリデーション・Pydantic リクエスト検証
    ▼
[cruds/auth.py | cruds/item.py] CRUD層
    │  ビジネスロジック・SQLAlchemy クエリ・JWT 生成/検証
    ▼
[database.py] セッション管理（get_db）
    │
    ▼
PostgreSQL（Docker コンテナ / port 5432）
```

---

## 🛠️ 使用技術（[requirements.txt](./requirements.txt)）

| カテゴリ | ライブラリ | バージョン |
|---|---|---|
| フレームワーク | fastapi | 0.104.1 |
| ASGI サーバー | uvicorn | 0.23.2 |
| ORM | SQLAlchemy | 2.0.23 |
| DB ドライバ | psycopg2-binary | 2.9.9 |
| 認証（JWT） | python-jose | 3.3.0 |
| バリデーション | pydantic | 2.4.2 |
| 設定管理 | pydantic-settings | 2.0.3 |
| フォームデータ | python-multipart | 0.0.6 |
| マイグレーション | alembic | 1.12.1 |
| テスト | pytest | 7.4.3 |
| HTTP テストクライアント | httpx | 0.25.1 |
| コンテナ | Docker / Docker Compose | — |
| DB 管理 GUI | pgAdmin 4 | — |
