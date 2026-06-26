# 🖥️ ブラウザベースIDEのSageMaker環境の構築

Amazon SageMaker Studio Code Editorを利用して、AWS上で完結するブラウザベースのIDE環境を構築する手順です。

## 📋 概要

構築は以下の順序で進めます。

1. ネットワークリソース作成(VPC・サブネット・IGW・NATゲートウェイ)
2. ドメイン作成
3. プロジェクト作成
4. ライフサイクルコンフィギュレーション作成
5. IDE稼働環境(EC2)作成
6. IDE利用
7. 利用者追加

---

## ✅ 事前準備

### 🔑 ログインユーザへの権限付与

Amazon SageMaker Studioへログインするユーザには、事前に以下のアクセス権限を付与しておく必要があります。

- `AmazonSageMakerFullAccess` ポリシー等のアタッチ

この権限が無い場合、ドメイン作成画面でのログインユーザ設定やStudioへのアクセスができません。

---

## 🌐 ネットワークリソース作成

SageMaker Studioの機能を使い、VPCを新規作成し、ネットワークリソースを一括作成します(AWS CloudFormation StackSets利用)。

### 📝 手順

1. 「Amazon SageMaker」>「ドメイン」>「ドメインを作成」を選択
2. 「VPCを作成」を選択
3. 「スタックの作成」を選択
   - デフォルトのまま「スタックの作成」で問題ない
   - [パラメータ]欄はデフォルトの"false"を推奨
     - "true"の場合、データ分析・AI関連など数十個のVPCエンドポイントが作成され、ランニングコストに注意が必要
     - "false"の場合はS3アクセス用のVPCエンドポイントのみ作成される
   - [タグ]欄は必要に応じて設定
4. CloudFormation StackSetsが起動し、ネットワークリソースが作成される
   - VPC×1、プライベートサブネット×3、パブリックサブネット×1等が作成される
   - IDE稼働環境(EC2)はプライベートサブネットへ作成される

### 🔌 IGW・NATゲートウェイの追加

上記の標準構成では、プライベートサブネットに作成されたIDE稼働環境(EC2)から外部(npm・PyPI・GitHubなど)のパッケージ取得ができません。外部パッケージを取得するためには、IGW(インターネットゲートウェイ)とNATゲートウェイの追加構成が必要です。

1. **インターネットゲートウェイ(IGW)の作成・アタッチ**
   - VPCコンソールから「インターネットゲートウェイ」を作成
   - 作成したIGWを対象のVPCにアタッチ
2. **パブリックサブネットのルートテーブル設定**
   - 自動作成されたパブリックサブネット用のルートテーブルを開く
   - 宛先 `0.0.0.0/0` のルートを追加し、ターゲットに作成したIGWを指定
3. **NATゲートウェイの作成**
   - パブリックサブネット内にNATゲートウェイを作成(プライベートサブネット1のみに対応する1つを作成)
   - Elastic IPを新規割り当て、NATゲートウェイに関連付け
4. **プライベートサブネット1のルートテーブル設定**
   - プライベートサブネット1のルートテーブルを開く
   - 宛先 `0.0.0.0/0` のルートを追加し、ターゲットに作成したNATゲートウェイを指定

> NATゲートウェイはプライベートサブネット1にのみ作成します。プライベートサブネット2・3については本手順の対象外です。
5. **動作確認**
   - IDE稼働環境(EC2)のターミナルから `npm install` や `pip install` 等が実行できることを確認

> NATゲートウェイは稼働時間に対して課金が発生するため、利用しない場合は削除またはVPCエンドポイント構成への切り替えを検討してください。

---

## 🏛️ ドメイン作成

基盤となる(共通設定を定義する)ドメインを作成します。

1. 「Amazon SageMaker」>「ドメイン」>「ドメインを作成」を選択
2. 「続行」を選択
   - デフォルトのまま「続行」でも問題ない
   - [名前]欄は任意の名称へ変更可能
   - [サブネット]欄はプライベートサブネットを3つ指定する
3. ログインユーザ設定 & 「ドメインを作成」を選択
   - SageMaker Studioは既存のIAMユーザでログインする設定とする
   - ログインユーザには、事前準備で付与した `AmazonSageMakerFullAccess` 等のアクセス権限が必要
4. 「ドメインを作成」を選択し、ドメインが作成される

---

## 📁 プロジェクト作成

