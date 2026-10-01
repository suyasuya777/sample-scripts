# boto3 学習用テスト環境 構築手順

対象期間：2027/2/1（月）〜 3/14（日）（`【SRE】2027年02月学習進捗表ーboto3.md` と同じ日程）
使うもの：`環境-Terraform.zip`（Terraform 一式）
方針：**作りっぱなし。** ただし Aurora と EKS だけは、その日に作ってその日に消す

**コマンドはすべて WSL2 の Ubuntu で実行します。** 第3章以降は、Terraform のフォルダ（`~/boto3-study-tf`）に移動してから実行してください。

> zip 内の `README.md` は旧日程（1/18〜2/28）のままです。日付と手順は、この手順書に従ってください。

---

## 1. 事前準備（2/1 より前に1回だけ）

### 1-1. ツールを入れる

入っていれば、バージョン確認だけで次へ進んでください。

```bash
# Terraform と unzip
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y terraform unzip

# AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip -q awscliv2.zip && sudo ./aws/install

# 確認（Terraform は 1.6 以上、AWS CLI は 2.x であること）
terraform version
aws --version
```

**Python と boto3 を入れます。** これが無いと 2/1 の1本目（`ec2_describe_regions.py`）から動きません。

```bash
sudo apt install -y python3 python3-pip python3-venv

# Ubuntu 24.04 では pip の直接インストールが拒否される（PEP 668）ので venv を使う
python3 -m venv ~/boto3-venv
source ~/boto3-venv/bin/activate
pip install --upgrade pip boto3

# 確認（Python は 3.10 以上、boto3 が表示されること）
python3 -V
python3 -c "import boto3; print(boto3.__version__)"
```

**毎回 `source ~/boto3-venv/bin/activate` を忘れると `ModuleNotFoundError: No module named 'boto3'` になります。** 自動で有効化されるようにしておきます。

```bash
echo 'source ~/boto3-venv/bin/activate' >> ~/.bashrc
```

> Python 3.10 以上が必要です（`athena/` と `sts/` の計6本が `str | None` 記法を使っています）。Ubuntu 22.04 は 3.10、24.04 は 3.12 なのでどちらでも足ります。

### 1-2. AWS の認証を設定する

管理者権限を持つ IAM ユーザのアクセスキーを使います（ルートユーザのキーは使わないこと）。

```bash
aws configure
#   AWS Access Key ID     : （IAMユーザのキー）
#   AWS Secret Access Key : （IAMユーザのシークレット）
#   Default region name   : ap-northeast-1
#   Default output format : json

aws sts get-caller-identity    # 自分のアカウントIDが表示されればOK
```

### 1-3. Terraform 一式を置く

zip を WSL2 のホームに展開し、フォルダ名を英字に変えます。**展開したフォルダ名が文字化けすることがある**ので、ワイルドカードで移動します。

```bash
cd ~
unzip -q "/mnt/c/Users/<Windowsのユーザ名>/Downloads/環境-Terraform.zip"
mv ./*Terraform ~/boto3-study-tf
cd ~/boto3-study-tf
ls                                  # set_a.tf 〜 set_e.tf と .sh が2つ見えればOK
```

`/mnt/c/...`（Windows 側）に置いたまま作業しないでください。動作が遅くなります。

### 1-3b. 修正版が入っていることを確認する

zip には修正済みのファイルが入っています。念のため確認だけしてください。

```bash
cd ~/boto3-study-tf
ls athena.tf                     # 存在すればOK（Athena のクエリ結果バケット）
grep -c -- '--log-events "file://' set_c.tf   # 1 ならOK（0 なら旧版。ログ投入で apply が失敗する）
grep -c 'version_actual' set_e.tf  # 1 ならOK（Aurora のバージョン固定）
```

`boto3` サンプル集側も同様です。

```bash
grep -n "NEW_TYPE" ec2/ec2_modify_instance_type.py     # t3.small ならOK
grep -c "athena_results_location" athena/*.py          # 3本とも 1 以上ならOK
```

> zip 内の `README.md`・`terraform.tfvars.example` のコメント・`variables.tf` の説明文・`make_orphan_snapshot.sh` の完了メッセージは、いずれも**旧日程（1/18〜2/28）のまま**です。日付はすべてこの手順書に従ってください。`make_orphan_snapshot.sh` が最後に案内する `scripts/delete_orphan_snapshot.sh` は存在しません（掃除は 3/14 の `cleanup_leftovers.sh` が行います）。

