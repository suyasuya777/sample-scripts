#!/bin/bash
#===============================================================================
# Claude Code Bedrock 完全セットアップスクリプト (AWS CloudShell用)
# 
# 概要: Claude Code + S3マウント + EFSマウント + 環境変数の完全自動化
# 対象リージョン: ap-northeast-1 (東京)
# 
# 使用方法:
#   1. スクリプト冒頭の「設定セクション」で以下を設定してください:
#      - S3_BUCKET: S3バケット名（空の場合はスキップ）
#      - EFS_ID: EFSファイルシステムID（空の場合は自動検出を試行）
#      - REGION: AWSリージョン（デフォルト: ap-northeast-1）
#      - DEFAULT_MODEL: Claude モデル
#
#   2. スクリプトを実行:
#      source setup-claude-code.sh
#===============================================================================

# スクリプトが source で実行されているか確認
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo ""
    echo -e "\033[1;33m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
    echo -e "\033[1;33m 実行方法エラー\033[0m"
    echo -e "\033[1;33m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
    echo ""
    echo "このスクリプトは 'source' コマンドで実行する必要があります。"
    echo ""
    echo "正しい実行方法:"
    echo "  source $0"
    echo ""
    exit 1
fi

# エラーで終了しない（各ステップで個別にエラーハンドリング）
set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

#===============================================================================
# 設定セクション - ここで設定を変更してください
#===============================================================================

# S3バケット名（必要に応じて変更してください）
# 空文字列の場合、S3マウントをスキップします
S3_BUCKET="project-prod-abcdefgh-resources"

# EFSファイルシステムID（必要に応じて変更してください）
# 空文字列の場合、Billing=ate タグを持つEFSを自動検出します
EFS_ID=""

# AWSリージョン
REGION="ap-northeast-1"

# Claude Code のデフォルトモデル
DEFAULT_MODEL="jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

#===============================================================================

# セットアップ状態を記録
SETUP_STATUS=()

# Ctrl+C などでの中断をハンドリング
trap 'echo -e "\n${YELLOW}セットアップが中断されました${NC}"; return 130' INT TERM

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Claude Code Bedrock 完全セットアップ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}設定値${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  リージョン: ${REGION}"
if [ ! -z "$S3_BUCKET" ]; then
    echo "  S3バケット: ${S3_BUCKET}"
else
    echo "  S3バケット: 未設定（マウントをスキップ）"
fi
if [ ! -z "$EFS_ID" ]; then
    echo "  EFS ID: ${EFS_ID}"
else
    echo "  EFS ID: 未設定（自動検出を試行）"
fi
echo "  モデル: ${DEFAULT_MODEL}"
echo ""

#-------------------------------------------------------------------------------
# 1. 前提条件チェック
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[1/8] 前提条件チェック...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}エラー: AWS CLIがインストールされていません${NC}"
    SETUP_STATUS+=("前提条件:NG")
    return 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}エラー: npmがインストールされていません${NC}"
    SETUP_STATUS+=("前提条件:NG")
    return 1
else
    NPM_VERSION=$(npm --version 2>/dev/null)
    echo -e "${GREEN}✓ npm利用可能 (バージョン: ${NPM_VERSION})${NC}"
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}エラー: AWS認証が設定されていません${NC}"
    SETUP_STATUS+=("前提条件:NG")
    return 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ AWS認証OK (アカウント: ${ACCOUNT_ID})${NC}"
    SETUP_STATUS+=("前提条件:OK")
else
    echo -e "${RED}✗ AWS認証の確認に失敗${NC}"
    SETUP_STATUS+=("前提条件:NG")
fi

#-------------------------------------------------------------------------------
# 2. s3fs-fuse v1.91 のビルドとインストール
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[2/8] s3fs-fuse のインストール...${NC}"

S3FS_INSTALL_FAILED=false

