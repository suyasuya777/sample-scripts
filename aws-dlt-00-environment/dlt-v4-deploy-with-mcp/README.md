# 📘 DLT（v4 系・MCP 対応）新規構築 & Claude Code 分析 セットアップ手順書

Distributed Load Testing on AWS（DLT）を **v4 系で新規にデプロイ**し、同梱の **MCP Server** を有効化して、負荷テストの結果データを **Claude Code** から分析できるようにするための手順書です。既存環境のアップグレードではなく、**ゼロからの構築**を前提とします。

> 凡例（見出しレベルと絵文字）
> 📘 = 大見出し（h1） / 🧰 = フェーズ（h2） / ⚙️ = 手順セクション（h3） / 📍 = 作業ステップ（h4）

---

## 🧰 前提とゴール

- **構成**: 東京リージョン（`ap-northeast-1`）に DLT v4 系を新規デプロイ
- **ゴール**: 新規構築 → MCP Server を有効化 → Claude Code から結果データを分析
- **重要な前提**:
  - 東京リージョン（`ap-northeast-1`）は **MCP Server（AgentCore Gateway）対応リージョン**なので、東京にそのまま構築できます。
  - ホスティングは標準の **CloudFront + S3** を使用します（最も導入が簡単な既定構成）。
  - MCP Server のツールは**読み取り専用**（テストの作成・実行・変更は不可。分析専用）。
  - 新規構築のため、既存データの移行やバックアップは不要です。

### ⚙️ 全体の流れ

1. 事前確認（リージョン・権限）
2. テンプレートの準備（CloudFront + S3）
3. **新規デプロイ（Create stack ＋ パラメータ設定）★詳細あり**
4. MCP Server オプションの有効化
5. デプロイ実行と完了確認
6. 初回ログイン（メール受信 → ワンタイムパスワード → パスワード変更）
7. MCP エンドポイント＆トークンの取得
8. Claude Code へ登録
9. 動作確認と分析

---

## 🧰 1. 事前確認

### ⚙️ 1-1. リージョンと前提の確認

- デプロイ先は **東京（ap-northeast-1）**。AgentCore Gateway 対応リージョンであり、MCP Server を有効化できます。
- 本ソリューションは Amazon Cognito を使うため、Cognito 利用可能リージョンであること（東京は対応）。
- デプロイには **CloudFormation でスタックを作成し、IAM リソースを作成できる権限**が必要です。

### ⚙️ 1-2. 管理者メールの用意

- デプロイ時に **管理者ユーザー名**と**管理者メールアドレス**を指定します。
- デプロイ後、この**メールアドレス宛にログイン情報（ユーザー名・ワンタイムパスワード・コンソール URL）が届く**ので、受信できるアドレスを用意します。

---

## 🧰 2. テンプレートの準備

### ⚙️ 2-1. 使用するテンプレートの S3 URL

ホスティングオプションごとに、公式テンプレートが以下の URL で公開されています（`latest` は常に最新版＝ v4 系）。

| ホスティング方式 | テンプレート S3 URL |
| --- | --- |
| **CloudFront + S3（← 今回これを使用）** | `https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws.template` |
| ALB + ECS on Fargate | `https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws-alb-ecs.template` |
| Headless | `https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws-headless.template` |

- **今回使う URL（CloudFront + S3）**:
  ```
  https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws.template
  ```
- ※ 制限ネットワーク向けの ALB + ECS、完全プライベートの Headless もありますが、まず標準構成で構築するなら CloudFront + S3 を選びます。
- ※ 最新の URL は公式ページからも取得できます: `https://aws.amazon.com/solutions/implementations/distributed-load-testing-on-aws/`

---

## 🧰 3. 新規デプロイ（Create stack ＋ パラメータ設定）

### ⚙️ 3-1. CloudFormation で新規スタックを作成

1. **東京リージョン（ap-northeast-1）** で AWS マネジメントコンソールにサインインします。
   - ※ 公式の起動ボタンはデフォルトで us-east-1 が選ばれることがあります。**必ず右上のリージョンセレクタで東京に切り替えて**ください。
