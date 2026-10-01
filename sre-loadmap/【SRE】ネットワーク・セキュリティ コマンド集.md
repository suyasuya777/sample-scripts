# 【SRE】ネットワーク・セキュリティ コマンド集

対象：`【SRE】2026年12月学習進捗表-ネットワーク・セキュリティ ロードマップ.md` の【実機】【調査】項目
環境：`【SRE】ネットワーク・セキュリティ テスト環境構築手順.md` で作るテスト環境
使い方：その日のページを開いて、上から順に打つ。出力の**どこを見るか**を各コマンドの下に書いてあります

**済管理のルール**：`□` を `☑` に書き換えて進めます（進捗表・構築手順と同じ記法）。
見出しの `□` はその日全体の済、項目の `□` は個別コマンドの済です。

---

## 索引

| 済 | 日付 | 章 | 主に使うもの |
|---|---|---|---|
| □ | 事前準備 | ― | 実行場所の決定、ツールの導入（構築手順 §2） |
| □ | 12/7 | 1. トランスポート層 | `ss` `sysctl`／ALB・ターゲットグループの設定値取得 |
| □ | 12/8 | 2. 名前解決・DNS | `dig` `/etc/resolv.conf` |
| □ | 12/9 | 3. HTTP と上位プロトコル | Athena（ALBアクセスログ） |
| □ | 12/10 | 5. 負荷分散 | ヘルスチェック・登録解除遅延・各層タイムアウトの取得 |
| □ | 12/11 | 8. ネットワーク可観測性 | ALBログ再生成／`curl -w` `tcpdump`／Athena（Flow Logs・ALB） |
| □ | 12/13 | IAM・シークレット | `aws sts assume-role`／認証情報レポート／タスク定義 |
| □ | 12/14 | 4. TLS / PKI | `openssl s_client`／セキュリティポリシー確認／Athena（TLS分布） |
| □ | 12/15 | 6. クラウドネットワーク設計 | ルートテーブル・SG・NACL の確認 |
| □ | 12/16 | 7. コンテナNW ＋ 9. キャパシティ | `describe-subnets`／Service Quotas |
| □ | 12/17 | サプライチェーン | tfsec / Checkov / gitleaks |
| □ | 12/18 | 脆弱性・境界防御 | ECR スキャン／SSM Session Manager |
| □ | 12/20 | 監査ログ・脅威検知 | CloudTrail 検索／Security Hub |
| ― | 随時 | **詰まったときに見る** | 症状別の切り分け（巻末） |

---

## □ 0. 事前準備（11/23〜11/30）

### 0-1. どこで実行するか

コマンドによって「打つべき場所」が違います。**ここを先に決めておかないと、当日に詰まります。**

| コマンド | 実行場所 | 理由 |
|---|---|---|
| `ss` `sysctl` `tcpdump` | **調べたい通信が流れているホスト**（EC2 など） | 手元のPCで打っても、そのPC自身のソケットしか見えない |
| `dig`（社内・VPC内の名前） | **VPC 内のホスト** | プライベートホストゾーンは VPC 外から引けない |
| `dig`（外部の名前）・`curl`・`openssl` | 手元の Linux でよい | 外から見た挙動の確認 |
| `aws` CLI | 手元でよい | 認証情報があればどこからでも |
| `scripts/*.sh`（仕込み） | 手元。`~/netsec-study-tf` で実行 | 中で SSM 経由の実行と `terraform output` を使う |
| Athena のクエリ | マネジメントコンソール | **ワークグループを `netsec-study` に切り替えてから**実行する |
| tfsec / Checkov / gitleaks | 手元（リポジトリのある場所） | ― |

**`aws` CLI のコマンドは `~/netsec-study-tf` で実行してください。** この手順書では、値を `terraform output` から直接取る形で書いてあります。担当システムで打つ場合は、その部分を実際の値に置き換えます。

**Fargate の最小イメージには `ss` `tcpdump` `dig` が入っていません。** タスクの中を見たい場合は ECS Exec を使いますが、ツールが無ければ入れる必要があります。

```bash
# Fargate タスクに入る（タスク定義で enableExecuteCommand が有効なこと）
aws ecs execute-command --cluster <クラスタ名> --task <タスクID> \
  --container <コンテナ名> --interactive --command "/bin/sh"
```

> **このテスト環境には ECS のクラスタとサービスがありません**（タスク定義だけ作ってあります）。上のコマンドと、12/7・12/15・12/16 に出てくる `aws ecs describe-services` / `list-tasks` は**担当システム向け**です。テスト環境では、該当する値を仮置きして計算式だけを確立します（構築手順 §1「この環境で用意できない値」）。

- □ **0-2. ツールを入れる（手元の Linux / WSL2）**

**導入は構築手順 §2-1 と §2-1b で行います。**Terraform は Ubuntu の標準リポジトリに無いので、HashiCorp のリポジトリを追加してから `apt install` してください。**順序を誤ると1行まるごと中止され、`jq` が入りません**（`jq` が無いと仕込みスクリプトが動きません）。

```bash
# 確認だけ（すべてバージョンが出ればOK）
terraform version; aws --version; session-manager-plugin --version
jq --version; dig -v; curl --version | head -1; openssl version
tfsec --version; checkov --version; gitleaks version
```

`ss` と `tcpdump` は**EC2 の中で打ちます**（手元で打っても手元のソケットしか見えません）。EC2 側には `user_data` で導入済みなので、手元に入れる必要はありません。

- □ **0-3. 環境を使う準備（構築手順 §2）**

テスト環境は自分のアカウントに作るため、**権限の確認は不要です**（管理者権限で実施します）。代わりに、次の3つを構築手順 §2 で済ませてください。

- Terraform・AWS CLI・Session Manager プラグイン・`jq` の導入（§2-1）
- スキャンツール tfsec・Checkov・gitleaks の導入（§2-1b。12/17 で使う）
- `aws sts get-caller-identity` で認証を確認、予算アラートの作成
- Terraform 一式を配置し、`terraform init` と `terraform plan` が通ること

- □ **0-4. ログの用意（12/9・12/11・12/14 で使用）**

ALB アクセスログ・VPC Flow Logs・Athena のテーブルは、**テスト環境がすべて用意します。**
事前の確認は不要で、**12/6 の構築（構築手順 §3・§5）で揃います。**

```bash
# 構築後、有効になっていることの確認（12/6 に実施）
cd ~/netsec-study-tf
aws elbv2 describe-load-balancer-attributes --load-balancer-arn "$(terraform output -raw alb_arn)" \
  --query "Attributes[?starts_with(Key,'access_logs')]" --output table
aws ec2 describe-flow-logs \
  --query 'FlowLogs[].[FlowLogId,ResourceId,TrafficType,LogDestination]' --output table
```

