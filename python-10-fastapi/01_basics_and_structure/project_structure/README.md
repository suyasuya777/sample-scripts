# project_structure

FastAPIの推奨フォルダ構成サンプルです。

```
project_structure/
│ 
├── main.py            # エントリーポイント
├── config.py          # 環境変数管理（pydantic-settings）
├── database.py        # DB接続・セッション管理
│ 
├── routers/           # エンドポイント定義
│   ├── __init__.py
│   ├── user.py        # /users エンドポイント
│   └── item.py        # /items エンドポイント
│ 
├── cruds/             # DB操作ロジック
│   ├── __init__.py
│   ├── user.py        # users テーブルのDB操作
│   └── item.py        # items テーブルのDB操作
│ 
├── schemas/           # Pydanticスキーマ
│   ├── __init__.py
│   ├── user.py        # User の入出力スキーマ
│   └── item.py        # Item の入出力スキーマ
│ 
├── models/            # SQLAlchemy ORMモデル
│   ├── __init__.py
│   ├── user.py        # User ORMモデル（usersテーブル定義）
│   └── item.py        # Item ORMモデル（itemsテーブル定義）
│ 
└── tests/             # pytestテスト
    ├── __init__.py
    ├── test_user.py   # users エンドポイントのテスト
    └── test_item.py   # items エンドポイントのテスト
```

---

## ファイル一覧

### [main.py](main.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | アプリケーションインスタンス生成 |
| `routers.item`, `routers.user` | ルーター登録 |
| `models` | ORMモデルを `Base` に認識させるためのインポート |

**処理概要**

アプリケーションのエントリーポイント。`user` / `item` の各ルーターを `FastAPI` インスタンスに登録する。テーブル作成は Alembic マイグレーションで管理するため、`create_all()` は使用しない。

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

SQLAlchemy の非同期 `engine` / `async_session` / `Base` を生成・公開する。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出し、`async with` により終了後に確実にクローズする。データベースURLには非同期ドライバ（PostgreSQLの場合 `postgresql+asyncpg`）を使用する。

---

### [models/\_\_init\_\_.py](models/__init__.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `.user.User` | `User` モデルを再エクスポート |
| `.item.Item` | `Item` モデルを再エクスポート |

**処理概要**

`models` パッケージのエントリーポイント。`main.py` が `import models` した時点で全ORMモデルが `Base` のメタデータに登録される。

---

### [models/user.py](models/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.orm.Mapped` | カラム・リレーションの型アノテーション |
| `sqlalchemy.orm.mapped_column` | 型付きカラム定義（SQLAlchemy 2.0スタイル） |
| `sqlalchemy.orm.relationship` | Itemとの1対多リレーション定義 |
| `sqlalchemy.String` | 文字列型カラムの型指定 |
| `database.Base` | ORMモデルの基底クラス |

**処理概要**

`users` テーブルに対応するORMモデル `User` を定義する。SQLAlchemy 2.0スタイルの `Mapped` + `mapped_column` を使い、`id` / `name` / `email` の3カラムをPython型アノテーションで宣言する。`items: Mapped[list["Item"]]` により1人のUserが複数のItemを所有する1対多リレーションを構成し、`cascade="all, delete-orphan"` でUserを削除すると紐づくItemも連鎖削除される。

---

### [models/item.py](models/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.orm.Mapped` | カラム・リレーションの型アノテーション |
| `sqlalchemy.orm.mapped_column` | 型付きカラム定義（SQLAlchemy 2.0スタイル） |
| `sqlalchemy.orm.relationship` | Userへの多対1リレーション定義 |
| `sqlalchemy.String` | 文字列型カラムの型指定 |
| `sqlalchemy.ForeignKey` | `users.id` への外部キー定義 |
| `database.Base` | ORMモデルの基底クラス |

**処理概要**

`items` テーブルに対応するORMモデル `Item` を定義する。SQLAlchemy 2.0スタイルの `Mapped` + `mapped_column` を使い、`id` / `title` / `description` / `user_id` の4カラムをPython型アノテーションで宣言する。`user_id: Mapped[int]` は `ForeignKey("users.id")` で `users` テーブルを参照し、`owner: Mapped["User"]` により多対1の逆参照を構成する。

---

### [schemas/\_\_init\_\_.py](schemas/__init__.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `.user.UserCreate`, `.user.UserResponse` | Userスキーマを再エクスポート |
| `.item.ItemCreate`, `.item.ItemResponse` | Itemスキーマを再エクスポート |

**処理概要**

`schemas` パッケージのエントリーポイント。各スキーマを一元的に再エクスポートし、他モジュールから `from schemas import UserCreate` のように簡潔にインポートできるようにする。

---

### [schemas/user.py](schemas/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `pydantic.BaseModel` | スキーマ基底クラス |
| `pydantic.Field` | バリデーション制約の付与 |
| `pydantic.EmailStr` | メールアドレス形式バリデーション |
| `schemas.item.ItemResponse` | ネストしたItemレスポンスの型（末尾インポート・循環参照解決） |

