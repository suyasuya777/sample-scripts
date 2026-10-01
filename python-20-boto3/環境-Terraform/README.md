# boto3 学習用テスト環境（Terraform）

`boto3学習スケジュール_2027年1-2月_実行版.md` の環境タイムラインに対応した Terraform 一式です。

## 構成

```
boto3-study-tf/
├── versions.tf                  provider・データソース・locals
├── variables.tf                 変数とセット有効化フラグ
├── terraform.tfvars.example     → terraform.tfvars にリネームして使う
├── set_a.tf                     VPC / ALB / ECS / EC2 / ASG / ログS3
├── set_b.tf                     S3(1200件) / IAM / SSM / Secrets
├── set_c.tf                     CloudWatch Logs
├── set_d.tf                     Lambda / SQS / SNS / SES
├── set_e.tf                     RDS（E-1）/ Aurora・EKS（E-2）
├── outputs.tf                   ALBのDNS名、各リソースID等
└── scripts/
    ├── make_orphan_snapshot.sh  孤立スナップショットの作成（1/26）
    └── cleanup_leftovers.sh     destroy で消えないものの掃除（2/28）
```

**ディレクトリは1つ、state も1つ**です。セットの切り替えは `terraform.tfvars` の
フラグで行います。ディレクトリを分けて state を跨ぐより、セットAのVPCを
そのまま参照できるぶん扱いが楽です。

## 前提

- Terraform >= 1.6
- AWS CLI v2（`local-exec` で S3 投入・ログ投入・DLQ投入に使う）
- 管理者相当の権限を持つプロファイル

## 初回

```bash
cp terraform.tfvars.example terraform.tfvars
vi terraform.tfvars          # notification_email を必ず埋める

export AWS_DEFAULT_REGION=ap-northeast-1

terraform init
terraform plan               # 必ず読む
terraform apply              # セットAが作られる（約10分）
```

apply 後の確認:

```bash
curl -I "http://$(terraform output -raw alb_dns_name)"    # 200 が返ること
```

## 環境タイムラインとフラグ

| 日付 | 操作 | コマンド |
|---|---|---|
| **1/18(月)** | セットA構築 | `terraform apply` |
| **1/19(火)** | セットB構築 | `enable_set_b = true` → `terraform apply` |
| 1/26(火) | 孤立スナップショット作成 | `bash scripts/make_orphan_snapshot.sh` |
| **2/7(日)** | セットC構築 | `enable_set_c = true` → `terraform apply` |
| **2/14(日)** | セットD構築 | `enable_set_d = true` → `terraform apply` |
| **2/21(日)** | セットE-1構築 | `enable_set_e1 = true` → `terraform apply` |
| **2/23(火)午前** | セットE-2構築 | `enable_set_e2 = true` → `terraform apply`（約20分） |
| **2/23(火)夜** | **セットE-2削除** | `enable_set_e2 = false` → `terraform apply`（約15分） |
| **2/28(日)** | 全削除 | `bash scripts/cleanup_leftovers.sh` → `terraform destroy` |

**2/23 の戻し忘れが一番高くつきます**（Aurora $4.8/日 + EKS $2.4/日）。
`terraform apply` の完了を確認するまでがその日の作業です。

## 手動作業が残るもの

Terraform だけでは完結しません。該当日に手で行ってください。

| 時期 | 作業 | 理由 |
|---|---|---|
| 1/18 | 予算アラートの作成（$70） | 構築手順書 §2-1 |
| 2/7 | **Organizations で2つ目のアカウントを作成** | 組織作成は Terraform で扱うと事故が大きい。CLI 推奨 |
| 2/7 | Cost Explorer の有効化 | データ反映に最大24時間 |
| 2/14 | **SNS 購読確認メールのリンクを踏む** | `protocol = "email"` は確認が手動 |
| 2/14 | **SES 検証メールのリンクを踏む** | 検証しないと送信できない |
| 2/14 | Athena テーブル作成 | 構築手順書 §5 の DDL。`terraform output athena_alb_log_location` の値を LOCATION に入れる |

## 意図的に「悪い状態」にしてあるもの

検出系スクリプトを実行しても何もヒットしないと、正しく動いているか判断できません。
そのため次を仕込んであります。