Athena のテーブルは **`netsec_study.alb_logs`** と **`netsec_study.vpc_flow_logs`** の2つです。どちらも `dt`（`yyyy/MM/dd` 形式の文字列）でパーティションを切ってあります。

**検索するときは必ず `WHERE dt = '2026/12/11'` のように指定してください。** `time` や `start` はログ本文の列なので、そこで絞ってもスキャン量は減りません。区切りはハイフンではなく**スラッシュ**です。ワークグループ `netsec-study` には1クエリ1GBの上限を設定してあります。

**`dt` は UTC の日付です。** S3 のパスの `年/月/日` が UTC で決まるため、JST とは9時間ずれます。**JST 09:00 より前に流したログは、前日の `dt` に入ります**（12/11 07:00 JST に流すと `dt = '2026/12/10'`）。朝に流す日は特に注意してください。ログ本文の `time`（ALB）と `start`（Flow Logs）も UTC です。

ログが作られる日は次のとおりです。**その日に流していない日付を指定しても0件です。**

| ログ | 作られる日（`dt`） | 作る手順 |
|---|---|---|
| ALB アクセスログ | 12/6・12/8・12/11 | `bash scripts/gen_alb_logs.sh` |
| VPC Flow Logs（REJECT） | 12/11 | `bash scripts/gen_reject.sh` |

担当システムで打つ場合の読み替えは構築手順 §4 にあります。

---

## □ 12/7（月）1. トランスポート層

- □ **TIME_WAIT の実数を数える**

EC2 の中で打ちます（`aws ssm start-session --target "$(terraform output -raw web_instance_id)"`）。

```bash
ss -Htan state time-wait | wc -l
```

**`-H` はヘッダ行を出さないオプションです。** これを付けないとヘッダの1行を数えてしまい、実数より1多くなります。**数千〜数万なら、短時間に大量の接続を開閉している**ということです。

テスト環境では、先に手元で `bash scripts/gen_timewait.sh` を流すと 3000 本ぶん作られます。

- □ **ソケットのサマリを見る**

```bash
ss -s
```

`TCP:` の行にある `estab`（確立済み）と `timewait` を見ます。`estab` の数が接続プールの上限付近で張り付いていれば、プールが枯渇しかけています。

```bash
# 特定の宛先ポート（例：PostgreSQL）への確立済み接続だけを数える
ss -Htan state established '( dport = :5432 )' | wc -l
```

- □ **エフェメラルポートの範囲を確認する**

```bash
sysctl net.ipv4.ip_local_port_range
```

既定はおおむね `32768 60999`（約28000個）です。**この数を1つの宛先に対して使い切ると、新規接続が張れなくなります。**

```bash
# 関連する設定もあわせて確認
sysctl net.ipv4.tcp_tw_reuse net.core.somaxconn
```

- □ **ALB の idle timeout とアプリ側 Keep-Alive を突き合わせる**

```bash
cd ~/netsec-study-tf
aws elbv2 describe-load-balancer-attributes \
  --load-balancer-arn "$(terraform output -raw alb_arn)" \
  --query "Attributes[?Key=='idle_timeout.timeout_seconds']" --output text
```

既定は60秒です。この環境の値は構築手順 §1 の設定値表で答え合わせします。**アプリ側の Keep-Alive はこれより長く**します。逆転していると、ALB が生きていると思っている接続をアプリ側が先に閉じ、次のリクエストで502になります。アプリ側の値は設定ファイル（nginx の `keepalive_timeout`、uvicorn の `--timeout-keep-alive` など）で確認します。

- □ **DB 接続数の検算**

```bash
# RDS の max_connections（パラメータグループの設定値）
cd ~/netsec-study-tf
aws rds describe-db-parameters \
  --db-parameter-group-name "$(terraform output -raw db_parameter_group)" \
  --query "Parameters[?ParameterName=='max_connections'].[ParameterValue,ApplyType]" --output text
```

```bash
# ECS サービスのタスク数 ※担当システム向け。テスト環境にサービスはありません
aws ecs describe-services --cluster <クラスタ名> --services <サービス名> \
  --query 'services[].[desiredCount,runningCount]' --output table
```

`max_connections` が `{DBInstanceClassMemory/9531392}` のような式で返る場合は、実値を DB に接続して確認します。

テスト環境では、RDS を作った日（12/7）に EC2 から接続して読みます。

```bash
aws ssm start-session --target "$(terraform output -raw web_instance_id)"
```

```bash
sudo dnf install -y postgresql16 || sudo dnf install -y postgresql15
PGPASSWORD='StudyOnly12345!' psql -h <rds_endpoint> -U postgres -d study -c "SHOW max_connections;"
```

`<rds_endpoint>` は手元で `terraform output -raw rds_endpoint` から取ります。db.t4g.micro（1GB）なら100前後です。

```sql
-- PostgreSQL
SHOW max_connections;
-- MySQL
SHOW VARIABLES LIKE 'max_connections';
```

**検算**：`プール最大数 × タスク数 ≦ max_connections`。アプリ側のプール設定（SQLAlchemy の `pool_size` + `max_overflow` など）を掛け合わせます。

- □ **ErrorPortAllocation の監視設定**

この環境には SNS トピックがないので、`--alarm-actions` は外します。**どのメトリクスを、どの Dimension で監視するか**を確かめるのが目的です。

```bash
cd ~/netsec-study-tf
aws cloudwatch put-metric-alarm \
  --alarm-name netsec-study-nat-port-allocation \
  --namespace AWS/NATGateway --metric-name ErrorPortAllocation \
  --dimensions Name=NatGatewayId,Value="$(terraform output -raw nat_gateway_id)" \
  --statistic Sum --period 300 --evaluation-periods 1 \
  --threshold 0 --comparison-operator GreaterThanThreshold

aws cloudwatch describe-alarms --alarm-names netsec-study-nat-port-allocation \
  --query 'MetricAlarms[].[AlarmName,StateValue]' --output table

# 確認できたら消す
aws cloudwatch delete-alarms --alarm-names netsec-study-nat-port-allocation
```

作成直後は `INSUFFICIENT_DATA` です。実際に値が入るのは NAT の背後から同一宛先へ大量に接続してポートを使い切ったときだけなので、学習環境では枯渇させません。通知先を付ける場合は `--alarm-actions <SNSトピックARN>` を足します。

**NAT Gateway はこの日だけ作ります**（構築手順 §6「12/7」①）。上のコマンドはその間に打ってください。

---

## □ 12/8（火）2. 名前解決・DNS

- □ **リゾルバと権威サーバを打ち分ける**

