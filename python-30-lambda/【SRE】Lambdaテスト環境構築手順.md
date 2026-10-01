# Lambda 学習用テスト環境 構築手順

対象期間：2027/3/15（月）〜 4/14（水）（`【SRE】2027年03月学習進捗表ーLambda.md` と同じ日程）
使うもの：`環境-Terraform.zip`（Terraform 一式）／`lambda.zip`（サンプル集14本）
方針：**基本は作りっぱなし。** ただし RDS まわり（RDS・RDS Proxy・VPCエンドポイント）だけは 4/8 に作って 4/9 中に消します。

**コマンドはすべて WSL2 の Ubuntu で実行します。** 第3章以降は Terraform のフォルダ（`~/lambda-study-tf`）に移動してから実行してください。

> **zip 内の `README.md`・`terraform.tfvars.example` のコメント・`variables.tf` の説明文・`scripts/build_layers.sh` のコメントは、すべて旧日程（3/1〜3/31）のままです。** 日付はこの手順書に従ってください。読み替えは「旧日程 ＋14日」です（例：README の 3/4 → 3/18、3/25 → 4/8）。ただし **API Gateway・Cognito の3日だけは ＋13日**（README の 3/10・3/11・3/12 → 3/23・3/24・3/25）です。第2期を組み直したためにここだけ1日前倒しになっています。

---

## 1. 事前準備（3/15 より前に1回だけ）

### 1-1. ツールを入れる

2月の boto3 環境をそのまま使うなら、バージョン確認だけで次に進んでください。

```bash
terraform version      # 1.6 以上
aws --version          # 2.x
python3 -V             # 3.12（Layer を Lambda の実行環境に合わせるため）
zip -v | head -2       # build_layers.sh が使う
```

`zip` が無い場合だけ入れます。

```bash
sudo apt install -y zip
```

### 1-2. AWS の認証

2月と同じアカウント・同じ IAM ユーザで構いません。

```bash
aws sts get-caller-identity
echo $AWS_DEFAULT_REGION      # ap-northeast-1 であること
```

**SES で検証済みのメールアドレスが必要です。** 2月（3/5 の `ses_send_email.py`）で検証したアドレスがそのまま使えます。消えていないか確認しておきます。

```bash
aws ses list-identities --identity-type EmailAddress
aws ses get-identity-verification-attributes --identities <自分のアドレス>
```

`Success` でなければ、4/7 の SES 送信が失敗します。先に検証し直してください。

```bash
aws ses verify-email-identity --email-address <自分のアドレス>   # 届いたメールのリンクを踏む
```

### 1-3. ファイルを置く

```bash
cd ~
unzip -q "/mnt/c/Users/<Windowsのユーザ名>/Downloads/環境-Terraform.zip"
mv ./*Terraform ~/lambda-study-tf

mkdir -p ~/lambda-samples
unzip -q "/mnt/c/Users/<Windowsのユーザ名>/Downloads/lambda.zip" -d ~/lambda-samples
ls ~/lambda-samples          # 14個のディレクトリが見えればOK
```

`/mnt/c/...`（Windows 側）に置いたまま作業しないでください。`archive_file` の zip 化が遅くなります。

### 1-4. 構成を確認する

配布した zip は次の構成になっています。**`stage1〜stage7.tf` が `./modules/lambda_fn` を参照するので、この配置が崩れていると `terraform init` が `Module not found` で失敗します。** 展開直後に確認しておいてください。

```
lambda-study-tf/
├── versions.tf                versions・データソース・locals
├── variables.tf               ルートの変数とステージ有効化フラグ
├── outputs.tf                 ルートの出力
├── terraform.tfvars.example   → terraform.tfvars にリネームして使う
├── modules/lambda_fn/         Lambda 1本ぶんの型（main.tf / variables.tf / outputs.tf）
├── stage1_base.tf 〜 stage7_sfn_powertools.tf
├── scripts/build_layers.sh    pymysql Layer のビルド
└── README.md
```