### 1-4. 設定ファイルを作る

```bash
cp terraform.tfvars.example terraform.tfvars
curl -s https://checkip.amazonaws.com      # 自宅のグローバルIPを確認
vi terraform.tfvars
```

書き換えるのは次の2か所だけです。

| 項目 | 設定する値 |
|---|---|
| `notification_email` | 自分のメールアドレス（**必須**。SNS と SES の確認メールが届く） |
| `my_ip_cidr` | 上で確認したIPの末尾に `/32` を付けたもの（例 `203.0.113.10/32`） |

`enable_set_b` 〜 `enable_set_e2` はすべて `false` のままにしておきます。該当日に1つずつ `true` にしていきます。

---

## 2. ガードレール（2/1 の最初に実施）

### 2-1. 予算アラート

**メールアドレスは `terraform.tfvars` に書いたものをそのまま使います。**手で書き換える箇所はありません。

```bash
cd ~/boto3-study-tf

ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
EMAIL=$(grep '^notification_email' terraform.tfvars | cut -d'"' -f2)

echo "アカウント: $ACCOUNT / 通知先: $EMAIL"   # ここで実アドレスが出ることを必ず確認

cat > /tmp/budget.json <<'EOF'
{
  "BudgetName": "boto3-study",
  "BudgetLimit": { "Amount": "120", "Unit": "USD" },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
EOF

# ここはクォート無しのヒアドキュメント（$EMAIL を展開させるため）
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

# 作成できたことを確認
aws budgets describe-budgets --account-id "$ACCOUNT" \
  --query 'Budgets[].[BudgetName,BudgetLimit.Amount]' --output table
```

`echo` の行で `$EMAIL` が空だったら、`terraform.tfvars` の `notification_email` がまだ `あなたのメールアドレス` のままです。先に §1-4 をやり直してください。

**通知は月$96（$120の80%）を超えたときに届きます。** 通常の利用額は2月が約$70、3月が約$40（内訳は第7章）なので、この額を超えるのは何かを消し忘れたときだけです。通知が来たら第7章を確認してください。

### 2-2. リージョンを固定する

```bash
echo 'export AWS_DEFAULT_REGION=ap-northeast-1' >> ~/.bashrc
source ~/.bashrc
```

---

## 3. 日別の作業

### 一覧

| 日付 | 作業 | 所要時間 |
|---|---|---|
| **2/1（月）** | ガードレール（第2章）／**セットA を作る** | 約15分 |
| **2/2（火）** | **セットB を作る** | 約3分 |
| 2/9（火） | 孤立スナップショットを作る | 約5分 |
| **2/21（日）** | **セットC を作る**／Cost Explorer を有効にする | 約3分 |
| **2/28（日）** | **セットD を作る**／確認メール2通／2つ目のアカウントを作る | 約15分 |
| **3/7（日）** | **セットE-1（RDS）を作る** | 約10分 |
| **3/9（火）** | **Aurora を作る → 演習 → その日のうちに消す** | 作成約15分・削除約15分 |
| **3/10（水）** | **EKS を作る → 演習 → その日のうちに消す** | 作成約10分・削除約10分 |
| **3/14（日）** | **すべて消す** | 約20分 |

`terraform apply` は、実行前に変更内容の一覧（plan）が表示され、`yes` を入力すると実行されます。**毎回、一覧を読んでから `yes` を入力してください。**

---

### 2/1（月）セットA

VPC・ALB・ECS・EC2・Auto Scaling・ログ用S3、および Athena のクエリ結果用S3（`athena.tf`）を作ります。

```bash
cd ~/boto3-study-tf
terraform init          # 初回のみ
terraform apply         # 約10分
```

完了したら、ALB が応答することを確認します。

```bash
curl -I "http://$(terraform output -raw alb_dns_name)"     # 「HTTP/1.1 200 OK」ならOK
```

**ALB にアクセスを流しておきます。** 2/28 の Athena で、このアクセスログを分析します。

```bash
for i in $(seq 1 200); do curl -s -o /dev/null "http://$(terraform output -raw alb_dns_name)/path$i"; done
```

---

### 2/2（火）セットB