```bash
# パブリックリゾルバに聞く
dig @8.8.8.8 example.com +noall +answer

# 権威サーバを調べてから、そこに直接聞く
dig NS example.com +short
dig @<上で出たNSサーバ> example.com +noall +answer
```

**両者の答えが食い違ったら、リゾルバ側のキャッシュが古い**ということです。切替作業後に「一部のクライアントだけ旧IPに行く」現象の正体がこれです。

EC2 の中で打ちます。この環境のプライベートホストゾーンは `study.internal` で、3つのレコードがあります。

```bash
# VPC 内から Amazon 提供の DNS に聞く（プライベートホストゾーンの確認）
dig @169.254.169.253 app.study.internal +noall +answer

dig app.study.internal   +noall +answer    # TTL 300
dig short.study.internal +noall +answer    # TTL 60
dig alias.study.internal +noall +answer    # CNAME（ANSWER が2行になる）
```

- □ **名前解決の経路をたどる**

```bash
dig +trace example.com
```

ルートサーバ（`.`）→ TLD（`com.`）→ 権威サーバ、と降りていきます。**どの段階で応答が止まったか**が、そのまま失敗箇所です。

```bash
cat /etc/resolv.conf
```

`nameserver` の行が、このホストが最初に聞きに行く先です。`search` と `ndots` の指定があると、短い名前に勝手にドメインが補完されます。

- □ **TTL と レコード種別を読む**

```bash
dig example.com A +noall +answer
```

```
example.com.   43  IN  A  93.184.216.34
               ↑ TTLの残り秒数
```

**同じコマンドを数秒後にもう一度打って、この数字が減っていればキャッシュ済み**、元の値に戻っていればキャッシュが切れて引き直された、と判断できます。

```bash
dig example.com +short          # 値だけほしいとき
```

- □ **切替の逆算（【調査】の材料）**

TTL を下げてから切り替えるまでの待機は、**旧TTLの秒数ぶん**必要です。現在のTTLが 86400（1日）なら、切替の**1日以上前**に TTL を 60 秒へ下げ、その後で切り替えます。

**切替完了までの最悪時間 ＝ 障害検知時間 ＋ 切替時点のTTL**。この式で試算し、記録します。

---

## □ 12/9（水）3. HTTP と上位プロトコル

この日は Athena で ALB アクセスログを読みます。**マネジメントコンソールの Athena で、ワークグループを `netsec-study` に切り替えてから**実行してください。

`dt` は前日までに `gen_alb_logs.sh` を流した日です（12/6 または 12/8）。**担当システムで打つ場合はテーブル名とパーティション列を読み替えてください。**

- □ **まずログが届いているか数える**

```sql
SELECT count(*) AS rows, min(time) AS first, max(time) AS last
FROM netsec_study.alb_logs
WHERE dt = '2026/12/08';
```

**0件なら配信待ちです**（S3 への配信は5分間隔、Athena で引けるまで5〜10分）。数百件あれば仕込みは成功しているので、次に進みます。**10分待っても0件なら、`gen_alb_logs.sh` を流した日付と `dt` が合っているかを疑ってください。**

- □ **LB が生成した 5xx と、アプリが返した 5xx を区別する**

```sql
SELECT time, elb_status_code, target_status_code,
       target_processing_time, request, target_ip_port
FROM netsec_study.alb_logs
WHERE dt = '2026/12/08'
  AND elb_status_code >= 500
  AND target_status_code <> CAST(elb_status_code AS varchar)
ORDER BY time
LIMIT 100;
```

**判別の基準**：`target_status_code` が `-` なら**ターゲットが応答を返していない**＝ALB が生成した 5xx（502・503・504）。数値が入っていて `elb_status_code` と一致していれば、アプリが返した 5xx です。

- □ **応答が返らなかった行を探す**

```sql
SELECT time, elb_status_code, target_status_code,
       request_processing_time, target_processing_time, response_processing_time
FROM netsec_study.alb_logs
WHERE dt = '2026/12/08'
  AND target_processing_time = -1
ORDER BY time
LIMIT 100;
```

`-1` は**ターゲットに繋がらなかった、または応答前に切れた**ことを示します。担当システムの平常時にはまず出ないので、その場合は負荷試験時のログを対象にしてください。テスト環境では `gen_alb_logs.sh` がアプリを一時停止して 503 を作るので、この行が出ます。

- □ **502 の原因を絞る**

```sql
SELECT elb_status_code, target_status_code, count(*) AS cnt
FROM netsec_study.alb_logs
WHERE dt = '2026/12/08'
GROUP BY 1, 2
ORDER BY cnt DESC;
```

**`dt` だけで1日ぶんに絞れます。** さらに時間帯を切る場合は `AND time BETWEEN '2026-12-08T09:00' AND '2026-12-08T10:00'` を足します（`time` は文字列なので前方一致の比較になります）。

502 が **デプロイ時刻に集中**していれば、登録解除遅延とアプリのドレイン処理の噛み合わせ（12/10 の項目）が原因である可能性が高くなります。

---

## □ 12/10（木）5. 負荷分散・トラフィック制御

- □ **切り離し時間を算出する**

```bash
cd ~/netsec-study-tf
aws elbv2 describe-target-groups --load-balancer-arn "$(terraform output -raw alb_arn)" \
  --query 'TargetGroups[].[TargetGroupName,HealthCheckIntervalSeconds,UnhealthyThresholdCount,HealthyThresholdCount,HealthCheckTimeoutSeconds]' \
  --output table
```

取れた値の答え合わせは構築手順 §1 の設定値表で行います。

**切り離しまでの時間 ＝ ヘルスチェック間隔 × 異常閾値**。間隔10秒・閾値2なら約20秒です。この間、異常なターゲットにリクエストが流れ続けます。

- □ **登録解除の遅延を確認する**

```bash
aws elbv2 describe-target-group-attributes \
  --target-group-arn "$(terraform output -raw target_group_arn)" \
  --query "Attributes[?Key=='deregistration_delay.timeout_seconds']" --output text
```

既定は300秒です。この環境の値は構築手順 §1 の設定値表にあります。**アプリの最長処理時間より短いと、処理中のリクエストが打ち切られます。**

- □ **各層のタイムアウトを全部並べる**

```bash
cd ~/netsec-study-tf

# ALB
aws elbv2 describe-load-balancer-attributes \
  --load-balancer-arn "$(terraform output -raw alb_arn)" \
  --query "Attributes[?Key=='idle_timeout.timeout_seconds']" --output text

# ECS タスクの停止猶予（この環境の見本タスク定義では未設定なので null が返る）
aws ecs describe-task-definition \
  --task-definition "$(terraform output -raw ecs_task_definition)" \
  --query 'taskDefinition.containerDefinitions[].[name,stopTimeout]' --output table
```

