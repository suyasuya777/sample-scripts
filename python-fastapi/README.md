# FastAPI サンプルコード一覧

## 基礎・構造 `basics_and_structure`

- **[project_structure.py](basics_and_structure/project_structure.py)** - プロジェクト構成（ディレクトリ構造・`main.py`）
  - `app/`配下にrouters・models・schemasを分割配置する推奨ディレクトリ構成と、アプリ起動エントリポイントの書き方

- **[router_splitting.py](basics_and_structure/router_splitting.py)** - ルーター分割（`APIRouter` によるエンドポイント整理）
  - 機能ごとに`APIRouter`を定義して`main.py`で`include_router`により統合する、スケーラブルなルーティング構成

- **[environment_variable_management.py](basics_and_structure/environment_variable_management.py)** - 環境変数管理（`pydantic-settings` / `.env`）
  - `BaseSettings`を使って`.env`ファイルや環境変数を型安全に読み込み、設定値をアプリ全体で共有する方法

- **[multi_env_config.py](basics_and_structure/multi_env_config.py)** - 複数環境の設定管理（dev/stg/prod）
  - `APP_ENV`などの変数で環境を切り替え、`.env.dev`/`.env.stg`/`.env.prod`を使い分ける設定切替パターン

---

## リクエスト・レスポンス `request_and_response`

- **[pydantic_model_definition.py](request_and_response/pydantic_model_definition.py)** - Pydanticモデル定義（RequestBody / ResponseModel）
  - リクエストボディの受け取りとレスポンス返却に使うPydanticモデルの基本定義と、`response_model`指定による出力フィールドの絞り込み

- **[path_query_header_params.py](request_and_response/path_query_header_params.py)** - パスパラメータ・クエリパラメータ・ヘッダー取得
  - `{id}`形式のパスパラメータ、`?page=1`形式のクエリパラメータ、`Header()`によるHTTPヘッダー値の取得方法

- **[validation.py](request_and_response/validation.py)** - バリデーション（Field / validator / カスタムバリデーター）
  - `Field(ge=0, max_length=100)`による宣言的バリデーションと、`@validator`を使った複雑な条件チェックの実装

- **[unified_response_format.py](request_and_response/unified_response_format.py)** - レスポンスの統一フォーマット（共通レスポンスモデル）
  - `{"status": "ok", "data": ..., "message": ...}`のような共通ラッパーモデルを定義してAPIレスポンスの形式を統一する

- **[pagination.py](request_and_response/pagination.py)** - ページネーション実装
  - `skip`/`limit`クエリパラメータによるオフセットページネーションと、総件数・現在ページを含むレスポンス構造の実装

- **[file_upload.py](request_and_response/file_upload.py)** - ファイルアップロード（フォーム・CSV対応）
  - `UploadFile`と`Form`を使ったマルチパートリクエストの処理と、CSVファイルの読み取り・バリデーション

---

## 認証・セキュリティ `authentication_and_security`

- **[jwt_authentication.py](authentication_and_security/jwt_authentication.py)** - JWT認証（Bearer Token / `python-jose`）
  - `python-jose`でJWTを発行・検証し、`Authorization: Bearer <token>`ヘッダーからユーザーを識別する認証フロー

- **[auth_middleware_with_depends.py](authentication_and_security/auth_middleware_with_depends.py)** - 依存性注入による認証ミドルウェア（`Depends`）
  - `Depends(get_current_user)`をエンドポイントに注入することで、認証チェックをルート間で再利用する設計パターン

- **[api_key_authentication.py](authentication_and_security/api_key_authentication.py)** - APIキー認証
  - `X-API-Key`ヘッダーやクエリパラメータでAPIキーを受け取り、DBや環境変数と照合してアクセスを制御する実装

- **[role_based_access_control.py](authentication_and_security/role_based_access_control.py)** - ロールベースアクセス制御（RBAC）
  - JWTペイロードにロール情報を持たせ、`admin`/`user`などの権限に応じてエンドポイントへのアクセスを制限する

---

## DB連携 `database_integration`

- **[sqlalchemy_session_management.py](database_integration/sqlalchemy_session_management.py)** - SQLAlchemy + セッション管理（`Depends` でDB注入）
  - `SessionLocal`をジェネレータ関数でラップし、`Depends(get_db)`でエンドポイントにDBセッションを注入してリクエスト単位で自動クローズ

- **[crud_class_pattern.py](database_integration/crud_class_pattern.py)** - CRUDクラスの実装パターン
  - `CRUDBase`クラスに`create`/`read`/`update`/`delete`を集約し、モデルごとに継承して再利用可能なDB操作層を構築

- **[migration_with_alembic.py](database_integration/migration_with_alembic.py)** - マイグレーション（Alembic連携）
  - `alembic init`によるセットアップからSQLAlchemyモデルとの連携、`alembic revision --autogenerate`でのマイグレーションファイル自動生成

- **[async_sqlalchemy.py](database_integration/async_sqlalchemy.py)** - 非同期SQLAlchemy（`asyncpg`）
  - `create_async_engine`と`AsyncSession`を使い、`asyncpg`ドライバーでPostgreSQLへ非同期接続してクエリを実行する

---

## 非同期・パフォーマンス `async_and_performance`

- **[async_endpoint.py](async_and_performance/async_endpoint.py)** - 非同期エンドポイント（`async def`）
  - `async def`によるエンドポイント定義と、`await`を用いたI/O待機処理でスループットを向上させる基本パターン

