# ネットワーク・セキュリティ学習 テスト環境 構築手順

対象：`【SRE】ネットワーク・セキュリティ コマンド集.md` の【実機】【調査】項目を、自分のAWSアカウントで実行するための環境
期間：**12/6（日）に作り、12/20（日）に壊す**（約2週間）
費用：**約 $1.5/日、合計 $20〜25**
方針：**【実機】【調査】はすべてこの環境で実施する。** 担当システムでは権限が無くて打てない項目や、平常時には現れない事象（502・REJECT・TIME_WAIT の山）を、ここで再現する

**コマンドはすべて WSL2 の Ubuntu で実行します。**

**済管理のルール**：`□` を `☑` に書き換えて進めます（進捗表・コマンド集と同じ記法）。
見出しの `□` はその日全体の済、項目の `□` は個別作業の済です。

| 済 | 日付 | この手順書でやること | 章 |
|---|---|---|---|
| □ | 11/23〜11/30 | 事前準備（ツール・スキャンツール・認証・予算アラート・`terraform init`） | §2 |
| □ | **12/6（日）** | **構築**、Athena テーブル作成、題材の仕込み | §3・§5 |
| □ | 12/7（月） | NAT と RDS を当日だけ作って壊す | §6 |
| □ | 12/8（火） | VPC内から `dig`、ALBログの再生成 | §6 |
| □ | 12/9（水） | 5xx の3パターンを確認 | §6 |
| □ | 12/10（木） | ALB・ターゲットグループの設定値を取得 | §6 |
| □ | 12/11（金） | ALBログの再生成、REJECT の生成、`tcpdump` | §6 |
| □ | 12/13（日） | AssumeRole、タスク定義 | §6 |
| □ | 12/14（月） | 自己署名証明書で SNI を確認 | §6 |
| □ | 12/15（火） | ルートテーブル3種と NACL の点検 | §6 |
| □ | 12/16（水） | `/28` サブネットで必要IP数を逆算 | §6 |
| □ | 12/17（木） | サンプルのスキャン、バックエンド4点 | §6 |
| □ | 12/18（金） | SSM 接続、ECR（任意） | §6 |
| □ | **12/20（日）** | **破棄**とチェックリスト | §9 |

> boto3 の環境で問題になった `local-exec`（Terraform の中から bash を呼ぶ処理）は、この環境では一切使っていません。データの仕込みはすべて、下記のスクリプトとコマンドで行います。

---

## 1. この環境で何が再現できるか

| 日付 | コマンド集の項目 | この環境で用意しているもの |
|---|---|---|
| 12/7 | `ss` で TIME_WAIT を数える | 接続を大量に開閉するスクリプト |
| 12/7 | ALB idle timeout と Keep-Alive | idle_timeout=60 を明示した ALB |
| 12/8 | `dig` の打ち分け、TTL の読み取り | TTL 300 / 60 のレコードを持つプライベートホストゾーン |
| 12/9 | 5xx の区別、`target_processing_time` = -1 | 4種類の 5xx を作り分けられる Web アプリ |
| 12/10 | 切り離し時間、登録解除遅延 | 間隔・閾値・登録解除遅延を設定したターゲットグループ（値は下の設定値表） |
| 12/11 | `tcpdump`、`curl -w` | SSM で入れる EC2 2台 |
| 12/11 | Flow Logs の REJECT 抽出 | 許可されていないポートを叩いて REJECT を作るスクリプト |
| 12/13 | `aws sts assume-role` | 同一アカウントから引き受けられるロール |
| 12/13 | 未使用キーを数える | 使用済みキーと未使用キーを持つ IAM ユーザ2名 |
| 12/13 | タスク定義でシークレットを参照 | `secrets` で渡す ECS タスク定義（起動はしない） |
| 12/14 | `openssl s_client`、SNI の確認 | 自己署名証明書を2枚入れた HTTPS リスナー |
| 12/15 | ルートテーブル・SG・NACL の点検 | 経路の異なるルートテーブル3つと、番号付き NACL |
| 12/16 | 空きIPの確認と逆算 | `/28` の小さいサブネット（下の設定値表） |
| 12/17 | tfsec / Checkov / gitleaks | わざと危険にしたサンプルリポジトリ |
| 12/17 | state バックエンドの4点確認 | 暗号化・バージョニング・PAB・ロックをそろえた S3 と DynamoDB |
| 12/18 | SSM Session Manager | SSM で入れる EC2 |
| 12/20 | CloudTrail の検索 | この環境の構築操作そのものが証跡になる |

### 環境の設定値（**数値はここが唯一の出所**）

ほかの文書には数値を書いていません。答え合わせはこの表で行います。

