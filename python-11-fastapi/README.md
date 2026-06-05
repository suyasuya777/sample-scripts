# FastAPI 学習サンプル集

FastAPIの各機能を個別に学習できるサンプルプログラム集です。

## 📁 カテゴリ構成

| フォルダ | 内容 |
|---|---|
| [`01_basics_and_structure/`](#01_basics_and_structure) | 基礎・構造（プロジェクト構成） |
| [`02_request_response/`](#02_request_response) | リクエスト・レスポンス（バリデーション・ページネーション・レスポンス設計） |
| [`03_auth_security/`](#03_auth_security) | 認証・セキュリティ（APIキー・RBAC） |
| [`04_async_performance/`](#04_async_performance) | 非同期・パフォーマンス（BackgroundTasks・外部API呼び出し） |
| [`05_error_handling/`](#05_error_handling) | エラーハンドリング（HTTPException・バリデーションエラー） |
| [`06_middleware/`](#06_middleware) | ミドルウェア・共通処理（ロギング・構造化ログ） |
| [`07_deploy/`](#07_deploy) | 運用・デプロイ（Docker・ヘルスチェック・CloudWatch） |

---

## 📁 カテゴリ・ディレクトリ構成

| カテゴリ | ディレクトリ | 日本語タイトル |
|---|---|---|
| [`01_basics_and_structure/`](#01_basics_and_structure) | [`project_structure/`](#project_structure) | FastAPI標準プロジェクト構成 |
| [`02_request_response/`](#02_request_response) | [`pagination/`](#pagination) | ページネーション（offset/limit・カーソル方式） |
| | [`response_model_filtering/`](#response_model_filtering) | レスポンスフィールドの絞り込みと機密情報除外 |
| | [`unified_response_format/`](#unified_response_format) | 統一レスポンスフォーマット（Generic[T]） |
| | [`validation/`](#validation) | バリデーション（フィールド制約・カスタムバリデーター） |
| [`03_auth_security/`](#03_auth_security) | [`api_key_authentication/`](#api_key_authentication) | APIキー認証（ヘッダー・クエリパラメーター） |
| | [`role_based_access_control/`](#role_based_access_control) | ロールベースアクセス制御（RBAC） |
| [`04_async_performance/`](#04_async_performance) | [`background_tasks/`](#background_tasks) | バックグラウンドタスク（レスポンス後の非同期処理） |
| | [`external_api_call_with_httpx/`](#external_api_call_with_httpx) | 外部API非同期呼び出し（httpx） |
| [`05_error_handling/`](#05_error_handling) | [`http_exception_usage/`](#http_exception_usage) | HTTPException の使い方とステータスコード定数 |
| | [`validation_error_response_format/`](#validation_error_response_format) | バリデーションエラーレスポンスの整形 |
| [`06_middleware/`](#06_middleware) | [`request_logging_middleware/`](#request_logging_middleware) | リクエストログ記録ミドルウェア |
| | [`structured_logging/`](#structured_logging) | 構造化ログ（JSON形式・CloudWatch対応） |
| [`07_deploy/`](#07_deploy) | [`cloudwatch_logging/`](#cloudwatch_logging) | CloudWatch Logsへのログ送信（watchtower） |
| | [`docker/`](#docker) | Dockerコンテナ化（Dockerfile・docker-compose） |
| | [`health_check_endpoint/`](#health_check_endpoint) | ヘルスチェックエンドポイント（ECS/ALB対応） |
| | [`startup_shutdown_events/`](#startup_shutdown_events) | 起動・終了イベント管理（lifespanパターン） |

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
pip install -r requirements.txt
```

各サンプルは単体で `uvicorn ファイル名:app --reload` で起動できます。

```bash
# ブラウザで確認
http://localhost:8000/docs
```

---

## 📄 Python ソース詳細

### <a id="01_basics_and_structure"></a>01_basics_and_structure/（基礎・構造）　―　FastAPIプロジェクトの標準的なディレクトリ構成・設定管理・DB接続の基盤を学ぶ

```
01_basics_and_structure/
└── project_structure/
    ├── main.py
    ├── config.py
    ├── database.py
    ├── routers/
    │   ├── item.py
    │   └── user.py
    ├── cruds/
    │   ├── item.py
    │   └── user.py
    ├── models/
    │   ├── item.py
    │   └── user.py
    ├── schemas/
    │   ├── item.py
    │   └── user.py
    └── tests/
        ├── test_item.py
        └── test_user.py
```

<a id="project_structure"></a>
#### [project_structure/](01_basics_and_structure/project_structure/)　―　FastAPI標準プロジェクト構成

FastAPIの標準的なプロジェクト構成サンプル。`config.py` による `BaseSettings` + `lru_cache` の設定管理、`database.py` による非同期セッション管理、`models/` → `schemas/` → `cruds/` → `routers/` の依存関係の流れ、`selectinload` によるN+1問題の回避、PUT（全更新）と PATCH（`exclude_unset=True`）の使い分け、`model_rebuild()` による循環参照の解決、pytest による統合テストまでを網羅した学習用ベースプロジェクト。

詳細は [project_structure 詳細 README](01_basics_and_structure/project_structure/README.md) を参照。

---

### <a id="02_request_response"></a>02_request_response/（リクエスト・レスポンス）　―　入力値の検証・ページング・レスポンス形式の設計パターンを学ぶ

```
02_request_response/
├── pagination/
│   └── pagination.py
├── response_model_filtering/
│   └── response_model_filtering.py
├── unified_response_format/
│   └── unified_response_format.py
└── validation/
    └── validation.py
```

<a id="pagination"></a>
#### [pagination.py](02_request_response/pagination/pagination.py)　―　ページネーション（offset/limit・カーソル方式）

| import モジュール | 用途 |
|---|---|
| `typing.List`, `typing.Optional` | 型ヒント |
| `fastapi.FastAPI`, `fastapi.Query`, `fastapi.Depends` | クエリパラメーター・DI |
| `pydantic.BaseModel` | レスポンススキーマ |

offset/limit方式とカーソル方式の2種類のページネーション実装。`Depends` を使った `PaginationParams` クラスによるページネーションパラメーターの共通化パターンも解説。

---

<a id="response_model_filtering"></a>
#### [response_model_filtering.py](02_request_response/response_model_filtering/response_model_filtering.py)　―　レスポンスフィールドの絞り込みと機密情報除外

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `pydantic.BaseModel`, `pydantic.ConfigDict` | スキーマ定義 |
| `typing.Optional` | 省略可能型 |

`response_model` / `response_model_exclude` / `response_model_include` によるレスポンスフィールドの絞り込み。パスワード・ソルト等の機密フィールドをJSONレスポンスから除外するセキュリティ設計パターンを示す。

---

<a id="unified_response_format"></a>
#### [unified_response_format.py](02_request_response/unified_response_format/unified_response_format.py)　―　統一レスポンスフォーマット（Generic[T]）

| import モジュール | 用途 |
|---|---|
| `typing.Generic`, `typing.TypeVar`, `typing.Optional`, `typing.List` | ジェネリック型定義 |
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `pydantic.BaseModel` | レスポンススキーマ基底 |

`Generic[T]` を使った全エンドポイント共通のAPIレスポンスフォーマット（`status` / `message` / `data`）を実装。成功・失敗・一覧レスポンスを同一構造で返すパターン。

---

<a id="validation"></a>
#### [validation.py](02_request_response/validation/validation.py)　―　バリデーション（フィールド制約・カスタムバリデーター）

| import モジュール | 用途 |
|---|---|
| `typing.Optional` | 省略可能型 |
| `pydantic.BaseModel`, `pydantic.Field`, `pydantic.field_validator`, `pydantic.model_validator` | バリデーション定義 |

`Field` 制約（`min_length` / `max_length` / `pattern` / `ge` / `le`）、`@field_validator` によるカスタム単フィールドバリデーション、`@model_validator` による複数フィールドまたぎバリデーション（パスワード一致確認等）を解説。

---

### <a id="03_auth_security"></a>03_auth_security/（認証・セキュリティ）　―　APIキー認証・JWT・RBACによるエンドポイント保護パターンを学ぶ

```
03_auth_security/
├── api_key_authentication/
│   └── api_key_authentication.py
└── role_based_access_control/
    └── role_based_access_control.py
```

<a id="api_key_authentication"></a>
#### [api_key_authentication.py](03_auth_security/api_key_authentication/api_key_authentication.py)　―　APIキー認証（ヘッダー・クエリパラメーター）

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.Security`, `fastapi.HTTPException` | セキュリティ依存注入・例外 |
| `fastapi.security.APIKeyHeader`, `fastapi.security.APIKeyQuery` | ヘッダー・クエリからのAPIキー取得 |

リクエストヘッダー（`X-API-Key`）またはクエリパラメーターからAPIキーを取得して検証する認証方式。バックエンド間通信や外部サービス連携向け。

---

<a id="role_based_access_control"></a>
#### [role_based_access_control.py](03_auth_security/role_based_access_control/role_based_access_control.py)　―　ロールベースアクセス制御（RBAC）

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

### <a id="04_async_performance"></a>04_async_performance/（非同期・パフォーマンス）　―　レスポンスをブロックしない非同期処理・外部API呼び出しパターンを学ぶ

```
04_async_performance/
├── background_tasks/
│   └── background_tasks.py
└── external_api_call_with_httpx/
    └── external_api_call_with_httpx.py
```

<a id="background_tasks"></a>
#### [background_tasks.py](04_async_performance/background_tasks/background_tasks.py)　―　バックグラウンドタスク（レスポンス後の非同期処理）

| import モジュール | 用途 |
|---|---|
| `time` | 重い処理のシミュレーション |
| `fastapi.FastAPI`, `fastapi.BackgroundTasks` | FastAPIアプリ・バックグラウンドタスク |

`BackgroundTasks.add_task()` を使ったレスポンス返却後の非同期処理実行。メール送信・ログ記録・通知など、レスポンスをブロックしたくない処理の実装パターン。

---

<a id="external_api_call_with_httpx"></a>
#### [external_api_call_with_httpx.py](04_async_performance/external_api_call_with_httpx/external_api_call_with_httpx.py)　―　外部API非同期呼び出し（httpx）

| import モジュール | 用途 |
|---|---|
| `httpx` | 非同期HTTPクライアント |
| `fastapi.FastAPI`, `fastapi.HTTPException` | FastAPIアプリ・例外 |

`httpx.AsyncClient` を使った外部APIへの非同期HTTP呼び出し。`connect` / `read` / `write` の個別タイムアウト設定、リトライ処理、コンテキストマネージャーによるリソース管理を実装。

---

### <a id="05_error_handling"></a>05_error_handling/（エラーハンドリング）　―　HTTPException・バリデーションエラーを統一フォーマットで返すパターンを学ぶ

```
05_error_handling/
├── http_exception_usage/
│   └── http_exception_usage.py
└── validation_error_response_format/
    └── validation_error_response_format.py
```

<a id="http_exception_usage"></a>
#### [http_exception_usage.py](05_error_handling/http_exception_usage/http_exception_usage.py)　―　HTTPException の使い方とステータスコード定数

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.HTTPException`, `fastapi.Path` | FastAPIアプリ・HTTP例外・パスパラメーター |
| `starlette.status` | HTTPステータスコード定数 |

FastAPI標準 `HTTPException` の使い方。`status_code` / `detail` / `headers` の設定と `starlette.status` のステータスコード定数（`HTTP_404_NOT_FOUND` 等）の活用。

---

<a id="validation_error_response_format"></a>
#### [validation_error_response_format.py](05_error_handling/validation_error_response_format/validation_error_response_format.py)　―　バリデーションエラーレスポンスの整形

| import モジュール | 用途 |
|---|---|
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |
| `fastapi.exceptions.RequestValidationError` | Pydanticバリデーション失敗例外 |
| `fastapi.responses.JSONResponse` | JSONレスポンス生成 |
| `pydantic.BaseModel`, `pydantic.Field` | スキーマ定義 |

`RequestValidationError` ハンドラーをカスタマイズして、フィールド名・入力値・エラーメッセージを分かりやすい構造のJSONで返すバリデーションエラーレスポンスの整形パターン。

---

### <a id="06_middleware"></a>06_middleware/（ミドルウェア）　―　全リクエストに横断的に適用するログ記録・JSON構造化ログのパターンを学ぶ

```
06_middleware/
├── request_logging_middleware/
│   └── request_logging_middleware.py
└── structured_logging/
    └── structured_logging.py
```

<a id="request_logging_middleware"></a>
#### [request_logging_middleware.py](06_middleware/request_logging_middleware/request_logging_middleware.py)　―　リクエストログ記録ミドルウェア

| import モジュール | 用途 |
|---|---|
| `time` | 処理時間計測 |
| `logging` | ログ出力 |
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |

`@app.middleware("http")` で全リクエストをインターセプトし、HTTPメソッド・パス・クライアントIP・処理時間を `logging` でログ記録するミドルウェア。

---

<a id="structured_logging"></a>
#### [structured_logging.py](06_middleware/structured_logging/structured_logging.py)　―　構造化ログ（JSON形式・CloudWatch対応）

| import モジュール | 用途 |
|---|---|
| `logging` | ログ出力基盤 |
| `json` | JSON形式フォーマット |
| `datetime.datetime` | タイムスタンプ生成 |
| `fastapi.FastAPI`, `fastapi.Request` | FastAPIアプリ・リクエスト |

`logging.Formatter` を継承したカスタム `JsonFormatter` でログをJSON形式で出力する実装。`timestamp` / `level` / `message` / `module` 等のフィールドを構造化し、AWS CloudWatch Logs Insightsでの検索・集計に対応。

---

### <a id="07_deploy"></a>07_deploy/（運用・デプロイ）　―　Docker・ヘルスチェック・CloudWatchなどAWS実務に直結するデプロイ設計を学ぶ

```
07_deploy/
├── cloudwatch_logging/
│   └── cloudwatch_logging.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── health_check_endpoint/
│   └── health_check_endpoint.py
└── startup_shutdown_events/
    └── startup_shutdown_events.py
```

<a id="cloudwatch_logging"></a>
#### [cloudwatch_logging.py](07_deploy/cloudwatch_logging/cloudwatch_logging.py)　―　CloudWatch Logsへのログ送信（watchtower）

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

<a id="docker"></a>
#### [docker/](07_deploy/docker/)　―　Dockerコンテナ化（Dockerfile・docker-compose）

| ファイル | 内容 |
|---|---|
| `Dockerfile` | FastAPIアプリのコンテナイメージ定義 |
| `docker-compose.yml` | アプリ + PostgreSQL の構成定義 |
| `requirements.txt` | コンテナ用依存パッケージ |

FastAPIアプリのDockerコンテナ化。マルチステージビルド、非rootユーザー実行、ヘルスチェック設定を含む本番向け `Dockerfile` と、PostgreSQLとの連携を含む `docker-compose.yml` の構成。

---

<a id="health_check_endpoint"></a>
#### [health_check_endpoint.py](07_deploy/health_check_endpoint/health_check_endpoint.py)　―　ヘルスチェックエンドポイント（ECS/ALB対応）

| import モジュール | 用途 |
|---|---|
| `time` | 起動時刻・稼働時間計算 |
| `fastapi.FastAPI` | FastAPIアプリ本体 |
| `fastapi.responses.JSONResponse` | JSONレスポンス生成 |

ECS/K8s向けの `/health`（死活監視）・`/ready`（DB接続確認）・`/live`（プロセス生存確認）の3エンドポイント実装。ALBヘルスチェックに最適なレスポンス設計。

---

<a id="startup_shutdown_events"></a>
#### [startup_shutdown_events.py](07_deploy/startup_shutdown_events/startup_shutdown_events.py)　―　起動・終了イベント管理（lifespanパターン）

| import モジュール | 用途 |
|---|---|
| `contextlib.asynccontextmanager` | 非同期コンテキストマネージャー |
| `fastapi.FastAPI` | FastAPIアプリ本体 |

FastAPI 0.93+ 推奨の `lifespan` パターン（`@asynccontextmanager`）と旧 `@app.on_event` パターンの比較。DB接続プール初期化・Redis接続・外部サービス疎通確認・クリーンアップの起動・終了イベント管理を解説。