```bash
# CloudFront ※担当システム向け。テスト環境に CloudFront はありません
aws cloudfront get-distribution-config --id <ディストリビューションID> \
  --query 'DistributionConfig.Origins.Items[].CustomOriginConfig.[OriginReadTimeout,OriginKeepaliveTimeout]' --output table
```

**テスト環境で実値が取れるのは ALB だけです。** DB の `max_connections` は **12/7 の【メモ】から転記**します（RDS は 12/7 のうちに破棄しているため、この日には取れません）。CloudFront とアプリ側は仮の値を置いて、全層の表を完成させるところまでが到達点です。アプリ側・DB側の値は設定ファイルから拾います。**外側ほど長く**なっているか（クライアント ＞ CloudFront ＞ ALB ＞ アプリ ＞ DB）を点検します。逆転があれば、そこが 504 の発生源です。

- □ **リトライの掛け算**

3層がそれぞれ3回リトライすると、**最下層には 3 × 3 × 3 = 27 リクエスト**が届きます。各層の設定値を拾って掛け算し、記録してください。

---

## □ 12/11（金）8. ネットワーク可観測性

- □ **先にログを仕込む**

この日の Athena クエリ2本に使うログを作ります。**手順は構築手順 §6「12/11」**（`gen_alb_logs.sh` と `gen_reject.sh` を続けて流し、配信待ちの10分で `tcpdump` を済ませる）。表示された ENI ID を控えてから、以下に進んでください。

- □ **時間の内訳を出す**

```bash
ALB=$(terraform output -raw alb_dns_name)
curl -o /dev/null -s -w \
'dns    : %{time_namelookup}\nconnect: %{time_connect}\ntls    : %{time_appconnect}\nttfb   : %{time_starttransfer}\ntotal  : %{time_total}\n' \
"https://${ALB}/"
```

**証明書は自己署名なので、検証を通すなら `-k` を付けます。** `https://` で叩くと `time_appconnect` に TLS ハンドシェイクの時間が入ります。`http://` では 0 になります。サーバ側の処理時間を見たいときは `/slow?sec=3` を叩くと `time_starttransfer` が伸びます。

**読み方**：

| 区間 | 意味 | 遅いときに疑うもの |
|---|---|---|
| `time_namelookup` | 名前解決まで | DNS、`ndots` による余計な検索 |
| `time_connect` − `time_namelookup` | TCP 接続確立 | 経路、SG、距離（RTT） |
| `time_appconnect` − `time_connect` | TLS ハンドシェイク | 証明書チェーン、TLSバージョン |
| `time_starttransfer` − `time_appconnect` | サーバ側の処理 | **アプリと DB** |
| `time_total` − `time_starttransfer` | 応答の転送 | レスポンスサイズ、帯域 |

```bash
# 毎回書くのが面倒なら、書式をファイルにしておく
cat > ~/curl-format.txt <<'EOF'
dns:%{time_namelookup} connect:%{time_connect} tls:%{time_appconnect} ttfb:%{time_starttransfer} total:%{time_total}\n
EOF
curl -ko /dev/null -s -w "@$HOME/curl-format.txt" "https://${ALB}/slow?sec=3"
```

- □ **tcpdump の基本フィルタ**

**EC2 の中で打ちます**（`aws ssm start-session --target "$(terraform output -raw web_instance_id)"`）。手元の WSL2 で打っても、WSL2 自身の通信しか見えません。

```bash
# ホストとポートを絞る（-nn で名前解決を止め、-c で件数を区切る）
sudo tcpdump -i any -nn host <相手のIP> and port 80 -c 20

# 3ウェイハンドシェイクを観測する（SYN を含むパケットだけ）
sudo tcpdump -i any -nn 'tcp[tcpflags] & (tcp-syn) != 0' -c 10

# あとで読み返せるようファイルに保存する
sudo tcpdump -i any -nn port 80 -w /tmp/cap.pcap -c 200
tcpdump -nn -r /tmp/cap.pcap | head -40
```

パケットを流す側は**別のターミナル（手元）**から打ちます。**`curl` 1回では SYN が捕まりません。** ALB はターゲットへの接続を使い回すので、既存の接続に乗ると3ウェイハンドシェイクが起きないためです。

```bash
ALB=$(terraform output -raw alb_dns_name)
for i in $(seq 1 30); do curl -s -o /dev/null "http://${ALB}/?i=$i"; done
```

**SYN だけが並んで SYN/ACK が返っていなければ、パケットが届いていないか、届いても破棄されています**（経路か SG か NACL）。`Connection refused` が返る場合は、届いてはいるが待ち受けているプロセスがいない、という切り分けになります。

**本番で実行する場合は事前に承認を取ってください。** キャプチャには通信内容が含まれます。

- □ **Athena：特定 ENI の REJECT を時系列で抽出する**

ENI は `gen_reject.sh` が表示します（`terraform output -raw web_eni_id` でも取れます）。

```sql
SELECT from_unixtime(start) AS t,
       srcaddr, srcport, dstaddr, dstport, protocol, action
FROM netsec_study.vpc_flow_logs
WHERE dt = '2026/12/11'
  AND interface_id = '【gen_reject.sh が表示した ENI】'
  AND action = 'REJECT'
ORDER BY start DESC
LIMIT 200;
```

時間帯でさらに絞るなら、`AND start BETWEEN to_unixtime(TIMESTAMP '2026-12-11 09:00:00') AND to_unixtime(TIMESTAMP '2026-12-11 10:00:00')` を足します。`start` は UNIX 時刻の `bigint` で、**UTC** である点に注意してください（JST とは9時間ずれます）。

**REJECT が出ていればセキュリティグループか NACL で落ちています。** 逆に Flow Logs に**何も記録がなければ、パケットがその ENI に届いていません**（経路の問題）。同一ホスト内の通信や、Amazon DNS 宛てなど一部は記録されない点に注意してください。

- □ **Athena：5xx 発生時刻の前後で p99 を集計する**

```sql
SELECT date_trunc('minute', from_iso8601_timestamp(time)) AS minute,
       count(*) AS requests,
       sum(CASE WHEN elb_status_code >= 500 THEN 1 ELSE 0 END) AS errors,
       approx_percentile(target_processing_time, 0.99) AS p99,
       approx_percentile(target_processing_time, 0.50) AS p50
FROM netsec_study.alb_logs
WHERE dt = '2026/12/11'
  AND target_processing_time >= 0
GROUP BY 1
ORDER BY 1;
```

