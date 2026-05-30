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
└── tests/             # pytestテスト
    ├── test_user.py   # users エンドポイントのテスト
    └── test_item.py   # items エンドポイントのテスト
```

---

## エンドポイント一覧

### Users `/users`

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/users` | ユーザー一覧取得 |
| GET | `/users/paged?skip=0&limit=100` | ページネーション付き一覧取得 |
| GET | `/users/{user_id}` | ユーザー1件取得 |
| POST | `/users` | ユーザー作成 |
| PUT | `/users/{user_id}` | ユーザー全フィールド更新 |
| PATCH | `/users/{user_id}` | ユーザー部分更新 |
| DELETE | `/users/{user_id}` | ユーザー削除 |

### Items `/items`

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/items` | アイテム一覧取得 |
| GET | `/items/paged?skip=0&limit=100` | ページネーション付き一覧取得 |
| GET | `/items/{item_id}` | アイテム1件取得 |
| GET | `/items/user/{user_id}` | ユーザーに紐づくアイテム一覧取得 |
| POST | `/items` | アイテム作成 |
| PUT | `/items/{item_id}` | アイテム全フィールド更新 |
| PATCH | `/items/{item_id}` | アイテム部分更新 |
| DELETE | `/items/{item_id}` | アイテム削除 |

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

アプリケーションのエントリーポイント。`user` / `item` の各ルーターを `FastAPI` インスタンスに登録する。`lifespan` で起動時に `Base.metadata.create_all` を実行しテーブルを自動作成する。

---

### [config.py](config.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `pydantic_settings.BaseSettings` | 環境変数を型安全に管理するベースクラス |
| `pydantic_settings.SettingsConfigDict` | `.env` ファイル読み込み設定 |
| `functools.lru_cache` | `Settings` インスタンスをキャッシュし再生成を防ぐ |

**処理概要**

`BaseSettings` を継承した `Settings` クラスで環境変数（`secret_key`・`database_url`）を管理する。`get_settings()` に `@lru_cache` を付与し、アプリ全体で同一インスタンスを共有する。

---

### [database.py](database.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `sqlalchemy.ext.asyncio.create_async_engine` | 非同期DBエンジン生成 |
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッションクラス |
| `sqlalchemy.ext.asyncio.async_sessionmaker` | 非同期セッションファクトリ生成 |
| `sqlalchemy.orm.declarative_base` | ORMモデルの基底クラス生成 |
| `config.get_settings` | `database_url` の取得 |

**処理概要**

SQLAlchemy の非同期 `engine` / `AsyncSessionLocal` / `Base` を生成・公開する。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出す。

---

### [models/user.py](models/user.py)

**処理概要**

`users` テーブルに対応するORMモデル `User` を定義する。`id` / `name` / `email` の3カラムを持つ。`items: Mapped[list["Item"]]` により1対多リレーションを構成し、`cascade="all, delete-orphan"` でUser削除時に紐づくItemも連鎖削除される。

---

### [models/item.py](models/item.py)

**処理概要**

`items` テーブルに対応するORMモデル `Item` を定義する。`id` / `title` / `description` / `user_id` の4カラムを持つ。`user_id` は `ForeignKey("users.id")` で `users` テーブルを参照し、`owner: Mapped["User"]` により多対1の逆参照を構成する。

---

### [schemas/user.py](schemas/user.py)

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `UserBase` | `name`・`email` の共通フィールド定義 |
| `UserCreate` | POST リクエストボディ（UserBase をそのまま継承） |
| `UserUpdate` | PUT/PATCH リクエストボディ（全フィールド Optional） |
| `UserResponse` | レスポンス（`id`・`items` を追加） |

**処理概要**

`UserResponse` には `items: list[ItemResponse]` を含む。`ItemResponse` との循環参照を `model_rebuild()` で解決する。

---

### [schemas/item.py](schemas/item.py)

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `ItemBase` | `title`・`description`・`user_id` の共通フィールド定義 |
| `ItemCreate` | POST リクエストボディ（ItemBase をそのまま継承） |
| `ItemUpdate` | PUT/PATCH リクエストボディ（全フィールド Optional） |
| `ItemResponse` | レスポンス（`id` を追加） |

---

### [cruds/user.py](cruds/user.py)

**関数一覧**

| 関数 | 説明 |
|---|---|
| `get_users` | 全ユーザー取得 |
| `get_user` | id で1件取得 |
| `get_user_by_email` | email で1件取得 |
| `get_users_paged` | ページネーション付き取得 |
| `create_user` | ユーザー作成 |
| `update_user` | 全フィールド更新（PUT） |
| `patch_user` | 部分更新（PATCH）`exclude_unset=True` 使用 |
| `delete_user` | 削除（成功: `True` / 未存在: `False`） |

---

### [cruds/item.py](cruds/item.py)

**関数一覧**

| 関数 | 説明 |
|---|---|
| `get_items` | 全アイテム取得 |
| `get_item` | id で1件取得 |
| `get_items_by_user` | user_id で絞り込み取得 |
| `get_items_paged` | ページネーション付き取得 |
| `create_user_item` | ユーザーに紐づくアイテム作成 |
| `update_item` | 全フィールド更新（PUT） |
| `patch_item` | 部分更新（PATCH）`exclude_unset=True` 使用 |
| `delete_item` | 削除（成功: `True` / 未存在: `False`） |

---

### [routers/user.py](routers/user.py)

**エンドポイント一覧**

| メソッド | パス | crud関数 |
|---|---|---|
| GET | `/users` | `get_users` |
| GET | `/users/paged` | `get_users_paged` |
| GET | `/users/{user_id}` | `get_user` |
| POST | `/users` | `create_user` |
| PUT | `/users/{user_id}` | `update_user` |
| PATCH | `/users/{user_id}` | `patch_user` |
| DELETE | `/users/{user_id}` | `delete_user` |

未存在リソースへのアクセスは `HTTPException(status_code=404)` を返す。

---

### [routers/item.py](routers/item.py)

**エンドポイント一覧**

| メソッド | パス | crud関数 |
|---|---|---|
| GET | `/items` | `get_items` |
| GET | `/items/paged` | `get_items_paged` |
| GET | `/items/{item_id}` | `get_item` |
| GET | `/items/user/{user_id}` | `get_items_by_user` |
| POST | `/items` | `create_user_item` |
| PUT | `/items/{item_id}` | `update_item` |
| PATCH | `/items/{item_id}` | `patch_item` |
| DELETE | `/items/{item_id}` | `delete_item` |

未存在リソースへのアクセスは `HTTPException(status_code=404)` を返す。

---

## セットアップ

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

APIドキュメントは `http://localhost:8000/docs` で確認できます。

---

## テスト実行

```bash
pytest tests/
```
