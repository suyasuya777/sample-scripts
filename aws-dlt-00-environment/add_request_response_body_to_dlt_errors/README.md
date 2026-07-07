# 📘 Claude + S3 MCP サーバー連携 実行ガイド

Claude（claude.ai）に S3 MCP サーバーを接続し、**DLT が S3 に出力した結果ファイルを Claude から取得・分析できる状態**を、初めての人が一通り作るための手順書です。まずは「連携が動く」ことをゴールに、最小構成・小規模で通します。動いた先の活用例として、リクエスト/レスポンスボディを使ったエラー原因分析も扱います。

> 凡例: 🧰 = フェーズ / ⚙️ = 手順セクション / 📍 = 作業ステップ
>
> ※ はじめての実行を想定し、最小構成・小規模で進めます。S3 のパスは load-test.sh の実際の挙動（UUID を含む動的キー）に合わせています。

---

## 🧰 このガイドのゴールと背景

**ゴール**: Claude に S3 MCP サーバーを接続し、DLT が S3 に出力した結果（特に詳細結果 `results-detail.jtl`）を Claude から取得・分析できる状態を作ること。

**背景**: DLT が S3 に出力する標準の JMeter 結果には、エラー率・レスポンスタイムは含まれますが、**リクエスト/レスポンスボディが含まれない**ため、エラー原因の特定が困難です。本ガイドでは、詳細結果（ボディ込み）を S3 に出して、Claude から読めるようにします。

---

## 🧰 解決方針

JMeter 実行時のエラー詳細（リクエスト/レスポンスボディ）をコンテナ内に記録し、DLT 標準の load-test.sh が S3 に自動アップロードしたファイルを、Claude が S3 MCP サーバー経由で取得・分析します。

```
JMeter 実行（ECS Fargate / Taurus 経由）
    ↓  JMX のリスナーが詳細結果を出力（例: /tmp/results-detail.jtl）
load-test.sh の既存処理が S3 に自動アップロード   ← Dockerfile 改修は原則不要
    ↓  実際のキー: results/<test-id>/JMeter_Result/<prefix>/<uuid>/tmp/results-detail.jtl
Claude（claude.ai）が S3 MCP サーバー経由で取得して分析
```

> ⚠️ 重要（当初版からの修正点）
> - アップロード先は**固定パスではなく、UUID を含む動的なキー**になります。
> - そのため Claude へは「固定パスを取得」ではなく「**該当 test-id のプレフィックス配下を List して、詳細 JTL を見つけて取得**」と指示します（後述）。

---

## 🧰 仕組み（load-test.sh の挙動）

load-test.sh は、JMX 内の `filename` タグを検出して、その出力ファイルを S3 にアップロードします。要点は次のとおりです。

- JMX から `filename` を含む行を抽出し、`<stringProp name="filename">` と閉じタグを除去、さらに**空白を全削除**してパスを得る。
- 得たパス `$f` のローカルファイルを、次のキーでアップロードする。
  - 相対パスの場合: `s3://<bucket>/results/<test-id>/JMeter_Result/<prefix>/<uuid>/<f>`
  - 絶対パス（`/` 始まり）の場合: `s3://<bucket>/results/<test-id>/JMeter_Result/<prefix>/<uuid><f>`
- アップロードは `aws s3 cp <ローカルパス> <S3キー>` で行うため、**ローカルにそのファイルが実在している**ことが前提。

この挙動は v3 系・v4 系で本質的に共通です（v4 へアップグレードしても仕組みは同じ）。

---

## 🧰 事前作業 1: JMX ファイルへのリスナー追加

リクエスト/レスポンスボディを記録するため、JMX に SimpleDataWriter リスナーを追加します。`filename` タグの記載により load-test.sh が自動で S3 にアップロードします。

### ⚙️ 1-1. 追加する XML

