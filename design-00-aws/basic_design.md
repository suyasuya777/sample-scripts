# インフラ基本設計書

**Infrastructure Basic Design Document**

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

> 本書は社外秘です。無断複製・配布を禁じます。

---

## 目次

- [1. 目的・スコープ](#1-目的スコープ)
  - [1.1 ドキュメントの目的](#11-ドキュメントの目的)
  - [1.2 対象システム・範囲](#12-対象システム範囲)
  - [1.3 前提条件・制約](#13-前提条件制約)
- [2. システム概要](#2-システム概要)
  - [2.1 システム全体像](#21-システム全体像)
  - [2.2 非機能要件](#22-非機能要件)
- [3. ネットワーク設計](#3-ネットワーク設計)
  - [3.1 VPC設計](#31-vpc設計)
  - [3.2 サブネット設計](#32-サブネット設計)
  - [3.3 VPC Endpoint](#33-vpc-endpoint)
  - [3.4 セキュリティグループ設計](#34-セキュリティグループ設計)
- [4. コンピューティング設計](#4-コンピューティング設計)
  - [4.1 ECS / Fargate](#41-ecs--fargate)
  - [4.2 Auto Scaling](#42-auto-scaling)
  - [4.3 タスクロール設計](#43-タスクロール設計)
- [5. データ層設計](#5-データ層設計)
  - [5.1 RDS / Aurora](#51-rds--aurora)
  - [5.2 S3](#52-s3)
- [6. セキュリティ設計](#6-セキュリティ設計)
  - [6.1 IAM設計方針](#61-iam設計方針)
  - [6.2 シークレット管理](#62-シークレット管理)
  - [6.3 WAF設計](#63-waf設計)
  - [6.4 セキュリティサービス](#64-セキュリティサービス)
- [7. 可観測性設計（SRE観点）](#7-可観測性設計sre観点)
  - [7.1 ログ設計](#71-ログ設計)
  - [7.2 メトリクス・アラート設計](#72-メトリクスアラート設計)
  - [7.3 SLI / SLO定義](#73-sli--slo定義)
- [8. CI/CD設計](#8-cicd設計)
  - [8.1 パイプライン構成](#81-パイプライン構成)
  - [8.2 デプロイフロー](#82-デプロイフロー)
- [9. バックアップ・DR設計](#9-バックアップdr設計)
  - [9.1 バックアップ計画](#91-バックアップ計画)
  - [9.2 DR方針](#92-dr方針)
- [10. コスト設計](#10-コスト設計)
  - [10.1 月次コスト見積もり（概算）](#101-月次コスト見積もり概算)
  - [10.2 コスト最適化方針](#102-コスト最適化方針)
- [11. 課題・TODO](#11-課題todo)
- [12. 用語集](#12-用語集)

---

## 改訂履歴

| バージョン | 日付 | 変更者 | 変更内容 |
|-----------|------|--------|---------|
| 1.0 | YYYY/MM/DD | 【氏名】 | 初版作成 |
| | | | |

---

## 1. 目的・スコープ

### 1.1 ドキュメントの目的

本書は【システム名】のAWSインフラ基本設計を定義するものです。開発チーム・インフラチーム・レビュアーが共通認識を持つことを目的とします。

### 1.2 対象システム・範囲

| 項目 | 内容 |
|------|------|
| システム名 | 【システム名を入力】 |
| 対象環境 | 開発（dev）/ ステージング（stg）/ 本番（prod） |
| クラウド | AWS |
| 主要リージョン | ap-northeast-1（東京） |
| DR リージョン | ap-northeast-3（大阪）※必要な場合 |

### 1.3 前提条件・制約

- AWSアカウントは既に作成済みであること
- Terraformによるインフラのコード管理を前提とする
- 【その他の前提条件を記載】

---

## 2. システム概要

### 2.1 システム全体像

【システムの概要・目的・主要機能を記載。アーキテクチャ図を添付する場合はここに挿入。】

### 2.2 非機能要件

| 観点 | 要件 | 備考 |
|------|------|------|
| 可用性 | 99.9%（月間ダウンタイム 43分以内） | |
| RPO（目標復旧時点） | 1時間以内 | |
| RTO（目標復旧時間） | 4時間以内 | |
| 最大同時接続数 | 【数値を入力】 | |
| レスポンスタイム | 95パーセンタイル 500ms以内 | |
| データ保持期間 | 【年数を入力】年間 | 法令要件を確認 |

---

## 3. ネットワーク設計

### 3.1 VPC設計

| 項目 | 内容 |
|------|------|
| VPC CIDR | 10.0.0.0/16 |
| リージョン | ap-northeast-1（東京） |
| AZ数 | 3（ap-northeast-1a / 1c / 1d） |
| サブネット構成 | Public / Private / DB の3層分離 |

### 3.2 サブネット設計

| サブネット種別 | AZ | CIDR | 用途 | 備考 |
|--------------|-----|------|------|------|
| Public | ap-northeast-1a | 10.0.1.0/24 | ALB, NAT GW | |
| Public | ap-northeast-1c | 10.0.2.0/24 | ALB, NAT GW | |
| Public | ap-northeast-1d | 10.0.3.0/24 | ALB, NAT GW | |
| Private | ap-northeast-1a | 10.0.11.0/24 | ECS Fargate, Lambda | |
| Private | ap-northeast-1c | 10.0.12.0/24 | ECS Fargate, Lambda | |
| Private | ap-northeast-1d | 10.0.13.0/24 | ECS Fargate, Lambda | |
| DB | ap-northeast-1a | 10.0.21.0/24 | RDS, ElastiCache | |
| DB | ap-northeast-1c | 10.0.22.0/24 | RDS, ElastiCache | |
| DB | ap-northeast-1d | 10.0.23.0/24 | RDS, ElastiCache | |

### 3.3 VPC Endpoint

| サービス | タイプ | 用途 |
|---------|--------|------|
| com.amazonaws.ap-northeast-1.ecr.api | Interface | ECR API 通信 |
| com.amazonaws.ap-northeast-1.ecr.dkr | Interface | ECR Docker Registry 通信 |
| com.amazonaws.ap-northeast-1.s3 | Gateway | S3 アクセス |
| com.amazonaws.ap-northeast-1.logs | Interface | CloudWatch Logs 送信 |
| com.amazonaws.ap-northeast-1.ssm | Interface | SSM Session Manager |
| com.amazonaws.ap-northeast-1.secretsmanager | Interface | Secrets Manager アクセス |

### 3.4 セキュリティグループ設計

| SG名 | 方向 | ポート | ソース/宛先 | 用途 |
|------|------|--------|------------|------|
| sg-alb | Inbound | 443 | 0.0.0.0/0 | HTTPS受信 |
| sg-alb | Inbound | 80 | 0.0.0.0/0 | HTTP受信（HTTPSリダイレクト用） |
| sg-ecs | Inbound | 8080 | sg-alb | ALBからのトラフィック |
| sg-rds | Inbound | 5432 | sg-ecs | ECSからのDB接続 |
| sg-cache | Inbound | 6379 | sg-ecs | ECSからのRedis接続 |

---

## 4. コンピューティング設計

### 4.1 ECS / Fargate

| 項目 | 内容 |
|------|------|
| クラスター名 | 【env】-app-cluster |
| 起動タイプ | Fargate |
| タスクCPU | 512（0.5 vCPU）※本番は1024以上を検討 |
| タスクMemory | 1024 MB（1 GB） |
| Desired Count | 本番: 2 / STG: 1 / DEV: 1 |
| デプロイ方式 | Blue/Green Deploy（CodeDeploy連携） |

### 4.2 Auto Scaling

| 項目 | 内容 |
|------|------|
| スケーリングポリシー | ターゲット追跡スケーリング |
| スケールアウト閾値 | CPU使用率 70% |
| Min Capacity | 本番: 2 / STG: 1 / DEV: 1 |
| Max Capacity | 本番: 10 / STG: 3 / DEV: 2 |
| スケールイン保護 | 実行中タスクのdraining: 30秒 |

### 4.3 タスクロール設計

| ロール種別 | ロール名 | 主な権限 |
|-----------|---------|---------|
| タスク実行ロール | 【env】-ecs-task-execution-role | ECR Pull, CloudWatch Logs, Secrets Manager |
| タスクロール | 【env】-ecs-task-role | アプリが必要とするAWSサービス権限 |

---

## 5. データ層設計

### 5.1 RDS / Aurora

| 項目 | 内容 |
|------|------|
| エンジン | Amazon Aurora PostgreSQL 15.x |
| クラスター構成 | Writer 1台 + Reader 1台（本番） |
| インスタンスタイプ | db.r6g.large（本番）/ db.t4g.medium（STG/DEV） |
| ストレージ | Aurora自動拡張（最大 128 TB） |
| マルチAZ | 有効（Writer/Reader を別AZに配置） |
| 自動バックアップ | 保持期間: 本番7日 / STG・DEV 3日 |
| 削除保護 | 本番: 有効 / STG・DEV: 無効 |
| 暗号化 | AWS KMS（aws/rds） |

### 5.2 S3

| バケット名 | 用途 | 主な設定 |
|-----------|------|---------|
| 【env】-app-assets | アプリケーション静的ファイル | バージョニング有効, SSE-S3 |
| 【env】-app-logs | アクセスログ・アプリログ | ライフサイクル（90日後Glacier） |
| 【env】-terraform-state | Terraform State | バージョニング有効, SSE-S3, MFA Delete |

---

## 6. セキュリティ設計

### 6.1 IAM設計方針

- ルートアカウント: MFA有効化・アクセスキー未発行
- IAMユーザー: 個人ごとに発行、共有アカウント禁止
- サービス間通信: IAMロール使用（アクセスキー発行禁止）
- ポリシー: 最小権限の原則、管理ポリシー優先

### 6.2 シークレット管理

| 項目 | 内容 |
|------|------|
| DBパスワード | Secrets Manager（自動ローテーション: 30日） |
| APIキー等の機密情報 | Parameter Store（SecureString型） |
| TLS証明書 | ACM（自動更新） |
| 環境変数 | 機密情報はSecretsManagerARNで参照（ハードコード禁止） |

### 6.3 WAF設計

| ルール名 | 優先度 | 内容 |
|---------|--------|------|
| AWSManagedRulesCommonRuleSet | 1 | OWASP Top 10 基本ルール |
| AWSManagedRulesSQLiRuleSet | 2 | SQLインジェクション対策 |
| AWSManagedRulesKnownBadInputsRuleSet | 3 | 既知の悪意あるリクエスト遮断 |
| RateBasedRule | 4 | 同一IPから5分間2000リクエスト超で遮断 |
| IPBlockList | 5 | ブロックリストIP遮断（必要に応じて） |

### 6.4 セキュリティサービス

| サービス | 有効/無効 | 目的 |
|---------|----------|------|
| GuardDuty | 有効 | 脅威検知・異常アクセス監視 |
| CloudTrail | 有効 | APIコール操作ログ（S3に90日保存） |
| AWS Config | 有効 | リソース変更履歴・コンプライアンス評価 |
| SecurityHub | 有効 | セキュリティスコア可視化・統合管理 |
| Inspector | 有効（本番） | EC2/ECRイメージの脆弱性スキャン |

---

## 7. 可観測性設計（SRE観点）

### 7.1 ログ設計

| ログ種別 | 送信先 | 保持期間 | 備考 |
|---------|--------|---------|------|
| アプリログ | CloudWatch Logs | 30日（本番）/ 7日（DEV） | JSON形式推奨 |
| ALBアクセスログ | S3（app-logs） | 90日 | |
| CloudFrontログ | S3（app-logs） | 90日 | |
| WAFログ | CloudWatch Logs | 30日 | |
| CloudTrailログ | S3（app-logs） | 365日 | 変更不可設定 |

### 7.2 メトリクス・アラート設計

| 対象 | メトリクス | Warning閾値 | Critical閾値 | 通知先 |
|------|-----------|------------|-------------|--------|
| ECS | CPU使用率 | 70% | 90% | Slack #alert |
| ECS | Memory使用率 | 70% | 90% | Slack #alert |
| ALB | 5xxエラー率 | 1% | 5% | Slack #alert |
| ALB | TargetResponseTime | 500ms | 1000ms | Slack #alert |
| RDS | CPU使用率 | 70% | 90% | Slack #alert |
| RDS | FreeStorageSpace | 10GB | 5GB | Slack #alert |

### 7.3 SLI / SLO定義

| SLI | 計測方法 | SLO目標値 | 備考 |
|-----|---------|----------|------|
| 可用性 | ALB 2xx+3xx / 総リクエスト | 99.9% / 月 | |
| レイテンシ | ALB TargetResponseTime p95 | 500ms以内 | |
| エラー率 | ALB 5xx / 総リクエスト | 0.1%以下 | |

---

## 8. CI/CD設計

### 8.1 パイプライン構成

| 項目 | 内容 |
|------|------|
| ソースリポジトリ | GitHub（mainブランチ） |
| ビルドサービス | AWS CodeBuild |
| デプロイサービス | AWS CodePipeline + CodeDeploy |
| デプロイ方式 | ECS Blue/Green Deploy |
| コンテナレジストリ | Amazon ECR |
| IaC管理 | Terraform（S3 Backend + DynamoDB Lock） |

### 8.2 デプロイフロー

| 手順 | ステージ | 内容 |
|------|---------|------|
| 1 | Source | GitHubへのPushをトリガーにCodePipelineが起動 |
| 2 | Build | CodeBuildでDockerイメージビルド・ユニットテスト実行 |
| 3 | Push | ECRへイメージをプッシュ（タグ: GitコミットSHA） |
| 4 | Deploy（STG） | STG環境へBlue/Greenデプロイ・スモークテスト |
| 5 | Approval | 本番デプロイの手動承認（Manual Approval） |
| 6 | Deploy（PROD） | 本番環境へBlue/Greenデプロイ |
| 7 | Verify | ヘルスチェック確認・アラート監視 |

---

## 9. バックアップ・DR設計

### 9.1 バックアップ計画

| 対象 | 方法 | 頻度 | 保持期間 |
|------|------|------|---------|
| RDS Aurora | 自動スナップショット | 毎日 | 本番7日 / STG3日 |
| RDS Aurora | 手動スナップショット | リリース前 | 無期限（手動削除） |
| S3 | バージョニング | 変更時 | 90日（ライフサイクル） |
| ECSタスク定義 | Terraformコード管理 | 変更時（Git） | 無期限 |

### 9.2 DR方針

| 項目 | 内容 |
|------|------|
| RTO（目標復旧時間） | 4時間以内 |
| RPO（目標復旧時点） | 1時間以内 |
| DR方式 | バックアップ&リストア（Warm Standby検討） |
| DRリージョン | ap-northeast-3（大阪） |
| 切り替えトリガー | 東京リージョン障害時（AWSサポート確認後） |

---

## 10. コスト設計

### 10.1 月次コスト見積もり（概算）

| サービス | スペック | 月額目安（USD） | 備考 |
|---------|---------|----------------|------|
| ECS Fargate | 0.5vCPU, 1GB × 2タスク | 〜$30 | |
| ALB | 1台 | 〜$20 | |
| RDS Aurora | db.r6g.large × 2 | 〜$250 | Writer + Reader |
| NAT Gateway | 3AZ | 〜$100 | 高コスト要注意 |
| CloudWatch Logs | 〜10GB/月 | 〜$5 | |
| WAF | WebACL + ルール | 〜$10 | |
| **合計（参考）** | | **〜$415 / 月** | 実際の使用量で変動 |

> ※ 上記はあくまで概算です。実際のコストはトラフィック量・データ転送量により大きく変動します。

### 10.2 コスト最適化方針

- AWS Budgets: 月次上限アラート設定（超過80%/100%で通知）
- 開発・STG環境: 夜間・週末はECSタスクをDesired Count=0に設定
- Compute Savings Plans: 本番稼働後1年以上経過したら検討
- NAT Gateway: VPC Endpoint活用でNAT GW経由通信を最小化

---

## 11. 課題・TODO

| No. | 課題・TODO | 担当者 | 期日 | ステータス |
|-----|-----------|--------|------|-----------|
| 1 | 【課題1を記載】 | 【担当者】 | YYYY/MM/DD | 未着手 |
| 2 | 【課題2を記載】 | 【担当者】 | YYYY/MM/DD | 未着手 |
| 3 | 【課題3を記載】 | 【担当者】 | YYYY/MM/DD | 未着手 |

---

## 12. 用語集

| 用語 | 説明 |
|------|------|
| VPC | Virtual Private Cloud。AWS上の仮想ネットワーク環境 |
| ECS | Elastic Container Service。コンテナオーケストレーションサービス |
| Fargate | サーバーレスコンテナ実行環境。EC2管理不要 |
| ALB | Application Load Balancer。L7レイヤーのロードバランサー |
| RDS | Relational Database Service。マネージドRDBサービス |
| WAF | Web Application Firewall。Webアプリへの攻撃を遮断 |
| SLO | Service Level Objective。サービスレベル目標値 |
| SLI | Service Level Indicator。SLO達成状況を測る指標 |
| RTO | Recovery Time Objective。目標復旧時間 |
| RPO | Recovery Point Objective。目標復旧時点 |
| IaC | Infrastructure as Code。インフラをコードで管理 |
