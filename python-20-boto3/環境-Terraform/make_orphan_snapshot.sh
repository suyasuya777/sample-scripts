#!/usr/bin/env bash
# ec2_snapshots.py の「孤立スナップショット」検出の題材を作る。
#
# 孤立＝スナップショットの元ボリュームがすでに存在しない状態。
# Terraform の依存関係では「ボリュームを消してスナップショットを残す」が
# 表現できないため、このスクリプトで作る。
#
# 使用: 1/26（火）の学習前に1回だけ実行する
# 削除: terraform destroy では消えない。2/28 に delete_orphan_snapshot.sh を実行

set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-ap-northeast-1}"
AZ="$(aws ec2 describe-availability-zones --region "$REGION" \
  --query 'AvailabilityZones[0].ZoneName' --output text)"

echo "[1/4] ボリュームを作成"
VOL=$(aws ec2 create-volume --region "$REGION" \
  --availability-zone "$AZ" --size 1 --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Project,Value=boto3-study},{Key=Name,Value=boto3-study-orphan-source}]' \
  --query VolumeId --output text)
aws ec2 wait volume-available --region "$REGION" --volume-ids "$VOL"
echo "      volume: $VOL"

echo "[2/4] スナップショットを作成"
SNAP=$(aws ec2 create-snapshot --region "$REGION" \
  --volume-id "$VOL" --description "boto3-study orphan snapshot" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Project,Value=boto3-study},{Key=Name,Value=boto3-study-orphan}]' \
  --query SnapshotId --output text)

echo "[3/4] スナップショット完了を待機（数分かかります）"
aws ec2 wait snapshot-completed --region "$REGION" --snapshot-ids "$SNAP"
echo "      snapshot: $SNAP"

echo "[4/4] 元ボリュームを削除（これで孤立状態になる）"
aws ec2 delete-volume --region "$REGION" --volume-id "$VOL"

echo
echo "完了。孤立スナップショット: $SNAP"
echo "ec2_snapshots.py を実行すると、このスナップショットが検出されます。"
echo "2/28 に scripts/delete_orphan_snapshot.sh で削除してください。"