| 項目 | 値 | 定義場所 |
|---|---|---|
| VPC CIDR | `10.30.0.0/16` | `network.tf` |
| ALB の idle timeout | **60秒** | `compute.tf` |
| ヘルスチェック間隔 / 異常閾値 / 正常閾値 | **10秒 / 2回 / 2回**（切り離しまで約20秒） | `compute.tf` |
| 登録解除の遅延 | **30秒** | `compute.tf` |
| TLS セキュリティポリシー | `ELBSecurityPolicy-TLS13-1-2-2021-06`（TLS 1.2 以上） | `compute.tf` |
| 証明書 | 自己署名2枚（`default.study.internal` / `app.study.internal`） | `compute.tf` |
| プライベートホストゾーン | `study.internal`（`app` TTL300 / `short` TTL60 / `alias` CNAME） | `dns.tf` |
| ルートテーブル | **3種**（public: IGW向き / isolated: 経路なし / private: 経路なし、NAT時のみ1本） | `network.tf` `onday.tf` |
| 小さいサブネット | `10.30.9.0/28`（**使えるIPは11個**） | `network.tf` |
| NACL（nacl-demo） | 受信100番で80許可 / 110番で22拒否 / 送信100番で1024-65535許可 | `network.tf` |
| Athena | DB `netsec_study` / ワークグループ `netsec-study`（1クエリ1GB上限） | `logs.tf` |
| Athena テーブル | `netsec_study.alb_logs` / `netsec_study.vpc_flow_logs`（パーティション列 `dt`） | §5 の DDL |
| RDS | PostgreSQL 16 / db.t4g.micro（`max_connections` は約100） | `onday.tf` |
| ログ配信の遅れ | ALB は5分間隔、Flow Logs は最大10分 | ― |

### この環境で用意できない値

次の5つは、実稼働のシステムでないと出てきません。**仮の値を置いて、手順と計算式を確立するところまで**が到達点です（進捗表の該当日にも注記してあります）。

| 用意できないもの | 使う日 | 代わりにやること |
|---|---|---|
| アプリ側の Keep-Alive | 12/7 | ALB の idle timeout と並べ、**外側＜内側**の判定手順を作る |
| コネクションプールの設定値 | 12/7 | `max_connections` は実値、プール数とタスク数は仮置きで検算 |
| CloudFront のタイムアウト | 12/10 | ALB は当日取得、DB は 12/7 の記録から転記（RDS は 12/7 に破棄済み）。CloudFront とアプリは仮の値で表を完成させる |
| 実稼働のトラフィック量 | 12/15 | 仮の使用率を置いて、AZ障害時の試算手順を確立する |
| ECS のクラスタ・サービス・実行中のタスク | 12/7・12/15・12/16 | **タスク定義は作ってあります**（12/13 で使用）が、クラスタとサービスはありません。タスク数・AZ分布・`deploymentConfiguration` は仮の値を置いて逆算する |

現場で値が取れるようになった時点で差し替えれば、そのまま実務で使えます。

### 当日だけ作って当日壊すもの

**NAT Gateway と RDS は、高い割に使う日が限られる**ので、常時は作りません。12/7 のその日だけ作り、終わったら戻します。

| 済 | 対象 | 使う場面 | 費用 | 作成・削除にかかる時間 |
|---|---|---|---|---|
| □ | **NAT Gateway** | 12/7 `ErrorPortAllocation` のアラーム作成、12/15 の経路の題材 | **約 $1.5/日**（数時間なら $0.3 程度） | 作成2分・削除2分 |
| □ | **RDS** | 12/7 `max_connections` の実値確認 | **約 $0.75/日**（数時間なら $0.2 程度） | 作成10分・削除5〜10分 |

`terraform.tfvars` は書き換えません。コマンドのオプションで有効にします（手順は6章の 12/7）。

**RDS のパラメータグループだけは常時作ってあります（無料）。** ただし `max_connections` は `LEAST({DBInstanceClassMemory/9531392},5000)` のような**式**で返るだけで、実値は分かりません。

**RDS インスタンスは 12/7 に必ず作ってください。** 12/10 の「各層のタイムアウト値を全部書き出す」で DB 側の実値を使うので、**ここを飛ばすと 12/10 が埋まりません。** 数時間で $0.2 です。

---

## □ 2. 事前準備（12/6 より前に1回だけ）

- □ **2-1. ツール**

**Terraform は Ubuntu の標準リポジトリに入っていません。** 先に HashiCorp のリポジトリを追加します（boto3 環境の手順書 §1-1 と同じ）。この順序を守らないと、`apt install` が「パッケージが見つからない」で**1行まるごと中止され、同じ行の `jq` なども入りません。**

**AWS CLI はこの手順では導入しません。** boto3 のブロックで入れたものをそのまま使います。`aws --version` が通らない場合は、公式のインストーラ（`awscli-exe-linux-x86_64.zip`）で先に入れ、`aws configure` まで済ませてください。

```bash
# 1. HashiCorp のリポジトリを追加（Terraform 用）
sudo apt update && sudo apt install -y gnupg software-properties-common curl lsb-release
curl -fsSL https://apt.releases.hashicorp.com/gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update

# 2. ツール一式
sudo apt install -y terraform unzip jq iproute2 tcpdump dnsutils curl openssl
```

`jq` は仕込みスクリプト（`scripts/*.sh`）が使います。**これが入っていないと 12/6 の仕込みが動きません。**

```bash
# Session Manager プラグイン（EC2 に入るために必要）
curl -o /tmp/session-manager-plugin.deb \
  "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb"
sudo dpkg -i /tmp/session-manager-plugin.deb

# 確認（すべてバージョンが出ればOK）
terraform version; aws --version; session-manager-plugin --version; jq --version
```

- □ **2-1b. スキャンツール（12/17 で使う）**

12/17 は項目が多い日です。**ツールの導入はこの週に済ませておきます。**

```bash
# tfsec
curl -sL https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash

# Checkov
pip install --user checkov

# gitleaks
curl -sL -o /tmp/gitleaks.tar.gz \
  https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz
tar xzf /tmp/gitleaks.tar.gz -C /tmp && sudo mv /tmp/gitleaks /usr/local/bin/

# 確認
tfsec --version; checkov --version; gitleaks version
```