ドメイン作成後、ワークスペースとなるプロジェクトを作成します。

1. 作成したドメインの「統合スタジオを開く」を選択し、統合スタジオへログイン
   - 既存のIAMユーザでログイン
2. 「Select a project」>「Create project」を選択
3. [Project name]欄へ任意のプロジェクト名を入力し、「All capabilities」を選択
4. 「Continue」を選択してデフォルトのままページ遷移後、「Create project」を選択
   - プロジェクトが作成される
   - [Project files]はプロジェクトで共有しているS3バケットのファイルで、IDE稼働環境(EC2)作成後に自動でマウントされる

---

## 🔄 ライフサイクルコンフィギュレーション作成

IDE稼働環境(EC2)を作成する前に、起動時の初期化処理を自動化する「ライフサイクルコンフィギュレーション(LCC)」を作成します。

### 📌 ライフサイクルコンフィギュレーションとは

ライフサイクルコンフィギュレーションは、IDE稼働環境(EC2)の起動時に自動実行されるシェルスクリプトです。Spaceの作成・起動のたびに毎回実行されるため、環境構築の手作業を省き、チーム全員で同じ初期設定を再現できます。主に以下のような初期化処理を自動化する用途で利用します。

- viエディタや日本語パッケージ等のインストール・文字化け対策
- Claude Code(Bedrock経由)のインストールと環境変数設定
- VSCode拡張機能(日本語化パッケージ等)のインストール
- MCPサーバ(Playwright・AWS API等)の登録
- 負荷試験・テスト自動化など、用途に応じた依存パッケージの導入

> ライフサイクルコンフィギュレーションは、IDE稼働環境(EC2)作成時にアタッチして利用します。そのため、EC2を作成する**前**に作成しておく必要があります。

### 📝 作成手順

1. 統合スタジオから対象プロジェクトを開く
2. プロジェクトの設定メニューより「Lifecycle configurations」を選択
3. 「Create」を選択し、[Name]欄へ任意の名前を入力
4. [Application]欄で適用先(`Code Editor`等)を選択
5. [Script]欄へ後述のスクリプト内容を貼り付け、保存する
6. IDE稼働環境(EC2)作成時に、本ライフサイクルコンフィギュレーションをアタッチする

> スクリプトは冪等(べきとう)に作られており、`.bashrc`へのマーカー判定やインストール済みチェックにより、再起動のたびに重複実行されないよう制御しています。

### 🧪 スクリプト例①: Playwrightを使ったテスト自動化環境

E2Eテスト自動化向けに、Claude Code(Bedrock経由)とPlaywright拡張機能・依存関係・Playwright MCPをセットアップする例です。