- **[background_tasks.py](async_and_performance/background_tasks.py)** - バックグラウンドタスク（`BackgroundTasks`）
  - `BackgroundTasks.add_task()`でメール送信やログ書き込みなどの処理をレスポンス返却後に非同期実行する方法

- **[external_api_call_with_httpx.py](async_and_performance/external_api_call_with_httpx.py)** - 外部API呼び出し（`httpx` 非同期クライアント）
  - `httpx.AsyncClient`を`lifespan`で管理し、外部REST APIへの非同期HTTPリクエストを効率的に発行する

- **[redis_cache.py](async_and_performance/redis_cache.py)** - Redisキャッシュ連携
  - `aioredis`でRedisに接続し、エンドポイントのレスポンスをTTL付きでキャッシュしてDB負荷を削減する実装

- **[rate_limiting.py](async_and_performance/rate_limiting.py)** - レート制限（Rate Limiting）
  - RedisやインメモリカウンターをベースにIPやAPIキー単位でリクエスト数を制限し、超過時に`429`を返す

---

## エラーハンドリング `error_handling`

- **[custom_exception_handler.py](error_handling/custom_exception_handler.py)** - カスタム例外クラスと例外ハンドラー
  - アプリ固有の例外クラスを定義し、`@app.exception_handler`で統一フォーマットのエラーレスポンスに変換する

- **[http_exception_usage.py](error_handling/http_exception_usage.py)** - HTTPException の使い分け
  - `404`/`400`/`403`/`422`などのステータスコードを適切なケースで使い分けるベストプラクティスと実装例

- **[validation_error_response_format.py](error_handling/validation_error_response_format.py)** - バリデーションエラーのレスポンス整形
  - Pydanticの`RequestValidationError`をキャッチし、フィールド名・エラー理由を含む独自フォーマットに整形して返す

---

## ミドルウェア・共通処理 `middleware_and_common`

- **[cors_middleware.py](middleware_and_common/cors_middleware.py)** - CORSミドルウェア設定
  - `CORSMiddleware`で許可オリジン・メソッド・ヘッダーを設定し、フロントエンドからのクロスオリジンリクエストを制御する

- **[request_logging_middleware.py](middleware_and_common/request_logging_middleware.py)** - リクエストログミドルウェア
  - 全リクエストのメソッド・URL・ステータスコードをミドルウェア層でインターセプトしてログ出力する

- **[latency_measurement_middleware.py](middleware_and_common/latency_measurement_middleware.py)** - レイテンシ計測ミドルウェア
  - リクエスト前後で`time.time()`を計測し、処理時間を`X-Process-Time`レスポンスヘッダーやログに記録する

- **[structured_logging.py](middleware_and_common/structured_logging.py)** - 構造化ログ（CloudWatch出力対応）
  - `python-json-logger`などでログをJSON形式に統一し、CloudWatch Logs Insightsでのクエリに対応した出力構成

---

## テスト `testing`

- **[unit_test_with_pytest_and_test_client.py](testing/unit_test_with_pytest_and_test_client.py)** - `pytest` + `TestClient` による単体テスト
  - `TestClient`でHTTPリクエストを擬似発行し、ステータスコード・レスポンスボディをpytestでアサートする基本テスト構成

- **[integration_test_with_db_mock.py](testing/integration_test_with_db_mock.py)** - DBモックを使った統合テスト
  - `unittest.mock`や`pytest-mock`でDBセッションをモック化し、実DBに依存しない統合テストを実現する

- **[dependency_injection_override.py](testing/dependency_injection_override.py)** - 依存性注入のオーバーライド（テスト用DI差し替え）
  - `app.dependency_overrides`を使って認証やDBの依存関係をテスト用スタブに差し替え、本番コードを変更せずにテストする

- **[async_test.py](testing/async_test.py)** - 非同期エンドポイントのテスト（`pytest-asyncio`）
  - `pytest-asyncio`と`AsyncClient`（httpx）を組み合わせ、`async def`エンドポイントを非同期のままテストする

---

## 運用・デプロイ `operations_and_deployment`

- **[dockerfile_and_docker_compose.py](operations_and_deployment/dockerfile_and_docker_compose.py)** - Dockerfileとdocker-compose構成
  - FastAPI + Uvicornを動かすマルチステージDockerfileと、DBコンテナと連携するdocker-compose構成例

- **[health_check_endpoint.py](operations_and_deployment/health_check_endpoint.py)** - ヘルスチェックエンドポイント（`/health`）
  - ECSやALBのヘルスチェックに対応した`/health`エンドポイントで、DB疎通確認を含むリッチなステータス応答を返す

- **[openapi_customization.py](operations_and_deployment/openapi_customization.py)** - OpenAPI（Swagger）カスタマイズ
  - `openapi_tags`やカスタム`openapi()`関数でSwagger UIのタイトル・説明・タグ分類・認証設定を整える

- **[s3_file_upload.py](operations_and_deployment/s3_file_upload.py)** - S3ファイルアップロード連携
  - `boto3`を使ってアップロードされたファイルをS3バケットに保存し、署名付きURLを発行して返す実装

- **[cloudwatch_logging.py](operations_and_deployment/cloudwatch_logging.py)** - CloudWatchログ連携
  - `watchtower`ライブラリでPythonのloggingハンドラーにCloudWatch Logsを追加し、ECS/Lambda環境からのログ集約に対応する