**処理概要**

Userの入出力スキーマを定義する。`UserBase` で共通フィールド（`name`: 1〜50文字、`email`: メール形式）を宣言し、`UserCreate`（作成リクエスト）と `UserResponse`（レスポンス）に継承させる。`UserResponse` にはリレーション先の `items: list[ItemResponse]` を含み、`model_rebuild()` で循環参照を解決する。

---

### [schemas/item.py](schemas/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `pydantic.BaseModel` | スキーマ基底クラス |
| `pydantic.Field` | バリデーション制約の付与 |

**処理概要**

Itemの入出力スキーマを定義する。`ItemBase` で共通フィールド（`title`: 1〜100文字、`description`: 500文字以内・省略可、`user_id`: 1以上の整数）を宣言し、`ItemCreate`（作成リクエスト）と `ItemResponse`（レスポンス）に継承させる。

---

### [cruds/\_\_init\_\_.py](cruds/__init__.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `.user` | userモジュールをサブモジュールとして公開 |
| `.item` | itemモジュールをサブモジュールとして公開 |

**処理概要**

`cruds` パッケージのエントリーポイント。`from cruds import user` のように各crudsモジュールをまとめてインポートできるようにする。

---

### [cruds/user.py](cruds/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DB操作に使用するセッション型 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `models.user.User` | usersテーブルのORMモデル |
| `schemas.user.UserCreate` | 作成リクエストの入力スキーマ |

**処理概要**

`users` テーブルに対する非同期DB操作関数を提供する。`get_users()` は `await db.execute(select(User))` で全ユーザーを一覧取得し、`create_user()` はスキーマから `User` インスタンスを生成してDBに追加・`await db.commit()` でコミットする。

---

### [cruds/item.py](cruds/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DB操作に使用するセッション型 |
| `sqlalchemy.select` | SQLAlchemy 2.0スタイルのSELECT文生成 |
| `models.item.Item` | itemsテーブルのORMモデル |
| `schemas.item.ItemCreate` | 作成リクエストの入力スキーマ |

**処理概要**

`items` テーブルに対する非同期DB操作関数を提供する。`get_items()` は全アイテムを取得、`get_items_by_user()` は指定した `user_id` に紐づくアイテムのみをフィルタして取得、`create_item()` は新規アイテムをDBに追加する。すべての関数は `async def` で定義し、DB操作には `await` を使用する。

---

### [routers/user.py](routers/user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends` | DIコンテナ（DBセッション注入） |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `cruds.user` | usersテーブルのDB操作関数 |
| `schemas.user.UserCreate`, `UserResponse` | リクエスト・レスポンスのスキーマ |

**処理概要**

`/users` プレフィックスのエンドポイントを定義する。`GET /users` で全ユーザー一覧を返し、`POST /users` でユーザーを新規作成する。すべてのエンドポイントは `async def` で定義し、CRUD関数の呼び出しには `await` を使用する。レスポンスには所有する `items` のネストデータも含まれる。

---

### [routers/item.py](routers/item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.APIRouter` | ルーター定義 |
| `fastapi.Depends` | DIコンテナ（DBセッション注入） |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期DBセッション型 |
| `database.get_db` | 非同期DBセッション取得ジェネレータ |
| `cruds.item` | itemsテーブルのDB操作関数 |
| `schemas.item.ItemCreate`, `ItemResponse` | リクエスト・レスポンスのスキーマ |

**処理概要**

`/items` プレフィックスのエンドポイントを定義する。`GET /items` で全アイテム一覧、`GET /items/user/{user_id}` で特定ユーザーのアイテム一覧を返し、`POST /items` でアイテムを新規作成する。すべてのエンドポイントは `async def` で定義し、CRUD関数の呼び出しには `await` を使用する。

---

### [tests/test_user.py](tests/test_user.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.testclient.TestClient` | HTTPリクエストをシミュレートするテストクライアント |
| `main.app` | テスト対象のFastAPIアプリケーション |

**処理概要**

`/users` エンドポイントのpytestテストを定義する。`test_get_users()` はGETリクエストのステータスコード200とリスト形式レスポンスを検証し、`test_create_user()` はPOSTリクエストでユーザーを作成し `name` / `email` / `id` の各フィールドを検証する。`TestClient` を使用した同期テストパターンで実装する。

---

### [tests/test_item.py](tests/test_item.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.testclient.TestClient` | HTTPリクエストをシミュレートするテストクライアント |
| `main.app` | テスト対象のFastAPIアプリケーション |

**処理概要**

`/items` エンドポイントのpytestテストを定義する。`test_get_items()` はGETリクエストのステータスコード200とリスト形式レスポンスを検証し、`test_create_item()` はPOSTリクエストでアイテムを作成し `title` / `description` / `id` の各フィールドを検証する。`TestClient` を使用した同期テストパターンで実装する。