> **挿入位置**: `</jmeterTestPlan>` の直前ではなく、**Test Plan の hashTree が閉じる直前**（最後の ThreadGroup とその `<hashTree>` の後）に、`<ResultCollector>…</ResultCollector>` と対の `<hashTree/>` を**セットで**挿入します。手で位置を合わせるのが不安なら、JMeter GUI で対象 JMX を開き、Test Plan を右クリック →「Add → Listener → Simple Data Writer」で追加すると、構造が自動的に正しくなります。
>
> **初回実行のコツ**: はじめてなので `error_logging=true`（エラーのみ記録）で小さく始めます。ただしこの設定では**エラーが 0 件だとファイルが生成されません**。初回は、わざと失敗するリクエスト（存在しない URL や不正なパラメータ等）を 1 ケース含めるか、確実にエラーが出る条件で実行して、ファイルが S3 に出ることを確認します。
>
> **当初版からの主な修正点**: フィールド名を JMeter 正式名に修正（`responseCode`→`code`、`responseMessage`→`message`、`requestData`→`samplerData`）／`enabled="true"` を追加／対の `<hashTree/>` を追加。

```xml
<ResultCollector guiclass="SimpleDataWriter"
                 testclass="ResultCollector"
                 testname="error-detail-writer"
                 enabled="true">
  <boolProp name="ResultCollector.error_logging">true</boolProp>  <!-- エラーのみ記録 -->
  <objProp>
    <name>saveConfig</name>
    <value class="SampleSaveConfiguration">
      <time>true</time>
      <latency>true</latency>
      <timestamp>true</timestamp>
      <success>true</success>
      <label>true</label>
      <code>true</code>                <!-- レスポンスコード -->
      <message>true</message>          <!-- レスポンスメッセージ -->
      <threadName>true</threadName>
      <dataType>true</dataType>
      <encoding>false</encoding>
      <assertions>true</assertions>
      <subresults>true</subresults>
      <responseData>true</responseData>   <!-- レスポンスボディ -->
      <samplerData>true</samplerData>     <!-- リクエストボディ -->
      <xml>true</xml>
      <fieldNames>true</fieldNames>
      <responseHeaders>true</responseHeaders>
      <requestHeaders>true</requestHeaders>
      <responseDataOnError>false</responseDataOnError>
      <saveAssertionResultsFailureMessage>false</saveAssertionResultsFailureMessage>
      <assertionsResultsToSave>0</assertionsResultsToSave>
      <bytes>true</bytes>
      <sentBytes>true</sentBytes>
      <url>true</url>
      <threadCounts>true</threadCounts>
      <idleTime>true</idleTime>
      <connectTime>true</connectTime>
    </value>
  </objProp>
  <stringProp name="filename">/tmp/results-detail.jtl</stringProp>
</ResultCollector>
<hashTree/>
```

### ⚙️ 1-2. `filename` 指定の注意（★ 固定指定にまつわる修正点）

- **パスは絶対パス推奨**: `/tmp/results-detail.jtl` のように絶対パスにします。Taurus（bzt）経由で JMeter が動くため、相対パスは Taurus の作業ディレクトリ基準になり、load-test.sh から見える場所とズレることがあります。絶対パスなら出力先が一意に定まります。
- **パスに空白を入れない**: load-test.sh が抽出時に空白を全削除するため、空白を含むパス/ファイル名は壊れます。
- **`filename` タグは 1 行で記述**: `<stringProp name="filename">パス</stringProp>` を 1 行で書きます。改行や属性の差異があると抽出（sed）が失敗します。
- **ローカルのファイル名が固定でも S3 上は一意**: コンテナごとに独立した `/tmp` を使い、S3 側は `<uuid>` で区別されるため、ローカル名が固定でも衝突しません。
- **既存リスナーとの重複に注意**: JMX 内に他の `filename` 付きリスナー（View Results Tree 等）があると、それらも一緒にアップロード対象になります。不要なものは外します。

---

## 🧰 事前作業 2: S3 MCP サーバーのセットアップ（ローカル PC）

### ⚙️ 2-1. uv のインストール（未導入の場合）

```bash
pip install uv
```

### ⚙️ 2-2. MCP クライアント設定に追記

```json
{
  "mcpServers": {
    "awslabs.aws-api-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-api-mcp-server@latest"],
      "env": {
        "AWS_REGION": "ap-northeast-1",
        "AWS_PROFILE": "your-profile"
      }
    }
  }
}
```

### ⚙️ 2-3. AWS 認証情報と権限の確認