if ! command -v s3fs &> /dev/null; then
    echo -e "${YELLOW}s3fs-fuse v1.91 をビルドしています (初回のみ2-3分)...${NC}"
    
    WORK_DIR="${HOME}/.s3fs-build"
    rm -rf "${WORK_DIR}"
    mkdir -p "${WORK_DIR}"
    cd "${WORK_DIR}"
    
    sudo yum install -y automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel pkg-config wget &> /dev/null
    
    if wget -q https://github.com/s3fs-fuse/s3fs-fuse/archive/refs/tags/v1.91.tar.gz; then
        tar -xzf v1.91.tar.gz
        cd s3fs-fuse-1.91
        
        if ./autogen.sh &> /dev/null && \
           ./configure --prefix=/usr --with-openssl &> /dev/null && \
           make -j$(nproc) &> /dev/null && \
           sudo make install &> /dev/null; then
            
            if command -v s3fs &> /dev/null; then
                echo -e "${GREEN}✓ s3fs-fuse インストール完了${NC}"
                SETUP_STATUS+=("s3fs-fuse:OK")
                cd "${HOME}"
                rm -rf "${WORK_DIR}"
            else
                echo -e "${RED}✗ s3fs-fuseのインストールに失敗しました${NC}"
                S3FS_INSTALL_FAILED=true
                SETUP_STATUS+=("s3fs-fuse:NG")
            fi
        else
            echo -e "${RED}✗ s3fs-fuseのビルドに失敗しました${NC}"
            S3FS_INSTALL_FAILED=true
            SETUP_STATUS+=("s3fs-fuse:NG")
        fi
    else
        echo -e "${RED}✗ s3fs-fuseのダウンロードに失敗しました${NC}"
        S3FS_INSTALL_FAILED=true
        SETUP_STATUS+=("s3fs-fuse:NG")
    fi
    
    cd "${HOME}"
else
    echo -e "${GREEN}✓ s3fs-fuse インストール済み${NC}"
    SETUP_STATUS+=("s3fs-fuse:既存")
fi

#-------------------------------------------------------------------------------
# 3. S3バケットのマウント
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[3/8] S3バケットのマウント...${NC}"

if [ -z "$S3_BUCKET" ]; then
    echo -e "${YELLOW}S3バケット名が設定されていません${NC}"
    echo -e "${YELLOW}S3マウントをスキップします${NC}"
    echo -e "${BLUE}ヒント: スクリプト冒頭の設定セクションで S3_BUCKET を設定してください${NC}"
    SETUP_STATUS+=("S3マウント:スキップ")
elif [ "$S3FS_INSTALL_FAILED" = "false" ] && command -v s3fs &> /dev/null; then
    S3_MOUNT_POINT="/mnt/s3"

    # /etc/fuse.confでallow_otherを有効化
    if ! grep -q "^user_allow_other" /etc/fuse.conf 2>/dev/null; then
        echo "user_allow_other" | sudo tee -a /etc/fuse.conf > /dev/null
        echo -e "${GREEN}✓ /etc/fuse.confを設定しました${NC}"
    fi

    # マウントポイント作成
    if [ ! -d "${S3_MOUNT_POINT}" ]; then
        sudo mkdir -p "${S3_MOUNT_POINT}"
        echo -e "${GREEN}✓ マウントポイント作成: ${S3_MOUNT_POINT}${NC}"
    fi

    # マウント状態を確認
    if mountpoint -q "${S3_MOUNT_POINT}" 2>/dev/null; then
        echo -e "${YELLOW}S3バケットは既にマウントされています${NC}"
        SETUP_STATUS+=("S3マウント:既存")
    else
        echo -e "${BLUE}S3バケットをマウント中...${NC}"
        
        # AWS認証情報を環境変数に取得
        if source <(aws configure export-credentials --format env-no-export) 2>/dev/null; then
            echo -e "${GREEN}✓ AWS認証情報を取得しました${NC}"
            
            # 環境変数を明示的に渡してマウント
            if sudo AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
                    AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
                    AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN}" \
                    s3fs "${S3_BUCKET}" "${S3_MOUNT_POINT}" \
                    -o use_session_token \
                    -o allow_other \
                    -o uid=$(id -u) \
                    -o gid=$(id -g) \
                    -o umask=022; then
                sleep 1
                if mountpoint -q "${S3_MOUNT_POINT}" 2>/dev/null; then
                    OWNER=$(stat -c '%U:%G' "${S3_MOUNT_POINT}" 2>/dev/null)
                    PERMS=$(stat -c '%a' "${S3_MOUNT_POINT}" 2>/dev/null)
                    echo -e "${GREEN}✓ S3バケットマウント成功: ${S3_BUCKET} -> ${S3_MOUNT_POINT}${NC}"
                    echo -e "${GREEN}✓ 所有者: ${OWNER}${NC}"
                    echo -e "${GREEN}✓ パーミッション: ${PERMS}${NC}"
                    SETUP_STATUS+=("S3マウント:OK")
                else
                    echo -e "${RED}✗ S3マウントの確認に失敗${NC}"
                    SETUP_STATUS+=("S3マウント:NG")
                fi
            else
                echo -e "${RED}✗ S3マウントコマンドが失敗${NC}"
                SETUP_STATUS+=("S3マウント:NG")
            fi
        else
            echo -e "${RED}✗ AWS認証情報の取得に失敗しました${NC}"
            SETUP_STATUS+=("S3マウント:NG")
        fi
    fi

    # 互換性のためシンボリックリンクを作成
    if [ ! -e "${HOME}/s3" ] && [ -d "${S3_MOUNT_POINT}" ]; then
        ln -s "${S3_MOUNT_POINT}" "${HOME}/s3" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ シンボリックリンク作成: ~/s3 -> ${S3_MOUNT_POINT}${NC}"
        fi
    fi

    # .bashrcにS3自動マウント設定を追加
    if ! grep -q "# S3 Auto Mount Configuration" ~/.bashrc 2>/dev/null; then
        cat >> ~/.bashrc << BASHRC_S3_EOF