S3（オブジェクト1200件）・IAM ユーザ2名・SSM パラメータ・Secrets Manager を作ります。

1. `terraform.tfvars` の `enable_set_b` を `true` にする
2. 実行する

```bash
terraform apply
```

---

### 2/9（火）孤立スナップショット

**この日の学習を始める前に**実行します。`ec2_snapshots.py` の検出対象になります。

```bash
bash make_orphan_snapshot.sh      # 最後に「完了。孤立スナップショット: snap-…」と出ればOK
```

この日はインスタンスタイプを t3.small に変える演習があります。**Terraform は元に戻してくれないので、その日のうちに t3.micro に戻してください**（第4章）。

---

### 2/21（日）セットC と Cost Explorer

CloudWatch Logs のロググループとログイベントを作ります。

1. `terraform.tfvars` の `enable_set_c` を `true` にする
2. 実行する

```bash
terraform apply
```

続けて、**マネジメントコンソールで「Cost Explorer」を一度開きます。** これで有効になります。データの反映に最大24時間かかるので、3/11 に使う前のこの日に済ませておきます。

---

### 2/28（日）セットD・確認メール・2つ目のアカウント

**① セットD を作る**（Lambda・SQS/SNS・SES）

1. `terraform.tfvars` の `enable_set_d` を `true` にする
2. 実行する

```bash
terraform apply
```

**② 確認メールのリンクを2つ踏む**

`notification_email` 宛てに次の2通が届きます。**両方のリンクを踏まないと、SNS も SES も使えません。**

- SNS のサブスクリプション確認（件名：AWS Notification - Subscription Confirmation）
- SES のメールアドレス検証（件名：Amazon Web Services – Email Address Verification Request）

**③ 2つ目のAWSアカウントを作る**（3/12 の `sts_multi_account_scan.py` 用）

Organizations でのアカウント作成は無料です。**メールアドレスは `terraform.tfvars` の値に `+aws2` を差し込んだ別名を自動生成します**（`user@example.com` → `user+aws2@example.com`）。Gmail・iCloud・Outlook などはこの別名で同じ受信箱に届きます。

> **作成完了まで数分〜（場合によっては数十分）かかります。**支払い方法の検証が入ると長引くことがあり、`SUCCEEDED` にならないと **3/12 と 3/14 の STS 演習が丸ごと潰れます。**この手順だけは前倒しで済ませて構いません（空のアカウントに費用はかかりません）。遅くとも 3/7 までに `SUCCEEDED` を確認しておいてください。

```bash
cd ~/boto3-study-tf

EMAIL=$(grep '^notification_email' terraform.tfvars | cut -d'"' -f2)
SUB_EMAIL="${EMAIL/@/+aws2@}"
echo "サブアカウント用: $SUB_EMAIL"    # user+aws2@... の形になることを確認

# 組織がまだない場合のみ（既にあれば AlreadyInOrganizationException が出る。無視してよい）
aws organizations create-organization --feature-set ALL

aws organizations create-account \
  --email "$SUB_EMAIL" \
  --account-name boto3-study-sub

# 数分後に確認。State が SUCCEEDED なら完了
aws organizations list-create-account-status \
  --query 'CreateAccountStatuses[].[AccountName,State,AccountId,FailureReason]' --output table
```

**表示された AccountId を控えて、次の3本の `SUB_ACCOUNT_ID` に設定してください。**

```
sts/sts_assume_role_client.py
sts/sts_multi_account_scan.py
sts/sts_credential_cache.py
```

assume に使うロールは、Organizations が新規アカウントに自動作成する `OrganizationAccountAccessRole` です。管理アカウント（＝いま操作しているアカウント）から追加設定なしで assume できます。3/12 の前に疎通だけ確認しておくと安全です。

```bash
SUB=<控えたAccountId>
aws sts assume-role \
  --role-arn "arn:aws:iam::$SUB:role/OrganizationAccountAccessRole" \
  --role-session-name precheck \
  --query 'AssumedRoleUser.Arn' --output text
```

作ったアカウントは**期間が終わっても消さずに置いておいて構いません**（中身が空なら費用はかかりません）。閉鎖すると90日間は同じメールアドレスを再利用できなくなります。

**④ Athena のテーブルを作る**

この日の学習（`athena_create_projection_table.py`）で作ります。実行前に、スクリプト冒頭の2か所を次の出力で置き換えてください。

