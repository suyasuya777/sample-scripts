# 🗂️ ユーザ・アイテム管理（FastAPI + SQLite）

FastAPIの推奨フォルダ構成サンプルです。

```
python-11-fastapi-user-itemapp/
│
├── main.py            # エントリーポイント
├── config.py          # 環境変数管理（pydantic-settings）
├── database.py        # DB接続・セッション管理
│
├── routers/           # エンドポイント定義
│   ├── user.py        # /users エンドポイント
│   └── item.py        # /items エンドポイント
│
├── cruds/             # DB操作ロジック
│   ├── user.py        # users テーブルのDB操作
│   └── item.py        # items テーブルのDB操作
│
├── schemas/           # Pydanticスキーマ
│   ├── user.py        # UserCreate / UserUpdate / UserResponse
│   └── item.py        # ItemCreate / ItemUpdate / ItemResponse
│
├── models/            # SQLAlchemy ORMモデル
│   ├── user.py        # User ORMモデル（usersテーブル定義）
│   └── item.py        # Item ORMモデル（itemsテーブル定義）
│
├── frontapp/          # フロントエンド（E2Eテスト・管理UI）
│   ├── index.html     # メイン画面
│   ├── app.js         # API呼び出しロジック
│   └── styles.css     # スタイル
│
└── tests/             # pytestテスト
    ├── test_user.py   # users エンドポイントのテスト
    └── test_item.py   # items エンドポイントのテスト
```

---

## 🛠️ セットアップ

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

# サーバーの起動
python -m uvicorn main:app --reload

起動後、Swagger UI は `http://127.0.0.1:8000/docs` で確認できます。

フロントエンドは `frontapp/index.html` を Live Server 等で開いてください（オリジン: `http://127.0.0.1:5500`）。

# 非アクティブ化
deactivate

# 仮想環境を削除
.venv フォルダを削除
```

---

## 🧪 テスト実行

```bash
pytest tests/
```

---

## 🔌 エンドポイント一覧

### 👤 Users `/users`

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/users` | ユーザー一覧取得 |
| GET | `/users/paged?skip=0&limit=100` | ページネーション付き一覧取得 |
| GET | `/users/{user_id}` | ユーザー1件取得 |
| POST | `/users` | ユーザー作成 |
| PATCH | `/users/{user_id}` | ユーザー部分更新 |
| DELETE | `/users/{user_id}` | ユーザー削除 |