# S3 Auto Mount Configuration
# S3バケット名（スクリプト実行時に設定）
S3_BUCKET="${S3_BUCKET}"

# S3バケットが設定されている場合のみマウント
if [ ! -z "\${S3_BUCKET}" ]; then
    if ! command -v s3fs &> /dev/null; then
        echo "s3fs-fuse をインストールしています（初回のみ2-3分）..."
        WORK_DIR="\${HOME}/.s3fs-build"
        mkdir -p "\${WORK_DIR}"
        cd "\${WORK_DIR}" 2>/dev/null
        sudo yum install -y automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel pkg-config wget &> /dev/null
        wget -q https://github.com/s3fs-fuse/s3fs-fuse/archive/refs/tags/v1.91.tar.gz
        tar -xzf v1.91.tar.gz
        cd s3fs-fuse-1.91
        ./autogen.sh &> /dev/null
        ./configure --prefix=/usr --with-openssl &> /dev/null
        make -j\$(nproc) &> /dev/null
        sudo make install &> /dev/null
        if command -v s3fs &> /dev/null; then
            echo "✓ s3fs-fuse インストール完了"
            cd "\${HOME}"
            rm -rf "\${WORK_DIR}"
        fi
        cd "\${HOME}" 2>/dev/null
    fi

    # /etc/fuse.confでallow_otherを有効化
    if ! grep -q "^user_allow_other" /etc/fuse.conf 2>/dev/null; then
        echo "user_allow_other" | sudo tee -a /etc/fuse.conf > /dev/null
    fi

    S3_MOUNT_POINT="/mnt/s3"

    # マウントポイント作成
    if [ ! -d "\${S3_MOUNT_POINT}" ]; then
        sudo mkdir -p "\${S3_MOUNT_POINT}" 2>/dev/null
    fi

    # S3マウント (CloudShellではコンテナロール認証を使用)
    if command -v s3fs &> /dev/null && ! mountpoint -q "\${S3_MOUNT_POINT}" 2>/dev/null; then
        # AWS認証情報を環境変数に取得
        if source <(aws configure export-credentials --format env-no-export) 2>/dev/null; then
            # 環境変数を明示的に渡してマウント
            sudo AWS_ACCESS_KEY_ID="\${AWS_ACCESS_KEY_ID}" \
                 AWS_SECRET_ACCESS_KEY="\${AWS_SECRET_ACCESS_KEY}" \
                 AWS_SESSION_TOKEN="\${AWS_SESSION_TOKEN}" \
                 s3fs "\${S3_BUCKET}" "\${S3_MOUNT_POINT}" \
                 -o use_session_token \
                 -o allow_other \
                 -o uid=\$(id -u) \
                 -o gid=\$(id -g) \
                 -o umask=022 2>/dev/null
            
            if mountpoint -q "\${S3_MOUNT_POINT}" 2>/dev/null; then
                echo "✓ S3バケット \${S3_BUCKET} がマウントされました: \${S3_MOUNT_POINT}"
            fi
        fi
    fi

    # シンボリックリンク作成
    if [ ! -e "\${HOME}/s3" ] && [ -d "\${S3_MOUNT_POINT}" ]; then
        ln -s "\${S3_MOUNT_POINT}" "\${HOME}/s3" 2>/dev/null
    fi
fi
BASHRC_S3_EOF
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ .bashrcにS3自動マウント設定を追加しました${NC}"
        else
            echo -e "${RED}✗ .bashrcへの設定追加に失敗しました${NC}"
        fi
    fi
else
    echo -e "${YELLOW}s3fs-fuseが利用できないため、S3マウントをスキップします${NC}"
    SETUP_STATUS+=("S3マウント:スキップ")
fi

#-------------------------------------------------------------------------------
# 4. EFSファイルシステムの検出
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[4/8] EFSファイルシステムを検出中...${NC}"

# EFS_ID が設定されている場合
if [ ! -z "$EFS_ID" ]; then
    echo -e "${GREEN}✓ EFSファイルシステムID（設定値）: ${EFS_ID}${NC}"
    SETUP_STATUS+=("EFS検出:設定値")
