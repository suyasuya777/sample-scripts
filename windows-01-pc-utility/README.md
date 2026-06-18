# 📘 開発環境 ツールインストール手順書

各種ツールの Windows へのインストール手順をまとめたものです。

> 凡例（見出しレベルと絵文字）
> 📘 = 大見出し（h1） / 🧰 = ツール（h2） / ⚙️ = 手順セクション（h3） / 📍 = 作業ステップ（h4）

---

## 🧰 目次

1. [Git](#-git)
2. [Visual Studio Code（VS Code）](#-visual-studio-codevs-code)
3. [Python（Anaconda）](#-pythonanaconda)
4. [Node.js](#-nodejs)
5. [Docker](#-docker)
6. [Terraform](#-terraform)
7. [AWS CLI](#-aws-cli)
8. [AWS SAM CLI](#-aws-sam-cli)
9. [jq / yq](#-jq--yq)
10. [WinSCP](#-winscp)
11. [Tera Term](#-tera-term)
12. [Wireshark](#-wireshark)
13. [WinMerge](#-winmerge)
14. [JMeter](#-jmeter)

---

## 🧰 Git

### ⚙️ 1. Git のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://git-scm.com/
- Windows タブの「Click here to download」からインストーラをダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します。
- 基本は **Next 連打**でOKです。

#### 📍 1-3. 動作確認
```bash
git --version
```

---

## 🧰 Visual Studio Code（VS Code）

### ⚙️ 1. VS Code のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://code.visualstudio.com/
- 「Download for Windows」からインストーラをダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します。
- 途中のオプション画面では、以下を **必ず ON** にします（迷ったら全部チェックでOK）。
  - Add to PATH
  - Open with Code（右クリック）
  - Register Code as an editor for supported file types

#### 📍 1-3. 動作確認
```bash
code --version
```
- スタートメニュー → VS Code でも起動を確認します。

#### 📍 1-4. 日本語化（必要に応じて拡張機能を追加）
- 左側の **Extensions**（四角アイコン）を開きます。
- 「Japanese Language Pack for Visual Studio Code」を検索して **Install** します。
- 完了後、VS Code を再起動します。

---

## 🧰 Python（Anaconda）

Anaconda は Python 本体に加え、`conda`（パッケージ／仮想環境マネージャ）、主要なデータ分析ライブラリ、GUI の Anaconda Navigator をまとめて導入できるディストリビューションです。

> ⚠️ ライセンスに関する注意:
> - **従業員・契約者が 200 名以上の組織**で Anaconda Distribution（公式インストーラ）や Anaconda 提供チャンネル（`defaults` / `main` など）を利用する場合は、**有料の Business ライセンス**が必要です（個人利用、および 200 名未満の組織は無料）。
> - 一方で `conda` コマンド自体、`conda-forge` チャンネル、Miniforge は無料で利用できます。組織で無償運用したい場合は、**Miniforge（conda-forge が既定）** を使うか、後述のように `conda-forge` チャンネルへ切り替える運用が安全です。
> - SES 先など大規模組織の環境で使う場合は、事前にライセンス可否を確認してください。

### ⚙️ 1. Anaconda のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://www.anaconda.com/download
- Windows 用インストーラ（64-bit Graphical Installer）をダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します。
- インストールタイプは「**Just Me (recommended)**」を選びます（現在のユーザーのみ）。
- インストール先は既定のままで OK です（**日本語やスペースを含まないパス**が無難です）。
- 「Advanced Options」では以下を推奨します。
  - 「Add Anaconda3 to my PATH environment variable」は **チェックしない**（公式推奨。代わりに後述の Anaconda Prompt を使います）。
  - 「Register Anaconda3 as my default Python」は **チェックする**。

#### 📍 1-3. 動作確認
- スタートメニュー → 「**Anaconda Prompt**」を起動します。
```bash
conda --version
python --version
```
- ※ 通常の PowerShell からも conda を使いたい場合は、Anaconda Prompt で一度だけ `conda init powershell` を実行し、ターミナルを開き直します。

#### 📍 1-4. 仮想環境の基本（参考）
- プロジェクトごとに環境を分けると、依存関係の衝突を防げます。
```bash
# Python 3.12 の環境を作成
conda create -n myenv python=3.12

# 環境を有効化 / 無効化
conda activate myenv
conda deactivate

# 環境一覧
conda env list
```
- ※ 組織でライセンス対象を避けたい場合は、`conda-forge` を明示して作成します。
```bash
conda create -n myenv -c conda-forge python=3.12
```

---

## 🧰 Node.js

JavaScript / TypeScript の実行環境です。フロントエンドのビルドツールや各種 CLI（AWS CDK、Lint ツールなど）の実行基盤として利用します。パッケージマネージャの **npm** が同梱されます。

### ⚙️ 1. Node.js のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://nodejs.org/
- **LTS 版**（推奨版）の Windows Installer（`.msi`、64-bit）をダウンロードします。
  - ※ 本番・実務では Current 版ではなく **LTS 版**を選びます（2026 年 6 月時点の Active LTS は Node.js 24 系です）。

#### 📍 1-2. インストール
- ダウンロードした MSI インストーラを実行します。
- 基本は **Next 連打**でOKです（「Add to PATH」は既定で有効です）。
- ※ 「Tools for Native Modules」のチェックは、ネイティブモジュールのビルドが不要なら外しても構いません。
- ※ インストール後、`node` / `npm` を認識させるため、開いている PowerShell / コマンドプロンプトは一度閉じて開き直します。

#### 📍 1-3. 動作確認
```bash
node --version
npm --version
```

#### 📍 1-4. 補足（複数バージョンの管理 / 任意）
- 複数の Node.js バージョンを切り替えたい場合は、**nvm-windows** が便利です。
  - https://github.com/coreybutler/nvm-windows/releases
- ※ winget が使える環境なら、`winget install OpenJS.NodeJS.LTS` で LTS 版を導入することも可能です。

---

## 🧰 Docker

> 前提:
> - Docker Desktop は **WSL2** をバックエンドとして利用します。
> - Docker のインストーラも WSL2 関連の有効化をある程度は行いますが、確実で詰まりにくいのは **先に WSL2 を完成させてから** Docker Desktop を入れる方法です。初回起動時の「WSL カーネルの更新が必要」等のエラーを避けられます。

### ⚙️ 1. （事前準備）WSL2 の有効化

#### 📍 1-1. 管理者権限の PowerShell を開く
- スタートメニューで「**PowerShell**」を検索し、右クリック →「**管理者として実行**」を選びます。

#### 📍 1-2. WSL2 のインストール
```bash
wsl --install
```
- **Virtual Machine Platform** / **Windows Subsystem for Linux** / **Ubuntu** がまとめてインストールされます。
- すでに WSL が入っている場合は、代わりに `wsl --update` で最新化します。
- 完了後、画面の指示に従って **PC を再起動**します（WSL カーネルの更新は再起動後に反映されます）。

#### 📍 1-3. 動作確認
```bash
wsl --list --verbose
```
- 一覧が表示され、**VERSION 列が「2」**になっていれば WSL2 として動作しています。
- ※ VERSION が「1」の場合は `wsl --set-version <ディストロ名> 2` で 2 に変換します。
- ※ Docker Desktop はエンジン用に `docker-desktop` という専用ディストロを自動作成するため、Ubuntu を入れていなくても `docker` コマンド自体は動きます（Ubuntu は WSL 上の Linux ターミナルから直接 docker を使いたい場合の連携用）。

#### 📍 1-4. 補足（ハードウェア仮想化の確認）
- WSL2 は仮想化機能を利用するため、BIOS/UEFI で **仮想化（Intel VT-x / AMD SVM）** が有効になっている必要があります。
- **タスクマネージャー → パフォーマンス → CPU** で「**仮想化: 有効**」と表示されていれば問題ありません。無効の場合は BIOS/UEFI で有効化します。

### ⚙️ 2. Docker Desktop のインストール

#### 📍 2-1. ダウンロード
- 以下の URL にアクセスします。
  - https://www.docker.com/products/docker-desktop/
- 「Download Docker Desktop」からインストーラをダウンロードします。

#### 📍 2-2. インストール
- インストーラを実行します。
- インストール中のオプションで「**Use WSL 2 instead of Hyper-V**」をチェックします（上記の事前準備で WSL2 を入れていれば、チェックを入れたまま進めるだけでOKです）。
- インストール完了後、再起動を求められたら **必ず再起動**します。

#### 📍 2-3. 動作確認
```bash
docker --version
```
- スタートメニュー → Docker Desktop を起動し、左下が「**Engine running**」になれば成功です。

---

## 🧰 Terraform

### ⚙️ 1. Terraform のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://developer.hashicorp.com/terraform/downloads
- バイナリ ZIP ファイル（**AMD64**）をダウンロードします。

#### 📍 1-2. 配置
- 解凍後、以下のフォルダに配置します。
  - `C:\terraform`

#### 📍 1-3. 環境変数（Path）の設定
- 検索窓で「**env**」を入力し、環境変数の設定を開きます。
- Path に以下を追加します。
  - `C:\terraform`

#### 📍 1-4. 動作確認
```bash
terraform --version
```

### ⚙️ 2. terraform-docs のインストール（ドキュメント自動生成）

terraform-docs は、Terraform モジュールの `.tf`（variables / outputs / providers など）を解析し、入力変数・出力・プロバイダー・リソース等の表を Markdown などの形式で自動生成するツールです。Go 製の単体バイナリで、README への差し込み（inject）や CI 連携により、コードとドキュメントのズレ（ドリフト）を防げます。

> 補足:
> - 自動生成されるのは「コードから読み取れる構造情報（変数・出力・プロバイダー等の表）」です。各項目の意味は `.tf` 内の `description` に書いておくと、そのまま表の説明欄に反映されます。

#### 📍 2-1. ダウンロード
- 以下の URL（GitHub リリースページ）にアクセスします。
  - https://github.com/terraform-docs/terraform-docs/releases
- Windows 向けの `terraform-docs-v<バージョン>-windows-amd64.zip` をダウンロードします。
  - 例（現行）: `terraform-docs-v0.24.0-windows-amd64.zip`

#### 📍 2-2. 配置
- ZIP を解凍し、中の実行ファイルを `terraform-docs.exe` にリネームします（バージョン入りの名前になっている場合があります）。
- Terraform 本体と同じ `C:\terraform` に置くと、Path 設定を使い回せます（「⚙️ 1-3」で設定済みのため、追加の Path 設定は不要です）。
- 別フォルダに置く場合は、そのフォルダを Path に追加します。

#### 📍 2-3. 動作確認
```bash
terraform-docs --version
```

#### 📍 2-4. 使い方の例
- モジュールのディレクトリを対象に実行します。
```bash
# Markdown テーブルを生成して標準出力に表示
terraform-docs markdown table .

# README.md のマーカー間に差し込み（inject）して更新
terraform-docs markdown table --output-file README.md --output-mode inject .
```
- inject を使う場合、対象の README.md に差し込み位置のマーカーをあらかじめ記述しておきます。
```markdown
<!-- BEGIN_TF_DOCS -->
<!-- END_TF_DOCS -->
```
- 表示するセクションや並び順などの詳細は、モジュール直下に `.terraform-docs.yml` を置いて設定できます。
- ※ winget が使える環境なら、`winget install -e --id Terraform-docs.Terraform-docs` で一括導入も可能です（Chocolatey は `choco install terraform-docs`、Scoop は `scoop install terraform-docs`）。

---

## 🧰 AWS CLI

### ⚙️ 1. AWS CLI v2 のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://aws.amazon.com/cli/
- Windows 用の MSI インストーラをダウンロードします（直リンク: `https://awscli.amazonaws.com/AWSCLIV2.msi`）。

#### 📍 1-2. インストール
- ダウンロードした MSI インストーラを実行します。
- 基本は **Next 連打**でOKです。
- ※ インストール後、`aws` コマンドを認識させるため、開いている PowerShell / コマンドプロンプトは一度閉じて開き直します。

#### 📍 1-3. 動作確認
```bash
aws --version
```

#### 📍 1-4. 初期設定（認証情報の登録 / 必要に応じて）
```bash
aws configure
```
- 以下を順に入力します。
  - AWS Access Key ID
  - AWS Secret Access Key
  - Default region name（例: `ap-northeast-1`）
  - Default output format（例: `json`）

### ⚙️ 2. Session Manager Plugin のインストール（SSM 接続）

AWS CLI から `aws ssm start-session` で EC2 に接続するためのプラグインです。AWS CLI 本体とは別に、ローカル PC へ追加でインストールします（AWS CLI v1.16.12 以降が前提のため、上記の v2 が入っていれば問題ありません）。

#### 📍 2-1. ダウンロード
- 以下の URL からインストーラ（`.exe`）をダウンロードします。
  - https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe
- ※ ZIP 版が必要な場合は次の URL を利用します（解凍後にインストーラを実行）。
  - https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPlugin.zip

#### 📍 2-2. インストール
- ダウンロードしたインストーラを **管理者権限** で実行します。
- インストール場所は空欄のまま（デフォルト）でOKです。
- インストール後、`session-manager-plugin` を認識させるため、開いている PowerShell / コマンドプロンプトは一度閉じて開き直します。
- ※ Windows では **PowerShell 5 以降、またはコマンドプロンプト** の利用が推奨です（一部のサードパーティ製ターミナルは非対応の場合があります）。

#### 📍 2-3. 動作確認
```bash
session-manager-plugin
```
- 「The Session Manager plugin was installed successfully. Use the AWS CLI to start a session.」と表示されれば成功です。
- ※ コマンドが見つからない場合は、ターミナルを開き直すか、インストール先（既定: `C:\Program Files\Amazon\SessionManagerPlugin\bin`）を Path に手動追加します。

### ⚙️ 3. SSM 接続のための前提（サーバー側）

SSM 接続は「ローカル（AWS CLI ＋ プラグイン）」だけでなく、接続先 EC2 側にも準備が必要です。以下が満たされていないと接続できません。

#### 📍 3-1. SSM Agent
- 接続先 EC2 に **SSM Agent（バージョン 2.3.68.0 以降）** が稼働している必要があります。
- Amazon Linux 2 / 2023、および比較的新しい Windows Server AMI には標準でプリインストールされています。

#### 📍 3-2. IAM ロール（インスタンスプロファイル）
- 接続先 EC2 に、SSM 権限を持つ IAM ロールがアタッチされている必要があります。
- 最小構成として、AWS 管理ポリシー **`AmazonSSMManagedInstanceCore`** をアタッチします。

#### 📍 3-3. ネットワーク
- EC2 から SSM エンドポイントへの **アウトバウンド 443** が通れば接続できます（インバウンドの SSH(22) 開放は不要）。
- インターネットに出られないプライベートサブネットの場合は、SSM 用の **VPC エンドポイント（PrivateLink）** を作成します。
  - 主なエンドポイント: `ssm` / `ssmmessages` / `ec2messages`

#### 📍 3-4. ローカル側の IAM 権限
- 接続を実行するユーザー / ロールに、`ssm:StartSession` 等の権限が必要です。

### ⚙️ 4. SSM で接続する

#### 📍 4-1. セッションを開始する
```bash
aws ssm start-session --target i-0123456789abcdef0
```
- `--target` にはインスタンス ID を指定します。
- 接続後はそのままシェル操作が可能です。終了するときは `exit` を入力します。

#### 📍 4-2. ポートフォワード（任意）
- ローカルのポートを EC2 のポートへトンネルできます（例: RDP やローカルからの DB 接続）。
```bash
aws ssm start-session --target i-0123456789abcdef0 --document-name AWS-StartPortForwardingSession --parameters "portNumber=3389,localPortNumber=13389"
```

#### 📍 4-3. メリット（SSH / 踏み台との比較）
- EC2 のインバウンド SSH(22) を開放せずに接続できます（セキュリティグループを締められます）。
- 踏み台サーバーが不要で、プライベートサブネットの EC2 にも届きます。
- 秘密鍵（`.pem`）の管理が不要で、認証を IAM に集約できます。
- 操作内容が **CloudTrail / セッションログ** に記録され、監査性が高まります。

---

## 🧰 AWS SAM CLI

Lambda / サーバーレスアプリケーションのローカル実行・テスト・デプロイを行うためのツールです。`sam` という独自コマンドを持つ、AWS CLI とは別の独立したツールです。

> 前提:
> - **デプロイ**には AWS 認証情報が必要です（→「🧰 AWS CLI」の `aws configure` を参照）。
> - **ローカル実行**（`sam local invoke` 等）には Docker が必要で、かつ起動している必要があります（→「🧰 Docker」を参照）。
> - `sam init`（テンプレートからの雛形生成）には Git が必要です（→「🧰 Git」を参照）。

### ⚙️ 1. AWS SAM CLI のインストール

#### 📍 1-1. ダウンロード
- 以下の URL（公式インストールガイド）にアクセスします。
  - https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
- Windows 用の MSI インストーラ（`AWS_SAM_CLI_64_PY3.msi`）をダウンロードします。
  - 最新版の直リンク: `https://github.com/aws/aws-sam-cli/releases/latest/download/AWS_SAM_CLI_64_PY3.msi`

#### 📍 1-2. インストール
- ダウンロードした MSI インストーラを実行します。
- 基本は **Next 連打**でOKです。
- ※ インストール後、`sam` コマンドを認識させるため、開いている PowerShell / コマンドプロンプトは一度閉じて開き直します。

#### 📍 1-3. ロングパスの有効化（Windows 10 以降 / 推奨）
- `sam init` 実行時に Windows のパス長上限（MAX_PATH）でエラーになることがあるため、ロングパスを有効化しておくことを推奨します。
- **管理者権限の PowerShell** で以下を実行します。
```bash
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

#### 📍 1-4. 動作確認
```bash
sam --version
```

### ⚙️ 2. 前提環境の確認

SAM を使い始める前に、関連ツールと認証情報が揃っているかをまとめて確認します。
```bash
aws --version                  # AWS CLI（デプロイ用）
sam --version                  # SAM CLI 本体
docker --version               # Docker（ローカル実行用）
aws sts get-caller-identity    # AWS 認証情報が有効かを確認
```
- `aws sts get-caller-identity` でアカウント ID / ARN が返れば、認証情報は有効です。
- `docker ps` がエラーになる場合は Docker が起動していません。Docker Desktop を起動してください。

---

## 🧰 jq / yq

JSON / YAML をコマンドラインで整形・抽出するための処理ツールです。AWS CLI や Terraform の出力加工、設定ファイルの確認などで使います。いずれも単体で動作する実行ファイルで、AWS CLI などへの依存はありません。

### ⚙️ 1. jq のインストール（JSON 処理）

#### 📍 1-1. ダウンロード
- 以下の URL（公式ダウンロードページ）にアクセスします。
  - https://jqlang.org/download/
- Windows 向けの `jq-windows-amd64.exe` をダウンロードします。
  - 直リンク例: `https://github.com/jqlang/jq/releases/download/jq-1.8.1/jq-windows-amd64.exe`

#### 📍 1-2. 配置
- ダウンロードしたファイルを `jq.exe` にリネームし、任意のフォルダに配置します。
  - 例: `C:\tools\bin\jq.exe`

#### 📍 1-3. 環境変数（Path）の設定
- 検索窓で「**env**」を入力し、環境変数の設定を開きます。
- Path に配置先フォルダを追加します。
  - 例: `C:\tools\bin`

#### 📍 1-4. 動作確認
```bash
jq --version
```
- ※ winget が使える環境なら、`winget install jqlang.jq` で一括導入も可能です（Path 設定も自動）。

### ⚙️ 2. yq のインストール（YAML 処理）

YAML（および JSON / XML / CSV）を扱えるツールです。jq に似た構文で操作できます。

> ⚠️ yq には同名の別実装が複数あります。必ず **mikefarah 版（Go 製の単体バイナリ）** を使用してください。

#### 📍 2-1. ダウンロード
- 以下の URL（GitHub リリースページ）にアクセスします。
  - https://github.com/mikefarah/yq/releases
- Windows 向けの `yq_windows_amd64.exe` をダウンロードします。
  - 最新版の直リンク: `https://github.com/mikefarah/yq/releases/latest/download/yq_windows_amd64.exe`

#### 📍 2-2. 配置
- ダウンロードしたファイルを `yq.exe` にリネームし、jq と同じフォルダに配置します。
  - 例: `C:\tools\bin\yq.exe`

#### 📍 2-3. 環境変数（Path）の設定
- jq と同じフォルダに配置した場合、Path の追加は不要です（jq の手順で設定済みのため）。
- 別フォルダに配置した場合は、そのフォルダを Path に追加します。

#### 📍 2-4. 動作確認
```bash
yq --version
```
- ※ winget が使える環境なら、`winget install --id MikeFarah.yq` で一括導入も可能です。

### ⚙️ 3. 使い方の例

```bash
# AWS CLI の JSON 出力から必要な値だけ抜き出す
aws ec2 describe-instances | jq -r ".Reservations[].Instances[].InstanceId"

# Terraform の出力（JSON）を整形して確認する
terraform output -json | jq

# YAML ファイルから特定のキーを取り出す
yq ".spec.replicas" deployment.yaml
```

---

## 🧰 WinSCP

### ⚙️ 1. WinSCP のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://winscp.net/eng/download.php
- インストーラ（**Installation package**）をダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します。
- 基本は **Next 連打**でOKです（セットアップ形式は「標準的なインストール」を選択）。

#### 📍 1-3. 動作確認
- スタートメニュー → WinSCP を起動します。
- ログイン画面（ホスト名・ユーザー名等の入力欄）が表示されれば成功です。

### ⚙️ 2. SSH config ファイルの設定（公開鍵認証）

接続先を毎回入力せずに「ホスト名（エイリアス）」で接続できるようにする設定です。すべて公開鍵暗号方式（`.pem` 秘密鍵）を使用する例です。

#### 📍 2-1. config ファイルの場所
- 以下のパスに `config`（拡張子なし）というファイルを作成します。
  - Windows: `C:\Users\<ユーザー名>\.ssh\config`
- 秘密鍵（`.pem`）も同じ `.ssh` フォルダに配置します。
  - 例: `C:\Users\<ユーザー名>\.ssh\yasuo-nakata.pem`

#### 📍 2-2. ダイレクト接続するパターン
踏み台を経由せず、各サーバーへ直接接続します。各ホストに秘密鍵（`IdentityFile`）を指定します。

```bash
# known_hosts から該当 IP を削除したいとき（鍵が変わった場合など）
# ssh-keygen -R xxx.xxx.xxx.xxx

Host jump
    HostName 13.113.143.94
    User ec2-user
    IdentityFile ~/.ssh/yasuo-nakata.pem

Host web1
    HostName 52.194.230.69
    User ec2-user
    IdentityFile ~/.ssh/yasuo-nakata.pem

Host web2
    HostName 54.250.63.62
    User ec2-user
    IdentityFile ~/.ssh/yasuo-nakata.pem
```

- 接続例:
```bash
ssh web1
```

#### 📍 2-3. 踏み台（bastion）経由で接続するパターン
プライベートサブネット上のサーバーへ、踏み台サーバー経由で接続します。`ProxyJump` に踏み台のエイリアスを指定するのがポイントです。

```bash
# 踏み台サーバー（先にこのホストへ接続される）
Host bastion
    HostName 3.112.223.234
    User ec2-user
    IdentityFile ~/.ssh/yasuo-nakata.pem

# 踏み台経由で接続するサーバー（ProxyJump で bastion を指定）
Host web1-b
    HostName 43.207.170.213
    User ec2-user
    ProxyJump bastion
    IdentityFile ~/.ssh/yasuo-nakata.pem

Host web2-b
    HostName 13.231.32.15
    User ec2-user
    ProxyJump bastion
    IdentityFile ~/.ssh/yasuo-nakata.pem
```

- 接続例（`web1-b` に接続すると、自動的に `bastion` を経由します）:
```bash
ssh web1-b
```

#### 📍 2-4. 設定のポイント
- `Host` … 接続時に使うエイリアス名（任意）。`ssh <エイリアス>` で接続します。
- `HostName` … 実際の接続先 IP / ホスト名。
- `User` … ログインユーザー（EC2 の Amazon Linux 等は `ec2-user`）。
- `IdentityFile` … 公開鍵認証で使う秘密鍵（`.pem`）のパス。
- `ProxyJump` … 経由する踏み台のエイリアス。踏み台経由接続の鍵となる設定です。
- ダイレクト用（`web1` / `web2`）と踏み台経由用（`web1-b` / `web2-b`）でエイリアスを分けておくと、用途に応じて使い分けられます。
- ※ WinSCP で `.pem` を使う場合は、PuTTYgen で `.ppk` 形式に変換するか、WinSCP のインポート機能を利用します。

秘密鍵は権限を厳しくしておきます（Linux/macOS の場合）。

```bash
chmod 600 ~/.ssh/yasuo-nakata.pem
```

---

## 🧰 Tera Term

SSH / Telnet / **シリアル（COM ポート）** 接続に対応したターミナルエミュレータです。特にネットワーク機器や物理サーバへの**シリアルコンソール接続**で利用します。TTL マクロによる操作の自動化も可能です。

### ⚙️ 1. Tera Term のインストール

#### 📍 1-1. ダウンロード
- 以下の URL（公式サイト / GitHub リリース）にアクセスします。
  - https://teratermproject.github.io/index-en.html
  - リリース一覧: https://github.com/TeraTermProject/teraterm/releases
- Windows 用インストーラ（`teraterm-<バージョン>-x64.exe`、64bit）をダウンロードします。
  - 例（現行安定版）: `teraterm-5.6.1-x64.exe`

#### 📍 1-2. インストール
- インストーラを実行します。
- 基本は **Next 連打**でOKです（途中で表示言語の選択ができます）。

#### 📍 1-3. 動作確認
- スタートメニュー → Tera Term を起動します。
- 「新しい接続」ダイアログ（TCP/IP・シリアルの選択欄）が表示されれば成功です。

#### 📍 1-4. 補足（用途）
- **SSH 接続**: 「TCP/IP」を選び、ホスト・ユーザー・認証方法（パスワード / `.pem` 等の公開鍵）を指定します。
- **シリアル接続**: 「シリアル」を選び、対象の COM ポートとボーレートを指定します（ネットワーク機器のコンソール接続などで使用）。

---

## 🧰 Wireshark

ネットワークを流れるパケットをキャプチャ・解析するためのツールです。通信トラブルの調査（接続できない / 遅い / 想定外の通信がある、など）で使用します。

### ⚙️ 1. Wireshark のインストール

#### 📍 1-1. ダウンロード
- 以下の URL（公式ダウンロードページ）にアクセスします。
  - https://www.wireshark.org/download.html
- Windows 用インストーラ（`Wireshark-<バージョン>-x64.exe`、64bit）をダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します（UAC のダイアログが出たら「はい」で許可します）。
- 基本は **Next 連打**でOKです。
- ※ 途中で **Npcap のインストール**を求められます。**ライブキャプチャ（実際の通信の取得）には Npcap が必須**のため、チェックを入れたまま進めます。
  - Npcap インストール時、ネットワークアダプタへのドライバ組み込みのため**一瞬通信が切れることがあります**（正常な動作です）。

#### 📍 1-3. 動作確認
- スタートメニュー → Wireshark を起動します。
- 起動直後に**ネットワークインターフェース一覧**が表示され、各回線のトラフィックの波形が見えれば成功です。

#### 📍 1-4. 補足
- 既定のインストール先は `C:\Program Files\Wireshark` です。
- コマンドラインで使いたい場合は、インストール時のコンポーネント選択で **TShark**（CLI 版）を有効にできます。

---

## 🧰 WinMerge

### ⚙️ 1. WinMerge のインストール（ファイル比較ツール）

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://winmerge.org/downloads/?lang=ja
- **x64 (64-bit)** のインストーラをダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します。
- 基本は **Next 連打**でOKです。

#### 📍 1-3. 動作確認
- スタートメニュー → WinMerge を起動します。

---

## 🧰 JMeter

### ⚙️ 1. Java 17 のインストール

#### 📍 1-1. ダウンロード
- 以下の URL にアクセスします。
  - https://www.oracle.com/jp/java/technologies/downloads/
- Windows タブから **x64 Installer** をダウンロードします。

#### 📍 1-2. インストール
- インストーラを実行します。

#### 📍 1-3. 動作確認
```bash
java --version
```

### ⚙️ 2. JMeter 5.6 のインストール

#### 📍 2-1. ダウンロード
- 以下の URL にアクセスします。
  - https://jmeter.apache.org/download_jmeter.cgi
- バイナリ ZIP ファイル（`apache-jmeter-5.6.3.zip`）をダウンロードします。

#### 📍 2-2. 配置
- 解凍後、以下のフォルダに配置します。
  - `C:\apache-jmeter-5.6.3`

#### 📍 2-3. 環境変数の設定
- 検索窓で「**env**」を入力し、環境変数の設定を開きます。
- 新規にシステム変数を作成します。
  - 変数名: `JMETER_HOME`
  - 変数値: `C:\apache-jmeter-5.6.3`
- Path に以下を追加します。
  - `C:\apache-jmeter-5.6.3\bin`

#### 📍 2-4. 動作確認
```bash
jmeter
```
- GUI が起動すれば成功です。
