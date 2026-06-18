# 📘 DLT 結果データを Claude Code で分析する セットアップ手順書

Distributed Load Testing on AWS（DLT）を **v3.4.5 → v4 系** へアップグレードし、同梱の **MCP Server** を有効化して、負荷テストの結果データを **Claude Code** から分析できるようにするための手順書です。

> 凡例（見出しレベルと絵文字）
> 📘 = 大見出し（h1） / 🧰 = フェーズ（h2） / ⚙️ = 手順セクション（h3） / 📍 = 作業ステップ（h4）

---

## 🧰 前提とゴール

- **現状**: DLT `v3.4.5` を東京リージョン（`ap-northeast-1`）で運用中
- **ゴール**: v4 系へアップグレード → MCP Server を有効化 → Claude Code から結果データを分析
- **重要な前提**:
  - 東京リージョン（`ap-northeast-1`）は **MCP Server（AgentCore Gateway）対応リージョン**のため、**リージョン移動は不要**
  - スタック更新（in-place update）のため、既存のテストシナリオ・結果データ（DynamoDB / S3）は**保持される**
  - `v3.4.5` は `v3.3.0` 以降なので、**標準のアップデート手順**が使える（旧版特有の追加作業は不要）
  - MCP Server のツールは**読み取り専用**（テストの作成・実行・変更は不可。分析専用）

### ⚙️ 全体の流れ

1. 事前確認（バージョン・リージョン・ホスティング方式）
2. 事前準備（テスト停止・バックアップ・changeset 確認）
3. **v4 へアップグレード（テンプレート S3 URL の差し替え）★詳細あり**
4. MCP Server オプションの有効化
5. 更新後の確認とログイン
6. MCP エンドポイント＆トークンの取得
7. Claude Code へ登録
8. 動作確認と分析

---

## 🧰 1. 事前確認

### ⚙️ 1-1. 現在のバージョンとスタックを確認

```bash
# 対象スタック名がわかっている場合（Description にバージョンが入る）
aws cloudformation describe-stacks \
  --region ap-northeast-1 \
  --stack-name <あなたのDLTスタック名> \
  --query "Stacks[0].Description" --output text

# スタック名がうろ覚えなら一覧から探す
aws cloudformation describe-stacks \
  --region ap-northeast-1 \
  --query "Stacks[].{Name:StackName,Desc:Description}" --output table
```

- Description に `(SO0062) ... Version v3.4.5` のように表示されることを確認します。

### ⚙️ 1-2. ホスティング方式を確認

- `v3.4.5`（v3 系）は **CloudFront + S3** ホスティングが標準です。
- 本手順でも同じ **CloudFront + S3** テンプレートでアップグレードします（方式を変えない方が更新がスムーズ）。
- ※ v4 で追加された **ALB + ECS** や **Headless** に「乗り換える」場合はホスティング構成の変更を伴うため、本手順の対象外（別途検討）とします。

---

## 🧰 2. 事前準備

メジャーバージョンアップ（v3 → v4）のため、本番スタックでは以下を必ず実施します。

### ⚙️ 2-1. 実行中テストの停止

- 更新中は一時的に可用性が落ちる可能性があります。**実行中の負荷テストがない状態**にしてから進めます。

### ⚙️ 2-2. バックアップの担保

- **DynamoDB**: 対象テーブル（シナリオ・結果）で **ポイントインタイムリカバリ（PITR）** が有効か確認します。
- **S3**: 結果・シナリオ格納バケットの **バージョニング**状況を確認します。
- 必要に応じて、更新前にエクスポート／スナップショットを取得します。

### ⚙️ 2-3. 変更セット（changeset）で差分を事前確認

- いきなり更新を流さず、まず changeset を作成して差分（置き換え・削除されるリソース）を確認します。
- 操作は「3. アップグレード」の画面で **View change set** から実行できます（後述）。

---

## 🧰 3. v4 へアップグレード（テンプレート S3 URL の差し替え）