else
    # 自動検出を試行（Billing=ate タグで検索）
    echo -e "${BLUE}EFS IDが未設定のため、自動検出を試行します...${NC}"
    EFS_ID=$(aws efs describe-file-systems \
      --region ${REGION} \
      --query "FileSystems[?Tags[?Key=='Billing' && Value=='ate']].FileSystemId" \
      --output text 2>/dev/null)
    
    if [ ! -z "$EFS_ID" ]; then
        echo -e "${GREEN}✓ EFSファイルシステム検出（自動検出）: ${EFS_ID}${NC}"
        SETUP_STATUS+=("EFS検出:自動検出")
    else
        echo -e "${YELLOW}Billing=ate タグを持つEFSファイルシステムが見つかりませんでした${NC}"
        echo -e "${BLUE}ヒント: スクリプト冒頭の設定セクションで EFS_ID を設定してください${NC}"
        SETUP_STATUS+=("EFS検出:スキップ")
    fi
fi

#-------------------------------------------------------------------------------
# 5. EFSのマウント
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[5/8] EFSをマウント中...${NC}"

if [ ! -z "$EFS_ID" ]; then
    EFS_MOUNT_POINT="/mnt/efs"
    
    # マウントポイント作成
    if [ ! -d "${EFS_MOUNT_POINT}" ]; then
        sudo mkdir -p "${EFS_MOUNT_POINT}"
        echo -e "${GREEN}✓ マウントポイント作成: ${EFS_MOUNT_POINT}${NC}"
    fi
    
    # EFSマウント状態を確認
    if mountpoint -q "${EFS_MOUNT_POINT}" 2>/dev/null; then
        echo -e "${YELLOW}EFSは既にマウントされています${NC}"
        SETUP_STATUS+=("EFSマウント:既存")
    else
        echo -e "${BLUE}EFSをマウント中...${NC}"
        if sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \
            ${EFS_ID}.efs.${REGION}.amazonaws.com:/ ${EFS_MOUNT_POINT}; then
            sleep 1
            
            # マウント成功確認
            if mountpoint -q "${EFS_MOUNT_POINT}" 2>/dev/null; then
                # 所有権をcloudshell-userに変更
                sudo chown cloudshell-user:cloudshell-user "${EFS_MOUNT_POINT}" 2>/dev/null
                sudo chmod 755 "${EFS_MOUNT_POINT}" 2>/dev/null
                
                OWNER=$(stat -c '%U:%G' "${EFS_MOUNT_POINT}" 2>/dev/null)
                PERMS=$(stat -c '%a' "${EFS_MOUNT_POINT}" 2>/dev/null)
                echo -e "${GREEN}✓ EFSマウント成功: ${EFS_ID} -> ${EFS_MOUNT_POINT}${NC}"
                echo -e "${GREEN}✓ 所有者: ${OWNER}${NC}"
                echo -e "${GREEN}✓ パーミッション: ${PERMS}${NC}"
                SETUP_STATUS+=("EFSマウント:OK")
            else
                echo -e "${RED}✗ EFSマウントの確認に失敗${NC}"
                SETUP_STATUS+=("EFSマウント:NG")
            fi
        else
            echo -e "${RED}✗ EFSマウントコマンドが失敗しました${NC}"
            echo -e "${YELLOW}  VPC CloudShellが正しく設定されているか確認してください${NC}"
            echo -e "${YELLOW}  EFSのセキュリティグループがNFS(2049)を許可しているか確認してください${NC}"
            SETUP_STATUS+=("EFSマウント:NG")
        fi
    fi
    
    # 互換性のためシンボリックリンクを作成
    if [ ! -e "${HOME}/efs" ] && [ -d "${EFS_MOUNT_POINT}" ]; then
        ln -s "${EFS_MOUNT_POINT}" "${HOME}/efs" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ シンボリックリンク作成: ~/efs -> ${EFS_MOUNT_POINT}${NC}"
        fi
    fi
    
    # .bashrcにEFS自動マウント設定を追加
    if ! grep -q "# EFS Auto Mount Configuration" ~/.bashrc 2>/dev/null; then
        cat >> ~/.bashrc << BASHRC_EFS_EOF

# EFS Auto Mount Configuration
EFS_ID="${EFS_ID}"
EFS_MOUNT_POINT="/mnt/efs"
REGION="${REGION}"

if [ ! -z "\$EFS_ID" ]; then
    # マウントポイント作成
    if [ ! -d "\${EFS_MOUNT_POINT}" ]; then
        sudo mkdir -p "\${EFS_MOUNT_POINT}" 2>/dev/null
    fi
    
    # EFSマウント
    if ! mountpoint -q "\${EFS_MOUNT_POINT}" 2>/dev/null; then
        sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \
            \${EFS_ID}.efs.\${REGION}.amazonaws.com:/ \${EFS_MOUNT_POINT} 2>/dev/null
        
        if mountpoint -q "\${EFS_MOUNT_POINT}" 2>/dev/null; then
            sudo chown cloudshell-user:cloudshell-user "\${EFS_MOUNT_POINT}" 2>/dev/null
            sudo chmod 755 "\${EFS_MOUNT_POINT}" 2>/dev/null
            echo "✓ EFS \${EFS_ID} がマウントされました: \${EFS_MOUNT_POINT}"
        fi
    fi
    
    # シンボリックリンク作成
    if [ ! -e "\${HOME}/efs" ] && [ -d "\${EFS_MOUNT_POINT}" ]; then
        ln -s "\${EFS_MOUNT_POINT}" "\${HOME}/efs" 2>/dev/null
    fi
