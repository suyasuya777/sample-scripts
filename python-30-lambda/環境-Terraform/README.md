# Lambda 学習用テスト環境（Terraform）

> **【重要】この README の日付はすべて旧日程（3/1〜3/31）のままです。**
> 実際の日程は 3/15〜4/14 で、読み替えは「旧日程 ＋14日」です（例：3/4 → 3/18、3/25 → 4/8）。
> ただし **API Gateway・Cognito の3日だけは ＋13日**（3/10・3/11・3/12 → 3/23・3/24・3/25）。
> **日付と手順は `【SRE】Lambdaテスト環境構築手順.md` に従ってください。**

`Lambda学習スケジュール_2027年3月.md` の環境タイムラインに対応した Terraform 一式です。

## 構成

```
lambda-study-tf/
├── versions.tf                  provider・データソース・locals
├── variables.tf                 変数とステージ有効化フラグ
├── terraform.tfvars.example     → terraform.tfvars にリネームして使う
├── modules/lambda_fn/           Lambda 1本ぶんの型（関数+ロール+ロググループ）
├── stage1_base.tf               3/1  EventBridge / Secrets / SSM
├── stage2_s3_sns.tf             3/4  S3 / SNS
├── stage3_apigw_cognito.tf      3/10 HTTP API・3/11 Cognito
├── stage4_sqs_dynamodb.tf       3/15 SQS・3/18 DynamoDB・error_handling_dlq
├── stage5_integration.tf        3/22 api_gateway_dynamodb_ses_integration
├── stage6_rds.tf                3/25 VPC / RDS / RDS Proxy（3/26 中に削除）
├── stage7_sfn_powertools.tf     3/28 Step Functions・3/29 Powertools
├── outputs.tf
└── scripts/build_layers.sh      pymysql Layer のビルド
```

**ディレクトリ1つ、state 1つ**です。2月の boto3 環境と同じ構成なので、扱い方は同じです。

## 前提

- Terraform >= 1.6、AWS CLI v2、Python 3.12（Layer ビルド用）
- **Lambda 実務サンプル集を展開したディレクトリ**（`samples_dir` に絶対パスを指定）
- SES で検証済みのメールアドレス（2月に済んでいるはず）

## 初回（3/1）

```bash
cp terraform.tfvars.example terraform.tfvars
vi terraform.tfvars    # samples_dir と notification_email は必須

export AWS_DEFAULT_REGION=ap-northeast-1
terraform init
terraform plan         # 必ず読む
terraform apply

# ログが出ることを確認
aws lambda invoke --function-name $(terraform output -raw fn_scheduled) \
  --cli-binary-format raw-in-base64-out --payload '{}' /tmp/out.json && cat /tmp/out.json
aws logs tail /aws/lambda/$(terraform output -raw fn_scheduled) --follow
```

## 環境タイムラインとコマンド

| 日付 | 操作 | コマンド |
|---|---|---|
| **3/1(月)** | 基盤構築 | `terraform apply` |
| **3/4(木)** | S3・SNS | `enable_s3_sns = true` → `apply` |
| **3/10(水)** | HTTP API | `enable_apigw = true` → `apply` |
| **3/11(木)** | Cognito | `enable_cognito = true` → `apply` |
| **3/15(月)** | SQS | `enable_sqs = true` → `apply` |
| **3/18(木)** | DynamoDB | `enable_dynamodb = true` → `apply` |
| **3/22(月)** | 統合サンプル | `enable_integration = true` → `apply` |
| **3/25(木)** | VPC・RDS | `bash scripts/build_layers.sh` → `enable_rds = true` → `apply`（約15分） |
| **3/26(金)夜** | **RDS 削除** | `enable_rds = false` → `apply` |
| **3/28(日)** | Step Functions | `enable_sfn = true` → `apply` |
| **3/29(月)** | Powertools | `enable_powertools = true` → `apply` |
| **3/31(水)** | 全削除 | `terraform destroy` |

**3/26 の戻し忘れが唯一の費用リスク**です（RDS + Proxy + VPCエンドポイントで約 $1.3/日）。`apply` の完了確認までがその日の作業です。

## 各日の演習との対応

Terraform 側に「演習のために意図的にそうしてある」箇所があります。