`pip` が無い場合は `sudo apt install -y python3-pip` を先に実行します。`~/.local/bin` が `PATH` に入っていないと `checkov` が見つからないので、その場合は `export PATH="$HOME/.local/bin:$PATH"` を `~/.bashrc` に追記してください。

- □ **2-2. 認証と予算アラート**

```bash
aws sts get-caller-identity          # 管理者権限のIAMユーザであること
export AWS_DEFAULT_REGION=ap-northeast-1
```

```bash
EMAIL="あなたのメールアドレス"        # ← ここだけ書き換える
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo "アカウント: $ACCOUNT / 通知先: $EMAIL"    # 実アドレスが出ることを必ず確認

cat > /tmp/budget.json <<'EOF'
{ "BudgetName": "netsec-study", "BudgetLimit": { "Amount": "40", "Unit": "USD" },
  "TimeUnit": "MONTHLY", "BudgetType": "COST" }
EOF

# こちらはクォート無しのヒアドキュメント（$EMAIL を展開させるため）
cat > /tmp/notify.json <<EOF
[{ "Notification": { "NotificationType": "ACTUAL", "ComparisonOperator": "GREATER_THAN",
     "Threshold": 80, "ThresholdType": "PERCENTAGE" },
   "Subscribers": [{ "SubscriptionType": "EMAIL", "Address": "$EMAIL" }] }]
EOF

aws budgets create-budget --account-id "$ACCOUNT" \
  --budget file:///tmp/budget.json --notifications-with-subscribers file:///tmp/notify.json

aws budgets describe-budgets --account-id "$ACCOUNT" \
  --query 'Budgets[].[BudgetName,BudgetLimit.Amount]' --output table
```

`notify.json` 側だけヒアドキュメントのクォートを外しています。`<<'EOF'` のままだと `$EMAIL` が展開されず、`Address` が文字列のまま渡ってバリデーションエラーになります。

**予算は $40、通知は80%の $32 です。** この環境の想定費用は15日で約 $22（§8）なので、**$32 を超えたら異常**と判断できます。予算を $30 にすると通知ラインが $24 になり、正常に使っていても通知が飛んで判断に使えません。

- □ **2-3. Terraform 一式を置く**

zip の中は `netsec-study-tf/` 一式になっているので、**ホームで展開すればそのまま `~/netsec-study-tf` になります。**移動は不要です。

```bash
cd ~
unzip -q -o "/mnt/c/Users/<Windowsのユーザ名>/Downloads/netsec-study-tf.zip"
cd ~/netsec-study-tf
ls                      # *.tf が10個、user_data.sh、scripts/、sample-insecure/ が見えればOK

terraform init
terraform plan          # エラーが出ないことだけ確認。apply はまだしない
```

`/mnt/c/...`（Windows 側）に置いたまま作業しないでください。動作が遅くなります。

`-o` は上書き指定です。付けないと、やり直しで展開したときに `replace netsec-study-tf/logs.tf? [y]es, [n]o, ...` と対話プロンプトが出て止まります。

`terraform plan` は変数の入力を求めてきません（`variables.tf` の9変数すべてに既定値があります）。ただし AMI ID・アカウントID・AZ 一覧を実際に AWS へ問い合わせるので、**2-2 の認証設定が済んでいることが前提**です。

---

## □ 3. 構築（12/6・日）

- □ **3-1. 作る**

```bash
cd ~/netsec-study-tf
terraform apply         # 約5分
```

一覧を読んでから `yes` を入力します。完了したら応答を確認します。

```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://$(terraform output -raw alb_dns_name)/"   # 200
```

**`curl -I` は使わないでください。** 検証用アプリは `do_GET` しか実装していないので、HEAD リクエストには `501 Unsupported method ('HEAD')` を返します。環境の異常ではありません。

200 が返らない場合、EC2 の起動処理（ツールの導入とアプリの起動）がまだ終わっていない可能性があります。2〜3分おいて再確認してください。

- □ **3-2. 仕込み（当日中にやっておく）**

  - □ **① user1 のキーを1回だけ使う**（12/13 の「使用済み／未使用」の差を作る）

```bash
AWS_ACCESS_KEY_ID=$(terraform output -raw iam_user1_access_key_id) \
AWS_SECRET_ACCESS_KEY=$(terraform output -raw iam_user1_secret_access_key) \
AWS_SESSION_TOKEN= \
aws sts get-caller-identity
```

user1 の ARN が返れば成功です（権限は何も付いていないので、これ以外は失敗します）。**user2 のキーは使わないでください。** 認証情報レポートへの反映には数時間かかります。

  - □ **② Athena のテーブルを2つ作る**（5章の DDL を実行）

  - □ **③ ALB にアクセスを流し始める**

**先に SSM への登録を確認してください。** このスクリプトは SSM 経由でアプリを一時停止して 503 を作ります。登録前に流すと**503 が1件も作られず、気づくのは 12/9 になります。**

```bash
aws ssm describe-instance-information \
  --query 'InstanceInformationList[].[InstanceId,PingStatus]' --output table
```

2台とも `Online` になってから実行します。

```bash
bash scripts/gen_alb_logs.sh
```

実行中、`=== 4/5` の行で **`503` が15個並ぶこと**を目で確認してください。`200` が並んでいたらアプリが止まっていないので、`status:` の行を見て SSM の失敗理由を確認します。