```bash
terraform output -raw athena_alb_log_location    # → ALB_LOG_LOCATION
terraform output -raw athena_results_location    # → OUTPUT_LOCATION
```

同じ `OUTPUT_LOCATION` を `athena_run_query.py` と `athena_workgroup_named_query.py` にも設定します。テーブル定義の詳細は第5章にあります。

**クエリの対象日は 2/14 です。** ALB アクセスログはリクエストがあった日にしか作られず、トラフィックを流すのは 2/1・2/11・2/14・2/23 の4日だけです。**2/28 当日のログは無い**ので、`athena_run_query.py` の `DAY` は既定の `2027/02/14`（2/14 に意図的に落とした 503 が入っている日）のまま実行してください。

---

### 3/7（日）セットE-1（RDS）

1. `terraform.tfvars` の `enable_set_e1` を `true` にする
2. 実行する

```bash
terraform apply        # 約10分
```

---

### 3/9（火）Aurora（作ってその日に消す）

**`terraform.tfvars` は書き換えません。** `enable_set_e2` は `false` のまま、コマンドの中でだけ有効にし、さらに Aurora だけを指定して作ります。

> zip の設定では、`enable_set_e2` を `true` にすると Aurora と EKS が一度に作られてしまいます。スケジュールでは 3/9 と 3/10 に分けているので、この方法で片方ずつ作ります。

**① 学習の最初に作る**（約15分。待ち時間はアプリに充てる）

```bash
terraform apply -var="enable_set_e2=true" \
  -target=aws_rds_cluster.aurora \
  -target=aws_rds_cluster_instance.aurora
```

`-target` を使っているという警告が出ますが、想定どおりです。一覧に **Aurora のクラスタ1つとインスタンス2つだけ**が作成対象として出ていることを確認して `yes` を入力します。

**② 演習をする**（フェイルオーバーなど。内容は進捗表を参照）

**③ その日のうちに消す**（約15分）

```bash
terraform apply
```

一覧に **Aurora のクラスタ1つとインスタンス2つが削除（destroy）対象**として出ていることを確認して `yes` を入力します。完了後、残っていないことを確認します。

```bash
aws rds describe-db-clusters --query 'DBClusters[].DBClusterIdentifier'     # [] ならOK
```

**消し忘れると1日 $4.8 かかります。** 確認まで終えて、その日の作業完了です。

---

### 3/10（水）EKS（作ってその日に消す）

3/9 と同じ要領です。**`terraform.tfvars` は書き換えません。**

**① 学習の最初に作る**（約10分）

```bash
terraform apply -var="enable_set_e2=true" -target=aws_eks_cluster.this
```

一覧に **EKS クラスタと、そのための IAM ロール・ポリシーの割り当て**の3つだけが作成対象として出ていることを確認して `yes` を入力します。

**② 演習をする**（`eks_describe_cluster.py`）

**③ その日のうちに消す**（約10分）

```bash
terraform apply
aws eks list-clusters          # "clusters": [] ならOK
```

**消し忘れると1日 $2.4 かかります。**

---

### 3/14（日）すべて消す

**① Terraform で消えないものを先に掃除する**

```bash
bash cleanup_leftovers.sh
```

途中で2回「削除しますか [y/N]」と聞かれます。どちらも `y` を入力します（孤立スナップショットと、3/8 の演習で作った RDS スナップショットが消えます）。

**② Terraform で作ったものを消す**（約15分）

```bash
terraform destroy
```

一覧を確認して `yes` を入力します。

**③ 残っていないことを確認する**

第8章のチェックリストをすべて確認します。

**④ 予算アラートを消す**（任意。残しても費用はかかりません）

```bash
aws budgets delete-budget --account-id "$(aws sts get-caller-identity --query Account --output text)" --budget-name boto3-study
```

---

## 4. 注意事項

### その日のうちに手で戻すもの

次の5つは、演習で変更しても **Terraform が元に戻しません。** 戻し忘れると課金が続いたり、以降の演習に影響したりします。

| 日付 | 変更するもの | 戻す状態 |
|---|---|---|
| 2/9 | EC2 のインスタンスタイプ | **t3.micro**（t3.small のままだと課金が倍） |
| 2/10 | ECS の desired_count | 2 |
| 2/14 | Auto Scaling の desired_capacity | 0 |
| 2/14 | タスク用セキュリティグループの許可ルール | ALB からの80番を許可した状態 |
| 3/2 | Lambda のタイムアウト・メモリ・同時実行数 | 変更前の値（同時実行数の予約は削除） |