**`target_processing_time >= 0` を入れているのは、応答が返らなかった行の `-1` が百分位を引き下げるためです。** エラー件数は `errors` の列で別に数えています。

**p50 は変わらないのに p99 だけ跳ねている**なら、一部のリクエストだけが詰まっています。全体が上がっていれば、依存先か容量の問題です。

この2本のクエリは、**本文ごと記録しておいてください。** 1/14 の引き継ぎでそのまま使えます。Athena はスキャンしたデータ量で課金されるので、`dt` は必ず指定してください。

---

## □ 12/13（日）IAM ＋ シークレット・鍵管理

- □ **AssumeRole を実行して中身を見る**

```bash
cd ~/netsec-study-tf
aws sts assume-role \
  --role-arn "$(terraform output -raw assume_role_arn)" \
  --role-session-name study-$(date +%H%M%S)
```

返ってくる `Credentials` の中身を確認します。

| 項目 | 意味 |
|---|---|
| `AccessKeyId` / `SecretAccessKey` | 一時的なキー |
| **`SessionToken`** | **これが一時認証情報の証**。IAMユーザのキーには無い |
| **`Expiration`** | 有効期限。既定1時間、`--duration-seconds` で変更（最大は信頼ポリシー側の上限まで） |

```bash
# 取得した認証情報で実際に切り替えて確認する
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
aws sts get-caller-identity      # Arn が assumed-role/... に変わる
```

- □ **未使用のアクセスキーを数える**

```bash
aws iam generate-credential-report
sleep 10
aws iam get-credential-report --query Content --output text | base64 -d > /tmp/cred.csv

# 有効だが一度も使われていないキーを数える
awk -F, 'NR>1 && $9=="true" && $11=="N/A" {print $1}' /tmp/cred.csv
```

9列目が `access_key_1_active`、11列目が `access_key_1_last_used_date` です。2本目のキーは 14・16列目にあります。

- □ **ECS タスク定義でシークレットを参照する**

```bash
# 現状の設定を確認する
aws ecs describe-task-definition \
  --task-definition "$(terraform output -raw ecs_task_definition)" \
  --query 'taskDefinition.containerDefinitions[].{name:name,secrets:secrets,env:environment}'
```

この環境の見本では `DB_CREDENTIALS`（Secrets Manager）と `API_KEY`（SSM パラメータ）を `secrets` で、`STAGE` を `environment` で渡しています。

**自分で書く**のがこの日の合格基準です。`containerDefinitions` に次を加えます。

```json
"secrets": [
  { "name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:prod/db-AbCdEf" },
  { "name": "API_KEY",     "valueFrom": "arn:aws:ssm:ap-northeast-1:123456789012:parameter/prod/api-key" }
]
```

`environment` ではなく `secrets` に書くのが要点です。**値がタスク定義に残らず、起動時に取得されます。** 実行ロールではなく**タスク実行ロール**に `secretsmanager:GetSecretValue`（SecureString なら `kms:Decrypt` も）が要ります。

---

## □ 12/14（月）4. TLS / PKI

- □ **プロトコルと暗号スイートを読む**

```bash
cd ~/netsec-study-tf
ALB=$(terraform output -raw alb_dns_name)

openssl s_client -connect ${ALB}:443 -servername app.study.internal </dev/null 2>/dev/null | \
  grep -E 'Protocol|Cipher|Verify return code'
```

`</dev/null` を付けないと入力待ちで止まります。**`Verify return code: 0 (ok)` 以外なら検証に失敗しています。** この環境の証明書は自己署名なので 18 や 19 が返りますが、**異常ではありません。**検証エラーの読み方を覚える題材になります。

- □ **証明書チェーンを追う**

```bash
openssl s_client -connect ${ALB}:443 -servername app.study.internal -showcerts </dev/null 2>/dev/null | \
  grep -E '^ *[si]:'
```

`s:`（subject）と `i:`（issuer）が交互に並びます。**0番の issuer が1番の subject になっていれば繋がっています。** サーバ証明書しか出てこない（中間CAを送っていない）場合、ブラウザは補完できても `curl` や Java クライアントは失敗します。

自己署名なので `s:` と `i:` が同じ値の1組だけ出ます。**中間CAが無い状態がどう見えるか**の見本になります。

```bash
# 有効期限だけ見る
openssl s_client -connect ${ALB}:443 -servername app.study.internal </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates
```

- □ **SNI の有無で証明書が変わることを確認する**

```bash
# SNI あり → app の証明書が返る
openssl s_client -connect ${ALB}:443 -servername app.study.internal </dev/null 2>/dev/null | \
  openssl x509 -noout -subject

# SNI なし → default の証明書が返る
openssl s_client -connect ${ALB}:443 -noservername </dev/null 2>/dev/null | \
  openssl x509 -noout -subject
```

`CN=app.study.internal` と `CN=default.study.internal` で切り替わります。

- □ **バージョンを指定して接続可否を試す**

```bash
openssl s_client -connect ${ALB}:443 -servername app.study.internal -tls1_2 </dev/null 2>&1 | grep -E 'Protocol|alert|failure'
openssl s_client -connect ${ALB}:443 -servername app.study.internal -tls1_3 </dev/null 2>&1 | grep -E 'Protocol|alert|failure'
```

**バージョン不一致なら `protocol version` を含むアラート、暗号スイート不一致なら `handshake failure`** が返ります。ここがエラーの読み分けです。

リスナーは TLS 1.2 以上のみ許可にしてあるので、`-tls1_1` は拒否されます。ただし**手元の OpenSSL 3.x が TLS 1.0/1.1 を既定で無効にしている場合、サーバに届く前にクライアント側で失敗します。** その場合は次のポリシー確認に切り替えてください。

- □ **ALB のセキュリティポリシーを確認する**

```bash
aws elbv2 describe-listeners --load-balancer-arn "$(terraform output -raw alb_arn)" \
  --query 'Listeners[?Protocol==`HTTPS`].[Port,SslPolicy]' --output table

# そのポリシーが許容している TLS バージョン（ポリシー名は上の出力、または構築手順 §1）
aws elbv2 describe-ssl-policies --names ELBSecurityPolicy-TLS13-1-2-2021-06 \
  --query 'SslPolicies[].[Name,SslProtocols]' --output table
```

- □ **クライアントの TLS バージョン分布（Athena）**

対象は **12/11 に流したログ**です。`gen_alb_logs.sh` が TLS 1.2 と 1.3 のアクセスを30件ずつ作っています。**12/11 に `gen_alb_logs.sh` を流さなかった場合は `dt = '2026/12/08'` に読み替えてください。**