```bash
cd ~/lambda-study-tf
ls modules/lambda_fn                            # main.tf  outputs.tf  variables.tf
grep -c 'variable "samples_dir"' variables.tf   # 1 ならOK
grep -c 'output "fn_scheduled"'  outputs.tf     # 1 ならOK
ls scripts/build_layers.sh                      # 存在すればOK
```

**ルートの `variables.tf` を開いて `variable "name"`（関数名）が先頭に来ていたら、それはモジュール側の変数定義です。** 古い配布物を展開しています。その場合は次で組み直してください。

```bash
mkdir -p modules/lambda_fn scripts
mv main.tf variables.tf outputs.tf modules/lambda_fn/
mv mnt/user-data/outputs/lambda-study-tf/variables.tf .
mv mnt/user-data/outputs/lambda-study-tf/outputs.tf  .
mv build_layers.sh scripts/
rm -rf mnt
```

### 1-5. 設定ファイルを作る

```bash
cp terraform.tfvars.example terraform.tfvars
vi terraform.tfvars
```

書き換えるのは次の3か所です。

| 項目 | 設定する値 |
|---|---|
| `samples_dir` | `~/lambda-samples` の**絶対パス**（例 `/home/nakata/lambda-samples`）。**末尾のスラッシュは付けない**。`~` は展開されないので使わない |
| `notification_email` | 1-2 で確認した**SES検証済みのアドレス**（SNS購読の宛先も兼ねる） |
| `allowed_signup_domain` | 自分のメールアドレスのドメイン（3/25 のサインアップ演習で、このドメインだけが自動承認される） |

`enable_*` はすべて `false` のままにしておきます。該当日に1つずつ `true` にします。

---

## 2. ガードレール（3/15 の最初に実施）

### 2-1. 予算アラート

2月の `boto3-study` 予算とは別名で作ります（残っていても構いません）。

```bash
cd ~/lambda-study-tf

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
EMAIL=$(grep '^notification_email' terraform.tfvars | cut -d'"' -f2)
echo "アカウント: $ACCOUNT / 通知先: $EMAIL"     # 実アドレスが出ることを確認

cat > /tmp/budget.json <<'EOF'
{
  "BudgetName": "lambda-study",
  "BudgetLimit": { "Amount": "15", "Unit": "USD" },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
EOF

cat > /tmp/notify.json <<EOF
[{
  "Notification": {
    "NotificationType": "ACTUAL",
    "ComparisonOperator": "GREATER_THAN",
    "Threshold": 80,
    "ThresholdType": "PERCENTAGE"
  },
  "Subscribers": [{ "SubscriptionType": "EMAIL", "Address": "$EMAIL" }]
}]
EOF

aws budgets create-budget --account-id "$ACCOUNT" \
  --budget file:///tmp/budget.json \
  --notifications-with-subscribers file:///tmp/notify.json
```

**通知は月$12（$15の80%）を超えたときに届きます。** この環境の通常の利用額は期間全体で $5〜8 なので、超えるのは **4/9 の RDS の消し忘れ**がほぼ唯一の原因です。

> 3月の請求には 2月の boto3 環境（3/1〜3/14 ぶん、約$40）も乗ります。**予算は環境ごとに分かれていないので、3月の通知は無視せず必ず内訳を見てください。** 4月になれば lambda-study のぶんだけになります。

### 2-2. リージョンを固定する

```bash
echo 'export AWS_DEFAULT_REGION=ap-northeast-1' >> ~/.bashrc
source ~/.bashrc
```

---

## 3. 日別の作業

### 一覧

