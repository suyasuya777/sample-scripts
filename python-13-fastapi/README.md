# FastAPI 学習サンプル集

## 🗺 カテゴリ一覧

| # | カテゴリ | このカテゴリで身につくこと |
|---|---|---|
| 01 | `request_response` | 入力の検証・ページング・レスポンス構造の設計。APIの「入口と出口」の型を固める。 |
| 02 | `error_handling` | バリデーション失敗や異常系を統一フォーマットで返す。01 の裏返しとして学ぶ。 |
| 03 | `auth_security` | APIキー認証・JWT・RBAC でエンドポイントを保護する。 |
| 04 | `async_performance` | レスポンスをブロックしない非同期処理・外部API連携。 |
| 05 | `middleware` | 全リクエストに横断適用するロギング・構造化ログ。 |
| 06 | `deploy` | Docker・ヘルスチェック・CloudWatch など運用・デプロイ設計。 |

---

## 📁 ディレクトリ構成

| カテゴリ | ファイル | 内容 |
|---|---|---|
| **01_request_response** | [`pagination/`](01_request_response/pagination/pagination.py) | ページネーション（offset/limit・カーソル方式） |
| | [`response_model_filtering/`](01_request_response/response_model_filtering/response_model_filtering.py) | レスポンスフィールドの絞り込みと機密情報除外 |
| | [`unified_response_format/`](01_request_response/unified_response_format/unified_response_format.py) | 統一レスポンスフォーマット（`Generic[T]`） |
| | [`validation/`](01_request_response/validation/validation.py) | バリデーション（Field制約・カスタムバリデーター） |
| **02_error_handling** | [`http_exception_usage/`](02_error_handling/http_exception_usage/http_exception_usage.py) | HTTPException とステータスコード定数 |
| | [`validation_error_response_format/`](02_error_handling/validation_error_response_format/validation_error_response_format.py) | バリデーションエラーレスポンスの整形 |
| **03_auth_security** | [`api_key_authentication/`](03_auth_security/api_key_authentication/api_key_authentication.py) | APIキー認証（ヘッダー・クエリ） |
| | [`role_based_access_control/`](03_auth_security/role_based_access_control/role_based_access_control.py) | ロールベースアクセス制御（RBAC / JWT） |
| **04_async_performance** | [`background_tasks/`](04_async_performance/background_tasks/background_tasks.py) | バックグラウンドタスク（レスポンス後の非同期処理） |
| | [`external_api_call_with_httpx/`](04_async_performance/external_api_call_with_httpx/external_api_call_with_httpx.py) | 外部API非同期呼び出し（httpx） |
| **05_middleware** | [`request_logging_middleware/`](05_middleware/request_logging_middleware/request_logging_middleware.py) | リクエストログ記録ミドルウェア |
| | [`structured_logging/`](05_middleware/structured_logging/structured_logging.py) | 構造化ログ（JSON形式・CloudWatch対応） |
| **06_deploy** | [`cloudwatch_logging/`](06_deploy/cloudwatch_logging/cloudwatch_logging.py) | CloudWatch Logs へのログ送信（watchtower） |
| | [`docker/`](06_deploy/docker/) | Docker コンテナ化（Dockerfile・compose） |
| | [`health_check_endpoint/`](06_deploy/health_check_endpoint/health_check_endpoint.py) | ヘルスチェック（ECS/ALB対応） |
| | [`startup_shutdown_events/`](06_deploy/startup_shutdown_events/startup_shutdown_events.py) | 起動・終了イベント管理（lifespan） |

---

## 🚀 セットアップ

```bash
# venv を使う場合
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

各サンプルの起動と確認:

```bash
# 例: バリデーションのサンプルを起動
uvicorn validation:app --reload      # ファイルのあるディレクトリで実行