| 日付 | 演習 | Terraform 側の仕込み |
|---|---|---|
| 3/2 | リソースベースポリシー | `aws_lambda_permission.scheduled`。**一度消して apply し、起動しなくなることを見る** |
| 3/3 | SecureString と KMS | `secrets_reader` の `kms:Decrypt` statement。**外して AccessDenied を出す** |
| 3/5 | 無限ループ防止 | `filter_prefix = "uploads/"` と出力先 `out/`。**プレフィックスを揃えると無限ループする** |
| 3/8 | REST と HTTP API の event 差 | `payload_format_version = "1.0"`。**"2.0" に変えると 405 が返るようになる** |
| 3/16 | SNS→SQS の入れ子 body | `raw_message_delivery = false`。**true にすると入れ子が消える** |
| 3/17 | 部分失敗 | `function_response_types = ["ReportBatchItemFailures"]`。**コメントアウトして10件全部が再試行されるのを見る** |
| 3/18 | シャードの詰まり | `maximum_retry_attempts` と `bisect_batch_on_function_error`。**外して詰まる挙動を見てから戻す** |
| 3/19 | 2種類の DLQ | `dlq_target_arn`（関数設定）と `DLQ_URL` 環境変数（アプリが自分で送る）の両方を渡してある |
| 3/21 | 冪等性 | `aws_dynamodb_table.idempotency` と `IDEMPOTENCY_TABLE` 環境変数。**コード側の `set()` をここに差し替える** |
| 3/25 | VPC の閉じ込め | **IGW も NAT も作っていない。** VPCエンドポイントを一時的に外せば「固まる」挙動を再現できる |
| 3/30 | X-Ray | `tracing_mode = "Active"`。IAM ポリシーはモジュールが自動で付ける |

## 手動作業が残るもの

| 時期 | 作業 |
|---|---|
| 3/1 | 予算アラートの作成（$15 程度で十分） |
| 3/4 | **SNS 購読確認メールのリンクを踏む**（`protocol = "email"` は確認が手動） |
| 3/25 | **`scripts/build_layers.sh` を apply の前に実行**（zip が無いと apply が失敗する） |
| 3/29 | **Powertools レイヤーのバージョン確認**（`powertools_layer_version` を最新に） |

## 注意点

**Powertools レイヤーのバージョンは既定値のままだと失敗する可能性が高い**です。最新版を確認してから `terraform.tfvars` を更新してください。

```bash
aws lambda list-layer-versions --region ap-northeast-1 \
  --layer-name arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64 \
  --query 'LayerVersions[0].Version'
```

**`ignore_changes = [environment]` をモジュールに入れてあります。** 3/21 の冪等性改造などでコンソールから環境変数を触っても、次の `apply` で巻き戻りません。裏返すと、**tfvars で環境変数を変えても反映されません。** 反映したいときは一度 `terraform state rm` するか、モジュールの `lifecycle` を一時的に外してください。

**教材のコードは環境変数を読まない箇所があります。** `error_handling_dlq.py` の `DLQ_URL` や `handler.py` の `NOTIFY_EMAIL` はハードコードされています。Terraform 側から環境変数は渡していますが、**コードを `os.environ` を読む形に直すのは演習の一部**です（3/21 で扱います）。

**state に機密が入ります。** RDS のパスワードとシークレットの中身が平文で `terraform.tfstate` に保存されます。`.gitignore` に `*.tfstate*`、`terraform.tfvars`、`.build/` を入れてください。

**このコードは実環境で apply して検証していません。** 必ず `terraform plan` を読んでから実行してください。特に Cognito の `lambda_config`、RDS Proxy の各リソース、Powertools レイヤー ARN はプロバイダのバージョンで挙動が変わります。

## 概算コスト

| 項目 | 期間 | 概算 |
|---|---|---|
| Lambda・SQS・SNS・DynamoDB・EventBridge・Step Functions | 全期間 | ほぼ無料枠 |
| API Gateway（HTTP API） | 全期間 | 1ドル未満 |
| Cognito | 全期間 | 無料枠（50,000 MAU） |
| Secrets Manager（2シークレット） | 全期間 | 約 $1 |
| CloudWatch Logs・X-Ray | 全期間 | 約 $1 |
| **RDS + RDS Proxy + VPCエンドポイント** | **3/25〜3/26 の2日** | **約 $3** |
| **合計** | | **約 $5〜8** |

2月（$60〜70）と比べてかなり軽くなります。予算アラートは $15 で十分です。