| 日付 | やること | コマンド | 所要 |
|---|---|---|---|
| **3/15（月）** | ガードレール／**基盤を作る** | `terraform init` → `terraform apply` | 約10分 |
| **3/16（火）** | 演習：権限を一度消して戻す | `terraform destroy -target=aws_lambda_permission.scheduled` → `apply` | 約5分 |
| **3/18（木）** | **S3・SNS を作る**／確認メール1通 | `enable_s3_sns = true` → `apply` | 約3分 |
| **3/23（火）** | **API Gateway を作る** | `enable_apigw = true` → `apply` | 約3分 |
| **3/24（水）** | **Cognito を作る** | `enable_cognito = true` → `apply` | 約3分 |
| **3/29（月）** | **SQS を作る** | `enable_sqs = true` → `apply` | 約3分 |
| **3/31（水）** | 演習：部分失敗の有効／無効 | `function_response_types` をコメントアウト → `apply` → 戻して `apply`（**apply 2回**） | 約10分 |
| **4/1（木）** | **DynamoDB を作る**／3/15 に外した2行を戻す | `enable_dynamodb = true` → `apply` | 約5分 |
| **4/5（月）** | **統合サンプルを作る** | `enable_integration = true` → `apply` | 約3分 |
| **4/8（木）** | **Layer をビルド → RDS 一式を作る** | `bash scripts/build_layers.sh` → `enable_rds = true` → `apply` | 約15分 |
| **4/9（金）** | **RDS 一式をその日のうちに消す** | `enable_rds = false` → `apply` | 約10分 |
| **4/11（日）** | **Step Functions を作る** | `enable_sfn = true` → `apply` | 約3分 |
| **4/12（月）** | レイヤー版数を確認 → **Powertools を作る** | `enable_powertools = true` → `apply` | 約5分 |
| **4/13（火）** | 予約済み同時実行数（CLI） | `aws lambda put-function-concurrency` → 演習後に `delete-function-concurrency` | 約5分 |
| **4/14（水）** | **すべて消す** | `terraform destroy` | 約10分 |

`terraform apply` は実行前に変更内容（plan）が表示されます。**毎回、一覧を読んでから `yes` を入力してください。**

### ステージ間の依存

**フラグは上の順番どおりに立ててください。** 次の3か所は、先のステージのリソースを直接参照しています。順番を飛ばすと、参照が `[0]` の index エラーになって apply が落ちます。

| 立てるフラグ（日） | 先に必要なフラグ（日） | 参照しているもの |
|---|---|---|
| `enable_sqs`（3/29） | `enable_s3_sns`（3/18） | SNS→SQS 購読が stage2 の SNS トピックを参照 |
| `enable_integration`（4/5） | `enable_apigw`（3/23） | HTTP API に `/records` ルートを足す |
| `enable_powertools`（4/12） | `enable_apigw`（3/23） | HTTP API に `/powertools` ルートを足す |

`enable_cognito`・`enable_dynamodb`・`enable_sfn`・`enable_rds` は他に依存しません。**進捗表の「遅れたときの削り方」に挙がっている候補（3/21 の署名付きURL、3/24〜3/25 の Cognito、4/9 の RDS Proxy）は、いずれも依存元ではないので飛ばしても影響しません。**

---

### 3/15（月）基盤

Lambda 2本（`eventbridge_scheduled_job` / `secrets_manager_ssm`）、実行ロール、ロググループ、EventBridge ルール、Secrets Manager、SSM パラメータを作ります。

```bash
cd ~/lambda-study-tf
terraform init
terraform apply
```

**apply の前に、`eventbridge_scheduled_job.py` を2か所だけ直します。** このコードは DynamoDB のテーブルを `scan` / `delete_item` しますが、**テーブルが出来るのは 4/1 です。** そのまま invoke すると `ResourceNotFoundException` で落ちて、初日に手が止まります。

```python
# ① テーブル名を環境変数から読む（Terraform が TABLE_NAME を渡しています）
import os
TABLE_NAME = os.environ.get("TABLE_NAME", "")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME) if TABLE_NAME else None

# ② lambda_handler の中の2行を、4/1 まで外しておく
    # deleted = cleanup_old_records(cutoff)
    # report = generate_daily_report()
    deleted, report = 0, {"total": 0}
```

**4/1（DynamoDB を作る日）に②を元に戻して `terraform apply`** すると、定期実行が実際にテーブルを掃除するようになります。実行ロールの DynamoDB 権限と `TABLE_NAME` は 3/15 の時点で入れてあるので、戻すのはコードだけです。

デプロイできたか確認します。