fi
BASHRC_EFS_EOF
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ .bashrcにEFS自動マウント設定を追加しました${NC}"
        else
            echo -e "${RED}✗ .bashrcへの設定追加に失敗しました${NC}"
        fi
    fi
else
    echo -e "${YELLOW}EFSファイルシステムが見つからないため、マウントをスキップします${NC}"
    SETUP_STATUS+=("EFSマウント:スキップ")
fi

#-------------------------------------------------------------------------------
# 6. Claude Code のインストール
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[6/8] Claude Code をインストール中...${NC}"

# npm 自体は CloudShell にプリインストール済み
# グローバルインストール先をホームディレクトリに変更
NPM_PREFIX="${HOME}/.npm-global"
if [ ! -d "${NPM_PREFIX}" ]; then
    mkdir -p "${NPM_PREFIX}"
    echo -e "${GREEN}✓ npm グローバルディレクトリを作成: ${NPM_PREFIX}${NC}"
fi

# npm のグローバルインストール先を設定（/usr/local から変更）
npm config set prefix "${NPM_PREFIX}"
export PATH="${NPM_PREFIX}/bin:${PATH}"

if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null | head -1 || echo "不明")
    echo -e "${GREEN}✓ Claude Code インストール済み (${CLAUDE_VERSION})${NC}"
    SETUP_STATUS+=("Claude Code:既存")
else
    echo -e "${BLUE}Claude Code をインストールしています...${NC}"
    NPM_OUTPUT=$(npm install -g @anthropic-ai/claude-code 2>&1)
    NPM_EXIT_CODE=$?
    
    if [ $NPM_EXIT_CODE -eq 0 ]; then
        # PATH を更新
        export PATH="${NPM_PREFIX}/bin:${PATH}"
        
        if command -v claude &> /dev/null; then
            CLAUDE_VERSION=$(claude --version 2>/dev/null | head -1 || echo "不明")
            echo -e "${GREEN}✓ Claude Code インストール完了 (${CLAUDE_VERSION})${NC}"
            SETUP_STATUS+=("Claude Code:OK")
        else
            echo -e "${RED}✗ Claude Codeのインストールに失敗しました${NC}"
            echo -e "${YELLOW}PATH: ${PATH}${NC}"
            echo -e "${YELLOW}インストール先を確認: ls -la ${NPM_PREFIX}/bin/${NC}"
            ls -la "${NPM_PREFIX}/bin/" 2>/dev/null | head -5
            SETUP_STATUS+=("Claude Code:NG")
        fi
    else
        echo -e "${RED}✗ Claude Code パッケージのインストールに失敗しました${NC}"
        echo -e "${YELLOW}エラー詳細:${NC}"
        echo "${NPM_OUTPUT}" | tail -10
        SETUP_STATUS+=("Claude Code:NG")
    fi
fi

#-------------------------------------------------------------------------------
# 7. 環境変数の設定
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[7/8] 環境変数を設定中...${NC}"

export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=${REGION}
export ANTHROPIC_MODEL=${DEFAULT_MODEL}

# npm グローバルコマンドのPATH設定
NPM_PREFIX="${HOME}/.npm-global"
if [ ! -d "${NPM_PREFIX}" ]; then
    mkdir -p "${NPM_PREFIX}"
fi
npm config set prefix "${NPM_PREFIX}" 2>/dev/null
export PATH="${NPM_PREFIX}/bin:${PATH}"

if ! grep -q "# Claude Code Bedrock Configuration" ~/.bashrc 2>/dev/null; then
    cat >> ~/.bashrc << BASHRC_ENV_EOF

# Claude Code Bedrock Configuration
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=${REGION}
export ANTHROPIC_MODEL=${DEFAULT_MODEL}

# npm グローバルコマンドのPATH設定
export PATH="\${HOME}/.npm-global/bin:\${PATH}"
BASHRC_ENV_EOF
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ .bashrcに環境変数を追加しました${NC}"
        SETUP_STATUS+=("環境変数:OK")
    else
        echo -e "${RED}✗ .bashrcへの環境変数追加に失敗しました${NC}"
        SETUP_STATUS+=("環境変数:NG")
    fi