| リソース | 検出するスクリプト |
|---|---|
| `boto3-study-intentionally-open` SG（22/3389 が 0.0.0.0/0） | `ec2_security_groups.py` |
| 未割り当て EIP | `ec2_unused_eip.py` |
| 孤立スナップショット（スクリプトで作成） | `ec2_snapshots.py` |
| `boto3-study-user2` に `AdministratorAccess` | `iam_admin_policy_entities.py` |
| `boto3-study-user1` にインラインポリシー | `iam_inline_policies.py` |
| user1 のキーは使用済み / user2 は未使用 | `iam_access_key_last_used.py` |
| バケットBのパブリックアクセスブロックが2項目だけ | `s3_public_access_block.py` |
| 保持期間未設定のロググループ2つ | `logs_list_log_groups.py` |
| DLQ に滞留メッセージ3件 | `sqs_dlq_reprocess.py` |
| プライベートサブネット（IGW向きルートなし） | `vpc_describe_network.py` |

**`intentionally-open` SG はどのリソースにもアタッチしないでください。**

## boto3 で状態を変える箇所の扱い

学習中に boto3 や CLI で変更するリソースには `lifecycle { ignore_changes }` を
入れてあります。次に `terraform apply` しても元に戻されません。

| リソース | 無視する属性 | 変更する日 |
|---|---|---|
| `aws_ecs_service.this` | `desired_count`, `task_definition` | 1/27, 1/29 |
| `aws_autoscaling_group.this` | `desired_capacity` | 1/31 |
| `aws_security_group.task` | `ingress` | 1/31（unhealthy 再現） |
| `aws_instance.this` | `instance_type`, `ami` | 1/22, 1/26 |
| `aws_iam_user_policy_attachment.u2_admin` | すべて | 2/5（detach） |
| `aws_cloudwatch_log_group.no_retention*` | `retention_in_days` | 2/11（一括設定） |
| `aws_lambda_function.fn` | `environment`, `timeout`, `memory_size` | 2/16 |
| `aws_secretsmanager_secret_version.db` | `secret_string` | 2/7 |

**1/26 でインスタンスタイプを t3.small にしたまま戻し忘れると、`ignore_changes` の
せいで Terraform も直してくれません。** その日のうちに手で戻してください。

## 注意点

**state に機密が入ります。** IAM アクセスキーのシークレット、RDS のパスワードが
平文で `terraform.tfstate` に保存されます。学習用アカウント限定の構成です。
リポジトリに push しないでください（`.gitignore` に `*.tfstate*` と
`terraform.tfvars` を入れること）。

**NAT Gateway は作っていません。** Fargate タスクは公開サブネットに
`assign_public_ip = true` で置いてイメージを取得します。$1.4/日 + データ処理料金の
節約のためで、学習内容には影響しません。

**`force_destroy = true` を S3 バケットに入れてあります。** destroy 時に
オブジェクトごと消えます。逆に言うと、ALBアクセスログも一緒に消えるので
**2/14 の Athena 演習が終わるまで destroy しないでください。**

**Aurora の `engine_version` は指定していません。** 既定で Serverless v2 対応版が
選ばれますが、固定したい場合は `aws rds describe-db-engine-versions
--engine aurora-postgresql --query 'DBEngineVersions[].EngineVersion'` で
確認してから指定してください。

**ALB アクセスログのバケットポリシーは `data.aws_elb_service_account` を使っています。**
ap-northeast-1 のようにサービスプリンシパル方式に対応していないリージョンでも
動くようにするためです。

**このコードは実環境で apply して検証していません。** 必ず `terraform plan` を
読んでから apply してください。特に Aurora の engine_version、EKS の
バージョン既定値、SESv2 のリソース定義はプロバイダのバージョンで挙動が変わります。

## 概算コスト

| 項目 | 期間 | 概算 |
|---|---|---|
| セットA（ALB + Fargate×2 + EC2 + EIP ≒ $1.32/日） | 1/18〜2/28（42日） | 約 $55 |
| セットB・C・D | 全期間 | 約 $2 |
| セットE-1（RDS） | 2/21〜2/28 | 約 $4 |
| セットE-2（Aurora + EKS） | 2/23 の数時間 | 約 $2 |
| **合計** | | **約 $60〜70** |

予算アラートは $70 で設定してください。超えたときに疑うのは次の3つです。

1. セットE-2 の戻し忘れ（$7.2/日）
2. 1/26 のインスタンスタイプ戻し忘れ（$0.66/日）
3. どこかで NAT Gateway を作った（$1.4/日 + データ処理料金）