```bash
FN=$(terraform output -raw fn_scheduled)
aws lambda invoke --function-name "$FN" \
  --cli-binary-format raw-in-base64-out --payload '{}' /tmp/out.json && cat /tmp/out.json
aws logs tail "/aws/lambda/$FN" --since 5m
```

**ログが出たらこの日の目標は達成です。** EventBridge のルールは `rate(5 minutes)` なので、5分待つと自動でも起動します（3/16 の確認材料になります）。

### 3/16（火）EventBridge

構築作業はありません。演習で `aws_lambda_permission.scheduled` を一度消します。

```bash
terraform destroy -target=aws_lambda_permission.scheduled     # 起動しなくなることをログで確認
terraform apply                                               # 元に戻す
```

### 3/18（木）S3・SNS

```bash
# terraform.tfvars で enable_s3_sns = true
terraform apply
```

**`notification_email` 宛に SNS の購読確認メールが届きます**（件名：AWS Notification - Subscription Confirmation）。**リンクを踏まないと 3/21 の `sns_publisher.py` でメールが届きません。**

トリガの対象は `uploads/` プレフィックスだけです。出力は `out/` に書かれます（無限ループ防止）。

```bash
BUCKET=$(terraform output -raw s3_bucket)
echo "a,b,c" > /tmp/sample.csv
aws s3 cp /tmp/sample.csv "s3://$BUCKET/uploads/sample.csv"
```

### 3/23（火）API Gateway

```bash
# enable_apigw = true
terraform apply

API=$(terraform output -raw api_endpoint)
curl -i "$API/items"
curl -i -X POST "$API/items" -H 'Content-Type: application/json' -d '{"id":"1","name":"test"}'
```

教材の `rest_api.py` は `event["httpMethod"]` を読むため、**ペイロード形式 1.0 を明示してあります。** 3/22 の「REST と HTTP で `event` の形が違う」を実際に見るには、`stage3_apigw_cognito.tf` の `payload_format_version` を `"2.0"` にして apply し、405 が返るようになることを確認してから戻してください。

### 3/24（水）Cognito

```bash
# enable_cognito = true
terraform apply
terraform output cognito_user_pool_id
terraform output cognito_client_id
```

### 3/25（木）サインアップの実行

```bash
CLIENT=$(terraform output -raw cognito_client_id)
aws cognito-idp sign-up --client-id "$CLIENT" \
  --username you@<許可ドメイン> --password 'StudyOnly12345!' \
  --user-attributes Name=email,Value=you@<許可ドメイン>

# 禁止ドメインで拒否されることも確認する
aws cognito-idp sign-up --client-id "$CLIENT" \
  --username you@notallowed.example --password 'StudyOnly12345!' \
  --user-attributes Name=email,Value=you@notallowed.example
```

**コード側の `ALLOWED_DOMAINS` はハードコードです。** 第4章のとおり、実行前に自分のドメインへ直してください。

### 3/29（月）SQS

```bash
# enable_sqs = true
terraform apply
terraform output sqs_main_url
terraform output sqs_from_sns_url
terraform output sqs_dlq_url
```

### 3/31（水）部分失敗の実測

構築ではなく設定の切り替えです。`stage4_sqs_dynamodb.tf` の `aws_lambda_event_source_mapping.sqs_main` にある

```hcl
function_response_types = ["ReportBatchItemFailures"]
```

を**コメントアウトして `apply`** し、10件中1件を失敗させて10件すべてが再試行されることを確認します。戻して `apply` すると、失敗した1件だけになります。

### 4/1（木）DynamoDB

```bash
# enable_dynamodb = true
terraform apply
terraform output dynamodb_items_table
terraform output dynamodb_idempotency_table
```

シャードの詰まりを見るなら、`aws_lambda_event_source_mapping.streams` の `maximum_retry_attempts` と `bisect_batch_on_function_error` を一時的に外して `apply` します。**見たあとは必ず戻してください。**

**あわせて、3/15 に外した `eventbridge_scheduled_job.py` の2行を戻します。** テーブルができたので、ここから定期実行が実際に動きます。

```python
    deleted = cleanup_old_records(cutoff)
    report = generate_daily_report()
```