> ★ ご要望の「S3 URL に差し替えるところ」を詳しく記載します。

### ⚙️ 3-1. 使用する最新テンプレートの S3 URL

AWS Solutions の公式テンプレートは、ホスティングオプションごとに以下の URL で公開されています（`latest` は常に最新版を指します）。

| ホスティング方式 | テンプレート S3 URL |
| --- | --- |
| **CloudFront + S3（← 今回これを使用）** | `https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws.template` |
| ALB + ECS on Fargate | `https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws-alb-ecs.template` |
| Headless | `https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws-headless.template` |

- **今回使う URL（CloudFront + S3）**:
  ```
  https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws.template
  ```
- ※ 既存が CloudFront + S3 構成のため、**必ず CloudFront + S3 のテンプレート**（`...-alb-ecs` や `...-headless` が付かないもの）を選びます。別方式のテンプレートを当てると、ホスティング構成が変わり更新が破綻する恐れがあります。
- ※ 最新の URL は公式ページの「Deployment tools → CloudFormation templates」からも取得できます: `https://aws.amazon.com/solutions/implementations/distributed-load-testing-on-aws/`

### ⚙️ 3-2. CloudFormation コンソールでテンプレートを差し替える

1. **東京リージョン（ap-northeast-1）** で AWS マネジメントコンソールにサインインします。
2. **CloudFormation** を開き、既存の DLT スタックを選択し、右上の **Update stack（スタックの更新）** をクリックします。
3. **Prepare template** で **Make a direct update（直接更新する）** を選択します。
4. **Template source（テンプレートソース）** で **Replace existing template（既存テンプレートを置き換える）** を選択します。
   - ※ ここで「Use existing template（既存テンプレートを使用）」を選ぶと差し替えになりません。**必ず Replace existing template** を選びます。
5. 表示された **Amazon S3 URL** を選択します（"Upload a template file" ではなく **Amazon S3 URL**）。
6. **Amazon S3 URL** のテキストボックスに、3-1 の CloudFront + S3 テンプレート URL を貼り付けます。
   ```
   https://solutions-reference.s3.amazonaws.com/distributed-load-testing-on-aws/latest/distributed-load-testing-on-aws.template
   ```
7. URL が正しく入っていることを確認し、**Next（次へ）** をクリックします。

### ⚙️ 3-3. パラメータの確認・設定

8. **Parameters（パラメータ）** 画面で、既存パラメータを確認します。基本は既存値を維持しつつ、次項「4. MCP Server オプションの有効化」を設定します。
   - 併せて、コンテナの自動更新設定（Automatic updates）も確認します。`No` ならバージョン固定、`Yes` なら同一マイナー内の更新が自動適用されます。運用ポリシーに合わせて選びます。
9. **Next** をクリックします。

---

## 🧰 4. MCP Server オプションの有効化

- 3-3 のパラメータ画面で、**MCP Server を有効化するパラメータ**（例: "Enable MCP Server" のような項目）を **Yes / true** に設定します。
  - ※ 正確なパラメータ名は最新テンプレートの表示に従ってください。MCP Server / AgentCore に関する項目を有効化します。
- 東京リージョンは AgentCore Gateway 対応のため、この有効化がそのまま機能します。
- このオプションを有効にすると、AgentCore Gateway + MCP Server 用 Lambda などのリソースが追加で作成されます。

---

## 🧰 5. 更新の実行と更新後の確認

### ⚙️ 5-1. 更新の実行

1. **Configure stack options** 画面はそのまま **Next** で進みます。
2. **Review** 画面で内容を確認し、**IAM リソースを作成する旨のチェックボックス**にチェックを入れます。
3. **View change set** を開き、変更内容（追加・置換・削除されるリソース）を確認します。← 2-3 の差分確認はここで実施。
4. 問題なければ **Update stack** を実行します。
5. CloudFormation コンソールの Status 列で進捗を確認し、**UPDATE_COMPLETE** になれば完了です（目安 15 分前後）。

