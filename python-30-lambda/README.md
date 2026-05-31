# Lambda 実務サンプルプログラム集

AWS Lambda の実務でよく使用するユースケースをまとめたサンプルプログラム集です。

## 📋 ファイル一覧

| ソース | 説明 |
|---|---|
| [`rest_api.py`](#rest-api-py) | API Gateway + Lambda によるシンプルな REST API の実装 |
| [`s3_event_integration.py`](#s3-event-integration-py) | S3 イベントをトリガーにした Lambda 連携 |
| [`s3_presigned_url.py`](#s3-presigned-url-py) | S3 署名付き URL（Presigned URL）の発行と利用 |
| [`api_gateway_dynamodb_ses_integration/`](#api-gateway-dynamodb-ses-integration) | API Gateway → DynamoDB → SES の一連のフロー実装 |
| [`dynamodb_streams_trigger.py`](#dynamodb-streams-trigger-py) | DynamoDB Streams をトリガーにした Lambda の起動 |
| [`sqs_sns_integration.py`](#sqs-sns-integration-py) | SQS キューをイベントソースとした Lambda のポーリング処理 |
| [`sns_publisher.py`](#sns-publisher-py) | Lambda から SNS トピックへのメッセージパブリッシュ |
| [`secrets_manager_ssm.py`](#secrets-manager-ssm-py) | Secrets Manager / SSM Parameter Store からの取得・キャッシュ実装 |
| [`cognito_pre_signup_trigger.py`](#cognito-pre-signup-trigger-py) | Cognito Pre Sign-up Lambda トリガー実装 |
| [`vpc_rds_connection.py`](#vpc-rds-connection-py) | VPC 内の RDS への Lambda からの接続 |
| [`eventbridge_scheduled_job.py`](#eventbridge-scheduled-job-py) | EventBridge スケジュールルールによる定期実行 |
| [`step_functions_trigger.py`](#step-functions-trigger-py) | Step Functions から呼び出される Lambda タスクの実装 |
| [`error_handling_dlq.py`](#error-handling-dlq-py) | Lambda の例外ハンドリングと DLQ 活用 |
| [`powertools_middleware.py`](#powertools-middleware-py) | AWS Lambda Powertools を活用したミドルウェア実装 |

---

## 📄 Python ソース詳細

<a id="rest-api-py"></a>

- **[`rest_api.py`](rest_api/rest_api.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  ```

  - API Gateway + Lambda によるシンプルな REST API の実装
  - GET / POST / PUT / DELETE のルーティング処理
  - リクエストバリデーション、レスポンス整形（JSON）、CORS ヘッダー付与

<a id="s3-event-integration-py"></a>

- **[`s3_event_integration.py`](s3_event_integration/s3_event_integration.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import urllib.parse
  import boto3
  ```

  - S3 バケットへのオブジェクトアップロードをトリガーにした Lambda 連携
  - `s3:ObjectCreated:*` イベントからバケット名・キー名を取得する処理
  - ファイル種別に応じた分岐処理（画像リサイズ、CSV パースなど）の雛形

<a id="s3-presigned-url-py"></a>

- **[`s3_presigned_url.py`](s3_presigned_url/s3_presigned_url.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import boto3
  from botocore.config import Config
  ```

  - S3 署名付き URL（Presigned URL）の発行と利用
  - アップロード用（`put_object`）・ダウンロード用（`get_object`）URL の生成
  - 有効期限の設定と Content-Type 制限の付け方

<a id="api-gateway-dynamodb-ses-integration"></a>

- **[`api_gateway_dynamodb_ses_integration/`](api_gateway_dynamodb_ses_integration/)**
  - API Gateway → Lambda → DynamoDB → SES の一連のフロー実装
  - DynamoDB への CRUD 操作（put / get / query / delete）
  - 処理完了後に SES でメール通知を送信するパターン

  **インポートするモジュール**

  `handler.py`
  ```python
  import json
  import logging
  import uuid
  import db      # 同ディレクトリの db.py
  import mailer  # 同ディレクトリの mailer.py
  ```

  `db.py`
  ```python
  import logging
  import boto3
  from boto3.dynamodb.conditions import Key
  from botocore.exceptions import ClientError
  ```

  `mailer.py`
  ```python
  import logging
  import boto3
  from botocore.exceptions import ClientError
  ```

  | ファイル | 役割 |
  |---|---|
  | `handler.py` | Lambda エントリーポイント（ルーティング） |
  | `db.py` | DynamoDB CRUD 操作 |
  | `mailer.py` | SES メール送信 |

<a id="dynamodb-streams-trigger-py"></a>

- **[`dynamodb_streams_trigger.py`](dynamodb_streams_trigger/dynamodb_streams_trigger.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import boto3
  from boto3.dynamodb.types import TypeDeserializer
  ```

  - DynamoDB Streams をトリガーにした Lambda の起動
  - INSERT / MODIFY / REMOVE イベントの判別と新旧レコードの取得
  - 変更差分の検知・後続処理（検索インデックス更新、監査ログ記録）への活用例

<a id="sqs-sns-integration-py"></a>

- **[`sqs_sns_integration.py`](sqs_sns_integration/sqs_sns_integration.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  ```

  - SQS キューをイベントソースとした Lambda のポーリング処理
  - メッセージのバッチ受信・個別処理・部分的な失敗（`batchItemFailures`）の返却
  - SNS → SQS のサブスクリプション構成でのメッセージ受信パターン

<a id="sns-publisher-py"></a>

- **[`sns_publisher.py`](sns_publisher/sns_publisher.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import boto3
  ```

  - Lambda から SNS トピックへのメッセージパブリッシュ
  - スタンダードトピックとFIFOトピックへの発行方法
  - メッセージ属性（MessageAttributes）を使ったフィルタリング対応

<a id="secrets-manager-ssm-py"></a>

- **[`secrets_manager_ssm.py`](secrets_manager_ssm/secrets_manager_ssm.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import boto3
  from botocore.exceptions import ClientError
  ```

  - Secrets Manager からシークレット（DB 認証情報など）を取得・キャッシュする実装
  - SSM Parameter Store から設定値（通常パラメータ / SecureString）を取得する実装
  - Lambda 実行環境のライフサイクルを活用したグローバルキャッシュパターン

<a id="cognito-pre-signup-trigger-py"></a>

- **[`cognito_pre_signup_trigger.py`](cognito_pre_signup_trigger/cognito_pre_signup_trigger.py)**

  **インポートするモジュール**
  ```python
  import logging
  import re
  ```

  - Cognito ユーザープールの Pre Sign-up Lambda トリガー実装
  - メールドメイン制限・禁止ワードチェックなどのカスタムバリデーション
  - 自動確認・自動検証フラグ（`autoConfirmUser` / `autoVerifyEmail`）の制御

<a id="vpc-rds-connection-py"></a>

- **[`vpc_rds_connection.py`](vpc_rds_connection/vpc_rds_connection.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import boto3
  import pymysql  # pip install pymysql
  ```

  - VPC 内の RDS（MySQL / PostgreSQL）への Lambda からの接続
  - `pymysql` / `psycopg2` を使ったコネクション管理と接続の再利用
  - Secrets Manager 経由での認証情報取得と RDS Proxy を使った接続プーリング

<a id="eventbridge-scheduled-job-py"></a>

- **[`eventbridge_scheduled_job.py`](eventbridge_scheduled_job/eventbridge_scheduled_job.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  from datetime import datetime, timezone
  import boto3
  ```

  - EventBridge（CloudWatch Events）のスケジュールルールによる定期実行
  - cron 式 / rate 式での起動と実行時刻の取得
  - バッチ処理・定期レポート生成・古いデータのクリーンアップなどの実装例

<a id="step-functions-trigger-py"></a>

- **[`step_functions_trigger.py`](step_functions_trigger/step_functions_trigger.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import boto3
  ```

  - Step Functions ステートマシンから呼び出される Lambda タスクの実装
  - 入力パラメータの受け取りと出力データの返却フォーマット
  - ウェイトフォータスク（`taskToken`）を使った非同期コールバックパターン

<a id="error-handling-dlq-py"></a>

- **[`error_handling_dlq.py`](error_handling_dlq/error_handling_dlq.py)**

  **インポートするモジュール**
  ```python
  import json
  import logging
  import hashlib
  import boto3
  from botocore.exceptions import ClientError
  ```

  - Lambda における例外ハンドリングのベストプラクティス
  - リトライ制御（`maximumRetryAttempts`）と冪等性を考慮した実装
  - DLQ（Dead Letter Queue）へのメッセージ送信と Lambda Destinations の活用

<a id="powertools-middleware-py"></a>

- **[`powertools_middleware.py`](powertools_middleware/powertools_middleware.py)**

  **インポートするモジュール**
  ```python
  import json
  from aws_lambda_powertools import Logger, Tracer, Metrics
  from aws_lambda_powertools.metrics import MetricUnit
  from aws_lambda_powertools.utilities.typing import LambdaContext
  from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source
  ```

  - AWS Lambda Powertools（Python）を活用したミドルウェア実装
  - Logger / Tracer / Metrics の設定と構造化ログ出力
  - `@event_source` デコレータ、`@tracer.capture_lambda_handler` などのユーティリティ活用例