else
    echo -e "${GREEN}✓ 環境変数は既に設定済みです${NC}"
    SETUP_STATUS+=("環境変数:既存")
fi

#-------------------------------------------------------------------------------
# 7.5. Claude Code 設定ファイルの作成
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[7.5/8] Claude Code 設定ファイルを作成中...${NC}"

CLAUDE_DIR="${HOME}/.claude"
CLAUDE_SETTINGS="${CLAUDE_DIR}/settings.json"

# .claude ディレクトリの作成
if [ ! -d "${CLAUDE_DIR}" ]; then
    mkdir -p "${CLAUDE_DIR}"
    echo -e "${GREEN}✓ ${CLAUDE_DIR} ディレクトリを作成しました${NC}"
fi

# settings.json の作成または更新
if [ ! -f "${CLAUDE_SETTINGS}" ]; then
    cat > "${CLAUDE_SETTINGS}" << SETTINGS_EOF
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "${REGION}",
    "ANTHROPIC_MODEL": "${DEFAULT_MODEL}"
  }
}
SETTINGS_EOF
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${CLAUDE_SETTINGS} を作成しました${NC}"
        SETUP_STATUS+=("Claude設定:OK")
    else
        echo -e "${RED}✗ 設定ファイルの作成に失敗しました${NC}"
        SETUP_STATUS+=("Claude設定:NG")
    fi
else
    echo -e "${YELLOW}設定ファイルは既に存在します: ${CLAUDE_SETTINGS}${NC}"
    echo -e "${BLUE}現在の設定:${NC}"
    cat "${CLAUDE_SETTINGS}" | head -20
    SETUP_STATUS+=("Claude設定:既存")
fi

# Claude Code の認証状態を確認
if command -v claude &> /dev/null; then
    echo ""
    echo -e "${BLUE}Claude Code 認証状態を確認中...${NC}"
    AUTH_STATUS=$(claude auth status 2>&1)
    
    if echo "${AUTH_STATUS}" | grep -q '"loggedIn": true' && echo "${AUTH_STATUS}" | grep -q '"apiProvider": "bedrock"'; then
        echo -e "${GREEN}✓ Bedrock 認証成功${NC}"
        echo "${AUTH_STATUS}" | grep -E '"(loggedIn|authMethod|apiProvider)"'
        SETUP_STATUS+=("Bedrock認証:OK")
    else
        echo -e "${YELLOW}認証状態:${NC}"
        echo "${AUTH_STATUS}"
        SETUP_STATUS+=("Bedrock認証:確認必要")
    fi
else
    echo -e "${YELLOW}claude コマンドが見つかりません。PATHを確認してください。${NC}"
fi

#-------------------------------------------------------------------------------
# 8. Playwright共有設定
#-------------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}[8/8] Playwright共有設定...${NC}"

PLAYWRIGHT_SHARED_DIR="/mnt/efs/playwright"

# Playwright共有ディレクトリの存在確認
if [ -d "$PLAYWRIGHT_SHARED_DIR" ]; then
    echo -e "${GREEN}✓ Playwright共有ディレクトリ検出: ${PLAYWRIGHT_SHARED_DIR}${NC}"
    
    # 環境変数を現在のセッションに適用
    export NODE_PATH="${PLAYWRIGHT_SHARED_DIR}/node_modules:${NODE_PATH}"
    export PATH="${PLAYWRIGHT_SHARED_DIR}/node_modules/.bin:${PATH}"
    export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_SHARED_DIR}/browsers"
    
    # .bashrcにPlaywright共有設定を追加
    if ! grep -q "# Playwright Shared Configuration" ~/.bashrc 2>/dev/null; then
        cat >> ~/.bashrc << 'BASHRC_PLAYWRIGHT_EOF'

# Playwright Shared Configuration
PLAYWRIGHT_SHARED_DIR="/mnt/efs/playwright"

if [ -d "$PLAYWRIGHT_SHARED_DIR" ]; then
    export NODE_PATH="${PLAYWRIGHT_SHARED_DIR}/node_modules:${NODE_PATH}"
    export PATH="${PLAYWRIGHT_SHARED_DIR}/node_modules/.bin:${PATH}"
    export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_SHARED_DIR}/browsers"