```sql
SELECT ssl_protocol, count(*) AS cnt
FROM netsec_study.alb_logs
WHERE dt = '2026/12/11'
  AND type = 'https'
GROUP BY 1
ORDER BY cnt DESC;
```

**TLS 1.0 / 1.1 のクライアントが残っていないか**を確認します。ゼロなら、セキュリティポリシーを厳しいものへ変更できます。

---

## □ 12/15（火）6. クラウドネットワーク設計

- □ **ルートテーブルを最長一致で追う**

```bash
cd ~/netsec-study-tf
aws ec2 describe-route-tables --filters Name=vpc-id,Values="$(terraform output -raw vpc_id)" \
  --query 'RouteTables[].{RT:RouteTableId,Subnets:Associations[].SubnetId,Routes:Routes[].[DestinationCidrBlock,GatewayId,NatGatewayId,TransitGatewayId,VpcPeeringConnectionId]}'
```

**宛先IPに最も長く一致するルートが選ばれます。** `0.0.0.0/0` があっても、より具体的な経路があればそちらが勝ちます。

この環境にはルートテーブルが**3つ**あります。どれがどのサブネットに付いているかは構築手順 §1 の設定値表にあります。数が合わないと悩むので、先に押さえてください。

**最長一致は `0.0.0.0/0` と VPC の local 経路の関係で読みます。** VPC 内宛ての通信は、`0.0.0.0/0` があっても local が勝ちます。

- □ **点検手順「SG → NACL → ルートテーブル → 宛先側」**

```bash
# 0. この環境の SG 一覧（ID を控える）
aws ec2 describe-security-groups --filters Name=tag:Project,Values=netsec-study \
  --query 'SecurityGroups[].[GroupName,GroupId]' --output table

# 1. セキュリティグループ（ステートフル。戻りは自動で許可される）
aws ec2 describe-security-groups --group-ids <上で控えたSG ID> \
  --query 'SecurityGroups[].[GroupName,IpPermissions,IpPermissionsEgress]'

# 2. NACL（ステートレス。戻りの許可も明示が必要）
aws ec2 describe-network-acls \
  --filters Name=association.subnet-id,Values="$(terraform output -raw nacl_demo_subnet_id)" \
  --query 'NetworkAcls[].Entries[].[RuleNumber,Protocol,RuleAction,CidrBlock,Egress,PortRange]' --output table

# 3. ルートテーブル（上記）
# 4. 宛先側のSGが、送信元SGからの通信を許可しているか
```

この環境の NACL の番号とルールは構築手順 §1 の設定値表にあります。`netsec-study-web` の SG は ALB からの80番しか許可していないので、`netsec-study-probe` から叩くと REJECT になります（12/11 の題材）。

**NACL は番号の小さい順に評価され、最初に一致したルールで確定します。** 戻りのエフェメラルポート（1024-65535）を許可し忘れているのが典型的な誤りです。

- □ **AZ 障害時のキャパシティ試算**

```bash
# AZ ごとのタスク分布 ※担当システム向け。テスト環境に ECS サービスはありません
aws ecs list-tasks --cluster <クラスタ名> --service-name <サービス名> --query 'taskArns' --output text | \
  xargs -n 100 aws ecs describe-tasks --cluster <クラスタ名> --tasks \
  --query 'tasks[].availabilityZone' --output text | sort | uniq -c
```

**片方の AZ が落ちたとき、残りの AZ で全トラフィックを捌けるか**を、現在の CPU・メモリ使用率と合わせて試算します。50%使用率で2AZなら、1AZに寄せた瞬間100%になります。

テスト環境ではタスク分布も使用率も仮置きです。**試算の式を確立するところまで**が到達点になります。EC2 の AZ 分布なら実データで確認できます。

```bash
aws ec2 describe-instances --filters Name=tag:Project,Values=netsec-study \
  Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`]|[0].Value,Placement.AvailabilityZone]' --output table
```

---

## □ 12/16（水）7. コンテナNW ＋ 9. キャパシティ・制限値

- □ **サブネットの空き IP を取得する**

```bash
cd ~/netsec-study-tf
aws ec2 describe-subnets --filters Name=vpc-id,Values="$(terraform output -raw vpc_id)" \
  --query 'Subnets[].[SubnetId,AvailabilityZone,CidrBlock,AvailableIpAddressCount]' --output table
```

**AWS は各サブネットで5つのIPを予約している**ので、/24 なら使えるのは251個です。この環境には逆算の題材として **`/28` のサブネット**（`netsec-study-tiny-28`）を置いてあります。

- □ **必要 IP 数を逆算する**

`awsvpc` モードでは **1タスク = 1 ENI = 1 IP** です。

```
必要IP数 ＝ 想定最大タスク数
          ＋ ローリング更新中の一時増分（maximumPercent が 200% なら同数）
          ＋ 予備
```

```bash
# ローリング更新の設定を確認 ※担当システム向け。テスト環境に ECS サービスはありません
aws ecs describe-services --cluster <クラスタ名> --services <サービス名> \
  --query 'services[].deploymentConfiguration' --output table
```

テスト環境ではタスク数と `maximumPercent` を仮の値（例：最大20タスク・200%）に置いて逆算します。上で取得した `AvailableIpAddressCount` と突き合わせ、**足りなければタスクが PENDING のまま起動しません。** `/28` の11個に対して逆算すると、すぐ足りなくなることが数字で見えます。

- □ **クォータの現在値と上限を確認する**

```bash
# ECS
aws service-quotas list-service-quotas --service-code ecs \
  --query 'Quotas[].[QuotaName,Value]' --output table

# ELB（ターゲット数・ALB数）
aws service-quotas list-service-quotas --service-code elasticloadbalancing \
  --query 'Quotas[].[QuotaName,Value]' --output table

# Lambda の同時実行数
aws service-quotas list-service-quotas --service-code lambda \
  --query "Quotas[?contains(QuotaName,'Concurrent')].[QuotaName,Value]" --output table

# VPC（ENI数・SG数）
aws service-quotas list-service-quotas --service-code vpc \
  --query 'Quotas[].[QuotaName,Value]' --output table
```

```bash
# 引き上げ申請（手順の確認まででよい）
aws service-quotas request-service-quota-increase \
  --service-code ecs --quota-code <クォータコード> --desired-value <希望値>
```

**申請は即時には通りません。** 負荷試験の前に確認しておくべき項目として一覧化しておきます。

---

## □ 12/17（木）サプライチェーン・CI/CD統制

- □ **IaC スキャン**

**ツールは第0期で導入済みのはずです**（構築手順 §2-1b）。未導入ならそちらを先に実行してください。スキャン対象は、わざと危険にしてあるサンプルです。

```bash
cd ~/netsec-study-tf/sample-insecure