```bash
#!/bin/bash
set -eux

# =========================
# 共通処理
# =========================
echo "ライフサイクル処理を開始します"

# --- node.js（初回更新：3分くらい） ---
# sudo apt update
# sudo apt install -y nodejs npm

# --- 初期処理 ---
MARKER="# color_settings"
BASHRC="/home/sagemaker-user/.bashrc"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

# color_settings
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# syslog
ATE_LOG='/tmp/ate_sys.log'

EOF
fi

# --- viエディタ のインストール ---
MARKER="# viエディタ のインストール"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

# viエディタ のインストール
if [ -x /usr/bin/vi ]; then
  : #echo -e "${RED}viエディタインストール済${NC}"
else
  echo -e "${RED}■初期設定中です。完了するまで、ターミナルの操作はしないでお待ち下さい。${NC}"
  echo -en "${RED}・viエディタインストール中...${NC}"

  echo -e "$(date) : sudo apt-get update" >> ${ATE_LOG}
  sudo apt-get update >> ${ATE_LOG} 2>&1

  echo -e "$(date) : sudo apt-get install -y vim" >> ${ATE_LOG}
  sudo apt-get install -y vim >> ${ATE_LOG} 2>&1

  echo -e "${RED}完了${NC}"
fi

# --- Ubuntuブラウザで日本語が文字化け対応 ---
if dpkg -s language-pack-ja >/dev/null 2>&1; then
  : #echo "language-pack-ja はすでにインストール済みです"
else
  echo -en "${RED}・Ubuntu向け日本語パッケージインストール中...${NC}"

  echo -e "$(date) : sudo apt install -y language-pack-ja" >> ${ATE_LOG}
  sudo apt install -y language-pack-ja >> ${ATE_LOG} 2>&1

  echo -e "$(date) : sudo apt install -y fonts-ipafont" >> ${ATE_LOG}
  sudo apt install -y fonts-ipafont >> ${ATE_LOG} 2>&1

  echo -e "$(date) : sudo apt install -y fonts-ipaexfont" >> ${ATE_LOG}
  sudo apt install -y fonts-ipaexfont >> ${ATE_LOG} 2>&1

  echo -e "$(date) : fc-cache -fv" >> ${ATE_LOG}
  fc-cache -fv >> ${ATE_LOG} 2>&1

  echo -e "${RED}完了${NC}"
fi

EOF
fi


# =========================
# テスト環境向け処理
# =========================

# ①Bedrock 経由で Claude Code を使用する設定
grep -qxF 'export CLAUDE_CODE_USE_BEDROCK=1' ~/.bashrc || echo 'export CLAUDE_CODE_USE_BEDROCK=1' >> ~/.bashrc
grep -qxF 'export AWS_REGION="ap-northeast-1"' ~/.bashrc || echo 'export AWS_REGION="ap-northeast-1"' >> ~/.bashrc
grep -qxF 'export ANTHROPIC_MODEL="jp.anthropic.claude-sonnet-4-5-20250929-v1:0"' ~/.bashrc || echo 'export ANTHROPIC_MODEL="jp.anthropic.claude-sonnet-4-5-20250929-v1:0"' >> ~/.bashrc


# ②Claude Code のインストール
MARKER="# Claude Code のインストール"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

# Claude Code のインストール
if [ -x /opt/conda/bin/claude ]; then
  : #echo -e "${RED}claude codeインストール済${NC}"
else
  echo -en "${RED}・claude codeインストール中...${NC}"

  echo -e "$(date) : npm install -g @anthropic-ai/claude-code" >> ${ATE_LOG}
  npm install -g @anthropic-ai/claude-code >> ${ATE_LOG} 2>&1
  echo -e "${RED}完了${NC}"
fi

EOF
fi

# ③vscode日本語化パッケージインストール
EXTENSIONS_DIR="/home/sagemaker-user/sagemaker-code-editor-server-data/extensions"
EXTENSION_ID="ms-ceintl.vscode-language-pack-ja"

if ! ls "$EXTENSIONS_DIR"/${EXTENSION_ID}-* 1>/dev/null 2>&1; then
  echo -e "【拡張機能】日本語化パッケージインストール中$"
  sagemaker-code-editor --install-extension "$EXTENSION_ID" --extensions-dir "$EXTENSIONS_DIR"
fi

# ④playwrightインストール
EXTENSION_ID="ms-playwright.playwright"

if ! ls "$EXTENSIONS_DIR"/${EXTENSION_ID}-* 1>/dev/null 2>&1; then
  echo -e "【拡張機能】playwrightインストール中"
  sagemaker-code-editor --install-extension "$EXTENSION_ID" --extensions-dir "$EXTENSIONS_DIR"
fi


# ⑤-1Playwright依存関係
MARKER="# Playwright依存関係"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'
# Playwright依存関係
if dpkg -s libxcb-shm0 >/dev/null 2>&1; then
  : #echo "libxcb-shm0 はすでにインストール済みです"
else

# 更新
echo -en "${RED}・依存関係同期中...${NC}"

echo -e "$(date) : sudo apt-get update" >> ${ATE_LOG}
sudo apt-get update >> ${ATE_LOG} 2>&1
echo -e " ${RED}同期完了${NC}"

# インストール
echo -en "${RED}・依存関係をインストール中です${NC}"

# バックグラウンドでインストール
echo -e "$(date) : npx playwright install-deps" >> ${ATE_LOG}
npx playwright install-deps >> ${ATE_LOG} &

pid=$!
disown $pid  # ジョブ番号の管理から外す

# 簡易スピナー（ドット表示）
while kill -0 $pid 2>/dev/null; do
  echo -en "${RED}.${NC}"
  sleep 2
done

wait $pid
echo -e "${RED}インストールしました${NC}"
fi
EOF
fi

# ⑥playwright/mcpインストール
MARKER="# playwright/mcpインストール"

# マーカーが無い場合のみ.bashrcに追記（初回のみ）
if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

  # playwright/mcpインストール
  # echo -e "${RED}・playwright/mcp更新中${NC}"
  echo -e "$(date) : claude mcp add playwright npx @playwright/mcp@latest" >> ${ATE_LOG}
  claude mcp add playwright npx @playwright/mcp@latest >> ${ATE_LOG} 2>&1

EOF
fi
```