2. **CloudFormation** を開き、**Create stack（スタックの作成）→ With new resources（新しいリソースを使用）** を選びます。
3. **Prerequisite - Prepare template** は **Template is ready（テンプレートの準備完了）** のままにします。
4. **Specify template** で **Amazon S3 URL** を選択し、2-1 の CloudFront + S3 テンプレート URL を貼り付けます。
   ```
   https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws.template
   ```
5. URL が正しく入っていることを確認し、**Next（次へ）** をクリックします。

### ⚙️ 3-2. スタック名とパラメータの設定

6. **Specify stack details** で、**Stack name（スタック名）** を入力します（例: `distributed-load-testing`）。
7. **Parameters** で、少なくとも以下を設定します（その他は基本デフォルトで可）。
   - **Administrator Name**: 初期管理者のユーザー名（スペースなし）。
   - **Administrator Email**: 管理者メール。**ここにログイン情報が届きます。**
   - **MCP Server 有効化パラメータ**: 次項「4」で Yes に設定。
   - **Automatic updates**: `No` ならバージョン固定、`Yes` なら同一マイナー内の更新を自動適用。運用ポリシーに合わせて選びます。
8. **Next** をクリックします。

---

## 🧰 4. MCP Server オプションの有効化

- 3-2 のパラメータ画面で、**MCP Server を有効化するパラメータ**（例: "Enable MCP Server" のような項目）を **Yes / true** に設定します。
  - ※ 正確なパラメータ名は最新テンプレートの表示に従ってください。MCP Server / AgentCore に関する項目を有効化します。
- 東京リージョンは AgentCore Gateway 対応のため、この有効化がそのまま機能します。
- 有効化すると、AgentCore Gateway や MCP Server 用 Lambda などのリソースが追加で作成されます。

---

## 🧰 5. デプロイの実行と完了確認

1. **Configure stack options** 画面はそのまま **Next** で進みます（必要に応じてタグ等を設定）。
2. **Review** 画面で内容を確認し、**IAM リソースを作成する旨のチェックボックス**にチェックを入れます。
3. **Create stack（スタックの作成）** をクリックします。
4. CloudFormation の Status 列で進捗を確認します。**CREATE_COMPLETE** になれば完了です（目安 15 分前後）。
5. 完了後、スタックの **Outputs** タブの **Console** に Web コンソール URL が出力されます（後述のメールにも含まれます）。

---

## 🧰 6. 初回ログイン

1. デプロイ完了後、**3-2 で指定した管理者メール宛にメールが届きます**（ユーザー名・ワンタイムパスワード・コンソール URL）。
2. メール内の **コンソール URL** を開きます（CloudFormation の Outputs の `Console` と同じ）。
3. ユーザー名と**ワンタイムパスワード**でサインインします。
4. 初回ログイン時に、**新しいパスワードへの変更**を求められるので設定します。
5. ログインできれば、Web コンソールから負荷テストのシナリオ作成・実行ができます。

---

## 🧰 7. MCP エンドポイントとアクセストークンの取得

1. DLT の **Web コンソール**にログインします。
2. 上部メニューから **MCP Server** ページを開きます。
3. **MCP Server Endpoint** セクションで **Copy Endpoint URL** をクリックし、エンドポイント URL をコピーします。
   - 形式の例: `https://{gateway-id}.gateway.bedrock-agentcore.ap-northeast-1.amazonaws.com/mcp`
   - ※ 正しい URL はコンソールが表示するものをそのままコピーするのが確実です。
4. **Access Token** セクションで **Copy Access Token** をクリックし、トークンをコピーします。
   - このトークンは **読み取り専用**アクセス用です。**公開しない**でください。
   - OAuth トークンのため**有効期限があります**（期限切れ時の対応は「補足」参照）。

---

## 🧰 8. Claude Code への登録

ターミナルで以下を実行し、DLT MCP Server をリモート HTTP サーバーとして登録します。