正常な200、アプリが返す500、ALBが生成する502、ターゲット不在の503、TLS 1.2と1.3のアクセスを一通り作ります。**約4分かかります**（アプリを止めて503を作り、再開してヘルスチェックが戻るまでの待機を含みます）。

ログが S3 に届くまで5〜10分かかります。**このスクリプトは 12/8 と 12/11 にも流します**（12/9・12/11・12/14 の Athena 演習で、それぞれ当日のログを使うため）。

---

## 4. 値の取り方の一覧

**コマンド集は、この環境で打つぶんについては `terraform output` を直接埋め込んだ形で書いてあります。** そのままコピーして打てるので、読み替えは不要です。`~/netsec-study-tf` で実行してください。

下の表は、値を単体で確認したいときと、**担当システムで同じ手順を打つときの読み替え**に使います。

| 項目 | この環境での取得方法 |
|---|---|
| ALB の ARN | `terraform output -raw alb_arn` |
| ターゲットグループの ARN | `terraform output -raw target_group_arn` |
| EC2 のインスタンスID | `terraform output -raw web_instance_id` / `probe_instance_id` |
| web の ENI ID | `terraform output -raw web_eni_id` |
| VPC ID | `terraform output -raw vpc_id` |
| サブネットID（NACL点検用） | `terraform output -raw nacl_demo_subnet_id` |
| RDS のパラメータグループ | `terraform output -raw db_parameter_group` |
| ECS タスク定義のファミリ名 | `terraform output -raw ecs_task_definition` |
| AssumeRole 対象のロール ARN | `terraform output -raw assume_role_arn` |
| state 用バケット / ロック用テーブル | `terraform output -raw tfstate_bucket` / `tflock_table` |
| NAT Gateway の ID（12/7 のみ） | `terraform output -raw nat_gateway_id` |
| セキュリティグループの ID | `aws ec2 describe-security-groups --filters Name=tag:Project,Values=netsec-study --query 'SecurityGroups[].[GroupName,GroupId]' --output table` |
| ALB ログの Athena テーブル | `netsec_study.alb_logs` |
| Flow Logs の Athena テーブル | `netsec_study.vpc_flow_logs` |

**コマンド集に `<クラスタ名>` `<ディストリビューションID>` などのプレースホルダが残っている箇所は、担当システム向けです。** この環境には対応するリソースがありません（§1 の「この環境で用意できない値」）。

**EC2 に入るとき**（`ss` `sysctl` `tcpdump` `dig` を打つ日）：

```bash
aws ssm start-session --target "$(terraform output -raw web_instance_id)"
```

---

## □ 5. Athena のテーブル定義（12/6 に実行）

マネジメントコンソールの Athena を開き、**ワークグループを `netsec-study` に切り替えてから**実行します。`【LOCATION】` は下のコマンドの出力に置き換えてください。

```bash
terraform output -raw athena_alb_log_location     # ALB ログ用
terraform output -raw athena_flowlog_location     # Flow Logs 用
```

**`projection.dt.range` の開始日は `2026/12/06` 固定です。** 都合で構築日を前倒しする場合は、DDL の range も合わせて変えてください。範囲外の日付のログは引けません。

両テーブルとも `dt`（`yyyy/MM/dd` 形式の文字列）でパーティションを切ります。**検索するときは必ず `WHERE dt = '2026/12/11'` のように指定してください。** `time` や `start` はログ本文の列なので、これで絞ってもスキャン量は減りません。区切りはハイフンではなく**スラッシュ**です。

**`dt` は UTC の日付です。** ALB も Flow Logs も、S3 に置かれるパスの `年/月/日` が UTC で決まります。JST とは9時間ずれるので、**JST 09:00 より前に流したログは、前日の `dt` に入ります。**

| 流した時刻（JST） | 入る `dt` |
|---|---|
| 12/11 10:00 | `2026/12/11` |
| 12/11 22:00 | `2026/12/11` |
| **12/11 07:00** | **`2026/12/10`** |

朝に流す日は特に注意してください。0件だったときは、まず前日の `dt` を試し、それでも出なければ実際のパスを見ます。

```bash
aws s3 ls "s3://$(terraform output -raw log_bucket)/alb/AWSLogs/" --recursive | tail -5
```

出力されるパスの末尾が `.../2026/12/11/xxxxx.log.gz` のようになっているので、その `年/月/日` をそのまま `dt` に入れます。

- □ **ALB アクセスログ**

```sql
CREATE EXTERNAL TABLE netsec_study.alb_logs (
  type string, time string, elb string,
  client_ip_port string, target_ip_port string,
  request_processing_time double, target_processing_time double,
  response_processing_time double,
  elb_status_code int, target_status_code string,
  received_bytes bigint, sent_bytes bigint,
  request string, user_agent string,
  ssl_cipher string, ssl_protocol string,
  target_group_arn string, trace_id string,
  domain_name string, chosen_cert_arn string,
  matched_rule_priority string, request_creation_time string,
  actions_executed string, redirect_url string,
  lambda_error_reason string, target_port_list string,
  target_status_code_list string, classification string,
  classification_reason string
)
PARTITIONED BY (dt string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1',
  'input.regex' = '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*:[0-9]*) ([^ ]*[:-][0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^\"]*)\" \"([^\"]*)\" ([A-Z0-9-_]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^ ]*)\" \"([^\\s]+?)\" \"([^\\s]+)\" \"([^ ]*)\" \"([^ ]*)\"(?: .*)?'
)
LOCATION '【ALBログのLOCATION】'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.dt.type' = 'date',
  'projection.dt.range' = '2026/12/06,NOW',
  'projection.dt.format' = 'yyyy/MM/dd',
  'projection.dt.interval' = '1',
  'projection.dt.interval.unit' = 'DAYS',
  'storage.location.template' = '【ALBログのLOCATION】${dt}'
);
```