### 📦 Items `/items`

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/items` | アイテム一覧取得 |
| GET | `/items/paged?skip=0&limit=100` | ページネーション付き一覧取得 |
| GET | `/items/{item_id}` | アイテム1件取得 |
| GET | `/items/user/{user_id}` | ユーザーに紐づくアイテム一覧取得 |
| POST | `/items` | アイテム作成 |
| PATCH | `/items/{item_id}` | アイテム部分更新 |
| DELETE | `/items/{item_id}` | アイテム削除 |

---

## 📁 ファイル一覧

### 📄 [config.py](config.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `pydantic_settings.BaseSettings` | 環境変数を型安全に管理するベースクラス |
| `pydantic_settings.SettingsConfigDict` | `.env` ファイル読み込み設定 |
| `functools.lru_cache` | `Settings` インスタンスをキャッシュし再生成を防ぐ |

**処理概要**

`BaseSettings` を継承した `Settings` クラスで環境変数（`secret_key`・`database_url`）を管理する。`get_settings()` に `@lru_cache` を付与し、アプリ全体で同一インスタンスを共有する。

---

### 📄 [database.py](database.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期DBエンジン生成 |
| `sqlalchemy.ext.asyncio.async_sessionmaker` | 非同期セッションファクトリ生成 |
| `sqlalchemy.orm.DeclarativeBase` | ORMモデルの基底クラス |
| `config` | `config.get_settings()` 経由で `database_url` を取得 |

**処理概要**

SQLAlchemy の非同期 `engine` / `async_session` / `Base` を生成・公開する。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出す。

---

### 📄 [models/user.py](models/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 文字列形式の型注釈（前方参照）を有効化 |
| `typing.TYPE_CHECKING` | 型チェック時のみ `Item` を import し循環参照を回避 |
| `sqlalchemy.String` | `name` / `email` カラムの文字列長指定 |
| `sqlalchemy.orm.Mapped`, `mapped_column`, `relationship` | ORMカラム・リレーション定義 |
| `database.Base` | ORMモデルの基底クラス（`class User(Base)`） |
| `models.item.Item`（型チェック時） | `items` リレーションの型注釈 |

**処理概要**

`users` テーブルに対応するORMモデル `User` を定義する。`id` / `name` / `email` の3カラムを持ち、`name` は `String(50)`、`email` は `String(254)` を指定する。`items` で `Item` への1対多リレーションを構成し、`cascade="all, delete-orphan"` によりUser削除時に紐づくItemを連鎖削除する。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `from __future__ import annotations` | すべての型注釈を文字列として遅延評価する（PEP 563）。実行時に評価されないため、後方やTYPE_CHECKINGブロック内で定義した型（`list["Item"]` 等）を循環import無しで参照できる。 |
| `from typing import TYPE_CHECKING` | 静的型チェック時のみ `True`、実行時は常に `False` となる定数。型ヒント専用のimportを分岐させるために使う。 |
| `if TYPE_CHECKING:` | 型チェッカーだけが評価し実行時には通らないブロック。ここでは `Item` を型注釈用にのみimportし、`models.user` ⇔ `models.item` の循環importを回避する。 |
| `back_populates="owner"` | `User.items` と `Item.owner` を相互に結び付ける双方向リレーション設定。一方を更新するともう一方にも反映される。 |
| `cascade="all, delete-orphan"` | User削除時に紐づくItemを連鎖削除し、さらに `items` コレクションから外された（孤児化した）Itemも削除する。 |

---

### 📄 [models/item.py](models/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 文字列形式の型注釈（前方参照）を有効化 |
| `typing.TYPE_CHECKING` | 型チェック時のみ `User` を import し循環参照を回避 |
| `sqlalchemy.String`, `ForeignKey` | 文字列長指定・外部キー制約 |
| `sqlalchemy.orm.Mapped`, `mapped_column`, `relationship` | ORMカラム・リレーション定義 |
| `database.Base` | ORMモデルの基底クラス（`class Item(Base)`） |
| `models.user.User`（型チェック時） | `owner` リレーションの型注釈 |

**処理概要**

`items` テーブルに対応するORMモデル `Item` を定義する。`id` / `title` / `description` / `user_id` の4カラムを持ち、`title` は `String(50)`、`description` は `String(255)`、`user_id` は `ForeignKey("users.id")` で `users` を参照する。`owner` で `User` への多対1リレーションを構成し、`User.items` と `back_populates` で対をなす。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `from __future__ import annotations` | すべての型注釈を文字列として遅延評価する（PEP 563）。実行時に評価されないため、TYPE_CHECKINGブロック内で定義した型（`"User"` 等）を循環import無しで参照できる。 |
| `from typing import TYPE_CHECKING` | 静的型チェック時のみ `True`、実行時は常に `False` となる定数。型ヒント専用のimportを分岐させるために使う。 |
| `if TYPE_CHECKING:` | 型チェッカーだけが評価し実行時には通らないブロック。ここでは `User` を型注釈用にのみimportし、`models.item` ⇔ `models.user` の循環importを回避する。 |
| `back_populates="items"` | `Item.owner` と `User.items` を相互に結び付ける双方向リレーション設定。User側の `back_populates="owner"` と対をなす。 |

---

### 📄 [schemas/user.py](schemas/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `__future__.annotations` | 文字列形式の型注釈（前方参照）を有効化 |
| `typing.Annotated` | 型エイリアスへの `Field` 付与 |
| `pydantic.BaseModel`, `ConfigDict`, `EmailStr`, `Field` | スキーマ定義・ORM変換設定・メール検証・バリデーション |
| `schemas.item.ItemResponse` | `UserItems` で所有アイテムの型として参照 |

**型エイリアス一覧**

| エイリアス | 型 | バリデーション |
|---|---|---|
| `UserName` | `str` | `min_length=1`, `max_length=50` |
| `UserEmail` | `EmailStr` | `max_length=254` |
| `UserOptionalName` | `str \| None` | `min_length=1`, `max_length=50` |
| `UserOptionalEmail` | `EmailStr \| None` | `max_length=254` |
| `UserItems` | `list[ItemResponse]` | （所有アイテム一覧） |

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `UserBase` | `name`・`email` の共通フィールド定義 |
| `UserCreate` | POST リクエストボディ（UserBase をそのまま継承） |
| `UserUpdate` | PATCH リクエストボディ（全フィールド Optional） |
| `UserResponse` | レスポンス（`id`・`items` を追加） |

**処理概要**

各フィールドは `Annotated` + `Field` の型エイリアスで定義し、バリデーションルールを一元管理する。`UserResponse` は `model_config = ConfigDict(from_attributes=True)` でORMオブジェクトからの変換を有効化し、所有アイテムを `items: UserItems`（`Field(default_factory=list)`）として含む。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `model_config = ConfigDict(from_attributes=True)` | 辞書だけでなくORMオブジェクトの属性からもインスタンス生成を許可する設定。`UserResponse.model_validate(user_orm)` のように `.id` / `.name` 等を読み取って変換できる（Pydantic v1 の `orm_mode` に相当）。 |
| `default_factory=list` | `items` の既定値をインスタンス生成のたびに `list()` を呼んで生成する。各インスタンスが独立した空リストを持ち、ミュータブルなデフォルト値が共有される問題を防ぐ。 |

---

### 📄 [schemas/item.py](schemas/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `typing.Annotated` | 型エイリアスへの `Field` 付与 |
| `pydantic.BaseModel`, `ConfigDict`, `Field` | スキーマ定義・ORM変換設定・バリデーション |

**型エイリアス一覧**

| エイリアス | 型 | バリデーション |
|---|---|---|
| `ItemTitle` | `str` | `min_length=1`, `max_length=50` |
| `ItemDescription` | `str \| None` | `min_length=1`, `max_length=255` |
| `ItemUserId` | `int` | `gt=0` |
| `ItemOptionalTitle` | `str \| None` | `min_length=1`, `max_length=50` |
| `ItemOptionalDescription` | `str \| None` | `min_length=1`, `max_length=255` |
| `ItemOptionalUserId` | `int \| None` | `gt=0` |

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `ItemBase` | `title`・`description`・`user_id` の共通フィールド定義 |
| `ItemCreate` | POST リクエストボディ（ItemBase をそのまま継承） |
| `ItemUpdate` | PATCH リクエストボディ（全フィールド Optional） |
| `ItemResponse` | レスポンス（`id` を追加） |

**処理概要**

各フィールドは `Annotated` + `Field` の型エイリアスで定義し、バリデーションルールを一元管理する。`ItemBase`（`title` / `description` / `user_id`）を基底に `ItemCreate` / `ItemUpdate` / `ItemResponse` を派生させ、`ItemResponse` は `model_config = ConfigDict(from_attributes=True)` でORMオブジェクトからの変換を有効化する。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `model_config = ConfigDict(from_attributes=True)` | 辞書だけでなくORMオブジェクトの属性からもインスタンス生成を許可する設定。`ItemResponse.model_validate(item_orm)` のように `.id` / `.title` 等を読み取って変換できる（Pydantic v1 の `orm_mode` に相当）。 |

---

### 📄 [cruds/user.py](cruds/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.select` | SELECT 文の構築 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッションの型注釈 |
| `sqlalchemy.orm.selectinload` | `items` の事前ロード（N+1回避） |
| `models.user.User` | 操作対象のORMモデル |
| `schemas.user.UserCreate`, `UserUpdate` | 入力スキーマの型注釈 |