### apply のたびに元に戻るもの

逆に、次の2つは演習で直しても、**次に `terraform apply` したときに「わざと悪い状態」へ戻ります。**

- 2/16 に4項目すべて有効にした、バケットBのパブリックアクセスブロック
- 2/19 に外した、user2 の `AdministratorAccess`

どちらも演習の題材として作ってあるもので、戻っても学習上の問題はありません。一覧に出てきても慌てずに `yes` で進めてください。3/14 にすべて消します。

### その他

- **`boto3-study-intentionally-open` というセキュリティグループは、どこにも割り当てないでください。** SSH（22番）とRDP（3389番）が全開放になっている、検出演習用の題材です
- **途中で `terraform destroy` しないでください。** ログ用S3ごと消えるため、2/28 の Athena で分析するアクセスログがなくなります
- **Terraform の管理情報（`terraform.tfstate`）には、IAM のアクセスキーや RDS のパスワードが平文で入ります。** フォルダを Git やクラウドストレージで共有しないでください

---

## 5. Athena のテーブル定義（2/28 で使用）

`athena_create_projection_table.py` が実行する DDL です。**AWS 公式（Athena ユーザーガイドの Partition Projection 版）のものをそのまま使っています。**マネジメントコンソールから手で流す場合もこれを使ってください。

### 5-1. 置き換える値

```bash
terraform output -raw athena_alb_log_location
# → s3://boto3-study-logs-<アカウントID>/alb/AWSLogs/<アカウントID>/elasticloadbalancing/ap-northeast-1/

terraform output -raw athena_results_location
# → s3://boto3-study-athena-<アカウントID>/query-results/
```

下の DDL の `【LOCATION】` **2か所**を、1つ目の出力（`athena_alb_log_location`）で置き換えます。**末尾のスラッシュは必ず残してください。** `storage.location.template` はこの値に `${day}` を直接つなげる形なので、スラッシュが無いとパスが壊れます。

2つ目の出力（`athena_results_location`）は、スクリプト側の `OUTPUT_LOCATION` に設定する値です。ワークグループ `primary` は結果出力先が未設定のため、これを渡さないと次のエラーで即座に落ちます。

```
InvalidRequestException: No output location provided.
```

### 5-2. DDL

```sql
CREATE DATABASE IF NOT EXISTS boto3_study;

CREATE EXTERNAL TABLE IF NOT EXISTS boto3_study.alb_logs (
  type string,
  time string,
  elb string,
  client_ip string,
  client_port int,
  target_ip string,
  target_port int,
  request_processing_time double,
  target_processing_time double,
  response_processing_time double,
  elb_status_code int,
  target_status_code string,
  received_bytes bigint,
  sent_bytes bigint,
  request_verb string,
  request_url string,
  request_proto string,
  user_agent string,
  ssl_cipher string,
  ssl_protocol string,
  target_group_arn string,
  trace_id string,
  domain_name string,
  chosen_cert_arn string,
  matched_rule_priority string,
  request_creation_time string,
  actions_executed string,
  redirect_url string,
  lambda_error_reason string,
  target_port_list string,
  target_status_code_list string,
  classification string,
  classification_reason string,
  conn_trace_id string
)
PARTITIONED BY (day string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1',
  'input.regex' = '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) (.*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-_]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^ ]*)\" \"([^\\s]+?)\" \"([^\\s]+)\" \"([^ ]*)\" \"([^ ]*)\" ?([^ ]*)? ?( .*)?'
)
LOCATION '【LOCATION】'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.day.type' = 'date',
  'projection.day.range' = '2027/02/01,NOW',
  'projection.day.format' = 'yyyy/MM/dd',
  'projection.day.interval' = '1',
  'projection.day.interval.unit' = 'DAYS',
  'storage.location.template' = '【LOCATION】${day}'
);
```

### 5-3. 列と正規表現の対応について

**列は34、`input.regex` のキャプチャグループは35です。数が一致していないのは正常です。** 末尾の `?( .*)?` は列を持たない意図的な余りで、ALB のログ形式に将来フィールドが追加されても壊れないようにするためのものです。AWS も「常に残しておくこと」と明記しています。余りは末尾にあるだけなので列のズレは起きません。