**正規表現は AWS のドキュメントの例と2箇所違います。**意図的なものなので、そのまま使ってください。

1. クライアントとターゲットを `([^ ]*:[0-9]*)` `([^ ]*[:-][0-9]*)` と**1グループにまとめて**います。ドキュメントの例は IP とポートを別グループに分けており、そのままだと**グループ31個・列29個**で食い違い、4列目以降が全部ずれます（`elb_status_code` に `0.002` が入って NULL になる、など）。列を `client_ip_port` `target_ip_port` の2列にしているので、正規表現側も合わせます。
2. 末尾に `(?: .*)?` を付けています。ALB のログ形式は将来フィールドが**後ろに追加される**ことがあり、その場合この正規表現は行全体にマッチしなくなって**全行 NULL** になります。キャプチャしない形で余りを吸収しておきます。

作成したら、**先に1行読んで列の中身を確かめてください。**ここがずれていると、12/9・12/11・12/14 の ALB クエリがすべて空振りします。実行するのは 3-2 ③ の `gen_alb_logs.sh` を流し、**10分ほど待ってから**です（S3 への配信に時間がかかります）。

```sql
SELECT time, client_ip_port, target_ip_port, elb_status_code, target_status_code, ssl_protocol
FROM netsec_study.alb_logs
WHERE dt = '2026/12/06'
LIMIT 5;
```

`client_ip_port` が `10.0.1.5:52840` のように**IP:ポートの形**で、`elb_status_code` が `200` のような**3桁の数値**になっていれば正しく読めています。`elb_status_code` が NULL だったり、`target_ip_port` にポート番号だけが入っていたら、列がずれています。

- □ **VPC Flow Logs（既定フォーマット）**

```sql
CREATE EXTERNAL TABLE netsec_study.vpc_flow_logs (
  version int, account_id string, interface_id string,
  srcaddr string, dstaddr string, srcport int, dstport int,
  protocol bigint, packets bigint, bytes bigint,
  start bigint, `end` bigint, action string, log_status string
)
PARTITIONED BY (dt string)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ' '
LOCATION '【FlowLogsのLOCATION】'
TBLPROPERTIES (
  'skip.header.line.count' = '1',
  'projection.enabled' = 'true',
  'projection.dt.type' = 'date',
  'projection.dt.range' = '2026/12/06,NOW',
  'projection.dt.format' = 'yyyy/MM/dd',
  'projection.dt.interval' = '1',
  'projection.dt.interval.unit' = 'DAYS',
  'storage.location.template' = '【FlowLogsのLOCATION】${dt}'
);
```

`end` は予約語なので、クエリで使うときもバッククォートで囲みます。

こちらも1行読んで確認します。Flow Logs は S3 に届くまで**10分前後**かかります。

```sql
SELECT from_unixtime(start) AS t, interface_id, srcaddr, dstaddr, dstport, action
FROM netsec_study.vpc_flow_logs
WHERE dt = '2026/12/06'
LIMIT 5;
```

`version` が `2`、`action` が `ACCEPT` か `REJECT` になっていれば読めています。全列が NULL なら、`skip.header.line.count` で読み飛ばすヘッダ行の扱いか、LOCATION の指定を見直してください。

---

## 6. 日別の追加作業

各日の項目はコマンド集の該当日を開いて打ちます。**この章にあるのは、この環境でだけ必要になる追加の操作**（題材の仕込み、当日だけ作るリソース、環境固有の値）です。

### □ 12/7（月）トランスポート層

**この日だけ NAT Gateway と RDS を作ります。**

- □ **① 学習の最初に作る**（RDS の作成に約10分。待ち時間はアプリの四択に充てる）

```bash
cd ~/netsec-study-tf
terraform apply -var="enable_nat=true" -var="enable_rds=true"
```

一覧に **NAT Gateway・EIP・ルート1本・RDS インスタンス**が作成対象として出ていることを確認して `yes` を入力します。

- □ **② TIME_WAIT を作って数える**

```bash
bash scripts/gen_timewait.sh
```

実行前後の件数が表示されます。その後 EC2 に入って、コマンド集の `ss -s` や `sysctl` を自分の手で打ってください。

- □ **③ `max_connections` を検算する**

手順はコマンド集 12/7「DB 接続数の検算」にあります。**RDS が存在するのはこの日だけ**なので、実値は必ず今日取って【メモ】に残してください（12/10 で転記して使います）。

```bash
terraform output -raw rds_endpoint      # psql の接続先
```

- □ **④ ErrorPortAllocation のアラームを作る**

手順はコマンド集 12/7「ErrorPortAllocation の監視設定」にあります。**NAT があるのはこの日だけ**です。作ったら**必ず削除**してください（コマンド集の最後のコマンド）。

- □ **⑤ その日のうちに壊す**

```bash
terraform apply
```

一覧に **NAT Gateway・EIP・ルート・RDS が削除（destroy）対象**として出ていることを確認して `yes` を入力します。RDS の削除に5〜10分かかります。完了後、残っていないことを確認します。