- `aws configure` またはプロファイルが設定済みであること。
- 実行ユーザーに以下の S3 権限があること（★ 当初版の修正点: **List 権限も必要**）。
  - `s3:GetObject`（オブジェクト取得）
  - `s3:ListBucket`（UUID を含むキーを探すために必要）

---

## 🧰 Claude での実行手順

### ⚙️ 手順

1. Claude（claude.ai）を開く。
2. S3 MCP サーバーが接続されていることを確認する。
3. まず**疎通確認**を行う（初回はここまで動けば連携成功です）。

```text
s3://<バケット名>/results/<test-id>/JMeter_Result/ 配下を List して、
results-detail.jtl があるか確認してください。
```

4. 取得できたら、**分析を依頼**する（連携が動いた先の活用例）。

```text
上記の results-detail.jtl を取得して、エラー原因を分析してください。
リクエスト/レスポンスボディを参照して、失敗の傾向と根本原因の仮説を挙げてください。
```

- 実際のキー例: `s3://<バケット名>/results/<test-id>/JMeter_Result/<prefix>/<uuid>/tmp/results-detail.jtl`
- `<test-id>` は対象テストの ID、`<prefix>`・`<uuid>` は実行時に動的に決まります。

### ⚙️ Claude が自動で行う内容

1. S3 MCP サーバー経由で対象プレフィックスを List し、詳細 JTL を特定。
2. ファイルを取得して内容を解析。
3. エラー原因・傾向をレポート生成。

---

## 🧰 うまくいかない場合のチェックポイント

「S3 に出てこない」「中身が空」といった症状は、設定・仕組みの両面で起こり得ます。次を順に確認します。

1. **JMeter が実際にファイルを書いたか**: `error_logging=true` はエラーのみ記録のため、エラーが 0 件だとファイルが生成されず、`aws s3 cp` が対象なしで失敗します。まずはエラーが出る条件で検証します。
2. **Taurus 経由でリスナーが効いているか**: bzt が JMX を実行する際、カスタムリスナーの出力先が想定どおりか。絶対パス指定にしているか確認します。
3. **`filename` タグの書式**: 1 行記述・空白なし・標準的なタグ書式か。抽出（grep/sed）の前提に合っているか確認します。
4. **S3 のキーを固定で探していないか**: `<uuid>` を含む動的キーです。List して探します。
5. **権限**: `s3:GetObject` に加え `s3:ListBucket` があるか。
6. **それでも出ない場合**: コンテナ側（load-test.sh）のカスタマイズが必要なケースもあります。その場合は load-test.sh を改修し、コンテナイメージを再ビルド・登録します（Dockerfile/ECR の更新）。

---

## 🧰 注意事項

- **結果サイズと負荷**: `responseData=true` はレスポンスボディを丸ごと記録します。エラー多発時は JTL が肥大化し、ディスク・メモリ・アップロード時間に影響します。エラーのみ記録（`error_logging=true`）で範囲を絞っていますが、規模に応じて注意します。
- **機密情報**: リクエスト/レスポンスボディには認証トークンや個人情報が含まれ得ます。S3 の暗号化・アクセス制御と、Claude に渡す範囲の管理に配慮します。
- **v3/v4 共通**: この方式の load-test.sh ロジックは v3・v4 で本質的に同じです。**v4 にアップグレードしても、設定が同じなら同じ結果（成功/失敗）になります**。アップグレード後は一度小規模テストで「詳細 JTL が S3 に上がるか」を実機確認してください。
- **位置づけ**: 本方式は汎用 S3 MCP で生の JTL を直接読む独立アプローチです。DLT 同梱の MCP Server（AgentCore 経由・メトリクス分析）とは別物で、両立・補完できます。
- **Claude Code は不要**: claude.ai に S3 MCP を接続するだけで完結します。

---

## 🧰 参考リンク

- load-test.sh（コンテナのアップロード処理）: https://github.com/aws-solutions/distributed-load-testing-on-aws/blob/main/deployment/ecr/distributed-load-testing-on-aws-load-tester/load-test.sh
- コンテナイメージのカスタマイズ: https://docs.aws.amazon.com/solutions/latest/distributed-load-testing-on-aws/container-image.html
- AWS API MCP Server: https://github.com/awslabs/mcp