# gitleaks で履歴を検査するため、git リポジトリにする
git init -q && git add -A
git -c user.email=study@example.com -c user.name=study commit -qm "initial"
```

```bash
# tfsec
tfsec .
tfsec . --minimum-severity HIGH        # 重大なものだけ見る
```

```bash
# Checkov
checkov -d . --compact
checkov -d . --compact --hard-fail-on HIGH    # CI で失敗させる設定
```

`sample-insecure` には、22番の全世界開放・暗号化とバージョニングの無い S3・アクセスログの無い ALB を仕込んであります。

**CI に組み込むときの要点**は、終了コードで失敗させることです。`--soft-fail` を付けると常に 0 で返るので、**検出しても止まりません。** 重大度で線を引き、そこを超えたら落とす形にします。

- □ **シークレットのハードコード検出**

```bash
# 作業ツリーを検査
gitleaks detect --source . --redact -v

# コミット履歴も検査（こちらが本番）
gitleaks detect --source . --log-opts="--all" --redact
```

**`--redact` を付けないと、検出した秘密そのものが画面とログに出ます。** 必ず付けてください。

**一度コミットされた秘密は履歴に残ります。** 消しても意味がないので、検出したら**失効と再発行**が必要です。

- □ **state の S3 バックエンド設定（自分で書く）**

確認すべきは次の4点です。

```bash
cd ~/netsec-study-tf
BUCKET=$(terraform output -raw tfstate_bucket)
TABLE=$(terraform output -raw tflock_table)

# 1. 暗号化
aws s3api get-bucket-encryption --bucket "$BUCKET"
# 2. バージョニング（Status が Enabled であること）
aws s3api get-bucket-versioning --bucket "$BUCKET"
# 3. パブリックアクセスブロック（4項目すべて true）
aws s3api get-public-access-block --bucket "$BUCKET"
# 4. ロック（DynamoDB テーブル、または S3 のネイティブロック）
aws dynamodb describe-table --table-name "$TABLE" --query 'Table.TableStatus'
```

**4点すべてが揃った状態を作ってあります。** 1つずつ打って、どのAPIで何が確認できるかを押さえてください。

---

## □ 12/18（金）脆弱性・パッチ管理 ＋ ネットワーク境界防御

- □ **ECR の拡張スキャンを有効化する**

**この項目は任意です。** Inspector の課金が発生し、イメージの push に Docker が要ります（構築手順 §2 では導入していません）。飛ばす場合は、手順を読み下して【メモ】に書き出すまでで構いません。

```bash
docker --version                          # 入っているか先に確認
cd ~/netsec-study-tf
terraform apply -var="enable_ecr=true"    # リポジトリを作る
```

```bash
# Inspector を有効化（拡張スキャンの実体）
aws inspector2 enable --resource-types ECR

# レジストリのスキャン設定を拡張に切り替える
aws ecr put-registry-scanning-configuration --scan-type ENHANCED \
  --rules '[{"scanFrequency":"SCAN_ON_PUSH","repositoryFilters":[{"filter":"*","filterType":"WILDCARD"}]}]'

# 現在の設定を確認
aws ecr get-registry-scanning-configuration
```

**拡張スキャンは Inspector の課金対象です。** 学習で有効化した場合は、確認後に戻すかどうかを判断してください。

```bash
# 検出結果を深刻度別に数える
aws inspector2 list-findings \
  --filter-criteria '{"resourceType":[{"comparison":"EQUALS","value":"AWS_ECR_CONTAINER_IMAGE"}]}' \
  --query 'findings[].severity' --output text | tr '\t' '\n' | sort | uniq -c
```

```bash
# 基本スキャンの場合はこちら
aws ecr describe-image-scan-findings \
  --repository-name "$(terraform output -raw ecr_repository)" --image-id imageTag=old \
  --query 'imageScanFindings.findingSeverityCounts'
```

**確認が終わったら、その日のうちに戻してください。**

```bash
aws inspector2 disable --resource-types ECR
terraform apply -var="enable_ecr=false"
```

- □ **KEV カタログを見る**

```bash
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | \
  jq '.vulnerabilities | length'

# 自分のスキャン結果に出た CVE が KEV に載っているか
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | \
  jq -r '.vulnerabilities[] | select(.cveID=="CVE-2021-44228") | [.cveID,.dueDate,.shortDescription] | @tsv'
```

**KEV に載っている＝実際に悪用が確認されている**という意味です。CVSS スコアより優先度の判断に効きます。

- □ **SSM Session Manager で接続する**

```bash
# プラグインを入れる（初回のみ）
curl -o /tmp/session-manager-plugin.deb \
  "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb"
sudo dpkg -i /tmp/session-manager-plugin.deb

# 接続できるインスタンスを確認して接続する
aws ssm describe-instance-information \
  --query 'InstanceInformationList[].[InstanceId,PingStatus]' --output table

cd ~/netsec-study-tf
aws ssm start-session --target "$(terraform output -raw web_instance_id)"
```

**SSH ポートを開けずに接続でき、操作は CloudTrail に残ります。** 踏み台サーバを置く構成との比較が、この日の論点です。

---

## □ 12/20（日）監査ログ・脅威検知

- □ **誰がいつ変更・削除したかを特定する**

この環境の構築操作そのものが証跡になっています。`AttributeValue` には実際に作ったリソース名（`netsec-study-web` など）を入れます。

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=netsec-study-web \
  --start-time 2026-12-06T00:00:00Z --end-time 2026-12-20T23:59:59Z \
  --query 'Events[].[EventTime,EventName,Username]' --output table
```

```bash
# イベント名で引く（削除操作を探す）
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteSecurityGroup \
  --query 'Events[].[EventTime,Username,Resources[0].ResourceName]' --output table

# 1件の詳細を読む（送信元IP、リクエストパラメータまで入っている）
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteSecurityGroup \
  --max-results 1 --query 'Events[0].CloudTrailEvent' --output text | jq
```

**`lookup-events` で引けるのは直近90日の管理イベントだけです。** それ以前や、S3 のオブジェクト操作などのデータイベントは、S3 に配信したログを Athena で検索します。

- □ **Security Hub の未達項目を追う**

**この項目は任意です。** 有効化すると AWS Config の記録も必要になり、月に数ドルかかります。試す場合は `aws securityhub enable-security-hub --enable-default-standards` で有効化し、**当日中に `aws securityhub disable-security-hub` で戻してください。**