```bash
aws ec2 describe-nat-gateways --filter Name=state,Values=available \
  --query 'NatGateways[].NatGatewayId'                                  # [] ならOK
aws rds describe-db-instances --query 'DBInstances[].DBInstanceIdentifier'  # [] ならOK
```

**消し忘れると NAT Gateway が $1.5/日、RDS が $0.75/日**かかり続けます。ここまでやってその日の作業完了です。

> 12/15 の「最長一致で経路を追う」を、より本番に近い形（プライベートサブネットが NAT 経由で外に出る状態）でやりたい場合は、同じ方法でその日も NAT を作れます。追加で $0.3 程度です。NAT が無い状態でも、**外への経路を持たないプライベートサブネット**として点検の題材にはなります。

### □ 12/8（火）名前解決・DNS

- □ **① VPC内の EC2 から `dig` を打つ**
- □ **② ALB アクセスログを再生成する**（12/9 で使う）

プライベートホストゾーンは **VPC の中からしか引けません。** EC2 に入って打ちます。

```bash
aws ssm start-session --target "$(terraform output -raw web_instance_id)"
```

引く名前はコマンド集 12/8「リゾルバと権威サーバを打ち分ける」にまとめてあります（`app` / `short` / `alias` の3レコード）。`dig @8.8.8.8` `+trace` は外部の名前（example.com など）で試します。

**②** は手元（WSL2）に戻ってから実行します。翌日の Athena で使うログを、余裕をもって貯めておくためです。

```bash
exit                                # EC2 から抜ける
cd ~/netsec-study-tf
bash scripts/gen_alb_logs.sh        # 約4分（アプリ停止・再開の待機を含む）
```

### □ 12/9（水）HTTP と上位プロトコル

- □ **① ログが届いていることを確認する**（コマンド集 12/9 の件数クエリ）
- □ **② 5xx の3パターンを Athena で読み分ける**

**前日までに `gen_alb_logs.sh` を流してあること。** 流していなければ、朝に実行して10分待ってから Athena を使ってください。この日のクエリの対象は **12/8 に流したログ**（`dt = '2026/12/08'`）です。

作られる行の対応は次のとおりです。

| 作った操作 | ログ上の見え方 |
|---|---|
| `/status500` | `elb_status_code` = 500、`target_status_code` = 500（**アプリが返した 5xx**） |
| `/abort` | `elb_status_code` = 502、`target_status_code` = `-`（**ALB が生成した 5xx**） |
| アプリ停止中のアクセス | `elb_status_code` = 503、`target_processing_time` = **-1** |

### □ 12/10（木）負荷分散・トラフィック制御

- □ **① ALB とターゲットグループの設定値を取得する**
- □ **② 切り離し時間を算出する**

この日は新しく作るものも、環境固有の追加操作もありません。コマンド集 12/10 をそのまま打ってください。取れた値の答え合わせは **§1 の設定値表**で行います。

**DB のタイムアウト値（`max_connections`）は 12/7 の【メモ】から転記します。** RDS は 12/7 のうちに破棄しているので、この日には取れません。

### □ 12/11（金）ネットワーク可観測性

- □ **① ALB アクセスログを再生成する**（この日の p99 集計と、12/14 の TLS 分布で使う）
- □ **② Flow Logs に REJECT を生成する**
- □ **③ Athena で ENI を絞って抽出する**
- □ **④ EC2 の中で `tcpdump` を打つ**

**①と②を続けて流し、待ち時間をまとめてください。** どちらも S3 への配信に5〜10分かかるので、別々に待つと20分が溶けます。①を流す理由は、この日の演習（「5xx 発生時刻の前後で p99 を集計する」）を当日のログで行うためと、12/14 の TLS バージョン分布がこのログを使うためです。12/6・12/8 のログも残っているので、時間が無ければ①は飛ばして `dt = '2026/12/08'` を対象にしても構いません。**その場合は 12/14 の TLS バージョン分布も `dt = '2026/12/08'` に読み替えてください**（12/11 のログが存在しないので、`dt = '2026/12/11'` のままだと0件になります）。

```bash
cd ~/netsec-study-tf
bash scripts/gen_alb_logs.sh        # 約4分
bash scripts/gen_reject.sh          # 表示される ENI ID を控える
```

**ここで③④の順序を入れ替えて、配信待ちの間に `tcpdump`（④）を先に済ませます。** クエリ2本はコマンド集 12/11 にあります。10分たったらそちらに戻ってください。

`tcpdump` もコマンド集 12/11「tcpdump の基本フィルタ」のとおり、EC2 の中で打ちます。**この環境で注意が要るのはパケットを流す側です。** `curl` 1回では ALB がターゲットへの接続を使い回すため、3ウェイハンドシェイクが起きず SYN が捕まりません。別ターミナルから `bash scripts/gen_timewait.sh 200` を流すのが確実です。

### □ 12/13（日）IAM ＋ シークレット

- □ **① `aws sts assume-role` を実行し、一時認証情報の中身と有効期限を見る**
- □ **② 認証情報レポートで user1（使用済み）と user2（未使用）の差を見る**
- □ **③ タスク定義の `secrets` の書き方を読む**

コマンド集 12/13 をそのまま打ちます。この環境で見るべき点は2つです。

- 認証情報レポートでは **user1 が「使用済み」、user2 が「未使用」**として出ます（12/6 に user1 のキーだけ1回使ったため）
- 見本のタスク定義は `DB_CREDENTIALS`（Secrets Manager）と `API_KEY`（SSM パラメータ）を `secrets` で、`STAGE` を `environment` で渡しています