# ブラウザで Swagger UI を開く
http://localhost:8000/docs
```

---

## 📄 サンプル詳細

### 01_request_response — 入出力の設計

| ファイル | 学ぶこと | 使いどころ | 補足 |
|---|---|---|---|
| [pagination.py](01_request_response/pagination/pagination.py) | `offset/limit` 方式と `cursor` 方式の実装差。`Depends` に渡す `PaginationParams` クラスで共通パラメーターを再利用。 | 一覧APIの標準装備。件数が多い・追記が頻繁なテーブルではカーソル方式が有利。 | ― |
| [response_model_filtering.py](01_request_response/response_model_filtering/response_model_filtering.py) | `response_model` による自動フィルタ、`response_model_exclude` / `response_model_include` の使い分け。`ConfigDict(from_attributes=True)` でORMから変換。 | `password` / `salt` など内部モデルにあるが外に出せないフィールドの漏洩防止。セキュリティ設計の基本。 | ― |
| [unified_response_format.py](01_request_response/unified_response_format/unified_response_format.py) | `Generic[T]` で成功・失敗・一覧を `status` / `message` / `data` の同一構造で返す。 | フロントとの契約を安定させたいとき。クライアント側のハンドリングが単純化する。 | ― |
| [validation.py](01_request_response/validation/validation.py) | `Field` 制約（min_length / max_length / pattern / ge / le）、`@field_validator`（単一フィールド）、`@model_validator(mode="after")`（複数またぎ・パスワード一致確認）。 | 入力仕様の宣言的な定義。ビジネスルール（予約語禁止・確認用パスワード一致）はバリデーター側へ寄せる。 | ― |

### 02_error_handling — 異常系の設計（01 とセットで）

| ファイル | 学ぶこと | 使いどころ | 補足 |
|---|---|---|---|
| [http_exception_usage.py](02_error_handling/http_exception_usage/http_exception_usage.py) | `status_code` / `detail`（文字列 or dict）/ `headers`（認証エラー時の `WWW-Authenticate` 等）の指定。`status` 定数（`HTTP_404_NOT_FOUND`）の活用。 | 4xx/5xx を意図通りに返す基本。`detail` を dict にするとエラーコードを機械可読で返せる。 | `from fastapi import status` に統一（`starlette.status` と同一）。 |
| [validation_error_response_format.py](02_error_handling/validation_error_response_format/validation_error_response_format.py) | `@app.exception_handler(RequestValidationError)` を上書きし、`field` / `message` / `input` を含む分かりやすいJSONに整形。 | 標準の422レスポンスは冗長。フロントに優しい形へ統一したいとき。01 の validation の裏返し。 | ― |

### 03_auth_security — 認証・認可

| ファイル | 学ぶこと | 使いどころ | 補足 |
|---|---|---|---|
| [api_key_authentication.py](03_auth_security/api_key_authentication/api_key_authentication.py) | `APIKeyHeader` / `APIKeyQuery` でキーを取得し、`Security` 依存で検証。`auto_error=False` でヘッダー・クエリ両対応。 | マシン間認証（バックエンド間通信・外部サービス連携）。ユーザーログインを伴わない場面。 | ― |
| [role_based_access_control.py](03_auth_security/role_based_access_control/role_based_access_control.py) | JWTペイロードに `role` を含め、`require_role(*roles)` ファクトリで「必要ロールを満たす依存」を生成して注入。admin / user / guest を例示。 | エンドポイント単位のアクセス制御。ファクトリ + `Depends` は FastAPI らしい再利用パターン。 | JWTに `PyJWT` を採用。`exp` は tz-aware（`datetime.now(timezone.utc)`）、失効・改ざんは `jwt.InvalidTokenError` で捕捉。 |

### 04_async_performance — 非同期・パフォーマンス

| ファイル | 学ぶこと | 使いどころ | 補足 |
|---|---|---|---|
| [background_tasks.py](04_async_performance/background_tasks/background_tasks.py) | `BackgroundTasks.add_task()` でレスポンス返却後に処理を実行。 | メール送信・ログ記録・通知など待たせたくない軽量処理。重い/信頼性が要る処理は Celery や SQS 等へ。 | ― |
| [external_api_call_with_httpx.py](04_async_performance/external_api_call_with_httpx/external_api_call_with_httpx.py) | `httpx.AsyncClient`、`Timeout(connect/read/write/pool)` の個別設定、リトライ、`async with` でのリソース管理と例外変換（504/503）。 | `async def` から外部APIを叩くとき。同期の `requests` はイベントループをブロックするので不可。 | ― |

### 05_middleware — 横断処理

| ファイル | 学ぶこと | 使いどころ | 補足 |
|---|---|---|---|
| [request_logging_middleware.py](05_middleware/request_logging_middleware/request_logging_middleware.py) | `@app.middleware("http")` で全リクエストをインターセプト。`call_next` の前後でメソッド・パス・IP・処理時間・ステータスを記録。 | アクセスログ・処理時間計測の共通化。例外時のログも一元化できる。 | ― |
| [structured_logging.py](05_middleware/structured_logging/structured_logging.py) | `logging.Formatter` 継承の自作 `JsonFormatter` でJSON化。`timestamp` / `level` / `message` / `module` 等を構造化し、`extra` で任意付与。 | CloudWatch Logs Insights など、JSONログ前提で検索・集計する運用。 | 自作 `JsonFormatter`（追加ライブラリ不要）でJSON出力。タイムスタンプは tz-aware（UTC）。 |

### 06_deploy — 運用・デプロイ

| ファイル | 学ぶこと | 使いどころ | 補足 |
|---|---|---|---|
| [cloudwatch_logging.py](06_deploy/cloudwatch_logging/cloudwatch_logging.py) | `watchtower.CloudWatchLogHandler` と JSON フォーマッタの組み合わせ。必要IAM（`logs:CreateLogGroup` / `CreateLogStream` / `PutLogEvents`）。 | ECS/Lambda 等から直接 CloudWatch へ送るケース。 | `watchtower` はコメントアウト状態で `StreamHandler` にフォールバック。<br>ECS で標準出力を awslogs ドライバで拾う構成なら watchtower 不要。 |
| [docker/](06_deploy/docker/) | マルチステージビルド・非root実行の `Dockerfile`。compose で app + PostgreSQL + pgAdmin の3サービス、`depends_on` の `service_healthy` 条件、`healthcheck`。 | ローカルでのDB込み動作確認・本番イメージの雛形。 | 起動手順は [`docker/README.md`](06_deploy/docker/README.md) 参照。 |
| [health_check_endpoint.py](06_deploy/health_check_endpoint/health_check_endpoint.py) | `/health`（軽量・死活）/ `/ready`（DB等の準備確認・503を返す）/ `/live`（プロセス生存）の使い分け。 | ALB/ECS/K8s のヘルスチェック。軽量な死活と依存確認を分ける。 | ― |
| [startup_shutdown_events.py](06_deploy/startup_shutdown_events/startup_shutdown_events.py) | `@asynccontextmanager` の `lifespan`（`yield` 前=起動、後=終了）。旧 `@app.on_event` との比較。 | DB接続プール・Redis・外部疎通確認の初期化とクリーンアップ。 | FastAPI 0.93+ は lifespan 推奨（`on_event` は非推奨）。 |

---

## 🔧 技術メモ（対応状況）

- **JWTライブラリ**: `python-jose` → `PyJWT` へ移行済み（`role_based_access_control.py` / ルート `requirements.txt`）。例外は `jwt.InvalidTokenError` で捕捉。
- **`datetime` のタイムゾーン**: `datetime.utcnow()`（3.12で非推奨）を廃し、`datetime.now(timezone.utc)`（tz-aware）に統一済み（`structured_logging.py` / `cloudwatch_logging.py` / RBAC の `exp`）。
- **`status` の import 元**: `fastapi.status` に統一済み（`http_exception_usage.py`）。
- **`06_deploy/docker/requirements.txt`**: バージョン固定（`fastapi==0.104.1` 等・2023年頃）と `python-jose` は**据え置き**。フリマアプリ本体のデプロイ用マニフェストのため、アプリ側の移行に合わせて更新するのが安全。
- **`on_event`**: `startup_shutdown_events.py` は新旧比較のため意図的に併記（新規は `lifespan`）。修正不要。