```bash
terraform apply     # ソースの変更を archive_file が拾って関数コードが更新される
aws lambda invoke --function-name "$(terraform output -raw fn_scheduled)" \
  --cli-binary-format raw-in-base64-out --payload '{}' /tmp/out.json && cat /tmp/out.json
```

`{"deleted": 0, "report": {"total": 0}}` のように返れば、権限もテーブル名も通っています。

### 4/5（月）統合サンプル

**前提は `enable_apigw` が `true` であることだけです。** HTTP API に `/records` ルートを足す作りなので、API Gateway が無いと apply が失敗します。統合用の DynamoDB テーブルは `stage5_integration.tf` が自前で作るので、`enable_dynamodb` は関係ありません（日程上は 4/1 に有効化済みですが、前提ではありません）。

```bash
# enable_integration = true
terraform apply
terraform output integration_table
```

### 4/8（木）RDS 一式（当日作成）

**Layer のビルドを先に実行します。** zip が無いと apply が失敗します。

```bash
cd ~/lambda-study-tf
bash scripts/build_layers.sh          # .build/pymysql-layer.zip ができる
ls -la .build/pymysql-layer.zip

# enable_rds = true
terraform apply                       # RDS の作成に約10〜15分
```

**「VPC Lambda はインターネットに出られない」の実測**は、作られた VPCエンドポイントを一時的に外して行います。ファイルを書き換える必要はありません。

```bash
terraform destroy -target=aws_vpc_endpoint.secretsmanager

FN=lambda-study-vpc-rds-connection
aws lambda invoke --function-name "$FN" \
  --cli-binary-format raw-in-base64-out --payload '{}' /tmp/out.json
# → get_secret が返らず、30秒のタイムアウトで落ちる。ログで確認する
```

### 4/9（金）VPCエンドポイントと Proxy、そして削除

```bash
terraform apply        # エンドポイントが戻り、疎通するようになる
aws lambda invoke --function-name lambda-study-vpc-rds-connection \
  --cli-binary-format raw-in-base64-out --payload '{}' /tmp/out.json && cat /tmp/out.json
```

**RDS Proxy 経由で接続するときの注意。** シークレットの `host` は RDS インスタンスのアドレスです。Proxy を通すには、`vpc_rds_connection.py` の接続先を環境変数 `DB_HOST`（＝Proxy のエンドポイント）から読むように1行変える必要があります。

```python
host=os.environ.get("DB_HOST", secret["host"]),
```

**演習が終わったら、その日のうちに消します。**

```bash
# enable_rds = false
terraform apply        # 約10分
```

一覧に **VPC・RDS・RDS Proxy・VPCエンドポイント・Layer・`fn_vpc_rds` が削除（destroy）対象**として出ていることを確認して `yes` を入力します。完了後、残っていないことを確認します。

```bash
aws rds describe-db-instances --query 'DBInstances[].DBInstanceIdentifier'   # [] ならOK
aws rds describe-db-proxies --query 'DBProxies[].DBProxyName'                # [] ならOK
aws ec2 describe-vpc-endpoints --query 'VpcEndpoints[].ServiceName'          # [] ならOK
```

**消し忘れると1日 $1.9 かかります。** 確認まで終えて、その日の作業完了です。

### 4/11（日）Step Functions

```bash
# enable_sfn = true
terraform apply
aws stepfunctions start-execution \
  --state-machine-arn "$(terraform output -raw sfn_sequential_arn)" \
  --input '{"task":"first"}'
```

### 4/12（月）Powertools

**マネージドレイヤーのバージョンを先に確認します。** 既定値（`3`）のままだと存在しない版数を指して apply が失敗します。

```bash
aws lambda list-layer-versions --region ap-northeast-1 \
  --layer-name arn:aws:lambda:ap-northeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64 \
  --query 'LayerVersions[0].Version'
```

出た数字を `terraform.tfvars` の `powertools_layer_version` に入れてから、

```bash
# enable_powertools = true
terraform apply
curl -i "$(terraform output -raw api_endpoint)/powertools"
```