fi
BASHRC_PLAYWRIGHT_EOF
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ .bashrcにPlaywright共有設定を追加しました${NC}"
            SETUP_STATUS+=("Playwright設定:OK")
        else
            echo -e "${RED}✗ .bashrcへのPlaywright設定追加に失敗しました${NC}"
            SETUP_STATUS+=("Playwright設定:NG")
        fi
    else
        echo -e "${GREEN}✓ Playwright共有設定は既に設定済みです${NC}"
        SETUP_STATUS+=("Playwright設定:既存")
    fi
    
    # Playwrightが正しく動作するか確認
    if command -v playwright &> /dev/null; then
        PLAYWRIGHT_VERSION=$(playwright --version 2>/dev/null || echo "不明")
        echo -e "${GREEN}✓ Playwright利用可能 (${PLAYWRIGHT_VERSION})${NC}"
    else
        echo -e "${YELLOW}Playwrightコマンドが見つかりません${NC}"
        echo -e "${YELLOW}  ${PLAYWRIGHT_SHARED_DIR}/node_modules/.bin/playwright を確認してください${NC}"
    fi
else
    echo -e "${YELLOW}Playwright共有ディレクトリが見つかりません${NC}"
    echo -e "${YELLOW}  EFS上にPlaywrightをインストールする場合：${NC}"
    echo "    mkdir -p /mnt/efs/playwright"
    echo "    cd /mnt/efs/playwright"
    echo "    npm init -y"
    echo "    npm install playwright @playwright/test"
    echo "    export PLAYWRIGHT_BROWSERS_PATH=/mnt/efs/playwright/browsers"
    echo "    npx playwright install"
    SETUP_STATUS+=("Playwright設定:スキップ")
fi

source ~/.bashrc 2>/dev/null

echo -e "${GREEN}✓ 環境変数設定完了${NC}"

#-------------------------------------------------------------------------------
# セットアップ完了
#-------------------------------------------------------------------------------
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} セットアップ完了${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# セットアップ状態のサマリー表示
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}セットアップ状態${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
for status in "${SETUP_STATUS[@]}"; do
    echo "  $status"
done
echo ""

# 所有権の確認と表示
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}マウントポイント所有権確認${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ -d "/mnt/s3" ]; then
    S3_OWNER=$(stat -c '%U:%G' /mnt/s3 2>/dev/null || echo "確認不可")
    S3_MOUNTED=$(mountpoint -q /mnt/s3 2>/dev/null && echo "✓" || echo "✗")
    echo "  /mnt/s3: ${S3_OWNER} (マウント: ${S3_MOUNTED})"
fi
if [ -d "/mnt/efs" ]; then
    EFS_OWNER=$(stat -c '%U:%G' /mnt/efs 2>/dev/null || echo "確認不可")
    EFS_MOUNTED=$(mountpoint -q /mnt/efs 2>/dev/null && echo "✓" || echo "✗")
    echo "  /mnt/efs: ${EFS_OWNER} (マウント: ${EFS_MOUNTED})"
fi
echo ""