```bash
claude mcp add --transport http dlt-mcp \
  "<7 でコピーしたエンドポイントURL>" \
  --header "Authorization: Bearer <7 でコピーしたアクセストークン>"
```

- `--transport` や `--header` などのオプションは**サーバー名（dlt-mcp）より前**に置きます。
- どのディレクトリからでも使いたい場合は `--scope user` を付けます（付けない場合は登録したプロジェクトでのみ有効）。
- 登録内容は `claude mcp list` で確認できます。

---

## 🧰 9. 動作確認と分析

### ⚙️ 9-1. 接続確認

- Claude Code 内で `/mcp` を実行し、`dlt-mcp` の接続状態を確認します。
- `list_scenarios` を呼んでシナリオ一覧が返れば接続成功です（トークン有効で `connected` 表示）。

### ⚙️ 9-2. 利用できる主なツール（読み取り専用）

- `list_scenarios` — 全テストシナリオの一覧
- `get_scenario_details` — あるシナリオの設定と直近の実行
- `list_test_runs` — 特定シナリオの実行履歴（新しい順）
- `get_test_run` — 個別実行の応答時間・スループット・エラー率などの詳細

### ⚙️ 9-3. 分析プロンプト例

```text
対象シナリオを list_scenarios で一覧化し、直近 5 回の test_run について
get_test_run で応答時間（p50/p90/p99）・スループット・エラー率を取得して、
回ごとの推移を表にまとめ、悪化している指標があれば原因の仮説を挙げて。
```

> ※ MCP Server で分析するには、先に Web コンソールでシナリオを作成・実行し、結果データを蓄積しておく必要があります（新規構築直後はデータが空のため）。

---

## 🧰 補足: トークン期限の運用

AgentCore Gateway のアクセストークン（Cognito OAuth）は有効期限があります。`--header` に静的に書くと、期限切れ後に接続が失敗します。対処は次のいずれかです。

- **環境変数で渡す**: `.mcp.json` の環境変数展開（`${DLT_MCP_TOKEN}` 等）を使い、`headers.Authorization` を環境変数から読む。
  ```json
  {
    "mcpServers": {
      "dlt-mcp": {
        "type": "http",
        "url": "${DLT_MCP_ENDPOINT}",
        "headers": { "Authorization": "Bearer ${DLT_MCP_TOKEN}" }
      }
    }
  }
  ```
- **headersHelper で動的生成（推奨）**: 短命トークン向けに、トークンを取得して出力するスクリプト（Cognito から取得）を `headersHelper` に指定し、接続時に毎回ヘッダーを生成させる。貼り直しの手間がなくなります。

---

## 🧰 注意事項まとめ

- 新規構築なので、**Create stack**（Update ではない）。テンプレートは **CloudFront + S3** を使用。
- デプロイは**東京リージョン**で行う（起動時に us-east-1 になりやすいので要切り替え）。
- 管理者メールにログイン情報が届く → **初回ログインでパスワード変更**。
- MCP Server は**読み取り専用**。テストの作成・実行は Web コンソール / REST API / CLI で行う。
- 構築直後は結果データが空。MCP 分析の前に、まずシナリオを作成・実行してデータを溜める。
- 複数リージョンでテストを回す場合は、Web コンソールの「Manage Regions」からリージョナルスタックを追加デプロイする。

---

## 🧰 参考リンク

- ソリューション ページ（テンプレート URL の入手元）: https://aws.amazon.com/solutions/implementations/distributed-load-testing-on-aws/
- 実装ガイド（Solution overview）: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/solution-overview.html
- スタックのデプロイ手順（Launch the stack）: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/launch-the-stack.html
- MCP Server 連携: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/mcp-server-integration.html
- 対応リージョン（Plan your deployment）: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/plan-your-deployment.html
- GitHub リポジトリ: https://github.com/aws-solutions/distributed-load-testing-on-aws
- Claude Code の MCP 設定: https://docs.claude.com/en/docs/claude-code/mcp