### □ 12/14（月）TLS / PKI

- □ **① SNI の有無で返る証明書が変わることを確認する**
- □ **② 証明書チェーンとプロトコル・暗号スイートを読む**
- □ **③ リスナーのセキュリティポリシーを CLI で確認する**
- □ **④ ALB ログから TLS バージョン分布を集計する**

**④の対象は 12/11 に流したログです**（`dt = '2026/12/11'`）。12/11 の①を飛ばした場合は `dt = '2026/12/08'` に読み替えます。`gen_alb_logs.sh` が TLS 1.2 と 1.3 のアクセスを30件ずつ作っているので、その2種が出ます。**この日に新しくログを流す必要はありません。** クエリはコマンド集 12/14 の最後にあります。

**証明書は自己署名です。** `Verify return code` は 0 以外（18 や 19）になりますが、プロトコル・暗号スイート・SNI の確認には支障ありません。むしろ検証エラーの読み方を覚える題材になります。

コマンドはコマンド集 12/14 にあります。SNI に `app.study.internal` を付けると app の証明書、`-noservername` なら default の証明書が返ります。

リスナーのポリシーは TLS 1.2 以上のみ許可です（§1 の設定値表）。古いバージョンでの接続が拒否されることを確認してください。ただし**手元の OpenSSL 3.x が TLS 1.0/1.1 を既定で無効にしている場合、サーバに届く前にクライアント側で失敗します。** その場合はポリシーの中身を CLI で確認する方法に切り替えます。

### □ 12/15（火）クラウドネットワーク設計

- □ **① ルートテーブル3種の違いを見る**
- □ **② NACL の番号順の評価を読む**
- □ **③ 必要なら NAT を足して、経路が増える様子を見る（任意）**

コマンドはコマンド集 12/15 にあります。**この VPC にはルートテーブルが3つ**あり、どれがどのサブネットに付いているかは §1 の設定値表で確認できます。数が合わないと悩むので、先に押さえてください。

**最長一致は `0.0.0.0/0` と `10.30.0.0/16`（local）の関係で読めます。** VPC 内宛ての通信は、`0.0.0.0/0` があっても local が勝ちます。

**プライベートサブネットには外向きの経路がありません。** ③ で NAT を足すと `private` に `0.0.0.0/0` が1本増え、最長一致の題材がより本番に近くなります（12/7 と同じ方法、追加 $0.3 程度）。

```bash
terraform apply -var="enable_nat=true"    # 経路が1本増える
# 確認が終わったら
terraform apply                           # 元に戻す（NAT を壊す）
```

### □ 12/16（水）キャパシティ

- □ **① サブネットごとの空きIP数を取得する**
- □ **② `/28` を題材に必要IP数を逆算する**

コマンドはコマンド集 12/16 にあります。逆算の題材は `netsec-study-tiny-28`（`/28`、使えるIPの数は §1 の設定値表）です。

### □ 12/17（木）サプライチェーン

- □ **① `sample-insecure` を git リポジトリにする**
- □ **② tfsec / Checkov を実行する**
- □ **③ gitleaks で履歴を検査する（`--redact` を必ず付ける）**
- □ **④ state バックエンドの4点（暗号化・バージョニング・PAB・ロック）を確認する**

**tfsec・Checkov・gitleaks は §2-1b で導入済みのはずです。** 入っていなければ、この日の作業に入る前に §2-1b を実行してください（ネットワーク越しの取得と `pip install` で10分ほどかかります）。

```bash
tfsec --version; checkov --version; gitleaks version   # 3つともバージョンが出ること

cd ~/netsec-study-tf/sample-insecure
# README.md のとおり git init → commit してからスキャンする
```

state バックエンドの4点確認は、作った S3 と DynamoDB に対して打ちます（4章の読み替え表）。

### □ 12/18（金）脆弱性・境界防御

- □ **① SSM Session Manager で EC2 に接続する**
- □ **② ECR の拡張スキャンを試す（任意。Inspector の課金が発生）**
- □ **③ ②を試した場合は、その日のうちに無効化してリポジトリも消す**

```bash
aws ssm start-session --target "$(terraform output -raw web_instance_id)"
```

ECR は既定では作りません。**②は任意です。** 試す場合は次の手順ですが、前提が2つあります。

- **Inspector の課金が発生します**（確認後に必ず無効化してください）
- **Docker が要ります。** §2 では導入していません。入っていない場合は WSL2 に Docker Engine を入れるところから始まるので、時間が無ければ②は飛ばして、コマンド集の手順を読み下すだけでも構いません

```bash
docker --version      # 入っているか先に確認する
```

```bash
# 1. リポジトリを作る
terraform apply -var="enable_ecr=true"

# 2. 古いイメージを push する（Docker が必要）
REPO=$(terraform output -raw ecr_repository)
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.ap-northeast-1.amazonaws.com
docker pull python:3.9-slim            # 古めのイメージほど検出が出る
docker tag python:3.9-slim ${ACCOUNT}.dkr.ecr.ap-northeast-1.amazonaws.com/${REPO}:old
docker push ${ACCOUNT}.dkr.ecr.ap-northeast-1.amazonaws.com/${REPO}:old

# 3. 拡張スキャンを有効化（コマンド集 12/18）
# 4. 確認後に無効化し、リポジトリも消す
aws inspector2 disable --resource-types ECR
terraform apply -var="enable_ecr=false"
```

### □ 12/20（日）監査ログ・脅威検知