if [ "$S3FS_INSTALL_FAILED" = "false" ] && command -v s3fs &> /dev/null && [ ! -z "$S3_BUCKET" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}S3マウント情報${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  マウントポイント: /mnt/s3"
    echo "  シンボリックリンク: ~/s3 -> /mnt/s3"
    echo "  S3バケット: ${S3_BUCKET}"
    echo "  所有者: $(stat -c '%U:%G' /mnt/s3 2>/dev/null || echo '確認不可')"
    echo "  パーミッション: $(stat -c '%a' /mnt/s3 2>/dev/null || echo '確認不可')"
    echo "  マウント状態: $(mountpoint -q /mnt/s3 2>/dev/null && echo '✓ マウント済み' || echo '未マウント')"
    echo "  認証方式: コンテナロール（セッショントークン使用）"
    echo ""
    
    echo -e "${BLUE}S3ファイル操作例:${NC}"
    echo "  ls /mnt/s3/                       # ファイル一覧"
    echo "  ls ~/s3/                          # シンボリックリンク経由"
    echo "  cd /mnt/s3/terraform/             # ディレクトリ移動"
    echo "  cat /mnt/s3/data/file.txt         # ファイル内容表示"
    echo "  vim /mnt/s3/config.yaml           # ファイル編集"
    echo ""
fi

if [ ! -z "$EFS_ID" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}EFSマウント情報${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  マウントポイント: /mnt/efs"
    echo "  シンボリックリンク: ~/efs -> /mnt/efs"
    echo "  EFS ID: ${EFS_ID}"
    echo "  所有者: $(stat -c '%U:%G' /mnt/efs 2>/dev/null || echo '確認不可')"
    echo "  パーミッション: $(stat -c '%a' /mnt/efs 2>/dev/null || echo '確認不可')"
    echo "  マウント状態: $(mountpoint -q /mnt/efs 2>/dev/null && echo '✓ マウント済み' || echo '未マウント')"
    echo "  マウント方式: NFS4（TLS暗号化なし）"
    echo ""
    
    echo -e "${BLUE}EFSファイル操作例:${NC}"
    echo "  ls /mnt/efs/                      # ファイル一覧"
    echo "  ls ~/efs/                         # シンボリックリンク経由"
    echo "  echo 'test' > /mnt/efs/test.txt   # ファイル作成"
    echo "  df -h /mnt/efs                    # 使用量確認"
    echo ""
    
    echo -e "${BLUE}Playwrightインストール例:${NC}"
    echo "  mkdir -p /mnt/efs/playwright"
    echo "  cd /mnt/efs/playwright"
    echo "  npm init -y"
    echo "  npm install playwright"
    echo "  export PLAYWRIGHT_BROWSERS_PATH=/mnt/efs/playwright/browsers"
    echo "  npx playwright install chromium firefox webkit"
    echo ""
fi

if [ -d "$PLAYWRIGHT_SHARED_DIR" ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Playwright共有設定${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "  共有ディレクトリ: ${PLAYWRIGHT_SHARED_DIR}"
    echo "  ブラウザパス: ${PLAYWRIGHT_SHARED_DIR}/browsers"
    echo ""
    
    echo -e "${BLUE}Playwright使用例:${NC}"
    echo "  playwright --version              # バージョン確認"
    echo "  npx playwright test               # テスト実行"
    echo "  npx playwright codegen            # コード生成"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Claude Code 使用方法${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  claude \"こんにちは\""
echo "  claude                               # インタラクティブモード"
echo "  claude --print \"プロンプト\"          # 非対話モード"
echo ""
echo -e "${BLUE}認証状態の確認:${NC}"
echo "  claude auth status                   # Bedrock 認証状態を確認"
echo ""
echo -e "${BLUE}設定ファイル:${NC}"
echo "  ~/.claude/settings.json              # Claude Code 設定ファイル"
echo "  ~/.bashrc                             # 環境変数設定"
echo ""
echo -e "${BLUE}利用可能なモデル:${NC}"
echo "  jp.anthropic.claude-opus-4-5-20251101-v1:0     (デフォルト・最高性能)"
echo "  jp.anthropic.claude-sonnet-4-5-20250929-v1:0   (バランス)"
echo "  jp.anthropic.claude-haiku-4-5-20251001-v1:0    (高速)"
echo ""
echo -e "${YELLOW}次回ログイン時:${NC}"
echo "  ✓ npm グローバルディレクトリが自動設定 (~/.npm-global)"
if [ ! -z "$S3_BUCKET" ]; then
    echo "  ✓ s3fs-fuseが自動インストール（初回のみ2-3分）"
    echo "  ✓ S3バケットが自動マウント (/mnt/s3)"
    echo "    - バケット: ${S3_BUCKET}"
    echo "    - コンテナロール認証（セッショントークンを自動取得）"
    echo "    - cloudshell-userが所有者に設定"
else
    echo "  ℹ S3マウント未設定"
    echo "    - 使用する場合: スクリプト冒頭で S3_BUCKET を設定"
fi
if [ ! -z "$EFS_ID" ]; then
    echo "  ✓ EFSが自動マウント (/mnt/efs)"
    echo "    - EFS ID: ${EFS_ID}"
    echo "    - NFS4方式でマウント（TLS暗号化なし）"
    echo "    - マウント成功後にchown/chgrpで所有権変更"
else
    echo "  ℹ EFSマウント未設定"
    echo "    - 使用する場合: スクリプト冒頭で EFS_ID を設定"
fi
if [ -d "$PLAYWRIGHT_SHARED_DIR" ]; then
    echo "  ✓ Playwright共有環境が自動設定"
fi
echo "  ✓ 環境変数が自動設定"
echo "  ✓ Claude Code が Bedrock 経由で自動認証"
echo "    - ~/.claude/settings.json に設定保存済み"
echo ""
if [ ! -z "$S3_BUCKET" ] || [ ! -z "$EFS_ID" ]; then
    echo -e "${YELLOW}/dev/loop0 の容量節約:${NC}"
    echo "  ✓ /mnt 配下にマウントすることで /dev/loop0 の容量を大幅に削減"
    if [ ! -z "$S3_BUCKET" ]; then
        echo "  ✓ S3はセッショントークン認証で自動マウント、cloudshell-userが所有者"
    fi
    if [ ! -z "$EFS_ID" ]; then
        echo "  ✓ EFSはマウント後にcloudshell-userに変更"
    fi
    echo "  ✓ 互換性のため ~/s3 と ~/efs のシンボリックリンクを自動作成"
    echo ""
fi
echo -e "${YELLOW}トラブルシューティング:${NC}"
echo "  claude コマンドが見つからない場合:"
echo "    export PATH=\"\${HOME}/.npm-global/bin:\${PATH}\""
echo "    source ~/.bashrc"
echo ""
echo "  Bedrock 認証を確認:"
echo "    claude auth status"
echo ""
echo "  設定ファイルを確認:"
echo "    cat ~/.claude/settings.json"
echo ""