```bash
# 有効にしている基準
aws securityhub get-enabled-standards \
  --query 'StandardsSubscriptions[].[StandardsArn,StandardsStatus]' --output table

# 失敗している統制を深刻度別に数える
aws securityhub get-findings \
  --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}],"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' \
  --query 'Findings[].Severity.Label' --output text | tr '\t' '\n' | sort | uniq -c

# 失敗している統制の一覧
aws securityhub get-findings \
  --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}],"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' \
  --query 'Findings[].[Severity.Label,Title]' --output table | sort -u
```

**セキュリティスコアそのものはコンソールで確認します**（Security Hub のサマリ画面）。CLI では未達の統制を個別に拾う形になります。

---

## 安全上の注意

| 対象 | 注意 |
|---|---|
| `tcpdump` | 通信内容がそのまま記録されます。本番では事前に承認を取り、キャプチャファイルは確認後に削除してください |
| Athena | スキャンしたデータ量で課金されます。**`WHERE dt = 'yyyy/MM/dd'` を必ず入れてください**（`time` や `start` では絞れません） |
| ECR 拡張スキャン | Inspector の課金対象です。有効化したままにするかを判断してください |
| `assume-role` の一時認証情報 | `export` した端末に残ります。作業後は `unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN` |
| `gitleaks` | `--redact` を付けないと秘密が画面とログに残ります |
| CloudWatch アラームの作成テスト | 作ったら必ず削除してください |

---

## 記録の残し方

**書き方と記入欄は `【SRE】ネットワーク・セキュリティ 学習記録.md` にあります。** コマンドと結果をセットで、その日のうちに書いてください。

12/11 の Athena クエリ2本と 12/15 の点検手順は、**1/14 の引き継ぎメモにそのまま貼れる形**にしておいてください。

---

## 詰まったときに見る

環境の構築や仕込みで想定外の結果になったときの切り分けです。**起きやすい順**に並べてあります。

### `terraform apply` が途中で止まる

ACM への自己署名証明書のインポートか、ALB の作成で失敗することがあります。**まず同じコマンドをもう一度打ってください。** Terraform は作成済みのリソースを飛ばして途中から再開します。

同じ箇所で2回止まるなら、エラーに出ているリソース名とメッセージを控えて調べます。**部分的に作られた状態でも `terraform destroy` は効く**ので、課金が残る心配はありません。

```bash
terraform state list | head -30      # どこまで作られたかを見る
```

### apply は通ったが `curl` で 200 が返らない

EC2 の `user_data` がまだ終わっていないか、失敗しています。**2〜3分待って再確認**し、それでもダメなら中を見ます。

```bash
aws ssm start-session --target "$(terraform output -raw web_instance_id)"
```

```bash
sudo tail -30 /var/log/cloud-init-output.log
sudo systemctl status netsec-app
```

`dnf install` が失敗していると、`set -eux` で以降が実行されずアプリが起動しません。**その場合は手で起動すれば復旧します。**

```bash
sudo systemctl start netsec-app
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/health    # 200 ならOK
```

`curl -I`（HEAD）は使わないでください。アプリは `do_GET` しか実装していないので **501 を返します。環境の異常ではありません。**

### `scripts/*.sh` が落ちる

| 症状 | 原因 | 対処 |
|---|---|---|
| `jq: command not found` | ツールの導入漏れ | 構築手順 §2-1 をやり直す |
| `InvalidInstanceId` | SSM への登録がまだ | 下のコマンドで `Online` を待つ（起動直後は2〜3分） |
| `status: Failed` が出る | SSM のコマンド実行に失敗 | 出力の `!` 行（標準エラー）を読む |

```bash
aws ssm describe-instance-information \
  --query 'InstanceInformationList[].[InstanceId,PingStatus]' --output table
```

`gen_alb_logs.sh` は **`=== 4/5` の行で `503` が15個並ぶこと**を目で確認してください。`200` が並んでいたらアプリが止まっておらず、**12/9 の演習が空振りします。**

### Athena のクエリが0件

切り分けはこの順です。

1. **ワークグループが `netsec-study` になっているか**（コンソール右上）。`primary` のままだと結果の出力先が未設定でエラーになります
2. **`dt` が実際に流した日と合っているか**。ログがあるのは 12/06・12/08・12/11 の3日だけです。**`dt` は UTC 日付なので、JST 09:00 より前に流した場合は前日の `dt` に入ります。**まず前日を試してください
3. **S3 にオブジェクトが届いているか**。ALB は5分間隔、Flow Logs は最大10分かかります

```bash
aws s3 ls "s3://$(terraform output -raw log_bucket)/alb/AWSLogs/" --recursive | tail -5
aws s3 ls "s3://$(terraform output -raw log_bucket)/flowlogs/AWSLogs/" --recursive | tail -5
```

S3 にあるのに0件なら、**パーティションの指定か LOCATION の不一致**です。オブジェクトのパス末尾の `年/月/日` と `dt` の値を突き合わせてください。このパスは UTC なので、`2026/12/10/` に入っていれば `dt = '2026/12/10'` です。

### クエリは通るが `elb_status_code` が NULL

**ALB テーブルの正規表現と実ログの列数が合っていません。** 1行そのまま見て、どこからずれているかを確認します。

```sql
SELECT * FROM netsec_study.alb_logs WHERE dt = '2026/12/06' LIMIT 1;
```

`client_ip_port` が `10.30.0.5:52840` のように **IP:ポートの形**なら正常です。IP だけだったり、`target_ip_port` にポート番号だけが入っていたら、**グループ数が足りていません**（ALB のログ形式にフィールドが増えた場合に起きます）。

実ログ1行のフィールド数を数え、§5 の正規表現の末尾にグループを足して `CREATE EXTERNAL TABLE` を作り直します。**テーブルの作り直しは `DROP TABLE netsec_study.alb_logs;` のあと DDL を再実行するだけ**で、S3 のログは消えません。

### `terraform destroy` が止まる

S3 バケットは `force_destroy = true` にしてあるので通常は通ります。止まったら構築手順 §9 のチェックリストを上から確認し、残ったものをコンソールで消してください。

**消し忘れで課金が続くのは3つです。**

```bash
aws ec2 describe-nat-gateways --filter Name=state,Values=available --query 'NatGateways[].NatGatewayId'
aws rds describe-db-instances --query 'DBInstances[].DBInstanceIdentifier'
aws ec2 describe-addresses --query 'Addresses[].[PublicIp,AssociationId]' --output table
```

Inspector と Security Hub を有効にした場合も、`terraform destroy` の対象外です。§9 のチェックリストで確認してください。

### 調べても分からないとき

**その日の演習を飛ばして先に進んでください。** 12/20 に「環境が要る未消化項目」を消化する枠があります（構築手順 §1 の再現項目表を上から見る日）。原因と、どこまで切り分けたかを【メモ】に残しておけば、そこで再開できます。