### 🧪 スクリプト例②: DLT環境を使った負荷試験環境

負荷試験(DLT)向けに、Claude Code(Bedrock経由)・AWS API MCPサーバ(`awslabs.aws-api-mcp-server`)・`uv`をセットアップする例です。

```bash
#!/bin/bash
set -eux

# =========================
# 色・ログ変数の定義
# =========================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'
ATE_LOG='/tmp/ate_sys.log'

# =========================
# 開始ログ出力
# =========================
echo "ライフサイクル処理を開始します"

# =========================
# color_settingsの設定（.bashrcへ書込）
# =========================
MARKER="# color_settings"
BASHRC="/home/sagemaker-user/.bashrc"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

# color_settings
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# syslog
ATE_LOG='/tmp/ate_sys.log'

# PATH（claude→MCP/uvx 用）
export PATH="/home/sagemaker-user/.local/bin:$PATH"

EOF
fi

# =========================
# viエディタ のインストール ＆ Ubuntuブラウザで日本語が文字化け対応（.bashrcへ書込）
# =========================
MARKER="# viエディタ のインストール"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

# viエディタ のインストール
if [ -x /usr/bin/vi ]; then
  : #echo -e "${RED}viエディタインストール済${NC}"
else
  echo -e "${RED}■初期設定中です。完了するまで、ターミナルの操作はしないでお待ち下さい。${NC}"
  echo -en "${RED}・viエディタインストール中...${NC}"

  echo -e "$(date) : sudo apt-get update" >> ${ATE_LOG}
  sudo apt-get update >> ${ATE_LOG} 2>&1

  echo -e "$(date) : sudo apt-get install -y vim" >> ${ATE_LOG}
  sudo apt-get install -y vim >> ${ATE_LOG} 2>&1

  echo -e "${RED}完了${NC}"
fi

if dpkg -s language-pack-ja >/dev/null 2>&1; then
  : #echo "language-pack-ja はすでにインストール済みです"
else
  echo -en "${RED}・Ubuntu向け日本語パッケージインストール中...${NC}"

  echo -e "$(date) : sudo apt install -y language-pack-ja" >> ${ATE_LOG}
  sudo apt install -y language-pack-ja >> ${ATE_LOG} 2>&1

  echo -e "$(date) : sudo apt install -y fonts-ipafont" >> ${ATE_LOG}
  sudo apt install -y fonts-ipafont >> ${ATE_LOG} 2>&1

  echo -e "$(date) : sudo apt install -y fonts-ipaexfont" >> ${ATE_LOG}
  sudo apt install -y fonts-ipaexfont >> ${ATE_LOG} 2>&1

  echo -e "$(date) : fc-cache -fv" >> ${ATE_LOG}
  fc-cache -fv >> ${ATE_LOG} 2>&1

  echo -e "${RED}完了${NC}"
fi

EOF
fi

# =========================
# ①Bedrock 経由で Claude Code を使用する設定（.bashrcへ書込）
# =========================
grep -qxF 'export CLAUDE_CODE_USE_BEDROCK=1' ~/.bashrc || echo 'export CLAUDE_CODE_USE_BEDROCK=1' >> ~/.bashrc
grep -qxF 'export AWS_REGION="ap-northeast-1"' ~/.bashrc || echo 'export AWS_REGION="ap-northeast-1"' >> ~/.bashrc
grep -qxF 'export ANTHROPIC_MODEL="jp.anthropic.claude-sonnet-4-5-20250929-v1:0"' ~/.bashrc || echo 'export ANTHROPIC_MODEL="jp.anthropic.claude-sonnet-4-5-20250929-v1:0"' >> ~/.bashrc

# =========================
# ②Claude Code のインストール ＋ AWS MCP設定（.bashrcへ書込）
# =========================
MARKER="# Claude Code のインストール"

if ! grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
  cat >> "$BASHRC" << 'EOF'

# Claude Code のインストール
if [ -x /opt/conda/bin/claude ]; then
  : #echo -e "${RED}claude codeインストール済${NC}"
else
  echo -en "${RED}・claude codeインストール中...${NC}"

  echo -e "$(date) : npm install -g @anthropic-ai/claude-code" >> ${ATE_LOG}
  npm install -g @anthropic-ai/claude-code >> ${ATE_LOG} 2>&1
  echo -e "${RED}完了${NC}"
fi

MCP_CONFIG="$HOME/.claude.json"
if command -v claude >/dev/null 2>&1; then
  # aws-api MCPが未設定なら追加（~/.claude.json を冪等チェック）
  if [ ! -f "$MCP_CONFIG" ] || ! grep -q "aws-api" "$MCP_CONFIG" 2>/dev/null; then
    echo -en "${RED}・AWS MCP設定中...${NC}"
    echo -e "$(date) : claude mcp add aws-api" >> ${ATE_LOG}
    claude mcp add --scope user aws-api -- uvx awslabs.aws-api-mcp-server@latest >> ${ATE_LOG} 2>&1
    echo -e "${RED}完了${NC}"
  fi
fi

EOF
fi

# =========================
# ③vscode日本語化パッケージインストール
# =========================
EXTENSIONS_DIR="/home/sagemaker-user/sagemaker-code-editor-server-data/extensions"
EXTENSION_ID="ms-ceintl.vscode-language-pack-ja"

if ! ls "$EXTENSIONS_DIR"/${EXTENSION_ID}-* 1>/dev/null 2>&1; then
  echo -e "【拡張機能】日本語化パッケージインストール中"
  sagemaker-code-editor --install-extension "$EXTENSION_ID" --extensions-dir "$EXTENSIONS_DIR"
fi

# =========================
# ④PATHを追加する（.local/bin）
# =========================
export PATH="/home/sagemaker-user/.local/bin:$PATH"

# =========================
# ⑤uvのインストール
# =========================
if ! command -v uv >/dev/null 2>&1; then
  echo -en "${RED}・uvインストール中...${NC}"
  echo -e "$(date) : python -m pip install uv" >> ${ATE_LOG}
  python -m pip install uv >> ${ATE_LOG} 2>&1

  if command -v uv >/dev/null 2>&1; then
    echo -e "$(date) : uv python install 3.12" >> ${ATE_LOG}
    uv python install 3.12 >> ${ATE_LOG} 2>&1
  else
    echo -e "${YELLOW}警告: uv が見つかりません。python install をスキップ${NC}" | tee -a ${ATE_LOG}
  fi

  echo -e "${RED}完了${NC}"
fi
# =========================
# 完了ログ出力
# =========================
echo -e "${GREEN}✓ ライフサイクル処理が正常に完了しました${NC}"
```

