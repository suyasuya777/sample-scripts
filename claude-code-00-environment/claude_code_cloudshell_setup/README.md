# claude_code_cloudshell_setup

VPC CloudShell 上で Claude Code (Bedrock経由) + S3 + EFS 自動マウント環境を構築するためのセットアップスクリプトです。

## 前提作業

スクリプト実行前に、以下の準備を完了させてください。

### 1. Bedrockモデルアクセスの有効化

1. AWSマネジメントコンソールで Bedrock を開く（東京リージョン: ap-northeast-1、またはクロスリージョン推論プロファイルのソースリージョン）
2. 左メニューから「モデルアクセス」を選択
3. 使用する Claude モデル（Opus 4.5 / Sonnet 4.5 / Haiku 4.5 等）へのアクセスをリクエストし、有効化する
4. クロスリージョン推論プロファイル（`jp.anthropic.claude-*` 等）を利用する場合、プロファイルが参照する各リージョンでもモデルアクセスを有効化しておく

### 2. IAM権限の設定

CloudShell実行ロール（またはCloudShellに割り当てるIAMロール）に以下の権限を付与してください。

| サービス | 必要な権限 |
|---|---|
| STS | `sts:GetCallerIdentity` |
| S3 | 対象バケットに対する `s3:ListBucket`, `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` |
| EFS | `elasticfilesystem:DescribeFileSystems`, `elasticfilesystem:ClientMount`, `elasticfilesystem:ClientWrite`, `elasticfilesystem:ClientRootAccess` |
| Bedrock | `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` |

IAMポリシー例:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:GetCallerIdentity",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::<バケット名>",
        "arn:aws:s3:::<バケット名>/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "elasticfilesystem:DescribeFileSystems",
        "elasticfilesystem:ClientMount",
        "elasticfilesystem:ClientWrite",
        "elasticfilesystem:ClientRootAccess"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. CloudShell（VPC環境）の設定

通常のCloudShellはAWS管理VPC上で動作するため、EFSへ到達できません。VPC環境のCloudShellを構成してください。

1. CloudShell画面右上の「アクション」→「VPC環境の作成」を選択
2. EFSと同じVPC、かつEFSのマウントターゲットが存在するサブネットを選択
3. CloudShell用セキュリティグループを選択（後述のEFS用セキュリティグループからのインバウンドを許可するため、専用SGを作成しておくと管理しやすい）
4. VPC環境作成後、CloudShellを起動するとそのVPC環境に接続される

#### インターネットアクセスの確保（公開ツールのインストールに必要）

VPC環境のCloudShellは、選択したVPC/サブネットのルーティングに従って通信するため、デフォルトではインターネットに出られない場合があります。`yum`、`npm install`、`wget`/`curl` などで公開ツール（s3fs-fuse、Claude Code、Playwright等）を取得するには、以下のいずれかを構成してください。

- **NATゲートウェイ経由**: CloudShellが使用するサブネットをプライベートサブネットとし、NATゲートウェイを持つパブリックサブネット経由でインターネットアクセスを確保する
- **VPCエンドポイント**: 必要なAWSサービス（S3, ECR等）へのアクセスのみであれば、Gateway型/Interface型VPCエンドポイントで代替可能（ただしGitHub・npm registry・PyPI等の外部サイトへはNAT/IGWが必要）

未構成の場合、本スクリプトのs3fs-fuseビルドやClaude Codeのnpmインストールに失敗します。

### 4. S3バケット作成

```bash
aws s3 mb s3://<バケット名> --region ap-northeast-1
```

- 作成したバケット名をスクリプト冒頭の `S3_BUCKET` に設定する

### 5. EFS作成（VPC内・マウントターゲット・セキュリティグループ）

1. **EFSファイルシステム作成**
   - EFSコンソールで「ファイルシステムを作成」
   - VPC: CloudShell VPC環境と同じVPCを選択
   - タグに `Billing=ate` を付与（スクリプトの自動検出に使用）

2. **マウントターゲットの作成**
   - CloudShell VPC環境が使用するサブネットごとにマウントターゲットを配置
   - 各マウントターゲットにEFS用セキュリティグループを割り当て

3. **セキュリティグループ設定（NFS/2049許可）**
   - EFS用セキュリティグループのインバウンドルールに以下を追加

   | タイプ | プロトコル | ポート | ソース |
   |---|---|---|---|
   | NFS | TCP | 2049 | CloudShell用セキュリティグループ（またはそのCIDR） |

4. EFS_IDが分かっている場合はスクリプト冒頭の `EFS_ID` に設定（未設定の場合は `Billing=ate` タグで自動検出）

### 6. シェルスクリプトのS3アップロード

CloudShell（VPC環境）から取得できる場所にスクリプトを配置します。

```bash
aws s3 cp setup-claude-code.sh s3://<バケット名>/setup-claude-code.sh
```

CloudShell側での取得・実行例:

```bash
aws s3 cp s3://<バケット名>/setup-claude-code.sh .
source setup-claude-code.sh
```

## スクリプト実行

```bash
source setup-claude-code.sh
```

`source` で実行する必要があります（直接実行するとエラーになります）。

## セットアップ内容

- s3fs-fuse のビルド・インストール
- S3バケットの `/mnt/s3` への自動マウント（`~/s3` シンボリックリンク）
- EFSの `/mnt/efs` への自動マウント（`~/efs` シンボリックリンク）
- Claude Code のインストール（npmグローバルディレクトリを `~/.npm-global` に変更）
- Bedrock経由のClaude Code環境変数設定（`~/.bashrc`, `~/.claude/settings.json`）
- Playwright共有設定（`/mnt/efs/playwright` 利用時）

## トラブルシューティング

- `claude` コマンドが見つからない場合:
  ```bash
  export PATH="${HOME}/.npm-global/bin:${PATH}"
  source ~/.bashrc
  ```
- Bedrock認証確認:
  ```bash
  claude auth status
  ```
- EFSマウント失敗時:
  - CloudShellがVPC環境に接続されているか確認
  - EFS用セキュリティグループでNFS(2049)がCloudShellからのアクセスを許可しているか確認
- `yum install` / `npm install` / `wget` が失敗する場合:
  - VPCにNATゲートウェイまたはインターネットゲートウェイ経由の通信路があるか確認
  - 必要なVPCエンドポイント（S3, ECR等）が作成されているか確認
- CloudShellのストレージ容量(`/dev/loop0`)が不足する場合:
  - 大きいツール・データは `/mnt/efs` または `/mnt/s3` 配下に配置する