**関数一覧**

| 関数 | 説明 |
|---|---|
| `get_users` | 全ユーザー取得（items を `selectinload`） |
| `get_user` | id で1件取得（items を `selectinload`） |
| `get_users_paged` | ページネーション付き取得（items を `selectinload`） |
| `create_user` | ユーザー作成 |
| `patch_user` | 部分更新（`exclude_unset=True` 使用） |
| `delete_user` | 削除（成功: `True` / 未存在: `False`） |

**処理概要**

`users` テーブルに対する非同期CRUD操作を提供する。一覧・単件取得系は `selectinload(User.items)` で関連アイテムを事前ロードし、`create_user` / `patch_user` は更新後に `refresh(["items"])` で関連を再取得する。`patch_user` は `exclude_unset=True` で送信された項目のみを反映し、`delete_user` は対象の有無を真偽値（成功: `True` / 未存在: `False`）で返す。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `selectinload(User.items)` | 関連 `items` を別クエリ（`IN (...)`）でまとめて事前ロードする eager loading 戦略。N+1問題を避け、非同期セッションでも遅延ロードに頼らず関連へアクセスできる。 |
| `user = User(**user_in.model_dump())` | Pydantic入力モデルを辞書化し、キーワード引数として展開して `User` ORMインスタンスを生成する（`name=...`, `email=...`）。 |
| `for key, value in user_in.model_dump(exclude_unset=True).items(): setattr(user, key, value)` | 明示的に指定された項目だけを取り出し（`exclude_unset=True`）、既存 `user` オブジェクトへ順に代入する。未送信フィールドは現在値を保持し、PATCH の部分更新を実現する。 |
| `await db.refresh(user, ["items"])` | commit後にDBから `user` を再取得し、特に `items` リレーションを最新化する。返却オブジェクトが最新の関連データを持つようにする。 |

