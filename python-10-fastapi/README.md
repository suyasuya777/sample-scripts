# FastAPI 学習サンプル集

FastAPIの各機能を個別に学習できるサンプルプログラム集です。

## 📁 カテゴリ構成

| フォルダ | 内容 |
|---|---|
| [`01_basics_and_structure/`](#01_basics_and_structure) | 基礎・構造（プロジェクト構成・設定管理） |
| [`02_request_response/`](#02_request_response) | リクエスト・レスポンス（バリデーション・ページネーション・レスポンス設計） |
| [`03_auth_security/`](#03_auth_security) | 認証・セキュリティ（JWT・OAuth2・PBKDF2・RBAC） |
| [`04_database/`](#04_database) | DB連携（SQLAlchemy・リレーション・Alembic） |
| [`05_async_performance/`](#05_async_performance) | 非同期・パフォーマンス（async・BackgroundTasks・Redis） |
| [`06_error_handling/`](#06_error_handling) | エラーハンドリング（カスタム例外・HTTPException） |
| [`07_middleware/`](#07_middleware) | ミドルウェア・共通処理（CORS・ロギング・処理時間計測） |
| [`08_testing/`](#08_testing) | テスト（pytest・フィクスチャ・DI差し替え・DBモック） |
| [`09_deploy/`](#09_deploy) | 運用・デプロイ（Docker・ヘルスチェック・S3・CloudWatch） |

## 🚀 セットアップ

```bash
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

## 📂 Pythonソース一覧

### <a id="01_basics_and_structure"></a>01_basics_and_structure/（基礎・構造）

```
01_basics_and_structure/
├── project_structure/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── routers/
│   │   ├── item.py
│   │   └── user.py
│   ├── cruds/
│   │   ├── item.py
│   │   └── user.py
│   ├── models/
│   │   ├── item.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── item.py
│   │   └── user.py
│   └── tests/
│       ├── test_item.py
│       └── test_user.py
└── pydantic_settings_config/
    └── pydantic_settings_config.py
```

#### [pydantic_settings_config.py](01_basics_and_structure/pydantic_settings_config/pydantic_settings_config.py)

| import モジュール | 用途 |
|---|---|
| `os` | 環境変数取得 |
| `functools.lru_cache` | 設定インスタンスのキャッシュ |
| `pydantic.Field` | バリデーション付きフィールド定義 |
| `pydantic_settings.BaseSettings`, `pydantic_settings.SettingsConfigDict` | 環境変数設定クラス |

`APP_ENV` 変数で `DevelopmentConfig` / `ProductionConfig` / `TestingConfig` を切り替えるパターンと `lru_cache` によるインスタンスキャッシュを解説。project_structure の単一クラス構成に対して、環境別クラス切り替えの発展パターン。

---

### <a id="02_request_response"></a>02_request_response/（リクエスト・レスポンス）

```
02_request_response/
├── file_upload/
│   └── file_upload.py
├── pagination/
│   └── pagination.py
├── path_query_header_params/
│   └── path_query_header_params.py
├── response_model_filtering/
│   └── response_model_filtering.py
├── unified_response_format/
│   └── unified_response_format.py
└── validation/
    └── validation.py
```

#### [file_upload.py](02_request_response/file_upload/file_upload.py)

| import モジュール | 用途 |
|---|---|
| `os` | ディレクトリ作成 |
| `typing.List` | 型ヒント |
| `fastapi.FastAPI`, `fastapi.UploadFile`, `fastapi.File`, `fastapi.Form`, `fastapi.HTTPException` | ファイルアップロード・フォーム受信 |
| `fastapi.responses.JSONResponse` | JSONレスポンス生成 |

`UploadFile` / `File` / `Form` を使ったファイルアップロード。単一・複数ファイル対応、MIMEタイプ・サイズバリデーション、`/tmp` への保存処理を実装。

---

#### [pagination.py](02_request_response/pagination/pagination.py)

| import モジュール | 用途 |
|---|---|
| `typing.List`, `typing.Optional` | 型ヒント |
| `fastapi.FastAPI`, `fastapi.Query`, `fastapi.Depends` | クエリパラメーター・DI |
| `pydantic.BaseModel` | レスポンススキーマ |

offset/limit方式とカーソル方式の2種類のページネーション実装。`Depends` を使った `PaginationParams` クラスによるページネーションパラメーターの共通化パターンも解説。project_structure の単純な skip/limit に対して、カーソル方式と共通化パターンが発展内容。

---

#### [path_query_header_params.py](02_request_response/path_query_header_params/path_query_header_params.py)

| import モジュール | 用途 |
|---|---|
| `typing.Optional` | 省略可能型 |
| `fastapi.FastAPI`, `fastapi.Path`, `fastapi.Query`, `fastapi.Header`, `fastapi.HTTPException` | パス・クエリ・ヘッダーパラメーター取得 |

`Path` / `Query` / `Header` によるリクエストパラメーター受け取りとバリデーション（`gt` / `ge` / `max_length` 等）を解説。

---

#### [response_model_filtering.py](02_request_response/response_model_filtering/response_model_filtering.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `pydantic.BaseModel`, `pydantic.ConfigDict` | スキーマ定義 |
| `typing.Optional` | 省略可能型 |

`response_model` / `response_model_exclude` / `response_model_include` によるレスポンスフィールドの絞り込み。パスワード・ソルト等の機密フィールドをJSONレスポンスから除外するセキュリティ設計パターンを示す。

---

#### [unified_response_format.py](02_request_response/unified_response_format/unified_response_format.py)

| import モジュール | 用途 |
|---|---|
| `typing.Generic`, `typing.TypeVar`, `typing.Optional`, `typing.List` | ジェネリック型定義 |
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `pydantic.BaseModel` | レスポンススキーマ基底 |

`Generic[T]` を使った全エンドポイント共通のAPIレスポンスフォーマット（`status` / `message` / `data`）を実装。成功・失敗・一覧レスポンスを同一構造で返すパターン。

---

#### [validation.py](02_request_response/validation/validation.py)

| import モジュール | 用途 |
|---|---|
| `typing.Optional` | 省略可能型 |
| `pydantic.BaseModel`, `pydantic.Field`, `pydantic.field_validator`, `pydantic.model_validator` | バリデーション定義 |

`Field` 制約（`min_length` / `max_length` / `pattern` / `ge` / `le`）、`@field_validator` によるカスタム単フィールドバリデーション、`@model_validator` による複数フィールドまたぎバリデーション（パスワード一致確認等）を解説。

---

### <a id="03_auth_security"></a>03_auth_security/（認証・セキュリティ）

```
03_auth_security/
├── api_key_authentication/
│   └── api_key_authentication.py
├── jwt_authentication/
│   └── jwt_authentication.py
├── oauth2_password_bearer/
│   └── oauth2_password_bearer.py
├── password_hashing_with_pbkdf2/
│   └── password_hashing_with_pbkdf2.py
└── role_based_access_control/
    └── role_based_access_control.py
```

#### [api_key_authentication.py](03_auth_security/api_key_authentication/api_key_authentication.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.Security`, `fastapi.HTTPException` | セキュリティ依存注入・例外 |
| `fastapi.security.APIKeyHeader`, `fastapi.security.APIKeyQuery` | ヘッダー・クエリからのAPIキー取得 |

リクエストヘッダー（`X-API-Key`）またはクエリパラメーターからAPIキーを取得して検証する認証方式。バックエンド間通信や外部サービス連携向け。

---

#### [jwt_authentication.py](03_auth_security/jwt_authentication/jwt_authentication.py)

| import モジュール | 用途 |
|---|---|
| `datetime.datetime`, `datetime.timedelta` | トークン有効期限計算 |
| `fastapi.FastAPI`, `fastapi.HTTPException` | FastAPIアプリ・HTTP例外 |
| `jose.jwt`, `jose.JWTError` | JWT生成・検証（python-jose） |
| `pydantic.BaseModel` | リクエストスキーマ |

`python-jose` を使ったJWTトークンの生成（`jwt.encode`）・検証（`jwt.decode`）。`exp` クレームによる有効期限管理と `JWTError` のハンドリングを解説。

---

#### [oauth2_password_bearer.py](03_auth_security/oauth2_password_bearer/oauth2_password_bearer.py)

| import モジュール | 用途 |
|---|---|
| `datetime.datetime`, `datetime.timedelta` | トークン有効期限計算 |
| `typing.Annotated` | 型ヒントメタ情報付与 |
| `fastapi.FastAPI`, `fastapi.Depends`, `fastapi.HTTPException` | DI・例外 |
| `fastapi.security.OAuth2PasswordBearer`, `fastapi.security.OAuth2PasswordRequestForm` | OAuth2トークン抽出・ログインフォーム |
| `jose.jwt`, `jose.JWTError` | JWT処理 |
| `pydantic.BaseModel` | レスポンススキーマ |

`OAuth2PasswordBearer` によるBearerトークンの自動抽出と `OAuth2PasswordRequestForm` を使ったログインエンドポイント実装。Swagger UIの「Authorize」ボタン連携を含む完全な認証フロー。

---

#### [password_hashing_with_pbkdf2.py](03_auth_security/password_hashing_with_pbkdf2/password_hashing_with_pbkdf2.py)

| import モジュール | 用途 |
|---|---|
| `hashlib` | PBKDF2-HMAC-SHA256ハッシュ生成 |
| `base64` | バイト列のBase64エンコード |
| `os` | 暗号論的乱数生成（ソルト） |

`os.urandom(32)` によるランダムソルト生成と `hashlib.pbkdf2_hmac` を使ったパスワードのハッシュ化・検証。サードパーティライブラリなしで標準ライブラリのみで実装。

---

#### [role_based_access_control.py](03_auth_security/role_based_access_control/role_based_access_control.py)

| import モジュール | 用途 |
|---|---|
| `datetime.datetime`, `datetime.timedelta` | トークン有効期限 |
| `typing.Annotated` | 型ヒントメタ情報付与 |
| `fastapi.FastAPI`, `fastapi.Depends`, `fastapi.HTTPException` | DI・例外 |
| `fastapi.security.OAuth2PasswordBearer` | Bearerトークン取得 |
| `jose.jwt`, `jose.JWTError` | JWT処理 |
| `enum.Enum` | ロール列挙型定義 |

JWTペイロードに `role` フィールドを含め、`Depends` で役割チェック関数を注入してエンドポイントを保護するRBACパターン。`admin` / `user` / `guest` の3ロール制御を例示。

---

### <a id="04_database"></a>04_database/（DB連携）

```
04_database/
├── migration_with_alembic/
│   └── migration_with_alembic.py
└── sqlalchemy_models_and_relationships/
    └── sqlalchemy_models_and_relationships.py
```

#### [migration_with_alembic.py](04_database/migration_with_alembic/migration_with_alembic.py)

Alembicによるマイグレーション管理の学習リファレンス（実行コードなし）。`alembic init` → `env.py` 設定 → `alembic revision --autogenerate` → `alembic upgrade head` の手順と `down_revision` チェーンによるバージョン管理を解説するドキュメント兼コードサンプル。project_structure の `create_all` に対して、本番運用向けのマイグレーション管理が発展内容。

---

#### [sqlalchemy_models_and_relationships.py](04_database/sqlalchemy_models_and_relationships/sqlalchemy_models_and_relationships.py)

| import モジュール | 用途 |
|---|---|
| `datetime.datetime` | 日時カラム |
| `enum.Enum` | Python列挙型 |
| `sqlalchemy.Column`, `sqlalchemy.Integer`, `sqlalchemy.String`, `sqlalchemy.DateTime`, `sqlalchemy.ForeignKey` | カラム型・外部キー |
| `sqlalchemy.Enum` | SQLAlchemy列挙型カラム |
| `sqlalchemy.orm.relationship`, `sqlalchemy.orm.declarative_base` | リレーション・ベースクラス |

project_structure のシンプルなモデル定義に対して、`Enum` 型カラム・`created_at`/`updated_at` 自動設定・`ondelete=CASCADE` の詳細解説が発展内容。

---

### <a id="05_async_performance"></a>05_async_performance/（非同期・パフォーマンス）

```
05_async_performance/
├── async_endpoint/
│   └── async_endpoint.py
├── background_tasks/
│   └── background_tasks.py
├── external_api_call_with_httpx/
│   └── external_api_call_with_httpx.py
├── rate_limiting/
│   └── rate_limiting.py
└── redis_cache/
    └── redis_cache.py
```

#### [async_endpoint.py](05_async_performance/async_endpoint/async_endpoint.py)

| import モジュール | 用途 |
|---|---|
| `asyncio` | 非同期スリープ・イベントループ |
| `time` | 同期処理時間計測 |
| `fastapi.FastAPI` | FastAPIアプリ本体 |

`async def`（非同期）と `def`（同期・スレッドプール）エンドポイントの違いを `asyncio.sleep` と `time.sleep` で比較。I/O待ち中の並行処理の挙動を解説。

---

#### [background_tasks.py](05_async_performance/background_tasks/background_tasks.py)

| import モジュール | 用途 |
|---|---|
| `time` | 重い処理のシミュレーション |
| `fastapi.FastAPI`, `fastapi.BackgroundTasks` | FastAPIアプリ・バックグラウンドタスク |

`BackgroundTasks.add_task()` を使ったレスポンス返却後の非同期処理実行。メール送信・ログ記録・通知など、レスポンスをブロックしたくない処理の実装パターン。

---

#### [external_api_call_with_httpx.py](05_async_performance/external_api_call_with_httpx/external_api_call_with_httpx.py)

| import モジュール | 用途 |
|---|---|
| `httpx` | 非同期HTTPクライアント |
| `fastapi.FastAPI`, `fastapi.HTTPException` | FastAPIアプリ・例外 |

`httpx.AsyncClient` を使った外部APIへの非同期HTTP呼び出し。`connect` / `read` / `write` の個別タイムアウト設定、リトライ処理、コンテキストマネージャーによるリソース管理を実装。

---

#### [rate_limiting.py](05_async_performance/rate_limiting/rate_limiting.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.Request`, `fastapi.HTTPException` | FastAPIアプリ・リクエスト・例外 |
| `fastapi.responses.JSONResponse` | JSONレスポンス |
| `time` | タイムスタンプ取得 |
| `collections.defaultdict` | IPごとのカウンター管理 |

`defaultdict` を使ったインメモリレートリミット実装例と `slowapi` ライブラリ使用時のコメントコード。IPベースのリクエスト頻度制限とRedisバックエンドによる分散対応の解説。

---

#### [redis_cache.py](05_async_performance/redis_cache/redis_cache.py)

| import モジュール | 用途 |
|---|---|
| `json` | オブジェクトのJSON直列化 |
| `typing.Optional` | 型ヒント |
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `redis.asyncio` | 非同期Redisクライアント（`aioredis`） |

`redis.asyncio` を使ったCache-Asideパターンの実装。`SET` / `GET` / TTLによるキャッシュ保存・取得・有効期限管理とJSON直列化によるオブジェクトキャッシュを解説。

---

### <a id="06_error_handling"></a>06_error_handling/（エラーハンドリング）

```
06_error_handling/
├── custom_exception_handler/
│   └── custom_exception_handler.py
├── http_exception_usage/
│   └── http_exception_usage.py
└── validation_error_response_format/
    └── validation_error_response_format.py
```

#### [custom_exception_handler.py](06_error_handling/custom_exception_handler/custom_exception_handler.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |
| `fastapi.responses.JSONResponse` | JSONレスポンス生成 |

`@app.exception_handler()` でアプリ固有の例外クラス（`AppException` / `ItemNotFoundException`）を定義・キャッチし、全エラーを統一フォーマットのJSONで返すパターン。

---

#### [http_exception_usage.py](06_error_handling/http_exception_usage/http_exception_usage.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.HTTPException`, `fastapi.Path` | FastAPIアプリ・HTTP例外・パスパラメーター |
| `starlette.status` | HTTPステータスコード定数 |

FastAPI標準 `HTTPException` の使い方。`status_code` / `detail` / `headers` の設定と `starlette.status` のステータスコード定数（`HTTP_404_NOT_FOUND` 等）の活用。

---

#### [validation_error_response_format.py](06_error_handling/validation_error_response_format/validation_error_response_format.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |
| `fastapi.exceptions.RequestValidationError` | Pydanticバリデーション失敗例外 |
| `fastapi.responses.JSONResponse` | JSONレスポンス生成 |
| `pydantic.BaseModel`, `pydantic.Field` | スキーマ定義 |

`RequestValidationError` ハンドラーをカスタマイズして、フィールド名・入力値・エラーメッセージを分かりやすい構造のJSONで返すバリデーションエラーレスポンスの整形パターン。

---

### <a id="07_middleware"></a>07_middleware/（ミドルウェア）

```
07_middleware/
├── cors_middleware/
│   └── cors_middleware.py
├── latency_measurement_middleware/
│   └── latency_measurement_middleware.py
├── request_logging_middleware/
│   └── request_logging_middleware.py
└── structured_logging/
    └── structured_logging.py
```

#### [cors_middleware.py](07_middleware/cors_middleware/cors_middleware.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `fastapi.middleware.cors.CORSMiddleware` | CORSミドルウェア |

`CORSMiddleware` の設定。`allow_origins` / `allow_methods` / `allow_headers` / `allow_credentials` の設定と、`"*"` と `allow_credentials=True` の組み合わせ時の注意点を解説。開発環境・本番環境別の設定例を含む。

---

#### [latency_measurement_middleware.py](07_middleware/latency_measurement_middleware/latency_measurement_middleware.py)

| import モジュール | 用途 |
|---|---|
| `time` | リクエスト処理時間計測 |
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |

`@app.middleware("http")` で全リクエストの処理時間を計測し `X-Process-Time` レスポンスヘッダーに付与するパターン。

---

#### [request_logging_middleware.py](07_middleware/request_logging_middleware/request_logging_middleware.py)

| import モジュール | 用途 |
|---|---|
| `time` | 処理時間計測 |
| `logging` | ログ出力 |
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |

`@app.middleware("http")` で全リクエストをインターセプトし、HTTPメソッド・パス・クライアントIP・処理時間を `logging` でログ記録するミドルウェア。

---

#### [structured_logging.py](07_middleware/structured_logging/structured_logging.py)

| import モジュール | 用途 |
|---|---|
| `logging` | ログ出力基盤 |
| `json` | JSON形式フォーマット |
| `datetime.datetime` | タイムスタンプ生成 |
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |

`logging.Formatter` を継承したカスタム `JsonFormatter` でログをJSON形式で出力する実装。`timestamp` / `level` / `message` / `module` 等のフィールドを構造化し、AWS CloudWatch Logs Insightsでの検索・集計に対応。

---

### <a id="08_testing"></a>08_testing/（テスト）

```
08_testing/
├── dependency_injection_override/
│   └── dependency_injection_override.py
├── integration_test_with_db_mock/
│   └── integration_test_with_db_mock.py
└── pytest_fixtures_and_conftest/
    └── pytest_fixtures_and_conftest.py
```

#### [dependency_injection_override.py](08_testing/dependency_injection_override/dependency_injection_override.py)

| import モジュール | 用途 |
|---|---|
| `pytest` | テストフレームワーク |
| `fastapi.FastAPI`, `fastapi.Depends` | FastAPIアプリ・DI |
| `fastapi.testclient.TestClient` | テスト用HTTPクライアント |

`app.dependency_overrides[orig_func] = mock_func` でDB接続・認証・外部APIをテスト用モックに差し替えるパターン。テスト後の `dependency_overrides.clear()` によるクリーンアップも含む。

---

#### [integration_test_with_db_mock.py](08_testing/integration_test_with_db_mock/integration_test_with_db_mock.py)

| import モジュール | 用途 |
|---|---|
| `pytest` | テストフレームワーク |
| `fastapi.FastAPI`, `fastapi.Depends`, `fastapi.HTTPException` | FastAPIアプリ・DI・例外 |
| `fastapi.testclient.TestClient` | テスト用HTTPクライアント |
| `sqlalchemy.create_engine`, `sqlalchemy.Column`, `sqlalchemy.Integer`, `sqlalchemy.String` | テスト用DB・ORM定義 |
| `sqlalchemy.orm.sessionmaker`, `sqlalchemy.orm.declarative_base`, `sqlalchemy.orm.Session` | セッション管理 |
| `sqlalchemy.pool.StaticPool` | SQLiteインメモリ接続維持プール |

`StaticPool` を使ったSQLiteインメモリDBでの統合テスト。テスト前のフィクスチャデータ投入と、各テストが独立したDBセッションを使用することでのテスト間の独立性確保。

---

#### [pytest_fixtures_and_conftest.py](08_testing/pytest_fixtures_and_conftest/pytest_fixtures_and_conftest.py)

`@pytest.fixture()` の `scope`（`function` / `module` / `session`）によるライフサイクル制御、`yield` フィクスチャのsetup/teardownパターン、フィクスチャ間の依存関係、`conftest.py` で複数テストファイルにフィクスチャを共有する設計を解説するリファレンスサンプル。

---

### <a id="09_deploy"></a>09_deploy/（運用・デプロイ）

```
09_deploy/
├── cloudwatch_logging/
│   └── cloudwatch_logging.py
├── health_check_endpoint/
│   └── health_check_endpoint.py
├── openapi_customization/
│   └── openapi_customization.py
├── s3_file_upload/
│   └── s3_file_upload.py
└── startup_shutdown_events/
    └── startup_shutdown_events.py
```

#### [cloudwatch_logging.py](09_deploy/cloudwatch_logging/cloudwatch_logging.py)

| import モジュール | 用途 |
|---|---|
| `logging` | ログ基盤 |
| `json` | JSON形式フォーマット |
| `datetime.datetime` | タイムスタンプ生成 |
| `os` | 環境変数取得 |
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |
| `watchtower`（要インストール） | CloudWatch Logs向けハンドラー |

`watchtower` ライブラリとJSON形式ログを組み合わせたAWS CloudWatch Logsへのログ送信実装。必要なIAMポリシー（`logs:CreateLogGroup` / `logs:PutLogEvents` 等）の解説も含む。

---

#### [health_check_endpoint.py](09_deploy/health_check_endpoint/health_check_endpoint.py)

| import モジュール | 用途 |
|---|---|
| `time` | 起動時刻・稼働時間計算 |
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `fastapi.responses.JSONResponse` | JSONレスポンス生成 |

ECS/K8s向けの `/health`（死活監視）・`/ready`（DB接続確認）・`/live`（プロセス生存確認）の3エンドポイント実装。ALBヘルスチェックに最適なレスポンス設計。

---

#### [openapi_customization.py](09_deploy/openapi_customization/openapi_customization.py)

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `fastapi.openapi.utils.get_openapi` | OpenAPIスキーマのカスタム生成 |

`FastAPI()` のパラメーター（`title` / `description` / `version` / `docs_url`）、タグメタデータ、セキュリティスキーマ、レスポンス例追加によるSwagger UIのカスタマイズ。

---

#### [s3_file_upload.py](09_deploy/s3_file_upload/s3_file_upload.py)

| import モジュール | 用途 |
|---|---|
| `os` | 環境変数取得 |
| `boto3` | AWS SDK for Python |
| `fastapi.FastAPI`, `fastapi.UploadFile`, `fastapi.File`, `fastapi.HTTPException` | ファイルアップロード |
| `botocore.exceptions.ClientError` | AWS APIエラー |

`boto3` を使ったS3へのファイルアップロード。サーバー経由の `put_object` とクライアント直接アップロード用のPresigned URL生成の2パターンを実装。

---

#### [startup_shutdown_events.py](09_deploy/startup_shutdown_events/startup_shutdown_events.py)

| import モジュール | 用途 |
|---|---|
| `contextlib.asynccontextmanager` | 非同期コンテキストマネージャー |
| `fastapi.FastAPI` | FastAPIアプリ本体 |

FastAPI 0.93+ 推奨の `lifespan` パターン（`@asynccontextmanager`）と旧 `@app.on_event` パターンの比較。DB接続プール初期化・Redis接続・外部サービス疎通確認・クリーンアップの起動・終了イベント管理を解説。

---

## 🔗 関連ドキュメント

- [project_structure 詳細 README](01_basics_and_structure/project_structure/README.md)