---

## ⚙️ IDE稼働環境(EC2)作成

プロジェクト作成後、個人用の開発環境としてIDE稼働環境(EC2)を作成します。

1. プロジェクトから「Compute」>「Spaces」タブを選択
   - こちらのページでIDE稼働環境(EC2)の作成・起動・停止・削除・IDEアクセスを実施する
   - 「Spaces」タブへのページ遷移やブラウザ更新時、デフォルトで作成されているJupyterLabインスタンスが自動起動するが、1時間のアイドルタイム経過で自動停止する(削除手段は現時点でなし)
2. 「Create space」を選択
3. [Name]欄へ任意の名前を入力
4. [Application]欄で"Code Editor"を選択
5. 「Create and start space」を選択
   - EC2のインスタンスタイプの最小は"ml.t3.large"(メモリ8GiBが必要)
   - EC2インスタンスはAWSマネージドな領域で作成され、マネジメントコンソール上からは参照不可
   - [Lifecycle configuration]欄で、先に作成したライフサイクルコンフィギュレーションを選択
   - デフォルト設定で1時間のアイドルタイム経過後に自動停止
   - IDE稼働環境(EC2)が作成・起動される

---

## 🚀 IDE利用

### 🔓 IDEアクセス

1. IDE稼働環境(EC2)起動後、「Open」を選択
2. 警告が表示されるため、チェックを入れて「Yes, I trust the authors」を選択

### 📖 IDE概要