---

### 📄 [cruds/item.py](cruds/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.select` | SELECT 文の構築 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッションの型注釈 |
| `models.item.Item` | 操作対象のORMモデル |
| `schemas.item.ItemCreate`, `ItemUpdate` | 入力スキーマの型注釈 |

**関数一覧**

| 関数 | 説明 |
|---|---|
| `get_items` | 全アイテム取得 |
| `get_item` | id で1件取得 |
| `get_items_by_user` | user_id で絞り込み取得 |
| `get_items_paged` | ページネーション付き取得 |
| `create_item` | アイテム作成（`user_id` はリクエストボディに含む） |
| `patch_item` | 部分更新（`exclude_unset=True` 使用） |
| `delete_item` | 削除（成功: `True` / 未存在: `False`） |

**処理概要**

`items` テーブルに対する非同期CRUD操作を提供する。`get_items_by_user` は `user_id` で絞り込み取得する（取得系で `selectinload` は使用しない）。`patch_item` は `exclude_unset=True` で送信された項目のみを反映し、`delete_item` は対象の有無を真偽値（成功: `True` / 未存在: `False`）で返す。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `item = Item(**item_in.model_dump())` | Pydantic入力モデルを辞書化し、キーワード引数として展開して `Item` ORMインスタンスを生成する（`title=...`, `description=...`, `user_id=...`）。 |
| `for key, value in item_in.model_dump(exclude_unset=True).items(): setattr(item, key, value)` | 明示的に指定された項目だけを取り出し（`exclude_unset=True`）、既存 `item` オブジェクトへ順に代入する。未送信フィールドは現在値を保持し、PATCH の部分更新を実現する。 |
| `await db.refresh(item)` | commit後にDBから `item` を再取得し、行のカラム値を最新化する（リレーション未指定。Itemは事前ロード対象を持たないため列のみ更新）。 |

---

### 📄 [routers/user.py](routers/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `typing.Annotated` | `DBSession` 依存性注入の型定義 |
| `fastapi.APIRouter`, `Depends`, `HTTPException` | ルーター定義・DI・404応答 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッションの型注釈 |
| `cruds.user`（`user_crud`） | DB操作ロジックの呼び出し |
| `database.get_db` | DBセッション払い出し依存関数 |
| `schemas.user.UserCreate`, `UserResponse`, `UserUpdate` | リクエスト／レスポンススキーマ |

**エンドポイント一覧**

| メソッド | パス | crud関数 |
|---|---|---|
| GET | `/users` | `get_users` |
| GET | `/users/paged` | `get_users_paged` |
| GET | `/users/{user_id}` | `get_user` |
| POST | `/users` | `create_user` |
| PATCH | `/users/{user_id}` | `patch_user` |
| DELETE | `/users/{user_id}` | `delete_user` |

**処理概要**

