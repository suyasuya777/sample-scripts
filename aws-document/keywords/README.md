# AWS 用語まとめ

## 1. コンピューティング

### EC2
- **オンデマンド ⇔ リザーブド ⇔ スポット**（料金モデル。スポットは中断あり・最安）
- **EBS ⇔ インスタンスストア**（永続 ⇔ 一時・揮発性）
- **接続方法**：SSH / Session Manager（本番はSession Manager）

### Lambda
- **ZIP形式 ⇔ コンテナイメージ形式**（デプロイパッケージ。250MB ⇔ 10GB）
- **呼び出しタイプ**：同期 / 非同期 / イベントソースマッピング
  - 同期(RequestResponse) … 応答を待つ（プッシュ）→ **API Gateway / ALB / 手動実行(CLI)**
  - 非同期(Event) … 投げっぱなし（プッシュ）→ **S3イベント / SNS / EventBridge**
  - イベントソースマッピング(ポーリング) … Lambda側が取りに行く → **SQS / Kinesis Data Streams / DynamoDB Streams**
- **コールドスタート ⇔ ウォームスタート**（対策＝プロビジョニング済み同時実行）
- **予約済み同時実行 ⇔ プロビジョニング済み同時実行**（上限確保 ⇔ 事前ウォーム）
  - プロビジョニング済み同時実行は **Application Auto Scaling** で時間帯・スケジュール別に増減可（例：日中10個／夜間0個）

---

## 2. コンテナ（ECS/ECR）

### ECS
- **ECSサービス ⇔ スタンドアロンタスク（RunTask）**（常駐 ⇔ 非常駐）
- **起動タイプ：Fargate ⇔ EC2**（サーバレス ⇔ 自前インスタンス管理）
- **スケジューリング戦略：REPLICA ⇔ DAEMON**（指定数維持 ⇔ 全ホストに1つ／EC2限定）
- **構築順**：クラスタ → タスク定義 → サービス（依存順）
- **コントロールプレーン ⇔ データプレーン**（頭脳＝ECS ⇔ 実行環境＝Fargate/EC2）
- **起動方法**：サービス / スタンドアロン / スケジュールド / カスタムスケジューラ

### ECR
- **プライベート pull**：`ecr.api` / `ecr.dkr` / `S3(Gateway)`
- **プライベートリポジトリ ⇔ パブリックリポジトリ**

---

## 3. ストレージ

### S3
- **バケット ⇔ オブジェクト**（入れ物 ⇔ 中身）
- **ストレージクラス**：Standard / IA(低頻度) / Glacier(アーカイブ)
- **暗号化**：SSE-S3 / SSE-KMS / SSE-C（鍵の管理主体で区別）
- **アクセス制御：バケットポリシー ⇔ IAMポリシー ⇔ ACL**（推奨はポリシー、ACLは非推奨寄り）

### ストレージ種別の対比
- **EBS ⇔ EFS ⇔ S3**：ブロック(1台) / ファイル(複数共有・NFS) / オブジェクト(HTTP)

---

## 4. データベース

### RDS / Aurora
- **マルチAZ ⇔ リードレプリカ**（可用性・同期 ⇔ 性能・非同期）
- **RDS ⇔ Aurora**（標準エンジン ⇔ AWS最適化・高性能）
- **プロビジョンド ⇔ サーバーレス(Aurora Serverless)**

### DynamoDB
- **RDS(RDB) ⇔ DynamoDB(NoSQL)**
- **パーティションキー ⇔ ソートキー**（分散先の決定 ⇔ 範囲内の並び）
- **オンデマンド ⇔ プロビジョンド**（キャパシティモード）

---

## 5. ネットワーク（VPC）

### VPC 基本
- **パブリックサブネット ⇔ プライベートサブネット**（IGWへの経路の有無）
- **IGW ⇔ NAT Gateway**（双方向・パブリック ⇔ 外向き専用・プライベート）
- **ネットワーク制御【3層】**：ルートテーブル / NACL / セキュリティグループ

### セキュリティグループ / NACL
- **セキュリティグループ ⇔ NACL**
  - SG：ステートフル・ENI単位・許可のみ
  - NACL：ステートレス・サブネット単位・許可/拒否