- ブラウザベースでVSCodeが利用可能
- **ターミナル**: 左上のハンバーガーメニューから表示可能
- **日本語化**: ローカルのVSCode同様に拡張機能をインストールし、使用法記載の手順で日本語化可能
- **ディレクトリ構成**:

  | パス | 区 分 | 永 続 性 | 説明 |
  | --- | --- | --- | --- |
  | `/home/sagemaker-user/` | ホ ー ム デ ィ レ ク ト リ | 永 続 | IDE稼働環境(EC2)のホームディレクトリ |
  | `/home/sagemaker-user/shared/` | プ ロ ジ ェ ク ト 共 有 領 域 | 永 続 | S3バケットを自動マウント。プロジェクト作成時にS3バケットが自動作成・自動マウントされ、同じプロジェクト内のEC2間でファイルが共有される |
  | `/home/sagemaker-user/`配下(`shared/`以外) | 個 人 作 業 用 デ ィ レ ク ト リ | 永 続 | 例: `work/` など。個人の作業領域として作成を推奨(`shared/`以外の`/home/sagemaker-user/`配下に作成する) |
  | `/home/sagemaker-user/`配下以外 | 一 時 領 域 | 揮 発 性 | EC2停止時に削除される |
- **AWSリソースへのアクセス**: クレデンシャル情報(アクセスキー/シークレットキー)をターミナルなどから設定することでアクセス可能

### 🪣 共有S3(`shared/`)の自動構成について

`shared/` にマウントされる共有S3バケットは、利用者が個別に作成・権限設定をしなくても、SageMaker Unified Studioが自動で構成します。仕組みは以下の通りです。

1. **ドメイン作成時にS3バケットが1つ自動作成される**
   - バケット名は以下の形式
     ```
     amazon-datazone-<アカウントID>-<リージョン>-<ドメインID>
     ```
   - このバケットがドメイン全体で共有ストレージの実体となる(プロジェクトごとに別バケットが作られるわけではない)

2. **プロジェクト作成時に、その中のプレフィックスが自動で割り当てられる**
   - プロジェクトごとに以下の構造で専用の共有領域(プレフィックス)が割り当てられる
     ```
     [bucket]/[domain-id]/[project-id]/shared/
     ```
   - `shared/` にマウントされるのはこのプレフィックス配下
   - プロジェクトが異なれば `[project-id]` が変わるため別領域となり、同一プロジェクト内のスペース(EC2)間では同じプレフィックスを共有する

3. **プロジェクト作成時に自動作成される「プロジェクトロール」でS3アクセス権限が付与される**
   - プロジェクト作成時に、プロジェクト専用のIAMロールが自動生成される
     ```
     datazone_usr_role_xxxxx
     ```
   - このロールにS3アクセス権限を含む管理ポリシー(`SageMakerStudioProjectUserRolePolicy`)が自動でアタッチされ、上記プレフィックスへのアクセスが許可される
   - プロジェクトを開くことは、このプロジェクトロールをassumeすることと同義であり、ログインユーザのIAMグループ側に共有S3の許可が無くてもアクセスできるのはこのため

> 上記は、プロジェクト作成時のファイルストレージで「Amazon S3 storage」(デフォルト)を選択した場合の挙動です。Gitリポジトリを選択した場合や、プロジェクト外の既存バケットを利用したい場合は、別途権限設定が必要になります。

---

## 🤖 Claude Codeの起動

IDE稼働環境(EC2)のターミナルからClaude Codeをインストール・起動します。

### 📌 前提条件

- Node.js 18以降が必要(未導入の場合は別途インストール)

### 📝 手順

1. ターミナルを開く(左上のハンバーガーメニューから表示可能)
2. Claude Codeをインストール
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. Claude Codeを起動
   ```bash
   claude
   ```
4. 初回起動時、ブラウザでの認証が求められる場合はAnthropicアカウントでログインする
   - ブラウザ転送ができない環境の場合は、APIキーまたはAmazon Bedrock経由の認証設定を行う
5. プロジェクト用のディレクトリ(個人作業領域)へ移動してから起動することで、想定外の範囲を参照させないようにする

---

作成したプロジェクトへ利用者を追加したい場合は、ドメインとプロジェクトでそれぞれユーザ追加設定を実施します。

1. **ドメインへユーザ追加**
   - ドメインページ下部の「ユーザ管理」タブより「追加」を選択してユーザを追加
2. **プロジェクトへユーザ追加**
   - 統合スタジオから対象のプロジェクトへ遷移し、「Members」ページの「Add members」を選択してユーザを追加

---

## 📚 参考文献

- [AWSで完結するブラウザベースIDE＆Git構築への道① 〜Amazon SageMaker Studio編〜 | iret.media](https://iret.media/177072)