`DBSession`（`Annotated[AsyncSession, Depends(get_db)]`）を定義し、各ハンドラで共有する。未存在リソースへのアクセスには `HTTPException(status_code=404)` を返す。ルート定義順は `/paged` → `/{user_id}` とし、パスパラメータとの競合を回避している。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `DBSession = Annotated[AsyncSession, Depends(get_db)]` | 型（`AsyncSession`）とFastAPIの依存性（`Depends(get_db)`）を束ねた再利用可能な型エイリアス。各ハンドラで `db: DBSession` と書くだけでリクエストごとのDBセッションが注入され、`Depends(get_db)` の重複記述を省ける。 |

---

### 📄 [routers/item.py](routers/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `typing.Annotated` | `DBSession` 依存性注入の型定義 |
| `fastapi.APIRouter`, `Depends`, `HTTPException` | ルーター定義・DI・404応答 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッションの型注釈 |
| `cruds.item`（`item_crud`） | DB操作ロジックの呼び出し |
| `database.get_db` | DBセッション払い出し依存関数 |
| `schemas.item.ItemCreate`, `ItemResponse`, `ItemUpdate` | リクエスト／レスポンススキーマ |

**エンドポイント一覧**

| メソッド | パス | crud関数 |
|---|---|---|
| GET | `/items` | `get_items` |
| GET | `/items/paged` | `get_items_paged` |
| GET | `/items/user/{user_id}` | `get_items_by_user` |
| GET | `/items/{item_id}` | `get_item` |
| POST | `/items` | `create_item` |
| PATCH | `/items/{item_id}` | `patch_item` |
| DELETE | `/items/{item_id}` | `delete_item` |

**処理概要**

`DBSession`（`Annotated[AsyncSession, Depends(get_db)]`）を定義し、各ハンドラで共有する。未存在リソースへのアクセスには `HTTPException(status_code=404)` を返す。ルート定義順は `/paged` → `/user/{user_id}` → `/{item_id}` とし、パスパラメータとの競合を回避している。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `DBSession = Annotated[AsyncSession, Depends(get_db)]` | 型（`AsyncSession`）とFastAPIの依存性（`Depends(get_db)`）を束ねた再利用可能な型エイリアス。各ハンドラで `db: DBSession` と書くだけでリクエストごとのDBセッションが注入され、`Depends(get_db)` の重複記述を省ける。 |

---

### 📄 [main.py](main.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `contextlib.asynccontextmanager` | `lifespan` コンテキストマネージャ定義 |
| `fastapi.FastAPI` | アプリケーションインスタンス生成 |
| `fastapi.middleware.cors.CORSMiddleware` | CORSミドルウェア登録 |
| `database.Base`, `database.engine` | テーブル自動作成に使用 |
| `routers.item`, `routers.user` | ルーター登録 |

**処理概要**

アプリケーションのエントリーポイント。`user` / `item` の各ルーターを `FastAPI` インスタンスに登録する。`lifespan` で起動時に `Base.metadata.create_all` を実行しテーブルを自動作成する。CORS設定で `http://127.0.0.1:5500` からのアクセスを許可する。

**主な記述の解説**

| 記述 | 解説 |
|---|---|
| `lifespan()`（`@asynccontextmanager`） | アプリの起動・終了処理を定義する非同期コンテキストマネージャ。起動時に `async with engine.begin()` でトランザクションを開き、`run_sync(Base.metadata.create_all)` で全テーブルを作成する。`yield` で制御をアプリ本体へ渡し、`yield` 以降（本コードでは無し）が終了時処理となる。`FastAPI(lifespan=lifespan)` に渡して登録する。 |
| `app.add_middleware(CORSMiddleware, ...)` | CORSミドルウェアを登録する。`allow_origins=["http://127.0.0.1:5500"]` でフロントのオリジンからのアクセスを許可、`allow_credentials=True` で Cookie・認証ヘッダーの送受信を許可、`allow_methods=["*"]` / `allow_headers=["*"]` で全HTTPメソッド・全ヘッダーを許可する。 |

**用語解説: CORS**

CORS（Cross-Origin Resource Sharing）… 異なるオリジン間のリソース共有を制御する仕組み。

オリジンは「スキーム＋ホスト＋ポート」の組で構成される。

```
https://example.com:8080/path
│       │           │
│       │           └── ポート
│       └────────────── ホスト（ドメイン）
└────────────────────── スキーム（プロトコル）
```

---