逆に言うと、**余り以外の場所でグループと列の数が食い違うと、そこから先の列がすべて1つずつ後ろにズレます。** RegexSerDe は「N番目のグループ → N番目の列」で機械的に割り当てるだけなので、型が合わない列（`elb_status_code` は `int`）は `NULL` になります。検索結果が NULL だらけになったら、まずこれを疑ってください。

- `client:port` と `target:port` は、正規表現側で ip と port の2グループに分かれます。列も `client_ip` / `client_port` / `target_ip` / `target_port` の4列に分けること
- `"request"` は verb / url / proto の3グループに分かれます。列も `request_verb` / `request_url` / `request_proto` の3列に分けること

### 5-4. 0件だったときの確認順序

**まず `day` の指定を疑ってください。** ALB アクセスログはリクエストがあった日にしか作られません。この環境でトラフィックを流すのは **2/1・2/11・2/14・2/23 の4日だけ**で、**2/28 当日のログは存在しません。** 2/28 に `day = '2027/02/28'` で引くと、テーブルが正しくても 0 件になります。

```sql
-- 1. 生の行が引けるか（day は UTC 日付。ログ配信は5分ごとなので直近は空きうる）
SELECT * FROM boto3_study.alb_logs WHERE day = '2027/02/14' LIMIT 5;
```

1. 行が1件も返らない → `day` の指定を疑う。`aws s3 ls` で実際のパスに日付フォルダがあるか確認する
2. 行は返るが NULL だらけ → 5-3 の列と正規表現の対応を疑う
3. それでも解決しない → ALB のログ形式が変わった可能性。AWS 公式ドキュメントの最新の DDL を確認する

---

## 6. わざと「悪い状態」にしてあるもの

検出系のスクリプトは、何もヒットしないと正しく動いているか判断できません。そのため、次のリソースを意図的に仕込んであります。**不具合ではありません。**

| 仕込んである状態 | 検出するスクリプト |
|---|---|
| SSH・RDP が全開放のセキュリティグループ | `ec2_security_groups.py` |
| どこにも関連付けていない Elastic IP | `ec2_unused_eip.py` |
| 元のボリュームがない孤立スナップショット（2/9 に作成） | `ec2_snapshots.py` |
| `AdministratorAccess` が付いた user2 | `iam_admin_policy_entities.py` |
| インラインポリシーを持つ user1 | `iam_inline_policies.py` |
| 使用済みのキー（user1）と未使用のキー（user2） | `iam_access_key_last_used.py` |
| パブリックアクセスブロックが2項目だけのバケットB | `s3_public_access_block.py` |
| 保持期間が未設定のロググループ2つ | `logs_list_log_groups.py` |
| メッセージが3件たまった DLQ | `sqs_dlq_reprocess.py` |
| インターネットへの経路がないプライベートサブネット | `vpc_describe_network.py` |

---

## 7. 費用

| 項目 | 期間 | 概算 |
|---|---|---|
| セットA 本体（ALB $0.58・Fargate×2 $0.74・EC2 t3.micro $0.33・EBS $0.03＝約$1.68/日） | 2/1〜3/14（42日） | 約 $70 |
| パブリックIPv4アドレス 6個（$0.005/時＝約$0.72/日） | 2/1〜3/14（42日） | 約 $30 |
| セットB・C・D | 全期間 | 約 $2 |
| セットE-1（RDS） | 3/7〜3/14 | 約 $4 |
| Aurora | 3/9 の数時間 | 約 $2 |
| EKS | 3/10 の1時間 | 約 $0.1 |
| **合計** | | **約 $105〜115** |

月別では **2月が約$70、3月（1〜14日）が約$40** です。予算アラートの $120 と 80% 通知（$96）はこの実績を前提にしています。

**パブリックIPv4アドレスは1個あたり $0.005/時の課金対象です。** この環境では ALB に2個（2AZ）、Fargate タスクに2個（`assign_public_ip = true`）、EC2 に1個、未割り当てEIPに1個の計6個を使います。NAT Gateway を作らない代わりの費用なので、減らせません。

> 単価は東京リージョンの目安です。料金は改定されるので、正確な額は AWS 料金計算ツールで確認してください。