X-Ray は `stage7_sfn_powertools.tf` の `tracing_mode = "Active"` で有効になります（4/13 の演習）。IAM ポリシーはモジュールが自動で付けます。

### 4/13（火）予約済み同時実行数

Terraform からは渡していないので、CLI で当てて外します。**外し忘れるとアカウントの共有枠を1つ食い続けます。**

```bash
FN=lambda-study-powertools-middleware

aws lambda put-function-concurrency --function-name "$FN" \
  --reserved-concurrent-executions 1

# 並行 invoke でスロットリングを起こす
for i in $(seq 1 10); do
  aws lambda invoke --function-name "$FN" --invocation-type Event \
    --cli-binary-format raw-in-base64-out --payload '{}' /tmp/out$i.json &
done; wait

# Throttles メトリクスで確認
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Throttles \
  --dimensions Name=FunctionName,Value="$FN" \
  --start-time "$(date -u -d '15 min ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --period 60 --statistics Sum

# 必ず戻す
aws lambda delete-function-concurrency --function-name "$FN"
aws lambda get-function-concurrency --function-name "$FN"    # 空ならOK
```

X-Ray（`tracing_mode = "Active"`）は 4/12 の apply で既に有効になっています。

### 4/14（水）すべて消す

```bash
terraform destroy
```

一覧を確認して `yes` を入力し、第7章のチェックリストを確認します。予算アラートも消す場合は次のとおりです（残しても費用はかかりません）。

```bash
aws budgets delete-budget --account-id "$(aws sts get-caller-identity --query Account --output text)" --budget-name lambda-study
```

---

## 4. デプロイ前に直すコードの定数

**教材14本のうち7本は、バケット名やARNをソースにハードコードしています。** Terraform 側は環境変数を渡していますが、**コードが `os.environ` を読んでいないので、そのままでは動きません。**

直し方は2通りあります。**推奨は後者**です（4/4 の「`DLQ_URL` を環境変数に出す」と同じ作業で、そのまま演習になります）。

```python
BUCKET_NAME = "lambda-study-data-123456789012"          # ① 値を直接書く
BUCKET_NAME = os.environ.get("BUCKET_NAME", "")         # ② 環境変数から読む（推奨）
```

| 使う日 | ファイル | 定数 | 入れる値 |
|---|---|---|---|
| **3/15・4/1** | `eventbridge_scheduled_job.py` | `dynamodb.Table("items")` | **`os.environ["TABLE_NAME"]` から読む形に直す**（Terraform が `lambda-study-items` を渡している）。**3/15 はハンドラ内の `cleanup_old_records` と `generate_daily_report` の呼び出しを外し、4/1 に戻す**（§3 の 3/15・4/1） |
| 3/21 | `s3_presigned_url.py` | `BUCKET_NAME` | `terraform output -raw s3_bucket`（環境変数 `BUCKET_NAME` / `EXPIRES_IN` が渡っている） |
| 3/21 | `sns_publisher.py` | `STANDARD_TOPIC_ARN`<br>`FIFO_TOPIC_ARN` | `terraform output -raw sns_topic_arn`<br>`aws sns list-topics --query "Topics[?ends_with(TopicArn,'.fifo')].TopicArn" --output text`（環境変数 `TOPIC_ARN` / `FIFO_TOPIC_ARN`） |
| 3/25 | `cognito_pre_signup_trigger.py` | `ALLOWED_DOMAINS` | `terraform.tfvars` の `allowed_signup_domain` と同じ値（環境変数 `ALLOWED_DOMAIN`） |
| 4/2・4/4 | `error_handling_dlq.py` | `DLQ_URL` | `terraform output -raw sqs_dlq_url`（環境変数 `DLQ_URL` / `IDEMPOTENCY_TABLE`） |
| 4/5〜4/7 | `db.py` | `TABLE_NAME` | `terraform output -raw integration_table`（環境変数 `TABLE_NAME`） |
| 4/5〜4/7 | `handler.py` | `NOTIFY_EMAIL` | SES検証済みアドレス（環境変数 `NOTIFY_EMAIL`） |
| 4/5〜4/7 | `mailer.py` | `SENDER` | SES検証済みアドレス（環境変数 `SES_SOURCE`）。**サンドボックスなので送信元も宛先も検証済みでなければ送れない** |
| 4/8・4/9 | `vpc_rds_connection.py` | `SECRET_NAME` | `lambda-study/rds`（環境変数 `SECRET_ARN`。名前でもARNでも取得できる） |