### 📄 [tests/test_user.py](tests/test_user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.testclient.TestClient` | FastAPIアプリへHTTPリクエストを送るテスト用クライアント（実サーバの起動不要） |
| `main.app` | テスト対象の `FastAPI` アプリ本体 |

**処理概要**

`client = TestClient(app)` を生成し、`/users` エンドポイント群に対して実際のHTTPリクエストを発行する結合テスト。一覧・ページネーション・作成・取得・部分更新・削除の正常系と、未存在ID（`99999`）に対する404の異常系を検証する。`test_get_user` / `test_patch_user` / `test_delete_user` は事前に `POST /users` でユーザーを作成し、返却された `id` を用いて後続の操作を確認する。

**テスト項目**

| テスト関数 | 対象 | 検証内容 |
|---|---|---|
| `test_get_users` | `GET /users` | 200 / レスポンスが list |
| `test_get_users_paged` | `GET /users/paged?skip=0&limit=10` | 200 / レスポンスが list |
| `test_create_user` | `POST /users` | 200 / `name`・`email` 一致 / `id` を含む |
| `test_get_user` | `POST /users` → `GET /users/{id}` | 200 / 取得した `id` が作成時と一致 |
| `test_get_user_not_found` | `GET /users/99999` | 404 |
| `test_patch_user` | `POST /users` → `PATCH /users/{id}` | 200 / `name` が更新され `email` は不変（部分更新） |
| `test_patch_user_not_found` | `PATCH /users/99999` | 404 |
| `test_delete_user` | `POST /users` → `DELETE /users/{id}` | 200 / 戻り値 `True` / 削除後の `GET` が404 |
| `test_delete_user_not_found` | `DELETE /users/99999` | 404 |

---

### 📄 [tests/test_item.py](tests/test_item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.testclient.TestClient` | FastAPIアプリへHTTPリクエストを送るテスト用クライアント（実サーバの起動不要） |
| `main.app` | テスト対象の `FastAPI` アプリ本体 |

**処理概要**

`client = TestClient(app)` を生成し、`/items` エンドポイント群に対する結合テストを行う。Itemは `user_id`（外部キー）を必須とするため、ヘルパー関数 `_create_user(name, email)` で先にユーザーを作成し、その戻り値のIDを使ってアイテムを作成・検証する。一覧・ページネーション・作成・取得・ユーザー別取得・部分更新・削除の正常系と、未存在ID（`99999`）に対する404の異常系を検証する。

**ヘルパー関数**

| 関数 | 説明 |
|---|---|
| `_create_user(name, email) -> int` | `POST /users` でテスト用ユーザーを作成し、生成された `id` を返す（各テストの前提データ準備用） |

**テスト項目**

| テスト関数 | 対象 | 検証内容 |
|---|---|---|
| `test_get_items` | `GET /items` | 200 / レスポンスが list |
| `test_get_items_paged` | `GET /items/paged?skip=0&limit=10` | 200 / レスポンスが list |
| `test_create_item` | `POST /items` | 200 / `title`・`description` 一致 / `id` を含む |
| `test_get_item` | `POST /items` → `GET /items/{id}` | 200 / 取得した `id` が作成時と一致 |
| `test_get_item_not_found` | `GET /items/99999` | 404 |
| `test_get_items_by_user` | `POST /items` → `GET /items/user/{user_id}` | 200 / レスポンスが list / 1件以上存在 |
| `test_patch_item` | `POST /items` → `PATCH /items/{id}` | 200 / `title` が更新され `description` は不変（部分更新） |
| `test_patch_item_not_found` | `PATCH /items/99999` | 404 |
| `test_delete_item` | `POST /items` → `DELETE /items/{id}` | 200 / 戻り値 `True` / 削除後の `GET` が404 |
| `test_delete_item_not_found` | `DELETE /items/99999` | 404 |

---

### 📄 [frontapp/](frontapp/)

ブラウザから直接APIを操作できる管理UIです。

| ファイル | 説明 |
|---|---|
| `index.html` | Users / Items タブ切り替え、ページネーション、モーダルによるCRUD操作 |
| `app.js` | API呼び出しロジック（fetch、エンドポイント定義、ステータス表示） |
| `styles.css` | スタイル定義 |

Live Server 等で `index.html` を開き、BASE URL に `http://127.0.0.1:8000` を設定して使用する。