予算アラートが届いたら、次の3つを疑ってください。

1. **Aurora か EKS の消し忘れ**（$4.8/日・$2.4/日）
2. **2/9 のインスタンスタイプの戻し忘れ**（t3.small のままで $0.66/日）
3. **NAT Gateway を作ってしまった**（$1.4/日＋データ処理料金。この環境では作りません）

---

## 8. 破棄チェックリスト（3/14 の最後に確認）

**すべて空（または結果なし）になれば完了です。** 1行ずつ実行して確認します。

```bash
# まずタグで横断確認（Terraform で作ったものが残っていないか）
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=boto3-study \
  --query 'ResourceTagMappingList[].ResourceARN' --output table
```

| 対象 | 確認コマンド | 残ると |
|---|---|---|
| **EKS クラスタ** | `aws eks list-clusters` | **$2.4/日。最優先で確認** |
| **Aurora / RDS** | `aws rds describe-db-clusters` と `aws rds describe-db-instances` | **$4.8/日・$0.5/日** |
| RDS スナップショット | `aws rds describe-db-snapshots --snapshot-type manual` | ストレージ課金 |
| Elastic IP | `aws ec2 describe-addresses` | $0.12/日 |
| EBS スナップショット | `aws ec2 describe-snapshots --owner-ids self` | 微額だが溜まる |
| NAT Gateway | `aws ec2 describe-nat-gateways --filter Name=state,Values=available` | $1.4/日（作っていないはず） |
| IAM ユーザ | `aws iam list-users` | **`AdministratorAccess` 付きの user2 が残るのが一番危険** |
| S3 バケット | `aws s3 ls` | ― |
| CloudWatch アラーム | `aws cloudwatch describe-alarms --query 'MetricAlarms[].AlarmName'` | 2/23 の `boto3-study-alb-requestcount`。月 $0.1<br>`aws cloudwatch delete-alarms --alarm-names boto3-study-alb-requestcount` |
| CloudWatch ダッシュボード | `aws cloudwatch list-dashboards --query 'DashboardEntries[].DashboardName'` | 2/24 の `boto3-study`（スクリプト末尾で削除済みのはず）。3個まで無料 |
| Lambda の同時実行予約 | `aws lambda get-function-concurrency --function-name boto3-study-ok` | 3/2 の予約が残るとアカウントの共有枠を食う |
| Lambda のロググループ | `aws logs describe-log-groups --log-group-name-prefix /aws/lambda/boto3-study` | 実行時に自動で作られ、Terraform では消えない |
| その他のロググループ | `aws logs describe-log-groups --log-group-name-prefix /boto3-study` | 保持期間なしだと永久保存 |
| Athena のワークグループ | `aws athena list-work-groups` | 2/28 に作る `boto3-study-incident`。`primary` 以外が残っていれば削除<br>`aws athena delete-work-group --work-group boto3-study-incident --recursive-delete-option` |
| Athena のテーブル | `aws glue get-databases --query 'DatabaseList[].Name'` | 2/28 に作った `boto3_study` が残る |
| Secrets Manager | `aws secretsmanager list-secrets` | $0.4/月 |

**演習で作ったもの（CloudWatch アラームとダッシュボード、Lambda のロググループと同時実行予約、Athena のワークグループとテーブル）は Terraform の管理外なので、`terraform destroy` では消えません。** 残っていたら上の削除コマンド、またはマネジメントコンソールから削除してください。

SSM パラメータと Athena のクエリ結果バケットは Terraform 管理下なので、`terraform destroy` で消えます（`ssm_parameter_store.py` は新しいパスを作らず、セットBの `/boto3-study/app/` を読み書きして元に戻す作りです）。

最後に、**翌月の請求で boto3 学習分の課金が止まっていること**を確認して終了です。

---

## 9. スクリプトの設定値一覧

サンプル集は引数を取らず、ソース冒頭の定数を書き換えて使います。**ここに載っている値はすべて `terraform output` で取れます。**該当日の最初にまとめて控えておくと、当日に探す手間がありません。

```bash
cd ~/boto3-study-tf
terraform output          # 全部まとめて表示
```