- □ **① CloudTrail でこの環境の構築操作を検索する**
- □ **② Security Hub を試す（任意。AWS Config の課金が発生）**
- □ **③ ②を試した場合は、その日のうちに無効化する**
- □ **④ 環境を破棄する（§9）**

**CloudTrail はこの環境の構築操作がそのまま証跡になっています。** 検索はコマンド集 12/20 のとおりで、`AttributeValue` に `netsec-study-web` や `CreateSecurityGroup` を入れれば当たります。期間は 12/6 以降で足ります。

**Security Hub は既定では有効にしていません。** 有効化すると AWS Config の記録も必要になり、月に数ドルかかります。試す場合は当日に有効化し、確認が終わったら無効化してください。

```bash
aws securityhub enable-security-hub --enable-default-standards
# 確認後
aws securityhub disable-security-hub
```

---

## 7. 注意事項

- **ALB は全世界に開放しています。** 返すのは `ok` だけの検証用アプリですが、学習期間が終わったら必ず壊してください
- **`terraform.tfstate` に機密が入ります。** IAM ユーザのシークレットキー、自己署名証明書の秘密鍵、Secrets Manager の値が平文で保存されます。共有しないでください
- **ALB アクセスログの配信は5分間隔、Flow Logs は最大10分**かかります。流した直後に Athena で検索しても出ません
- **Athena のワークグループにスキャン量の上限（1GB/クエリ）を設定してあります。** 超えるとクエリが止まりますが、これは想定どおりの動作です
- **`tcpdump` は EC2 の中で打ちます。** 手元の WSL2 で打っても、WSL2 自身の通信しか見えません
- **NAT Gateway と RDS は、作った日のうちに必ず戻してください。** `terraform.tfvars` を書き換えず `-var` で有効にしているのは、戻し忘れても次の `terraform apply` で自動的に削除されるようにするためです
- **12/20 に壊します。** 口述中心の第4期（12/21〜1/10）では環境は不要です

---

## 8. 費用

| 項目 | 概算 |
|---|---|
| ALB | $0.58/日 |
| EC2 t4g.micro × 2（パブリックIPを含む） | $0.75/日 |
| Route 53 プライベートホストゾーン | $0.50/月 |
| Secrets Manager | $0.40/月 |
| S3・Flow Logs・Athena・DynamoDB | 合計で $1 未満 |
| NAT Gateway（12/7 に数時間だけ） | 約 $0.3 |
| RDS（12/7 に数時間だけ） | 約 $0.2 |
| **合計（12/6〜12/20 の15日）** | **約 $20〜25** |

想定を超えるとしたら、**壊し忘れ**か、ECR 拡張スキャン（Inspector）か Security Hub の有効化したままです。

---

## □ 9. 破棄（12/20・日）

- □ **① `terraform destroy` を実行する**
- □ **② 下のチェックリストをすべて確認する**
- □ **③ 予算アラートを削除する（任意）**

```bash
cd ~/netsec-study-tf
terraform destroy       # 約5分
```

一覧を確認して `yes` を入力します。そのあと、**Terraform で消えないもの**を確認します。**すべて空（または結果なし）になれば完了です。**

| 済 | 対象 | 確認コマンド |
|---|---|---|
| □ | EC2 とALB | `aws ec2 describe-instances --filters Name=tag:Project,Values=netsec-study Name=instance-state-name,Values=running --query 'Reservations[].Instances[].InstanceId'` |
| □ | **NAT Gateway**（12/7 に作った場合） | `aws ec2 describe-nat-gateways --filter Name=state,Values=available --query 'NatGateways[].NatGatewayId'` |
| □ | **Elastic IP** | `aws ec2 describe-addresses --query 'Addresses[].[PublicIp,AssociationId]' --output table` |
| □ | **RDS**（12/7 に作った場合） | `aws rds describe-db-instances --query 'DBInstances[].DBInstanceIdentifier'` |
| □ | RDS スナップショット | `aws rds describe-db-snapshots --snapshot-type manual --query 'DBSnapshots[].DBSnapshotIdentifier'` |
| □ | タグ付きリソース全般 | `aws resourcegroupstaggingapi get-resources --tag-filters Key=Project,Values=netsec-study --query 'ResourceTagMappingList[].ResourceARN' --output table` |
| □ | S3 バケット | `aws s3 ls \| grep netsec-study` |
| □ | IAM ユーザ | `aws iam list-users --query "Users[?starts_with(UserName,'netsec-study')].UserName"` |
| □ | ACM 証明書 | `aws acm list-certificates --query 'CertificateSummaryList[].[DomainName,CertificateArn]' --output table` |
| □ | Route 53 ホストゾーン | `aws route53 list-hosted-zones --query 'HostedZones[].Name'` |
| □ | **Inspector（ECRを試した場合）** | `aws inspector2 batch-get-account-status --query 'accounts[].resourceState'` |
| □ | **Security Hub（試した場合）** | `aws securityhub get-enabled-standards` |
| □ | **AWS Config（Security Hubを試した場合）** | `aws configservice describe-configuration-recorder-status` |
| □ | 予算アラート | `aws budgets delete-budget --account-id "$(aws sts get-caller-identity --query Account --output text)" --budget-name netsec-study` |

**Inspector・Security Hub・AWS Config を有効にした場合は、必ず無効に戻してください。** これらは `terraform destroy` の対象外で、有効なままだと課金が続きます。

最後に、翌月の請求でこの学習分の課金が止まっていることを確認して終了です。