**ソースを直したら `terraform apply` をやり直してください。** `archive_file` がソースの変更を検知して、新しい zip で関数を更新します。

> **モジュールに `ignore_changes = [environment]` が入っています。** 学習中にコンソールから環境変数を触っても巻き戻りませんが、裏返すと **tfvars 側で環境変数を変えても反映されません。** 反映させたいときは、`modules/lambda_fn/main.tf` の `lifecycle` ブロックを一時的に外してください。

---

## 5. 演習のために「わざと」そうしてある箇所

不具合ではありません。**日付はこの手順書（新日程）のものです。** zip 内 README の表は旧日程のままなので読み替えてください。

| 日付 | 演習 | 仕込み |
|---|---|---|
| 3/16 | リソースベースポリシー | `aws_lambda_permission.scheduled`。一度消すと起動しなくなる |
| 3/17 | SecureString と KMS | `fn_secrets` の `kms:Decrypt` statement。外すと AccessDenied になる |
| 3/19 | 無限ループ防止 | `filter_prefix = "uploads/"` と出力先 `out/`。揃えると無限ループする |
| 3/22 | REST と HTTP の `event` 差 | `payload_format_version = "1.0"`。`"2.0"` にすると 405 が返る |
| 3/30 | SNS→SQS の入れ子 body | `raw_message_delivery = false`。`true` にすると入れ子が消える |
| 3/31 | 部分失敗 | `function_response_types`。コメントアウトすると10件全部が再試行される |
| 4/1 | シャードの詰まり | `maximum_retry_attempts` と `bisect_batch_on_function_error`。外すと詰まる |
| 4/2 | 2種類の DLQ | `dlq_target_arn`（関数設定）と `DLQ_URL`（アプリが自分で送る）の両方を渡してある |
| 4/4 | 冪等性 | `aws_dynamodb_table.idempotency` と `IDEMPOTENCY_TABLE`。コードの `set()` をここへ差し替える |
| 4/8 | VPC の閉じ込め | **IGW も NAT も作っていない。** VPCエンドポイントを一時的に外すと「固まる」を再現できる |
| 4/13 | X-Ray | `tracing_mode = "Active"`。IAM はモジュールが自動で付ける |

---

## 6. 費用

| 項目 | 期間 | 概算 |
|---|---|---|
| Lambda・SQS・SNS・DynamoDB・EventBridge・Step Functions | 全期間 | ほぼ無料枠 |
| API Gateway（HTTP API）・Cognito | 全期間 | $1 未満 |
| Secrets Manager（2シークレット）・CloudWatch Logs・X-Ray | 全期間 | 約 $2 |
| **RDS ＋ RDS Proxy ＋ VPCエンドポイント（約$1.9/日）** | **4/8〜4/9 の2日** | **約 $4** |
| **合計** | | **約 $5〜8** |

RDS 一式の内訳は、RDS `db.t4g.micro` が約 $0.5/日、RDS Proxy が約 $0.7/日、**Secrets Manager のインタフェース型VPCエンドポイントが約 $0.67/日**です。エンドポイントは **AZ ごとの課金**（$0.014/時 × 2AZ）なので、1つぶんの $0.34 ではありません。

RDS Proxy（$0.7/日）を省くなら `enable_rds_proxy = false` にします。**接続プーリングが必要な理由を説明できれば、構築自体は省略してよい**という判断です（進捗表の「遅れたときの削り方」3番と同じ）。

予算通知が来たら、疑うのは次の2つだけです。

1. **4/9 の RDS 一式の消し忘れ**（$1.9/日）
2. 3月分の請求に 2月の boto3 環境（3/1〜3/14 ぶん）が混ざっている

---

