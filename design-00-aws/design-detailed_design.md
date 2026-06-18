# インフラ詳細設計書

**Infrastructure Detailed Design Document**

| 項目 | 内容 |
|------|------|
| プロジェクト名 | 【プロジェクト名を入力】 |
| システム名 | 【システム名を入力】 |
| バージョン | 1.0 |
| 作成日 | YYYY/MM/DD |
| 最終更新日 | YYYY/MM/DD |
| 作成者 | 【氏名】 |
| 承認者 | 【氏名】 |
| ステータス | ドラフト / レビュー中 / 承認済 |
| 関連文書 | インフラ基本設計書 v1.0 |

> 本書は社外秘です。無断複製・配布を禁じます。
> 本書は「インフラ基本設計書」の各章に対応し、実装に必要なパラメータ・設定値レベルまで記述するものです。

---

## 目次

- [1. 目的・スコープ（詳細）](#1-目的スコープ詳細)
  - [1.1 ドキュメントの目的・位置付け](#11-ドキュメントの目的位置付け)
  - [1.2 環境構成一覧](#12-環境構成一覧)
  - [1.3 命名規則](#13-命名規則)
  - [1.4 タグ付け規則](#14-タグ付け規則)
  - [1.5 Terraformディレクトリ構成](#15-terraformディレクトリ構成)
  - [1.6 Terraform Backend設定](#16-terraform-backend設定)
- [2. システム概要（詳細）](#2-システム概要詳細)
  - [2.1 アーキテクチャ構成図](#21-アーキテクチャ構成図)
  - [2.2 非機能要件（数値詳細）](#22-非機能要件数値詳細)
  - [2.3 環境別スペック差分サマリ](#23-環境別スペック差分サマリ)
- [3. ネットワーク設計（詳細）](#3-ネットワーク設計詳細)
  - [3.1 VPC詳細設定](#31-vpc詳細設定)
  - [3.2 サブネット詳細設定](#32-サブネット詳細設定)
  - [3.3 ルートテーブル詳細](#33-ルートテーブル詳細)
  - [3.4 Internet Gateway / NAT Gateway](#34-internet-gateway--nat-gateway)
  - [3.5 VPC Endpoint詳細設定](#35-vpc-endpoint詳細設定)
  - [3.6 セキュリティグループ詳細](#36-セキュリティグループ詳細)
- [4. コンピューティング設計（詳細）](#4-コンピューティング設計詳細)
  - [4.1 ECSクラスター設定](#41-ecsクラスター設定)
  - [4.2 タスク定義詳細](#42-タスク定義詳細)
  - [4.3 ECSサービス設定](#43-ecsサービス設定)
  - [4.4 Auto Scaling詳細設定](#44-auto-scaling詳細設定)
  - [4.5 タスクロール・実行ロール詳細](#45-タスクロール実行ロール詳細)
  - [4.6 Lambda設定（使用する場合）](#46-lambda設定使用する場合)
- [5. データ層設計（詳細）](#5-データ層設計詳細)
  - [5.1 RDS / Auroraクラスター詳細](#51-rds--auroraクラスター詳細)
  - [5.2 RDSパラメータグループ詳細値](#52-rdsパラメータグループ詳細値)
  - [5.3 バックアップ・メンテナンス設定](#53-バックアップメンテナンス設定)
  - [5.4 認証情報管理（Secrets Manager）](#54-認証情報管理secrets-manager)
  - [5.5 S3バケット詳細](#55-s3バケット詳細)
  - [5.6 ElastiCache詳細設定（使用する場合）](#56-elasticache詳細設定使用する場合)
- [6. セキュリティ設計（詳細）](#6-セキュリティ設計詳細)
  - [6.1 IAMロール一覧](#61-iamロール一覧)
  - [6.2 IAMポリシー詳細例](#62-iamポリシー詳細例)
  - [6.3 KMSキー設計](#63-kmsキー設計)
  - [6.4 ACM証明書設定](#64-acm証明書設定)
  - [6.5 WAF詳細設定](#65-waf詳細設定)
  - [6.6 セキュリティサービス詳細設定](#66-セキュリティサービス詳細設定)
- [7. 可観測性設計（詳細）](#7-可観測性設計詳細)
  - [7.1 CloudWatch Logグループ詳細](#71-cloudwatch-logグループ詳細)
  - [7.2 ログフォーマット規約](#72-ログフォーマット規約)
  - [7.3 メトリクスフィルター](#73-メトリクスフィルター)
  - [7.4 CloudWatch Alarm詳細一覧](#74-cloudwatch-alarm詳細一覧)
  - [7.5 SNS / Slack連携設定](#75-sns--slack連携設定)
  - [7.6 SLI/SLO詳細定義](#76-slislo詳細定義)
  - [7.7 ダッシュボード構成](#77-ダッシュボード構成)
- [8. CI/CD設計（詳細）](#8-cicd設計詳細)
  - [8.1 リポジトリ・ブランチ戦略](#81-リポジトリブランチ戦略)
  - [8.2 ECRリポジトリ詳細](#82-ecrリポジトリ詳細)
  - [8.3 CodeBuild詳細設定](#83-codebuild詳細設定)
  - [8.4 CodePipeline詳細設定](#84-codepipeline詳細設定)
  - [8.5 CodeDeploy（Blue/Green）詳細設定](#85-codeploybluegreen詳細設定)
- [9. バックアップ・DR設計（詳細）](#9-バックアップdr設計詳細)
  - [9.1 バックアップ詳細スケジュール](#91-バックアップ詳細スケジュール)
  - [9.2 DR詳細方針](#92-dr詳細方針)
  - [9.3 障害時エスカレーションフロー](#93-障害時エスカレーションフロー)
- [10. コスト設計（詳細）](#10-コスト設計詳細)
  - [10.1 環境別月次コスト見積もり詳細](#101-環境別月次コスト見積もり詳細)
  - [10.2 コスト最適化施策詳細](#102-コスト最適化施策詳細)
- [11. 課題・TODO](#11-課題todo)
- [12. 用語集](#12-用語集)

---

## 改訂履歴

| バージョン | 日付 | 変更者 | 変更内容 |
|-----------|------|--------|---------|
| 1.0 | YYYY/MM/DD | 【氏名】 | 初版作成 |
| | | | |

---

## 1. 目的・スコープ（詳細）

### 1.1 ドキュメントの目的・位置付け

| 項目 | 内容 |
|------|------|
| 目的 | 基本設計書で定義した方針を、実装可能なレベルのパラメータ・設定値として明確化する |
| 対象読者 | インフラ構築担当者、Terraform実装者、レビュアー、運用担当者 |
| 基本設計書との関係 | 基本設計書＝方針・選定理由 / 詳細設計書＝具体的な値・構成 |
| 適用範囲 | 第3章〜第10章で定義する全AWSリソース |

### 1.2 環境構成一覧

| 環境名 | AWSアカウントID | 用途 | アクセス制御 |
|--------|----------------|------|-------------|
| dev | 【111111111111】 | 開発・単体動作確認 | 開発者全員 |
| stg | 【222222222222】 | 結合テスト・リリース前検証 | 開発リーダー以上 |
| prod | 【333333333333】 | 本番運用 | インフラ担当者のみ（Assume Role） |

### 1.3 命名規則

| リソース種別 | 命名パターン | 例 |
|-------------|------------|-----|
| VPC | `{env}-{system}-vpc` | `prod-myapp-vpc` |
| サブネット | `{env}-{system}-{tier}-{az}` | `prod-myapp-private-1a` |
| セキュリティグループ | `{env}-{system}-{role}-sg` | `prod-myapp-ecs-sg` |
| ECSクラスター | `{env}-{system}-cluster` | `prod-myapp-cluster` |
| ECSサービス | `{env}-{system}-{component}-svc` | `prod-myapp-api-svc` |
| IAMロール | `{env}-{system}-{role}-role` | `prod-myapp-ecs-task-role` |
| S3バケット | `{env}-{system}-{purpose}` | `prod-myapp-assets` |
| RDSクラスター | `{env}-{system}-db-cluster` | `prod-myapp-db-cluster` |
| CloudWatch Logグループ | `/ecs/{env}-{system}-{component}` | `/ecs/prod-myapp-api` |
| Terraformリソース名 | スネークケース（AWS名と同一） | `aws_ecs_cluster.main` |

### 1.4 タグ付け規則

全リソースに以下の共通タグを必須付与する。

| タグキー | 値の例 | 説明 |
|---------|--------|------|
| `Project` | `myapp` | プロジェクト識別子 |
| `Environment` | `dev` / `stg` / `prod` | 環境識別子 |
| `ManagedBy` | `terraform` | 管理ツール |
| `Owner` | `infra-team` | 管理責任チーム |
| `CostCenter` | 【コストセンターコード】 | コスト按分用 |

### 1.5 Terraformディレクトリ構成

```
infra/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── stg/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── ecs/
│   ├── alb/
│   ├── rds/
│   ├── waf/
│   ├── iam/
│   └── monitoring/
└── shared/
    └── ecr/
```

### 1.6 Terraform Backend設定

| 項目 | 値 |
|------|-----|
| Backend種別 | S3 |
| State用バケット | `{env}-myapp-terraform-state` |
| Stateファイルパス | `infra/{env}/terraform.tfstate` |
| ロック方式 | DynamoDB |
| ロックテーブル名 | `{env}-myapp-terraform-lock` |
| バージョニング | 有効 |
| 暗号化 | SSE-S3 |

---

## 2. システム概要（詳細）

### 2.1 アーキテクチャ構成図

【ここにアーキテクチャ図（draw.io / Lucidchart等で作成したもの）を挿入】

主要コンポーネント間の通信は以下の通り。

| No. | 送信元 | 宛先 | プロトコル/ポート | 用途 |
|-----|-------|------|------------------|------|
| 1 | Internet | ALB | HTTPS/443 | エンドユーザーアクセス |
| 2 | ALB | ECS Task | HTTP/8080 | アプリケーション転送 |
| 3 | ECS Task | RDS | TCP/5432 | DB接続 |
| 4 | ECS Task | ElastiCache | TCP/6379 | セッション/キャッシュ |
| 5 | ECS Task | S3 | HTTPS/443（VPC Endpoint経由） | ファイル入出力 |
| 6 | ECS Task | Secrets Manager | HTTPS/443（VPC Endpoint経由） | シークレット取得 |
| 7 | ECS Task | CloudWatch Logs | HTTPS/443（VPC Endpoint経由） | ログ送信 |

### 2.2 非機能要件（数値詳細）

| 項目 | 目標値 | 測定方法 | 測定period |
|------|--------|---------|-----------|
| 可用性 | 99.9% | ALB合計リクエスト数 vs 5xx応答数（CloudWatchメトリクス） | 月次 |
| RPO | 1時間以内 | RDS自動バックアップ間隔 | - |
| RTO | 4時間以内 | DR訓練での復旧所要時間実測 | 半期 |
| 同時接続数 | 【】コネクション | ALB ActiveConnectionCount | ピーク時 |
| レスポンスタイム（p50） | 200ms以内 | ALB TargetResponseTime | 常時 |
| レスポンスタイム（p95） | 500ms以内 | ALB TargetResponseTime | 常時 |
| レスポンスタイム（p99） | 1000ms以内 | ALB TargetResponseTime | 常時 |
| データ保持期間 | 【】年 | S3ライフサイクルポリシー | - |

### 2.3 環境別スペック差分サマリ

| 項目 | dev | stg | prod |
|------|-----|-----|------|
| ECS Desired Count | 1 | 1 | 2 |
| ECS Task CPU/Memory | 256/512 | 512/1024 | 512/1024 |
| RDSインスタンスタイプ | db.t4g.medium | db.t4g.medium | db.r6g.large |
| RDS Multi-AZ | 無効 | 無効 | 有効 |
| NAT Gateway数 | 1 | 1 | 3（AZ冗長） |
| WAF | 簡易ルールのみ | フルルール | フルルール |
| バックアップ保持 | 1日 | 3日 | 7日 |
| 削除保護 | 無効 | 無効 | 有効 |

---

## 3. ネットワーク設計（詳細）

### 3.1 VPC詳細設定

| パラメータ | 値 |
|-----------|-----|
| VPC名 | `{env}-myapp-vpc` |
| CIDRブロック | `10.0.0.0/16`（dev: `10.1.0.0/16`, stg: `10.2.0.0/16`, prod: `10.0.0.0/16`） |
| インスタンステナンシー | default |
| DNS解決 | 有効（enableDnsSupport = true） |
| DNSホスト名 | 有効（enableDnsHostnames = true） |
| リージョン | ap-northeast-1 |
| 利用AZ | ap-northeast-1a, ap-northeast-1c, ap-northeast-1d |

### 3.2 サブネット詳細設定

| サブネット名 | AZ | CIDR | 利用可能IP数 | ルートテーブル | NACL |
|-------------|-----|------|------------|---------------|------|
| `{env}-myapp-public-1a` | ap-northeast-1a | 10.0.1.0/24 | 251 | `{env}-myapp-public-rt` | default |
| `{env}-myapp-public-1c` | ap-northeast-1c | 10.0.2.0/24 | 251 | `{env}-myapp-public-rt` | default |
| `{env}-myapp-public-1d` | ap-northeast-1d | 10.0.3.0/24 | 251 | `{env}-myapp-public-rt` | default |
| `{env}-myapp-private-1a` | ap-northeast-1a | 10.0.11.0/24 | 251 | `{env}-myapp-private-rt-1a` | default |
| `{env}-myapp-private-1c` | ap-northeast-1c | 10.0.12.0/24 | 251 | `{env}-myapp-private-rt-1c` | default |
| `{env}-myapp-private-1d` | ap-northeast-1d | 10.0.13.0/24 | 251 | `{env}-myapp-private-rt-1d` | default |
| `{env}-myapp-db-1a` | ap-northeast-1a | 10.0.21.0/24 | 251 | `{env}-myapp-db-rt` | default |
| `{env}-myapp-db-1c` | ap-northeast-1c | 10.0.22.0/24 | 251 | `{env}-myapp-db-rt` | default |
| `{env}-myapp-db-1d` | ap-northeast-1d | 10.0.23.0/24 | 251 | `{env}-myapp-db-rt` | default |

> dev/stg環境はAZ数を2（1a, 1c）に削減し、CIDRも `/25` 程度に縮小可（コスト削減）。

### 3.3 ルートテーブル詳細

| ルートテーブル名 | 関連サブネット | 宛先 | ターゲット |
|-----------------|---------------|------|-----------|
| `{env}-myapp-public-rt` | public-1a/1c/1d | 0.0.0.0/0 | Internet Gateway |
| `{env}-myapp-public-rt` | public-1a/1c/1d | 10.0.0.0/16 | local |
| `{env}-myapp-private-rt-1a` | private-1a | 0.0.0.0/0 | NAT Gateway (1a) |
| `{env}-myapp-private-rt-1c` | private-1c | 0.0.0.0/0 | NAT Gateway (1c) |
| `{env}-myapp-private-rt-1d` | private-1d | 0.0.0.0/0 | NAT Gateway (1d) |
| `{env}-myapp-db-rt` | db-1a/1c/1d | 10.0.0.0/16 | local（外部経路なし） |

### 3.4 Internet Gateway / NAT Gateway

| 項目 | 値 |
|------|-----|
| Internet Gateway名 | `{env}-myapp-igw` |
| NAT Gateway数（prod） | 3（各AZに1台、Elastic IP付与） |
| NAT Gateway数（dev/stg） | 1（コスト削減のため単一AZ配置） |
| NAT Gateway名 | `{env}-myapp-natgw-{az}` |
| Elastic IP | NAT Gatewayごとに1つ自動割当 |

### 3.5 VPC Endpoint詳細設定

| Endpoint名 | サービス名 | タイプ | 配置サブネット | セキュリティグループ |
|-----------|-----------|--------|---------------|---------------------|
| ecr-api | `com.amazonaws.ap-northeast-1.ecr.api` | Interface | private-1a/1c/1d | `{env}-myapp-vpce-sg` |
| ecr-dkr | `com.amazonaws.ap-northeast-1.ecr.dkr` | Interface | private-1a/1c/1d | `{env}-myapp-vpce-sg` |
| s3 | `com.amazonaws.ap-northeast-1.s3` | Gateway | private-rt全て | - |
| logs | `com.amazonaws.ap-northeast-1.logs` | Interface | private-1a/1c/1d | `{env}-myapp-vpce-sg` |
| ssm | `com.amazonaws.ap-northeast-1.ssm` | Interface | private-1a/1c/1d | `{env}-myapp-vpce-sg` |
| ssmmessages | `com.amazonaws.ap-northeast-1.ssmmessages` | Interface | private-1a/1c/1d | `{env}-myapp-vpce-sg` |
| secretsmanager | `com.amazonaws.ap-northeast-1.secretsmanager` | Interface | private-1a/1c/1d | `{env}-myapp-vpce-sg` |

| 項目 | 値 |
|------|-----|
| Private DNS有効化 | 全Interfaceエンドポイントで有効 |
| プライベートDNS解決 | enable_private_dns_enabled = true |

### 3.6 セキュリティグループ詳細

#### 3.6.1 `{env}-myapp-alb-sg`（ALB用）

| 方向 | プロトコル | ポート範囲 | ソース/宛先 | 説明 |
|------|-----------|-----------|------------|------|
| Inbound | TCP | 443 | 0.0.0.0/0 | HTTPS（インターネットから） |
| Inbound | TCP | 80 | 0.0.0.0/0 | HTTP（HTTPSへリダイレクト） |
| Outbound | TCP | 8080 | `{env}-myapp-ecs-sg` | ECSタスクへの転送 |

#### 3.6.2 `{env}-myapp-ecs-sg`（ECS用）

| 方向 | プロトコル | ポート範囲 | ソース/宛先 | 説明 |
|------|-----------|-----------|------------|------|
| Inbound | TCP | 8080 | `{env}-myapp-alb-sg` | ALBからのトラフィック |
| Outbound | TCP | 5432 | `{env}-myapp-rds-sg` | RDS接続 |
| Outbound | TCP | 6379 | `{env}-myapp-cache-sg` | ElastiCache接続 |
| Outbound | TCP | 443 | `{env}-myapp-vpce-sg` | VPC Endpoint経由通信 |

#### 3.6.3 `{env}-myapp-rds-sg`（RDS用）

| 方向 | プロトコル | ポート範囲 | ソース/宛先 | 説明 |
|------|-----------|-----------|------------|------|
| Inbound | TCP | 5432 | `{env}-myapp-ecs-sg` | ECSからのDB接続 |

#### 3.6.4 `{env}-myapp-cache-sg`（ElastiCache用）

| 方向 | プロトコル | ポート範囲 | ソース/宛先 | 説明 |
|------|-----------|-----------|------------|------|
| Inbound | TCP | 6379 | `{env}-myapp-ecs-sg` | ECSからのRedis接続 |

#### 3.6.5 `{env}-myapp-vpce-sg`（VPC Endpoint用）

| 方向 | プロトコル | ポート範囲 | ソース/宛先 | 説明 |
|------|-----------|-----------|------------|------|
| Inbound | TCP | 443 | `{env}-myapp-ecs-sg` | ECSからのHTTPS通信 |

---

## 4. コンピューティング設計（詳細）

### 4.1 ECSクラスター設定

| パラメータ | 値 |
|-----------|-----|
| クラスター名 | `{env}-myapp-cluster` |
| Capacity Provider | FARGATE, FARGATE_SPOT |
| Container Insights | 有効（prod）/ 無効（dev） |

### 4.2 タスク定義詳細

| パラメータ | dev | stg | prod |
|-----------|-----|-----|------|
| ファミリー名 | `{env}-myapp-api` | 同左 | 同左 |
| 起動タイプ | FARGATE | FARGATE | FARGATE |
| ネットワークモード | awsvpc | awsvpc | awsvpc |
| CPU | 256 (.25 vCPU) | 512 (.5 vCPU) | 512 (.5 vCPU) |
| Memory | 512 MB | 1024 MB | 1024 MB |
| OS/アーキテクチャ | Linux/X86_64 | Linux/X86_64 | Linux/X86_64 |

#### コンテナ定義

| パラメータ | 値 |
|-----------|-----|
| コンテナ名 | `app` |
| イメージ | `{ECR_REPO_URI}:{TAG}` |
| ポートマッピング | containerPort: 8080, protocol: tcp |
| ログドライバー | awslogs |
| ログ設定 - グループ名 | `/ecs/{env}-myapp-api` |
| ログ設定 - リージョン | ap-northeast-1 |
| ログ設定 - ストリームプレフィックス | `ecs` |
| ヘルスチェックコマンド | `CMD-SHELL, curl -f http://localhost:8080/health || exit 1` |
| ヘルスチェック間隔 | 30秒 |
| ヘルスチェックタイムアウト | 5秒 |
| ヘルスチェック再試行回数 | 3 |
| ヘルスチェック開始期間 | 60秒 |

#### 環境変数・シークレット

| キー | 種別 | 値/参照元 |
|------|------|----------|
| `APP_ENV` | environment | `{env}` |
| `LOG_LEVEL` | environment | `INFO`（prod）/ `DEBUG`（dev） |
| `DB_HOST` | environment | RDSエンドポイント（Terraform output参照） |
| `DB_NAME` | environment | アプリDB名 |
| `DB_USER` | secrets | Secrets Manager ARN: `{env}-myapp-db-credentials:username::` |
| `DB_PASSWORD` | secrets | Secrets Manager ARN: `{env}-myapp-db-credentials:password::` |
| `REDIS_HOST` | environment | ElastiCacheエンドポイント |

### 4.3 ECSサービス設定

| パラメータ | dev | stg | prod |
|-----------|-----|-----|------|
| サービス名 | `{env}-myapp-api-svc` | 同左 | 同左 |
| Desired Count | 1 | 1 | 2 |
| 最小ヘルス率（minimumHealthyPercent） | 100 | 100 | 100 |
| 最大率（maximumPercent） | 200 | 200 | 200 |
| デプロイコントローラ | CODE_DEPLOY（Blue/Green） | 同左 | 同左 |
| ヘルスチェック猶予期間 | 60秒 | 60秒 | 90秒 |
| プラットフォームバージョン | LATEST | LATEST | LATEST |
| 配置サブネット | private-1a/1c | private-1a/1c | private-1a/1c/1d |
| パブリックIP割当 | 無効 | 無効 | 無効 |

### 4.4 Auto Scaling詳細設定

| パラメータ | dev | stg | prod |
|-----------|-----|-----|------|
| Min Capacity | 1 | 1 | 2 |
| Max Capacity | 2 | 3 | 10 |
| スケーリングポリシータイプ | TargetTrackingScaling | 同左 | 同左 |
| メトリクス | ECSServiceAverageCPUUtilization | 同左 | 同左 |
| ターゲット値 | 70% | 70% | 70% |
| スケールアウトクールダウン | 60秒 | 60秒 | 60秒 |
| スケールインクールダウン | 300秒 | 300秒 | 300秒 |
| 追加ポリシー（Memory） | - | - | ターゲット70%、クールダウン同上 |

### 4.5 タスクロール・実行ロール詳細

#### `{env}-myapp-ecs-task-execution-role`

| 項目 | 値 |
|------|-----|
| 信頼関係（Principal） | `ecs-tasks.amazonaws.com` |
| アタッチポリシー | `AmazonECSTaskExecutionRolePolicy`（AWS管理ポリシー） |
| 追加インラインポリシー | Secrets Manager: `secretsmanager:GetSecretValue` を `{env}-myapp-db-credentials` ARNに限定 |

#### `{env}-myapp-ecs-task-role`

| 項目 | 値 |
|------|-----|
| 信頼関係（Principal） | `ecs-tasks.amazonaws.com` |
| 許可アクション例 | `s3:GetObject`, `s3:PutObject`（対象: `{env}-myapp-assets/*`） |
| 許可アクション例 | `logs:CreateLogStream`, `logs:PutLogEvents` |
| 権限境界 | 【設定する場合はARNを記載】 |

### 4.6 Lambda設定（使用する場合）

| パラメータ | 値 |
|-----------|-----|
| 関数名 | `{env}-myapp-{function}` |
| ランタイム | python3.12 / nodejs20.x（用途に応じ選択） |
| メモリサイズ | 256 MB（標準）〜 1024 MB（重い処理） |
| タイムアウト | 30秒（API Gateway連携時は最大29秒） |
| VPC配置 | 必要な場合のみ（private-1a/1c） |
| 同時実行数上限 | 10（reserved concurrency、必要に応じて） |
| DLQ | SQS（`{env}-myapp-{function}-dlq`） |
| トリガー | EventBridge Schedule / S3 Event / SQS（用途別に記載） |

---
## 5. データ層設計（詳細）

### 5.1 RDS / Auroraクラスター詳細

| パラメータ | dev | stg | prod |
|-----------|-----|-----|------|
| クラスター識別子 | `{env}-myapp-db-cluster` | 同左 | 同左 |
| エンジン | aurora-postgresql | 同左 | 同左 |
| エンジンバージョン | 15.4 | 15.4 | 15.4 |
| インスタンスクラス（Writer） | db.t4g.medium | db.t4g.medium | db.r6g.large |
| インスタンスクラス（Reader） | なし | なし | db.r6g.large |
| インスタンス数 | 1 | 1 | 2（Writer1+Reader1） |
| ストレージタイプ | Aurora（自動拡張） | 同左 | 同左 |
| マルチAZ | 無効 | 無効 | 有効 |
| ポート | 5432 | 5432 | 5432 |
| パラメータグループ | `{env}-myapp-pg15-cluster-params` | 同左 | 同左 |
| サブネットグループ | `{env}-myapp-db-subnet-group`（db-1a/1c/1d） | 同左 | 同左 |
| セキュリティグループ | `{env}-myapp-rds-sg` | 同左 | 同左 |

### 5.2 RDSパラメータグループ詳細値

| パラメータ名 | 値 | 説明 |
|-------------|-----|------|
| `max_connections` | `LEAST({DBInstanceClassMemory/9531392}, 5000)` | 接続数上限（Aurora推奨式） |
| `log_statement` | `ddl` | DDL文をログ出力 |
| `log_min_duration_statement` | `1000` | 1秒以上のクエリをログ出力（スロークエリ検知） |
| `shared_preload_libraries` | `pg_stat_statements` | クエリ統計情報拡張を有効化 |
| `timezone` | `Asia/Tokyo` | タイムゾーン設定 |
| `rds.force_ssl` | `1` | SSL接続を強制 |

### 5.3 バックアップ・メンテナンス設定

| パラメータ | dev | stg | prod |
|-----------|-----|-----|------|
| 自動バックアップ保持期間 | 1日 | 3日 | 7日 |
| バックアップウィンドウ | 18:00-19:00 UTC（03:00-04:00 JST） | 同左 | 同左 |
| メンテナンスウィンドウ | sun:19:00-sun:20:00 UTC | 同左 | 同左 |
| 削除保護 | 無効 | 無効 | 有効 |
| 最終スナップショット取得 | スキップ | スキップ | 必須（`{env}-myapp-final-snapshot`） |
| 暗号化 | 有効（aws/rds） | 有効（aws/rds） | 有効（カスタムKMSキー検討） |
| Performance Insights | 無効 | 有効（保持7日） | 有効（保持7日、prod長期化検討） |

### 5.4 認証情報管理（Secrets Manager）

| パラメータ | 値 |
|-----------|-----|
| シークレット名 | `{env}-myapp-db-credentials` |
| 自動生成パスワード長 | 32文字 |
| 除外文字 | `"@/\\` |
| ローテーション | 有効（prod: 30日 / dev・stg: 無効） |
| ローテーションLambda | AWS提供のRDS PostgreSQLシングルユーザーローテーション |

### 5.5 S3バケット詳細

| バケット名 | 用途 | バージョニング | 暗号化 | パブリックアクセスブロック | ライフサイクル |
|-----------|------|---------------|--------|--------------------------|--------------|
| `{env}-myapp-assets` | アプリ静的ファイル | 有効 | SSE-S3 | 全項目有効 | なし |
| `{env}-myapp-logs` | アクセスログ・アプリログ | 無効 | SSE-S3 | 全項目有効 | 90日後Glacier、365日後削除 |
| `{env}-myapp-terraform-state` | Terraform State | 有効（MFA Delete: prod有効） | SSE-S3 | 全項目有効 | なし |

#### 5.5.1 ライフサイクルルール詳細（`{env}-myapp-logs`）

| ルール名 | 適用対象 | アクション | 日数 |
|---------|---------|-----------|------|
| transition-to-glacier | 全オブジェクト | STANDARD → GLACIER | 90日経過後 |
| expire-old-logs | 全オブジェクト | 削除 | 365日経過後 |
| abort-incomplete-upload | 全オブジェクト | マルチパートアップロード中断分削除 | 7日経過後 |

#### 5.5.2 バケットポリシー要点

| 項目 | 内容 |
|------|------|
| `{env}-myapp-assets` | ECSタスクロールからの`GetObject`/`PutObject`のみ許可。CloudFront経由配信時はOACを使用 |
| `{env}-myapp-logs` | ALB/CloudFrontのログ配信用サービスプリンシパルからの`PutObject`を許可 |
| `{env}-myapp-terraform-state` | Terraform実行ロール（CI/CD用IAMロール）からのアクセスのみ許可 |

### 5.6 ElastiCache詳細設定（使用する場合）

| パラメータ | dev | stg | prod |
|-----------|-----|-----|------|
| クラスター識別子 | `{env}-myapp-redis` | 同左 | 同左 |
| エンジン | Redis | Redis | Redis |
| エンジンバージョン | 7.1 | 7.1 | 7.1 |
| ノードタイプ | cache.t4g.micro | cache.t4g.micro | cache.r6g.large |
| ノード数（クラスターモード無効時） | 1 | 1 | 2（プライマリ+レプリカ） |
| クラスターモード | 無効 | 無効 | 無効（必要に応じレプリケーショングループ検討） |
| ポート | 6379 | 6379 | 6379 |
| サブネットグループ | `{env}-myapp-cache-subnet-group`（db-1a/1c） | 同左 | 同左（db-1a/1c/1d） |
| 保存時暗号化 | 有効 | 有効 | 有効 |
| 転送時暗号化 | 有効 | 有効 | 有効 |
| 自動フェイルオーバー | 無効 | 無効 | 有効 |
| パラメータグループ | `default.redis7` | 同左 | 同左（カスタム化検討） |

---

## 6. セキュリティ設計（詳細）

### 6.1 IAMロール一覧

| ロール名 | 信頼するエンティティ | 主な用途 | アタッチポリシー |
|---------|---------------------|---------|------------------|
| `{env}-myapp-ecs-task-execution-role` | ecs-tasks.amazonaws.com | タスク起動（ECRプル、ログ送信） | AmazonECSTaskExecutionRolePolicy + Secrets Managerインライン |
| `{env}-myapp-ecs-task-role` | ecs-tasks.amazonaws.com | アプリ実行時のAWS API呼び出し | S3, CloudWatch Logsカスタムポリシー |
| `{env}-myapp-codebuild-role` | codebuild.amazonaws.com | CI/CDビルド実行 | ECR Push, S3, CloudWatch Logs |
| `{env}-myapp-codepipeline-role` | codepipeline.amazonaws.com | パイプライン実行 | CodeBuild起動、ECSデプロイ、S3 |
| `{env}-myapp-codedeploy-role` | codedeploy.amazonaws.com | Blue/Greenデプロイ | AWSCodeDeployRoleForECS |
| `{env}-myapp-terraform-ci-role` | GitHub Actions OIDC | Terraform plan/apply | AdministratorAccess相当（環境ごとに分離・要レビュー） |

### 6.2 IAMポリシー詳細例

#### 6.2.1 ECSタスクロール用ポリシー（S3アクセス）

| 項目 | 値 |
|------|-----|
| Effect | Allow |
| Action | `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` |
| Resource | `arn:aws:s3:::{env}-myapp-assets/*` |

#### 6.2.2 ECSタスク実行ロール用ポリシー（Secrets Manager）

| 項目 | 値 |
|------|-----|
| Effect | Allow |
| Action | `secretsmanager:GetSecretValue` |
| Resource | `arn:aws:secretsmanager:ap-northeast-1:{account_id}:secret:{env}-myapp-db-credentials-*` |

### 6.3 KMSキー設計

| キー名 | エイリアス | 用途 | キーローテーション |
|--------|-----------|------|-------------------|
| RDS用（デフォルト） | `aws/rds` | RDS暗号化（dev/stg） | AWS管理 |
| RDS用（カスタム） | `alias/{env}-myapp-rds-key` | RDS暗号化（prod、必要時） | 有効（年次） |
| S3用 | `aws/s3` または `alias/{env}-myapp-s3-key` | S3暗号化 | 有効（年次） |
| Secrets Manager用 | `aws/secretsmanager` | シークレット暗号化 | AWS管理 |

### 6.4 ACM証明書設定

| 項目 | 値 |
|------|-----|
| ドメイン名 | `{env}.example.com` / `www.example.com`（prod） |
| 検証方法 | DNS検証（Route53自動検証） |
| リージョン | ap-northeast-1（ALB用）、us-east-1（CloudFront用、必要時） |
| 自動更新 | 有効（ACMマネージド） |

### 6.5 WAF詳細設定

| パラメータ | 値 |
|-----------|-----|
| WebACL名 | `{env}-myapp-web-acl` |
| スコープ | REGIONAL（ALBアタッチ） |
| デフォルトアクション | Allow |
| ログ送信先 | `{env}-myapp-waf-logs`（CloudWatch Logs、Kinesis Firehose経由） |

#### 6.5.1 ルール詳細

| 優先度 | ルール名 | ルールタイプ | アクション | 設定値 |
|--------|---------|-------------|-----------|--------|
| 0 | AWS-AWSManagedRulesCommonRuleSet | マネージドルールグループ | Block | デフォルト設定 |
| 1 | AWS-AWSManagedRulesKnownBadInputsRuleSet | マネージドルールグループ | Block | デフォルト設定 |
| 2 | AWS-AWSManagedRulesSQLiRuleSet | マネージドルールグループ | Block | デフォルト設定 |
| 3 | AWS-AWSManagedRulesAmazonIpReputationList | マネージドルールグループ | Block | デフォルト設定（prodのみ） |
| 10 | RateLimitRule | レートベース | Block | 5分間あたり2000リクエスト/IP |
| 20 | GeoBlockRule | 地理的制限 | Block | 【対象国コードを記載、必要な場合のみ】 |

### 6.6 セキュリティサービス詳細設定

| サービス | パラメータ | 値 |
|---------|-----------|-----|
| GuardDuty | 検出頻度 | 15分 |
| GuardDuty | S3保護 | 有効 |
| GuardDuty | Malware Protection | 有効（prod） |
| GuardDuty | 通知先 | EventBridge → SNS → Slack |
| CloudTrail | 証跡名 | `{env}-myapp-trail` |
| CloudTrail | ログ保存先S3 | `{env}-myapp-logs/cloudtrail/` |
| CloudTrail | マルチリージョン | 有効 |
| CloudTrail | ログファイル検証 | 有効 |
| AWS Config | 記録対象 | 全リソースタイプ |
| AWS Config | 配信先S3 | `{env}-myapp-logs/config/` |
| AWS Config | 評価ルール例 | `s3-bucket-public-read-prohibited`, `rds-storage-encrypted`, `iam-user-mfa-enabled` |
| SecurityHub | 有効化する標準 | AWS基礎セキュリティベストプラクティス, CIS AWS Foundations Benchmark |
| Inspector | スキャン対象 | ECR（prod環境のリポジトリ） |
| Inspector | スキャントリガー | イメージプッシュ時 + 継続的スキャン |

---

## 7. 可観測性設計（詳細）

### 7.1 CloudWatch Logグループ詳細

| ロググループ名 | 保持期間（dev） | 保持期間（stg） | 保持期間（prod） | 暗号化 |
|---------------|----------------|----------------|------------------|--------|
| `/ecs/{env}-myapp-api` | 7日 | 14日 | 30日 | KMS（オプション） |
| `/aws/waf/{env}-myapp` | 7日 | 14日 | 30日 | - |
| ALBアクセスログ（S3） | - | - | 90日（ライフサイクル） | SSE-S3 |
| `/aws/rds/cluster/{env}-myapp-db-cluster/postgresql` | 7日 | 7日 | 14日 | - |

### 7.2 ログフォーマット規約

| 項目 | 値 |
|------|-----|
| 形式 | JSON（1行1レコード） |
| 必須フィールド | `timestamp`, `level`, `message`, `request_id`, `service` |
| タイムスタンプ形式 | ISO 8601（UTC） |
| ログレベル | `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL` |

### 7.3 メトリクスフィルター

| フィルター名 | 対象ロググループ | パターン | 出力メトリクス |
|-------------|------------------|---------|----------------|
| `{env}-myapp-error-count` | `/ecs/{env}-myapp-api` | `{ $.level = "ERROR" }` | `MyApp/ErrorCount` |
| `{env}-myapp-fatal-count` | `/ecs/{env}-myapp-api` | `{ $.level = "FATAL" }` | `MyApp/FatalCount` |

### 7.4 CloudWatch Alarm詳細一覧

| アラーム名 | メトリクス | 統計 | 期間 | Warning閾値 | Critical閾値 | 評価期間 | 通知先（SNSトピック） |
|-----------|-----------|------|------|------------|-------------|---------|----------------------|
| `{env}-myapp-ecs-cpu-high` | ECS CPUUtilization | Average | 5分 | 70% | 90% | 連続2回 | `{env}-myapp-alert-topic` |
| `{env}-myapp-ecs-memory-high` | ECS MemoryUtilization | Average | 5分 | 70% | 90% | 連続2回 | `{env}-myapp-alert-topic` |
| `{env}-myapp-alb-5xx-rate` | ALB HTTPCode_Target_5XX_Count / RequestCount | 計算式 | 5分 | 1% | 5% | 連続2回 | `{env}-myapp-alert-topic` |
| `{env}-myapp-alb-response-time` | ALB TargetResponseTime | p95 | 5分 | 500ms | 1000ms | 連続3回 | `{env}-myapp-alert-topic` |
| `{env}-myapp-rds-cpu-high` | RDS CPUUtilization | Average | 5分 | 70% | 90% | 連続2回 | `{env}-myapp-alert-topic` |
| `{env}-myapp-rds-storage-low` | RDS FreeStorageSpace | Minimum | 5分 | 10GB | 5GB | 連続1回 | `{env}-myapp-alert-topic` |
| `{env}-myapp-rds-connections-high` | RDS DatabaseConnections | Average | 5分 | 80%（max_connections比） | 95% | 連続2回 | `{env}-myapp-alert-topic` |

### 7.5 SNS / Slack連携設定

| パラメータ | 値 |
|-----------|-----|
| SNSトピック名 | `{env}-myapp-alert-topic` |
| サブスクリプション | AWS Chatbot（Slack連携） |
| Slackチャンネル（Warning） | `#myapp-alert-warning` |
| Slackチャンネル（Critical） | `#myapp-alert-critical` |
| Chatbot IAMロール | 通知のみ（読み取り専用権限） |

### 7.6 SLI/SLO詳細定義

| SLI名 | 定義式 | SLO目標 | エラーバジェット（月間） | 計測ソース |
|-------|--------|---------|--------------------------|-----------|
| 可用性 | (総リクエスト数 - 5xx数) / 総リクエスト数 | 99.9% | 43.2分 | ALBメトリクス |
| レイテンシ | p95 TargetResponseTime ≤ 500ms の割合 | 99% | - | ALBメトリクス |
| エラー率 | 5xx数 / 総リクエスト数 | 0.1%以下 | - | ALBメトリクス |

### 7.7 ダッシュボード構成

| ダッシュボード名 | 表示ウィジェット |
|-----------------|------------------|
| `{env}-myapp-overview` | ALBリクエスト数、5xx率、レスポンスタイム、ECS CPU/Memory、RDS CPU/接続数 |
| `{env}-myapp-cost` | サービス別コスト推移（Cost Explorer連携） |

---
## 8. CI/CD設計（詳細）

### 8.1 リポジトリ・ブランチ戦略

| 項目 | 値 |
|------|-----|
| リポジトリ | GitHub `{org}/{repo}` |
| ブランチ戦略 | GitHub Flow（`main` + フィーチャーブランチ） |
| `main`ブランチ保護 | 必須レビュー1名以上、CIパス必須 |
| デプロイトリガー（dev） | `develop`ブランチへのpush |
| デプロイトリガー（stg） | `main`ブランチへのpush |
| デプロイトリガー（prod） | `main`ブランチでのタグ作成（`v*`）+ 手動承認 |

### 8.2 ECRリポジトリ詳細

| パラメータ | 値 |
|-----------|-----|
| リポジトリ名 | `{system}/api` |
| イメージタグ可変性 | IMMUTABLE |
| スキャンオンプッシュ | 有効 |
| ライフサイクルポリシー | `untagged`イメージは1日後削除、保持タグ数は直近30件 |
| 暗号化 | AES256 |

### 8.3 CodeBuild詳細設定

| パラメータ | 値 |
|-----------|-----|
| プロジェクト名 | `{env}-myapp-build` |
| 環境イメージ | `aws/codebuild/standard:7.0` |
| コンピュートタイプ | `BUILD_GENERAL1_MEDIUM` |
| 環境変数 | `AWS_ACCOUNT_ID`, `ECR_REPO_URI`, `IMAGE_TAG` |
| buildspec配置 | リポジトリルート `buildspec.yml` |
| キャッシュ | ローカルキャッシュ（Dockerレイヤー） |
| タイムアウト | 30分 |

#### buildspec.yml主要フェーズ

| フェーズ | 内容 |
|---------|------|
| pre_build | ECRログイン、イメージタグ生成（Gitコミットハッシュ） |
| build | `docker build`、ユニットテスト実行 |
| post_build | ECRへ`docker push`、`imagedefinitions.json`生成 |

### 8.4 CodePipeline詳細設定

| パラメータ | 値 |
|-----------|-----|
| パイプライン名 | `{env}-myapp-pipeline` |
| アーティファクトストア | `{env}-myapp-pipeline-artifacts`（S3） |

#### ステージ構成

| ステージ名 | アクション | プロバイダ | 入力 | 出力 |
|-----------|-----------|-----------|------|------|
| Source | GitHub接続経由でソース取得 | CodeStarSourceConnection | - | SourceOutput |
| Build | Dockerビルド・テスト・ECR Push | CodeBuild | SourceOutput | BuildOutput |
| Deploy（STG） | ECS Blue/Greenデプロイ | CodeDeployToECS | BuildOutput | - |
| Approval | 手動承認 | Manual | - | - |
| Deploy（PROD） | ECS Blue/Greenデプロイ | CodeDeployToECS | BuildOutput | - |

### 8.5 CodeDeploy（Blue/Green）詳細設定

| パラメータ | 値 |
|-----------|-----|
| アプリケーション名 | `{env}-myapp-codedeploy-app` |
| デプロイグループ名 | `{env}-myapp-deploy-group` |
| デプロイ設定 | `CodeDeployDefault.ECSAllAtOnce`（dev/stg）/ `CodeDeployDefault.ECSCanary10Percent5Minutes`（prod） |
| ロードバランサー | ALB（本番/テストリスナー2つ使用） |
| 本番リスナーポート | 443 |
| テストリスナーポート | 8443 |
| トラフィック再ルーティング待機時間 | 5分 |
| 自動ロールバック条件 | デプロイ失敗時、アラーム発火時 |
| 関連CloudWatchアラーム | `{env}-myapp-alb-5xx-rate`（Critical） |

---

## 9. バックアップ・DR設計（詳細）

### 9.1 バックアップ詳細スケジュール

| 対象 | バックアップ方式 | スケジュール | 保持期間（prod） | 保管先 |
|------|------------------|-------------|------------------|--------|
| RDS Aurora | 自動スナップショット | 毎日 03:00 JST | 7日 | RDS管理領域 |
| RDS Aurora | 手動スナップショット | リリース直前 | 無期限（手動削除、命名規則: `{env}-myapp-pre-release-{date}`） | RDS管理領域 |
| RDS Aurora | AWS Backup（追加バックアップ、検討時） | 週次日曜02:00 JST | 35日 | AWS Backup Vault |
| S3（assets） | バージョニング | 常時 | オブジェクト上書き時に旧バージョン保持90日 | 同一バケット |
| Terraformコード | Gitリポジトリ | コミット単位 | 無期限 | GitHub |

### 9.2 DR詳細方針

| 項目 | 値 |
|------|-----|
| DR方式 | バックアップ&リストア（Pilot Light方式へ将来拡張検討） |
| プライマリリージョン | ap-northeast-1（東京） |
| DRリージョン | ap-northeast-3（大阪） |
| RDSスナップショットのクロスリージョンコピー | 有効（毎日、`ap-northeast-3`へコピー、保持7日） |
| S3クロスリージョンレプリケーション | `{env}-myapp-assets` → `{env}-myapp-assets-dr`（必要時のみ有効化） |
| Terraformコード | DR用環境ディレクトリ（`environments/dr/`）を事前準備 |
| DR切替手順書 | 別紙『DR切替手順書』を参照（作成要） |
| DR訓練頻度 | 半期に1回 |

### 9.3 障害時エスカレーションフロー

| 段階 | トリガー | 対応者 | 対応時間目標 |
|------|---------|--------|-------------|
| 一次対応 | CloudWatch Critical Alarm発報 | オンコール担当者 | 検知後15分以内に一次切り分け |
| 二次対応 | 一次対応で復旧不可 | インフラリーダー | 30分以内にエスカレーション判断 |
| DR発動判断 | リージョン規模の障害確認 | プロジェクトマネージャー承認 | 状況確認後1時間以内に判断 |

---

## 10. コスト設計（詳細）

### 10.1 環境別月次コスト見積もり詳細

#### prod環境

| サービス | スペック | 数量 | 単価目安（USD/月） | 小計（USD） |
|---------|---------|------|---------------------|------------|
| ECS Fargate | 0.5vCPU/1GBタスク | 2 | $15 | $30 |
| ALB | 標準 | 1 | $20 | $20 |
| RDS Aurora（Writer） | db.r6g.large | 1 | $130 | $130 |
| RDS Aurora（Reader） | db.r6g.large | 1 | $130 | $130 |
| Aurora ストレージ | 100GB想定 | - | $0.10/GB | $10 |
| NAT Gateway | 3AZ稼働 + データ処理 | 3 | $33 | $100 |
| ElastiCache | cache.r6g.large × 2 | 2 | $90 | $180 |
| CloudWatch Logs | 取り込み・保存10GB | - | $5 | $5 |
| WAF | WebACL + ルール5個 + リクエスト課金 | - | $10 | $10 |
| GuardDuty | 標準 | - | $5 | $5 |
| **合計（参考）** | | | | **約 $620 / 月** |

#### dev/stg環境（共通目安・各環境）

| サービス | スペック | 月額目安（USD） |
|---------|---------|-----------------|
| ECS Fargate | 0.25-0.5vCPU × 1タスク | $7-15 |
| ALB | 標準 | $20 |
| RDS Aurora | db.t4g.medium × 1 | $55 |
| NAT Gateway | 1台 | $33 |
| その他（ログ/WAF簡易/GuardDuty） | - | $10 |
| **合計（参考）** | | **約 $125-135 / 月** |

> ※ 上記は東京リージョンの2025年時点目安価格に基づく概算であり、実際のコストは利用状況・データ転送量・最新の料金体系により変動します。最新情報はAWS Pricing Calculatorで確認してください。

### 10.2 コスト最適化施策詳細

| 施策 | 対象環境 | 設定内容 | 想定削減効果 |
|------|---------|---------|--------------|
| AWS Budgets | 全環境 | 月次予算額の80%/100%でメール+Slack通知 | 予算超過の早期検知 |
| ECSスケジュール停止 | dev/stg | EventBridge Schedulerで平日19:00に`desired_count=0`、翌8:00に復帰 | 約60%の稼働時間削減 |
| NAT Gateway削減 | dev/stg | 単一AZ構成（3→1） | 約$66/月削減（環境あたり） |
| Aurora Serverless v2検討 | dev | 将来的にON-DEMAND→Serverless v2へ移行検討 | 低トラフィック時のコスト最適化 |
| Compute Savings Plans | prod | 本番稼働1年経過後、1年契約で適用検討 | Fargate費用の最大20%削減 |
| S3ライフサイクル | 全環境 | Glacier移行・自動削除（5.5.1参照） | ストレージコスト削減 |

---

## 11. 課題・TODO

| No. | 章番号 | 課題・TODO | 担当者 | 期日 | ステータス |
|-----|--------|-----------|--------|------|-----------|
| 1 | 3 | NAT Gateway構成（dev/stgのAZ数）の最終確認 | 【担当者】 | YYYY/MM/DD | 未着手 |
| 2 | 5 | ElastiCache利用要否の最終判断 | 【担当者】 | YYYY/MM/DD | 未着手 |
| 3 | 6 | KMSカスタムキーの要否・コンプライアンス確認 | 【担当者】 | YYYY/MM/DD | 未着手 |
| 4 | 8 | CodeDeployのCanaryデプロイ設定値の検証 | 【担当者】 | YYYY/MM/DD | 未着手 |
| 5 | 9 | DR切替手順書の作成 | 【担当者】 | YYYY/MM/DD | 未着手 |

---

## 12. 用語集

| 用語 | 説明 |
|------|------|
| VPC | Virtual Private Cloud。AWS上の仮想ネットワーク環境 |
| ECS | Elastic Container Service。コンテナオーケストレーションサービス |
| Fargate | サーバーレスコンテナ実行環境。EC2管理不要 |
| ALB | Application Load Balancer。L7レイヤーのロードバランサー |
| RDS | Relational Database Service。マネージドRDBサービス |
| Aurora | RDSの高性能・高可用性エンジン（MySQL/PostgreSQL互換） |
| WAF | Web Application Firewall。Webアプリへの攻撃を遮断 |
| SLO | Service Level Objective。サービスレベル目標値 |
| SLI | Service Level Indicator。SLO達成状況を測る指標 |
| RTO | Recovery Time Objective。目標復旧時間 |
| RPO | Recovery Point Objective。目標復旧時点 |
| IaC | Infrastructure as Code。インフラをコードで管理 |
| Blue/Greenデプロイ | 新旧2環境を並行稼働させ、トラフィックを切り替えてリリースする方式 |
| Canaryデプロイ | 新バージョンへのトラフィックを段階的に増やすデプロイ方式 |
| エラーバジェット | SLO未達まで許容できる障害時間・エラー量の枠 |
| OAC | Origin Access Control。CloudFrontからS3への安全なアクセス制御方式 |
| DLQ | Dead Letter Queue。処理失敗メッセージの退避先キュー |