### ⚙️ 5-2. ログイン確認（Cognito の変更に注意）

- v4 では認証が **Cognito Hosted UI** に変わります。
- 更新後にログインで認証エラーが出たら、**ブラウザのキャッシュをクリア**して再試行します。
  - Windows / Linux: `Ctrl + Shift + R`
  - Mac: `Cmd + Shift + R`

---

## 🧰 6. MCP エンドポイントとアクセストークンの取得

1. DLT の **Web コンソール**にログインします。
2. 上部メニューから **MCP Server** ページを開きます。
3. **MCP Server Endpoint** セクションで **Copy Endpoint URL** をクリックし、エンドポイント URL をコピーします。
   - 形式の例: `https://{gateway-id}.gateway.bedrock-agentcore.ap-northeast-1.amazonaws.com/mcp`
   - ※ 正しい URL はコンソールが表示するものをそのままコピーするのが確実です。
4. **Access Token** セクションで **Copy Access Token** をクリックし、トークンをコピーします。
   - このトークンは **読み取り専用**アクセス用です。**公開しない**でください。
   - OAuth トークンのため**有効期限があります**（期限切れ時の対応は「補足」参照）。

---

## 🧰 7. Claude Code への登録

ターミナルで以下を実行し、DLT MCP Server をリモート HTTP サーバーとして登録します。

```bash
claude mcp add --transport http dlt-mcp \
  "<6 でコピーしたエンドポイントURL>" \
  --header "Authorization: Bearer <6 でコピーしたアクセストークン>"
```

- `--transport` や `--header` などのオプションは**サーバー名（dlt-mcp）より前**に置きます。
- 登録内容は `claude mcp list` で確認できます。

---

## 🧰 8. 動作確認と分析

### ⚙️ 8-1. 接続確認

- Claude Code 内で `/mcp` を実行し、`dlt-mcp` の接続状態を確認します。
- `list_scenarios` を呼んでシナリオ一覧が返れば接続成功です。

### ⚙️ 8-2. 利用できる主なツール（読み取り専用）

- `list_scenarios` — 全テストシナリオの一覧
- `get_scenario_details` — あるシナリオの設定と直近の実行
- `list_test_runs` — 特定シナリオの実行履歴（新しい順）
- `get_test_run` — 個別実行の応答時間・スループット・エラー率などの詳細

### ⚙️ 8-3. 分析プロンプト例

```text
対象シナリオを list_scenarios で一覧化し、直近 5 回の test_run について
get_test_run で応答時間（p50/p90/p99）・スループット・エラー率を取得して、
回ごとの推移を表にまとめ、悪化している指標があれば原因の仮説を挙げて。
```

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

- 既存が CloudFront + S3 のため、アップグレードでも **CloudFront + S3 テンプレート**を使用（方式を変えない）。
- v3 → v4 はメジャーアップ。**実行中テスト停止 → バックアップ → changeset 確認 → 更新**の順を守る。
- MCP Server は**読み取り専用**。テストの作成・実行は従来どおり Web コンソール / REST API / CLI で行う。
- 複数リージョンでテストを回している場合は、ハブ（メイン）スタックを先に更新し、リージョナルスタックは再デプロイが必要（シングルリージョン運用なら不要）。

---

## 🧰 参考リンク

- ソリューション ページ（テンプレート URL の入手元）: https://aws.amazon.com/solutions/implementations/distributed-load-testing-on-aws/
- 実装ガイド（Solution overview）: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/solution-overview.html
- ソリューションの更新手順: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/update-the-solution.html
- MCP Server 連携: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/mcp-server-integration.html
- 対応リージョン（Plan your deployment）: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/plan-your-deployment.html
- GitHub リポジトリ: https://github.com/aws-solutions/distributed-load-testing-on-aws
- Claude Code の MCP 設定: https://docs.claude.com/en/docs/claude-code/mcp
