#!/usr/bin/env bash
# pymysql の Lambda Layer を作る。
#
# Lambda に同梱されているのは boto3 だけ。pymysql は自分で持ち込む必要がある。
# （3/25 の「ModuleNotFoundError」の対処）
#
# 使用: enable_rds = true にする前に1回実行する
#   bash scripts/build_layers.sh
#
# Layer の zip は python/ ディレクトリを root に持つ必要がある。

set -euo pipefail

cd "$(dirname "$0")/.."
BUILD=".build/pymysql-layer"
RUNTIME_PY="python3.12"

echo "[1/3] 既存のビルドを削除"
rm -rf "$BUILD" .build/pymysql-layer.zip
mkdir -p "$BUILD/python"

echo "[2/3] pymysql をインストール"
# Lambda の実行環境（Amazon Linux 2023 / x86_64）に合わせる。
# pymysql は純粋な Python なのでプラットフォーム指定は不要だが、
# psycopg2 などバイナリを含むパッケージでは --platform の指定が要る。
pip install pymysql \
  --target "$BUILD/python" \
  --only-binary=:all: \
  --quiet 2>/dev/null || pip install pymysql --target "$BUILD/python" --quiet

echo "[3/3] zip 化"
( cd "$BUILD" && zip -r -q ../pymysql-layer.zip python )

echo
echo "完了: .build/pymysql-layer.zip"
unzip -l .build/pymysql-layer.zip | head -8
echo
echo "この後 enable_rds = true にして terraform apply してください。"