### VPCエンドポイント
- **Gateway型 ⇔ Interface型**（S3/DynamoDBのみ・無料 ⇔ その他・有料PrivateLink）
- **SSM接続**：`ssm` / `ssmmessages` / `ec2messages`
- **ECR pull**：`ecr.api` / `ecr.dkr` / `S3(Gateway)`

---

## 6. 負荷分散・配信・DNS

### ELB
- **ALB(L7) ⇔ NLB(L4) ⇔ GWLB(L3)**（HTTP制御 / 高速TCP / 仮想アプライアンス）
- **リスナー ⇔ ターゲットグループ**（受口 ⇔ 振り分け先）

### CloudFront
- **オリジン ⇔ エッジロケーション**（配信元 ⇔ キャッシュ拠点）
- **CloudFront ⇔ Global Accelerator**（コンテンツ配信 ⇔ 経路最適化）

### Route 53
- **パブリックホストゾーン ⇔ プライベートホストゾーン**
- **ルーティングポリシー**：シンプル / 加重 / レイテンシ / フェイルオーバー / 位置情報

---

## 7. 認証・セキュリティ

### IAM
- **ユーザー ⇔ ロール**（永続的な人 ⇔ 一時的に引き受ける権限）
- **アイデンティティベース ⇔ リソースベース**（誰に付与 ⇔ 何に付与）
- **信頼ポリシー ⇔ 許可ポリシー**（AssumeRoleの可否 ⇔ できる操作）
- **ポリシー要素**：誰が(Principal) / 何に(Resource) / 何を(Action)
- **マネージドポリシー ⇔ インラインポリシー**

### 機密情報管理
- **KMS ⇔ Secrets Manager ⇔ Parameter Store**
  - KMS：暗号鍵そのものの管理
  - Secrets Manager：機密情報・自動ローテーション有・有料
  - Parameter Store：設定値/パラメータ・SecureString可・基本無料

### 脅威・脆弱性検知
- **GuardDuty ⇔ Inspector ⇔ Macie ⇔ Security Hub**
  - GuardDuty：脅威検知（不審な挙動）
  - Inspector：脆弱性スキャン（EC2/コンテナ/Lambda）
  - Macie：S3の機密データ検出
  - Security Hub：上記を統合・一元管理

### 境界防御
- **WAF(L7) ⇔ Shield(L3/4・DDoS)**（アプリ層 ⇔ ネットワーク層）

### Cognito
- **ユーザープール ⇔ IDプール**（認証＝サインイン ⇔ 認可＝AWS一時credential）
- **認証(Authentication) ⇔ 認可(Authorization)**

---

## 8. 監視・可観測性（CloudWatch）

### 基本
- **可観測性の三本柱**：メトリクス / ログ / トレース
- **基本機能【4点】**：Metrics / Logs / Alarms / Dashboards
- **標準メトリクス ⇔ カスタムメトリクス**
- **Logs ⇔ Logs Insights**（保存 ⇔ クエリ分析）

### 外形・アプリ監視
- **Synthetics ⇔ RUM**（合成監視・Canary ⇔ 実ユーザー監視）
- **Container Insights ⇔ Application Signals**（コンテナ資源 ⇔ SLO/SLI・APM）
- **X-Ray / ServiceLens**（分散トレーシング）

---

## 9. メッセージング・連携

- **SQS ⇔ SNS**（キュー・ポーリング・1対1 ⇔ Pub/Sub・プッシュ・1対多）
- **SQS標準 ⇔ SQS FIFO**（順序保証なし・高速 ⇔ 順序保証・重複排除）
- **用途の使い分け【3点】**：SQS(バッファ) / SNS(通知) / EventBridge(イベントルーティング)
- **Step Functions ⇔ EventBridge**（ワークフロー制御 ⇔ イベントバス）

---

## 10. IaC・CI/CD

### IaC
- **CloudFormation ⇔ Terraform**（AWSネイティブ ⇔ マルチクラウド・HCL）
- **CDK ⇔ CloudFormation**（プログラミング言語 ⇔ YAML/JSON）

### CI/CD（Code シリーズ）
- **Code シリーズ**：CodeBuild(ビルド) / CodeDeploy(デプロイ) / CodePipeline(全体統合)
- **デプロイ戦略**：ローリング / Blue-Green / カナリア