| 日付 | スクリプト | 定数 | 取得コマンド |
|---|---|---|---|
| 2/3・2/15〜2/17 | `s3/*.py`（5本） | `BUCKET` | `terraform output -raw s3_bucket_a`（公開設定の比較は `s3_bucket_b`） |
| 2/16 | `s3_bucket_policy` | `TRUSTED_ACCOUNT_ID` | `aws sts get-caller-identity --query Account --output text`<br>IP条件の Deny には `terraform.tfvars` の `my_ip_cidr` を使う |
| 2/5・2/9・3/10 | `ec2_start_stop_reboot` / `ec2_modify_instance_type` / `ssm_send_command` | `INSTANCE_ID` | `terraform output -raw ec2_instance_id` |
| 2/11・2/12 | `ecs_rolling_restart` / `ecs_list_tasks` / `ecs_task_definition` | `CLUSTER`, `SERVICE` | `terraform output -raw ecs_cluster` / `ecs_service` |
| 2/21 | `ssm_parameter_store` | `PREFIX` | 既定 `/boto3-study/app/`（`name_prefix` と同じなら変更不要） |
| 2/21 | `secretsmanager_get_put` | `SECRET_NAME` | `boto3-study/db`（`name_prefix` と同じなら変更不要） |
| 2/22・2/24 | `cloudwatch_get_metrics` / `cloudwatch_dashboard` | `ECS_CLUSTER`, `ECS_SERVICE` | `terraform output -raw ecs_cluster` / `ecs_service`<br>ALB の次元はスクリプトが自動解決 |
| 2/23 | `cloudwatch_put_alarm` | `SNS_TOPIC_ARN` | `terraform output -raw sns_topic_arn` |
| 2/25・2/26 | `logs_describe_streams` / `logs_filter_error` | `LOG_GROUP` | `/boto3-study/no-retention`（ストリームは `app-stream` と `stale-stream`） |
| 2/26 | `logs_insights_query` | `LOG_GROUP` | `/ecs/boto3-study` |
| 2/28 | `athena_create_projection_table` | `ALB_LOG_LOCATION` | `terraform output -raw athena_alb_log_location` |
| 2/28 | `athena/*.py`（3本） | `OUTPUT_LOCATION` | `terraform output -raw athena_results_location` |
| 2/28 | `athena_run_query` | `DAY` | 既定は `2027/02/14`（2/14 に落とした 503 を探す日）。**そのままでよい**<br>**2/28 当日のログは存在しない**ので `2027/02/28` にすると 0 件になる。ログがあるのは 2/1・2/11・2/14・2/23<br>**UTC 日付**なので 09:00 JST より前の時間帯は前日側に入る |
| 3/1〜3/3・3/2 | `lambda_*.py` | `FUNCTION_NAME` / `TARGET_FUNCTION` | `terraform output -json lambda_function_names`<br>（`boto3-study-ok` / `-canary` / `-config`） |
| 3/4 | `sqs_dlq_reprocess` | `DLQ_URL`, `SRC_URL` | `terraform output -raw sqs_dlq_url` / `sqs_main_url` |
| 3/4 | `sns_publish` | `TOPIC_ARN` | `terraform output -raw sns_topic_arn` |
| 3/5 | `ses_send_email` | `VERIFIED_EMAIL` | `terraform.tfvars` の `notification_email`<br>**サンドボックスなので送信元も宛先も検証済みアドレスでなければ送れない。**セットDで検証されるのはこの1つだけなので、`SENDER` と `RECIPIENT` は同じになる |
| 3/8 | `rds_snapshot` | `DB_IDENTIFIER` | `terraform output -raw rds_identifier` |
| 3/9 | `rds_failover_cluster` | `CLUSTER_ID` | `terraform output -raw aurora_cluster_identifier` |
| 3/12・3/14 | `sts/*.py`（3本） | `SUB_ACCOUNT_ID` | `aws organizations list-create-account-status`（§3 の 2/28 参照） |

修正済みのスクリプトは、置き換え忘れがあると実行開始前に

```
[ERROR] <定数名> を置き換えてください
```

と表示して止まります。API を叩く前に止まるので、中途半端な状態になることはありません。

**ALB の次元は自動解決させています。** CloudWatch の `LoadBalancer` 次元は ARN そのものではなく `app/boto3-study/<ID>` という末尾部分で、ここを間違えても**エラーにならず空配列が返る**だけです。手で書き写すと事故になるので、`describe_load_balancers` から組み立てる作りにしてあります。
