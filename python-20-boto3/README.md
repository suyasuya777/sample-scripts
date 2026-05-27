# AWS SDK for Python (boto3) サンプルプログラム集

AWS の各サービスを boto3 で操作する実務向けサンプルプログラム集です。

---

## 目次

- [EC2](#ec2)
- [S3](#s3)
- [IAM](#iam)
- [CloudWatch](#cloudwatch)
- [CloudWatch Logs](#cloudwatch-logs)
- [Lambda](#lambda)
- [ECS](#ecs)
- [SSM](#ssm)
- [RDS](#rds)
- [SQS](#sqs)
- [SNS](#sns)
- [VPC](#vpc)
- [Secrets Manager](#secrets-manager)
- [SES](#ses)

---

## EC2

### [`ec2_describe_instances.py`](ec2/ec2_describe_instances.py)

**インポートするモジュール**
```python
import boto3
```


- EC2 インスタンスの一覧取得（`describe_instances`）
- インスタンス ID・タイプ・状態・タグ情報の整形出力
- フィルター条件（タグ、ステータス）を指定した絞り込み取得

### [`ec2_start_stop_reboot.py`](ec2/ec2_start_stop_reboot.py)

**インポートするモジュール**
```python
import boto3
```


- EC2 インスタンスの起動（`start_instances`）・停止（`stop_instances`）・再起動（`reboot_instances`）
- 対象インスタンス ID を引数で受け取る汎用的な実装
- 操作前後のステータス確認とウェイター（`instance_running` / `instance_stopped`）の活用

### [`ec2_describe_regions.py`](ec2/ec2_describe_regions.py)

**インポートするモジュール**
```python
import boto3
```


- 有効なリージョン一覧の取得（`describe_regions`）
- リージョン名とエンドポイントの一覧表示
- オプトインリージョン（`opt-in-not-required` / `opted-in`）のフィルタリング

### [`ec2_unused_eip.py`](ec2/ec2_unused_eip.py)

**インポートするモジュール**
```python
import boto3
```


- Elastic IP（EIP）の一覧取得と未アタッチ EIP の検出
- インスタンスおよびネットワークインターフェースに未関連付けの EIP 抽出
- コスト削減のための未使用 EIP レポート出力

### [`ec2_security_groups.py`](ec2/ec2_security_groups.py)

**インポートするモジュール**
```python
import boto3
```


- セキュリティグループの一覧取得とインバウンド／アウトバウンドルールの確認
- 0.0.0.0/0（全開放）ルールが存在するグループの検出
- セキュリティグループのルール一覧を整形して出力

### [`ec2_old_ami.py`](ec2/ec2_old_ami.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- 自分のアカウントが所有する AMI（Amazon Machine Image）の一覧取得
- 作成日が一定期間以上経過した古い AMI の検出
- 不要な AMI と紐づくスナップショットの整理対象リスト出力

### [`ec2_snapshots.py`](ec2/ec2_snapshots.py)

**インポートするモジュール**
```python
import boto3
```


- EBS スナップショットの一覧取得（`describe_snapshots`）
- スナップショットのサイズ・作成日・説明などの情報整形
- 古いスナップショットや孤立スナップショット（AMI 未登録）の検出

### [`ec2_modify_instance_type.py`](ec2/ec2_modify_instance_type.py)

**インポートするモジュール**
```python
import boto3
```


- EC2 インスタンスタイプの変更（`modify_instance_attribute`）
- 変更前にインスタンスを停止し、変更後に再起動する安全な手順の実装
- ウェイターを使ったステータス遷移の待機処理

---

## S3

### [`s3_list_buckets.py`](s3/s3_list_buckets.py)

**インポートするモジュール**
```python
import boto3
```


- S3 バケットの一覧取得（`list_buckets`）
- バケット名・作成日・リージョンの一覧表示
- バケット数のカウントとサマリー出力

### [`s3_list_objects.py`](s3/s3_list_objects.py)

**インポートするモジュール**
```python
import boto3
```


- S3 バケット内オブジェクトの一覧取得（`list_objects_v2`）
- プレフィックス・デリミタを使ったフォルダ階層での絞り込み
- ページネーションを使った大量オブジェクトの全件取得

### [`s3_upload_download.py`](s3/s3_upload_download.py)

**インポートするモジュール**
```python
import boto3
import os
```


- ローカルファイルの S3 アップロード（`upload_file`）とダウンロード（`download_file`）
- マルチパートアップロードの設定（`TransferConfig`）と進捗コールバックの活用
- メタデータ・ContentType・ACL の指定方法

### [`s3_public_access_block.py`](s3/s3_public_access_block.py)

**インポートするモジュール**
```python
import boto3
```


- バケットのパブリックアクセスブロック設定の取得と変更
- 全バケットのパブリックアクセス設定を一括スキャンするセキュリティ監査の実装
- ブロック設定（BlockPublicAcls / IgnorePublicAcls / BlockPublicPolicy / RestrictPublicBuckets）の詳細確認

### [`s3_bucket_policy.py`](s3/s3_bucket_policy.py)

**インポートするモジュール**
```python
import boto3
import json
```


- バケットポリシーの取得（`get_bucket_policy`）・設定（`put_bucket_policy`）・削除（`delete_bucket_policy`）
- バケットポリシーの JSON 解析と Principal / Action / Resource の読み取り
- クロスアカウントアクセス許可ポリシーのテンプレート実装

### [`s3_lifecycle.py`](s3/s3_lifecycle.py)

**インポートするモジュール**
```python
import boto3
```


- バケットのライフサイクルルールの取得（`get_bucket_lifecycle_configuration`）と設定（`put_bucket_lifecycle_configuration`）
- 一定日数後に Glacier / Intelligent-Tiering へ移行するルールの実装
- 期限切れオブジェクトと不完全なマルチパートアップロードの自動削除設定

### [`s3_presigned_url.py`](s3/s3_presigned_url.py)

**インポートするモジュール**
```python
import boto3
from botocore.config import Config
```


- S3 署名付き URL（Presigned URL）のアップロード用（`put_object`）・ダウンロード用（`get_object`）生成
- 有効期限（ExpiresIn）と ContentType の指定方法
- 生成した URL を使ったクライアントからの直接アップロード／ダウンロードのフロー説明

---

## IAM

### [`iam_users_access_keys.py`](iam/iam_users_access_keys.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- IAM ユーザーの一覧取得とアクセスキーの状態確認（`list_access_keys`）
- アクセスキーの最終使用日時・有効期間の確認
- 長期間未使用のアクセスキーや期限超過キーのセキュリティ監査

### [`iam_roles_trust_policy.py`](iam/iam_roles_trust_policy.py)

**インポートするモジュール**
```python
import boto3
import json
```


- IAM ロールの一覧取得と信頼ポリシー（Trust Policy）の読み取り
- 信頼ポリシーの Principal（AWS サービス・アカウント・ユーザー）の確認
- クロスアカウントアクセスや意図しない信頼関係の検出

### [`iam_admin_policy_entities.py`](iam/iam_admin_policy_entities.py)

**インポートするモジュール**
```python
import boto3
```


- 管理者権限ポリシー（AdministratorAccess）がアタッチされたエンティティの特定
- ユーザー・グループ・ロールへのポリシーアタッチ状況の一括確認
- 最小権限原則に基づいた過剰権限の監査

### [`iam_inline_policies.py`](iam/iam_inline_policies.py)

**インポートするモジュール**
```python
import boto3
import json
```


- IAM ユーザー・グループ・ロールに設定されたインラインポリシーの一覧取得
- インラインポリシーの内容（JSON）の読み取りと解析
- 管理ポリシーへの移行推奨箇所の洗い出し

### [`iam_access_key_last_used.py`](iam/iam_access_key_last_used.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- アクセスキーの最終使用情報（`get_access_key_last_used`）の取得
- 最終使用サービス・リージョン・日時の確認
- 未使用アクセスキーの検出と無効化・削除の推奨レポート出力

---

## CloudWatch

### [`cloudwatch_alarm_state.py`](cloudwatch/cloudwatch_alarm_state.py)

**インポートするモジュール**
```python
import boto3
```


- CloudWatch アラームの一覧取得と状態（OK / ALARM / INSUFFICIENT_DATA）の確認
- アラーム名・メトリクス・閾値・SNS トピックの情報整形出力
- ALARM 状態にあるアラームの抽出と通知

### [`cloudwatch_get_metrics.py`](cloudwatch/cloudwatch_get_metrics.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- CloudWatch メトリクスのデータポイント取得（`get_metric_statistics`）
- 期間・集計統計（Average / Sum / Maximum）の指定方法
- EC2 CPU 使用率・ネットワーク転送量などの実用メトリクス取得例

### [`cloudwatch_put_metrics.py`](cloudwatch/cloudwatch_put_metrics.py)

**インポートするモジュール**
```python
import boto3
import time
from datetime import datetime, timezone
```


- カスタムメトリクスの送信（`put_metric_data`）
- 名前空間・メトリクス名・ディメンション・単位の設定方法
- アプリケーションの業務指標（処理件数、エラー率など）を CloudWatch に記録するパターン

### [`cloudwatch_put_alarm.py`](cloudwatch/cloudwatch_put_alarm.py)

**インポートするモジュール**
```python
import boto3
```


- CloudWatch アラームの作成・更新（`put_metric_alarm`）
- 閾値・評価期間・比較演算子・アクション（SNS 通知）の設定
- EC2 インスタンスや Lambda の監視アラーム自動作成スクリプト

### [`cloudwatch_dashboard.py`](cloudwatch/cloudwatch_dashboard.py)

**インポートするモジュール**
```python
import boto3
import json
```


- CloudWatch ダッシュボードの作成・取得・更新（`put_dashboard` / `get_dashboard`）
- ウィジェット（Line / Number / Alarm）の JSON 定義方法
- 複数サービスのメトリクスを集約した運用ダッシュボードの自動生成

---

## CloudWatch Logs

### [`logs_list_log_groups.py`](cloudwatch-logs/logs_list_log_groups.py)

**インポートするモジュール**
```python
import boto3
```


- CloudWatch Logs のロググループ一覧取得（`describe_log_groups`）
- ロググループ名・保持期間・サイズの確認
- 保持期間未設定（無期限）のロググループの検出とコスト管理

### [`logs_filter_error.py`](cloudwatch-logs/logs_filter_error.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- ログストリームのフィルタリング検索（`filter_log_events`）
- キーワード（ERROR / Exception など）を使ったエラーログの抽出
- 時間範囲指定による特定期間のログ絞り込みと出力

### [`logs_insights_query.py`](cloudwatch-logs/logs_insights_query.py)

**インポートするモジュール**
```python
import boto3
import time
from datetime import datetime, timezone, timedelta
```


- CloudWatch Logs Insights によるクエリ実行（`start_query` / `get_query_results`）
- エラー集計・レスポンスタイム分析などの実用クエリ例
- クエリ完了待機（ポーリング）と結果の整形出力

### [`logs_retention_policy.py`](cloudwatch-logs/logs_retention_policy.py)

**インポートするモジュール**
```python
import boto3
```


- ロググループの保持期間設定（`put_retention_policy`）と削除（`delete_retention_policy`）
- 全ロググループへの保持期間一括適用スクリプト
- コンプライアンス要件に応じた保持期間（30 日・90 日・1 年など）の管理

### [`logs_describe_streams.py`](cloudwatch-logs/logs_describe_streams.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone
```


- ロググループ内のログストリーム一覧取得（`describe_log_streams`）
- 最終イベント時刻・サイズ・ストリーム名の確認
- 長期間更新のない古いログストリームの検出と整理

---

## Lambda

### [`lambda_list_functions.py`](lambda/lambda_list_functions.py)

**インポートするモジュール**
```python
import boto3
```


- Lambda 関数の一覧取得（`list_functions`）
- 関数名・ランタイム・メモリサイズ・タイムアウト・最終更新日の整形出力
- 古いランタイム（EOL）が設定された関数の検出

### [`lambda_update_configuration.py`](lambda/lambda_update_configuration.py)

**インポートするモジュール**
```python
import boto3
import time
```


- Lambda 関数の設定更新（`update_function_configuration`）
- メモリサイズ・タイムアウト・環境変数・レイヤーの変更
- 複数関数へ設定を一括適用するバッチ更新スクリプト

### [`lambda_invoke.py`](lambda/lambda_invoke.py)

**インポートするモジュール**
```python
import boto3
import json
```


- Lambda 関数の同期（`RequestResponse`）・非同期（`Event`）呼び出し
- ペイロードの渡し方とレスポンスの解析（FunctionError の検出）
- Dry Run による実行可能性の確認と実行結果のログ出力

### [`lambda_concurrency.py`](lambda/lambda_concurrency.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- Lambda 関数の予約済み同時実行数（`put_function_concurrency`）の設定と確認
- プロビジョニング済み同時実行数（`put_provisioned_concurrency_config`）の設定
- アカウントレベルの同時実行数上限と関数ごとの使用状況の確認

### [`lambda_aliases_versions.py`](lambda/lambda_aliases_versions.py)

**インポートするモジュール**
```python
import boto3
```


- Lambda 関数のバージョン発行（`publish_version`）とエイリアス管理（`create_alias` / `update_alias`）
- カナリアデプロイのためのエイリアスルーティング設定（`RoutingConfig`）
- バージョン一覧取得と古いバージョンの整理

---

## ECS

### [`ecs_list_clusters_services.py`](ecs/ecs_list_clusters_services.py)

**インポートするモジュール**
```python
import boto3
```


- ECS クラスター一覧（`list_clusters`）とサービス一覧（`list_services`）の取得
- クラスター・サービスの ARN から詳細情報（`describe_clusters` / `describe_services`）の取得
- 稼働中タスク数・希望タスク数・サービスステータスの確認

### [`ecs_service_task_count.py`](ecs/ecs_service_task_count.py)

**インポートするモジュール**
```python
import boto3
```


- ECS サービスの希望タスク数（`desiredCount`）・実行中タスク数（`runningCount`）の確認
- サービスのスケールアウト／スケールイン（`update_service`）の実装
- タスク数の不一致（デプロイ失敗・スタック状態）の検出

### [`ecs_rolling_restart.py`](ecs/ecs_rolling_restart.py)

**インポートするモジュール**
```python
import boto3
```


- ECS サービスのローリングリスタート（`update_service` + `forceNewDeployment`）
- デプロイ完了までのウェイト処理（`services_stable`）の実装
- 環境変数の変更なしにコンテナを再起動する運用オペレーション

### [`ecs_list_tasks.py`](ecs/ecs_list_tasks.py)

**インポートするモジュール**
```python
import boto3
```


- ECS クラスター内の実行中タスク一覧（`list_tasks`）と詳細情報（`describe_tasks`）の取得
- タスク ID・タスク定義・起動タイプ・プライベート IP の確認
- 特定サービスやコンテナインスタンス上のタスク絞り込み

### [`ecs_task_definition.py`](ecs/ecs_task_definition.py)

**インポートするモジュール**
```python
import boto3
import json
```


- タスク定義の一覧取得（`list_task_definitions`）と詳細確認（`describe_task_definition`）
- コンテナ定義（イメージ・CPU・メモリ・環境変数・ポートマッピング）の読み取り
- 既存タスク定義を元に新しいリビジョンを登録するパターン

---

## SSM

### [`ssm_send_command.py`](ssm/ssm_send_command.py)

**インポートするモジュール**
```python
import boto3
import time
```


- SSM Run Command（`send_command`）による EC2 インスタンスへのリモートコマンド実行
- コマンド実行結果の取得（`get_command_invocation`）と成否判定
- 複数インスタンスへの一括コマンド実行とタグベースのターゲット指定

### [`ssm_parameter_store.py`](ssm/ssm_parameter_store.py)

**インポートするモジュール**
```python
import boto3
```


- SSM Parameter Store のパラメータ取得（`get_parameter`）・登録（`put_parameter`）・削除（`delete_parameter`）
- SecureString（KMS 暗号化）パラメータの取得と復号（`WithDecryption=True`）
- パスプレフィックスを使った階層構造パラメータの一括取得（`get_parameters_by_path`）

### [`ssm_patch_compliance.py`](ssm/ssm_patch_compliance.py)

**インポートするモジュール**
```python
import boto3
```


- SSM Patch Manager によるパッチコンプライアンス状態の取得（`describe_instance_patch_states`）
- インスタンスごとのパッチ適用状況（Compliant / NonCompliant / Missing）の確認
- 未適用パッチが存在するインスタンスの検出とレポート出力

---

## RDS

### [`rds_describe_instances.py`](rds/rds_describe_instances.py)

**インポートするモジュール**
```python
import boto3
```


- RDS インスタンスの一覧取得（`describe_db_instances`）
- インスタンス ID・エンドポイント・ステータス・エンジンバージョン・マルチ AZ 設定の確認
- メンテナンスウィンドウ・バックアップウィンドウの設定状況の確認

### [`rds_snapshot.py`](rds/rds_snapshot.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone, timedelta
```


- RDS インスタンスの手動スナップショット作成（`create_db_snapshot`）
- スナップショット一覧取得（`describe_db_snapshots`）と保持期間管理
- 古いスナップショットの検出と削除（`delete_db_snapshot`）によるコスト管理

---

## SQS

### [`sqs_queue_attributes.py`](sqs/sqs_queue_attributes.py)

**インポートするモジュール**
```python
import boto3
```


- SQS キューの一覧取得（`list_queues`）とキュー属性の取得（`get_queue_attributes`）
- メッセージ数（ApproximateNumberOfMessages）・可視性タイムアウト・保持期間の確認
- DLQ（Dead Letter Queue）の設定状況と RedrivePolicy の確認

### [`sqs_dlq_reprocess.py`](sqs/sqs_dlq_reprocess.py)

**インポートするモジュール**
```python
import boto3
import json
```


- DLQ に滞留したメッセージの取得（`receive_message`）と元キューへの再送信
- メッセージ属性を保持した再処理フローの実装
- 再処理後のメッセージ削除（`delete_message`）と処理件数のカウント

---

## SNS

### [`sns_publish.py`](sns/sns_publish.py)

**インポートするモジュール**
```python
import boto3
import json
from datetime import datetime, timezone
```


- SNS トピックへのメッセージパブリッシュ（`publish`）
- メッセージ属性（MessageAttributes）を使ったフィルタリング対応の発行
- FIFO トピックへの発行（`MessageGroupId` / `MessageDeduplicationId`）の実装

---

## VPC

### [`vpc_describe_network.py`](vpc/vpc_describe_network.py)

**インポートするモジュール**
```python
import boto3
```


- VPC・サブネット・ルートテーブル・インターネットゲートウェイの一覧取得
- サブネットのパブリック／プライベート判定（ルートテーブルの IGW 経路確認）
- VPC フローログの有効化状況の確認とネットワーク構成のサマリー出力

---

## Secrets Manager

### [`secretsmanager_get_put.py`](secrets-manager/secretsmanager_get_put.py)

**インポートするモジュール**
```python
import boto3
import json
from datetime import datetime, timezone
```


- シークレットの取得（`get_secret_value`）と登録・更新（`create_secret` / `update_secret`）
- JSON 形式のシークレット（DB 認証情報など）の取得とパース
- Lambda 実行環境のライフサイクルを活用したグローバルキャッシュパターン

---

## SES

### [`ses_list_identities.py`](ses/ses_list_identities.py)

**インポートするモジュール**
```python
import boto3
```


- SES に登録済みのアイデンティティ（メールアドレス・ドメイン）の一覧取得（`list_identities`）
- 各アイデンティティの検証ステータス（`get_identity_verification_attributes`）の確認
- 未検証アイデンティティの検出と検証メール再送信（`verify_email_identity`）

### [`ses_dkim_spf_status.py`](ses/ses_dkim_spf_status.py)

**インポートするモジュール**
```python
import boto3
```


- DKIM 設定の取得（`get_identity_dkim_attributes`）と有効化状況の確認
- SPF・DMARC の設定確認（`get_identity_mail_from_domain_attributes`）
- メール到達性向上のための認証設定状況レポート出力

### [`ses_send_email.py`](ses/ses_send_email.py)

**インポートするモジュール**
```python
import boto3
from botocore.exceptions import ClientError
```


- SES によるメール送信（`send_email`）の実装
- テキスト／HTML のマルチパートメール・宛先（To / CC / BCC）・返信先（ReplyToAddresses）の設定
- 設定セット（ConfigurationSet）を使った送信イベント追跡の有効化

### [`ses_send_statistics.py`](ses/ses_send_statistics.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone
```


- SES の送信統計（`get_send_statistics`）の取得
- 送信数・バウンス数・苦情数・拒否数のデータポイント集計
- バウンス率・苦情率の算出とアカウント送信制限リスクの監視

### [`ses_suppression_list.py`](ses/ses_suppression_list.py)

**インポートするモジュール**
```python
import boto3
from datetime import datetime, timezone
```


- SES アカウントレベルのサプレッションリストの取得（`list_suppressed_destinations`）
- サプレッション登録理由（BOUNCE / COMPLAINT）ごとの件数確認
- 特定アドレスのサプレッション解除（`delete_suppressed_destination`）の実装

---

## 共通事項

| 項目 | 内容 |
|------|------|
| ランタイム | Python 3.12 |
| AWS SDK | boto3 |
| 認証 | IAM ロール（EC2 / Lambda）または AWS CLI プロファイル |
| リージョン | 環境変数 `AWS_DEFAULT_REGION` または boto3 クライアント生成時に指定 |
| エラーハンドリング | `botocore.exceptions.ClientError` をキャッチし、エラーコードで分岐 |
