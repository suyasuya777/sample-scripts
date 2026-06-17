# 🗂️ ユーザ・アイテム管理アプリ（FastAPI + SQLite）

FastAPIの推奨フォルダ構成サンプルです。

```
python-11-fastapi-user-item-app/
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

### 📄 [main.py](main.py)

**インポート**

| モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | アプリケーションインスタンス生成 |
| `routers.item`, `routers.user` | ルーター登録 |
| `database.Base`, `database.engine` | テーブル自動作成に使用 |

**処理概要**

アプリケーションのエントリーポイント。`user` / `item` の各ルーターを `FastAPI` インスタンスに登録する。`lifespan` で起動時に `Base.metadata.create_all` を実行しテーブルを自動作成する。CORS設定で `http://127.0.0.1:5500` からのアクセスを許可する。

---

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
| `sqlalchemy.ext.asyncio.AsyncSession` | 非同期セッションクラス |
| `sqlalchemy.ext.asyncio.async_sessionmaker` | 非同期セッションファクトリ生成 |
| `sqlalchemy.orm.DeclarativeBase` | ORMモデルの基底クラス |
| `config.get_settings` | `database_url` の取得 |

**処理概要**

SQLAlchemy の非同期 `engine` / `async_session` / `Base` を生成・公開する。`get_db()` は非同期ジェネレータ関数で、FastAPI の `Depends` に渡すことでリクエストごとに非同期DBセッションを払い出す。

---

### 📄 [models/user.py](models/user.py)

**処理概要**

`users` テーブルに対応するORMモデル `User` を定義する。`id` / `name` / `email` の3カラムを持つ。`items: Mapped[list["Item"]]` により1対多リレーションを構成し、`cascade="all, delete-orphan"` でUser削除時に紐づくItemも連鎖削除される。

---

### 📄 [models/item.py](models/item.py)

**処理概要**

`items` テーブルに対応するORMモデル `Item` を定義する。`id` / `title` / `description` / `user_id` の4カラムを持つ。`user_id` は `ForeignKey("users.id")` で `users` テーブルを参照し、`owner: Mapped["User"]` により多対1の逆参照を構成する。

---

### 📄 [schemas/user.py](schemas/user.py)

**型エイリアス一覧**

| エイリアス | 型 | バリデーション |
|---|---|---|
| `UserName` | `str` | `min_length=1`, `max_length=50` |
| `UserEmail` | `EmailStr` | `max_length=50` |
| `UserOptionalName` | `str \| None` | `min_length=1`, `max_length=50` |
| `UserOptionalEmail` | `EmailStr \| None` | `max_length=50` |

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `UserBase` | `name`・`email` の共通フィールド定義 |
| `UserCreate` | POST リクエストボディ（UserBase をそのまま継承） |
| `UserUpdate` | PATCH リクエストボディ（全フィールド Optional） |
| `UserResponse` | レスポンス（`id`・`items` を追加） |

**処理概要**

`UserResponse` には `items: list[ItemResponse]` を含む。フィールドは `Annotated` + `Field` による型エイリアスで定義し、バリデーションルールを一元管理する。

---

### 📄 [schemas/item.py](schemas/item.py)

**型エイリアス一覧**

| エイリアス | 型 | バリデーション |
|---|---|---|
| `ItemTitle` | `str` | `min_length=1`, `max_length=50` |
| `ItemDescription` | `str \| None` | `max_length=255` |
| `ItemUserId` | `int` | `gt=0` |
| `ItemOptionalTitle` | `str \| None` | `max_length=50` |
| `ItemOptionalDescription` | `str \| None` | `max_length=255` |
| `ItemOptionalUserId` | `int \| None` | `gt=0` |

**スキーマ一覧**

| クラス | 用途 |
|---|---|
| `ItemBase` | `title`・`description`・`user_id` の共通フィールド定義 |
| `ItemCreate` | POST リクエストボディ（ItemBase をそのまま継承） |
| `ItemUpdate` | PATCH リクエストボディ（全フィールド Optional） |
| `ItemResponse` | レスポンス（`id` を追加） |

---

### 📄 [cruds/user.py](cruds/user.py)

**関数一覧**

| 関数 | 説明 |
|---|---|
| `get_users` | 全ユーザー取得（items を `selectinload`） |
| `get_user` | id で1件取得（items を `selectinload`） |
| `get_users_paged` | ページネーション付き取得（items を `selectinload`） |
| `create_user` | ユーザー作成 |
| `patch_user` | 部分更新（`exclude_unset=True` 使用） |
| `delete_user` | 削除（成功: `True` / 未存在: `False`） |

---

### 📄 [cruds/item.py](cruds/item.py)

**関数一覧**

| 関数 | 説明 |
|---|---|
| `get_items` | 全アイテム取得 |
| `get_item` | id で1件取得 |
| `get_items_by_user` | user_id で絞り込み取得 |
| `get_items_paged` | ページネーション付き取得 |
| `create_user_item` | ユーザーに紐づくアイテム作成 |
| `patch_item` | 部分更新（`exclude_unset=True` 使用） |
| `delete_item` | 削除（成功: `True` / 未存在: `False`） |

---

### 📄 [routers/user.py](routers/user.py)

**エンドポイント一覧**

| メソッド | パス | crud関数 |
|---|---|---|
| GET | `/users` | `get_users` |
| GET | `/users/paged` | `get_users_paged` |
| GET | `/users/{user_id}` | `get_user` |
| POST | `/users` | `create_user` |
| PATCH | `/users/{user_id}` | `patch_user` |
| DELETE | `/users/{user_id}` | `delete_user` |

未存在リソースへのアクセスは `HTTPException(status_code=404)` を返す。`DBSession` は `Annotated[AsyncSession, Depends(get_db)]` として定義し、各ハンドラで共有する。

---

### 📄 [routers/item.py](routers/item.py)

**エンドポイント一覧**

| メソッド | パス | crud関数 |
|---|---|---|
| GET | `/items` | `get_items` |
| GET | `/items/paged` | `get_items_paged` |
| GET | `/items/user/{user_id}` | `get_items_by_user` |
| GET | `/items/{item_id}` | `get_item` |
| POST | `/items` | `create_user_item` |
| PATCH | `/items/{item_id}` | `patch_item` |
| DELETE | `/items/{item_id}` | `delete_item` |

未存在リソースへのアクセスは `HTTPException(status_code=404)` を返す。ルート定義順は `/paged` → `/user/{user_id}` → `/{item_id}` の順で、パスパラメータとの競合を回避している。

---

### 📄 [frontapp/](frontapp/)

ブラウザから直接APIを操作できる管理UIです。

| ファイル | 説明 |
|---|---|
| `index.html` | Users / Items タブ切り替え、ページネーション、モーダルによるCRUD操作 |
| `app.js` | API呼び出しロジック（fetch、エンドポイント定義、ステータス表示） |
| `styles.css` | スタイル定義 |

Live Server 等で `index.html` を開き、BASE URL に `http://127.0.0.1:8000` を設定して使用する。