## 7. 破棄チェックリスト（4/14 の最後に確認）

まずタグで横断確認します。

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=lambda-study \
  --query 'ResourceTagMappingList[].ResourceARN' --output table
```

| 対象 | 確認コマンド | 備考 |
|---|---|---|
| **RDS / RDS Proxy** | `aws rds describe-db-instances` / `aws rds describe-db-proxies` | **4/9 に消えているはず。最優先** |
| **VPCエンドポイント** | `aws ec2 describe-vpc-endpoints` | 同上。$0.34/日 |
| Lambda 関数 | `aws lambda list-functions --query "Functions[?starts_with(FunctionName,'lambda-study')].FunctionName"` | ― |
| Lambda Layer | `aws lambda list-layers --query "Layers[].LayerName"` | `lambda-study-pymysql` は 4/9 に消えている |
| ロググループ | `aws logs describe-log-groups --log-group-name-prefix /aws/lambda/lambda-study` | Terraform 管理下なので destroy で消える |
| API Gateway のログ | `aws logs describe-log-groups --log-group-name-prefix /aws/apigateway/lambda-study` | 同上 |
| HTTP API | `aws apigatewayv2 get-apis --query 'Items[].Name'` | ― |
| Cognito | `aws cognito-idp list-user-pools --max-results 10 --query 'UserPools[].Name'` | ― |
| DynamoDB | `aws dynamodb list-tables` | 3テーブル（items / idempotency / integration） |
| SQS | `aws sqs list-queues` | main / dlq / from-sns |
| SNS | `aws sns list-topics` | 標準と FIFO。購読も一緒に消える |
| S3 | `aws s3 ls` | `force_destroy = true` なのでオブジェクトごと消える |
| Secrets Manager | `aws secretsmanager list-secrets --query 'SecretList[].Name'` | `recovery_window_in_days = 0` なので即時削除 |
| Step Functions | `aws stepfunctions list-state-machines --query 'stateMachines[].name'` | ― |
| EventBridge ルール | `aws events list-rules --name-prefix lambda-study` | ― |
| 予約済み同時実行数 | `aws lambda get-function-concurrency --function-name lambda-study-powertools-middleware` | 4/13 の予約。関数ごと消えるが、4/13 中に外しておく |

**`terraform destroy` で消えないもの**は、この環境では次の2つだけです。

- **3/25 の Cognito サインアップで作ったユーザ** … ユーザープールごと消えるので追加作業は不要
- **`.build/` のローカル zip** … 課金なし。気になれば `rm -rf .build`

最後に、**翌月の請求で lambda-study 分の課金が止まっていること**を確認して終了です。

---

## 8. 詰まったときの確認順序

| 症状 | まず見るところ |
|---|---|
| `terraform init` が `Module not found` で失敗 | `modules/lambda_fn/` が無い。§1-4 の構成確認 |
| `Error: Unsupported argument` が variables に出る | ルートの `variables.tf` がモジュール側のままになっている（§1-4 の確認コマンド） |
| `archive_file` が `no such file or directory` | `samples_dir` が相対パスか `~` になっている。絶対パスで書く |
| トリガを作ったのに Lambda が起動しない | `aws_lambda_permission` の付け忘れ。`aws lambda get-policy --function-name <名前>` で確認 |
| Lambda が `ModuleNotFoundError` | 4/8 の `pymysql`。`scripts/build_layers.sh` を実行して apply し直す |
| 3/15 の invoke が `ResourceNotFoundException` | `eventbridge_scheduled_job.py` の DynamoDB 呼び出しを外していない（§3 の 3/15） |
| Lambda が `AccessDenied` | モジュールの `policy_json` に statement を足す。**足しながら読むのが演習の本体**なので、最初から広い権限を付けない |
| 実行しても古い挙動のまま | ソースを直したあとに `terraform apply` をしていない |
| 環境変数を変えても反映されない | `ignore_changes = [environment]`（§4 の最後） |
| `apply` が Powertools レイヤーで失敗 | `powertools_layer_version` が古い。4/12 のコマンドで最新版数を確認する |
