#!/usr/bin/env bash
# terraform destroy では消えないものを掃除する。
# 2/28（日）に terraform destroy の「前」に実行すること。
#
# 対象:
#   - 孤立スナップショット（make_orphan_snapshot.sh で作ったもの）
#   - 手動 RDS スナップショット（2/22 に boto3 で作ったもの）
#   - boto3 の演習中に作った Lambda バージョン / エイリアス等は関数ごと消えるので対象外

set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-ap-northeast-1}"
ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"

echo "=== 1. Project=boto3-study タグのリソース一覧 ==="
aws resourcegroupstaggingapi get-resources --region "$REGION" \
  --tag-filters Key=Project,Values=boto3-study \
  --query 'ResourceTagMappingList[].ResourceARN' --output table || true

echo
echo "=== 2. 自前所有のEBSスナップショット ==="
aws ec2 describe-snapshots --region "$REGION" --owner-ids "$ACCOUNT" \
  --query 'Snapshots[].[SnapshotId,VolumeId,Description,StartTime]' --output table

read -r -p "上記のスナップショットを削除しますか（boto3-study のものだけ）[y/N] " ans
if [[ "$ans" == "y" ]]; then
  for s in $(aws ec2 describe-snapshots --region "$REGION" --owner-ids "$ACCOUNT" \
      --filters "Name=tag:Project,Values=boto3-study" \
      --query 'Snapshots[].SnapshotId' --output text); do
    echo "  削除: $s"
    aws ec2 delete-snapshot --region "$REGION" --snapshot-id "$s"
  done
fi

echo
echo "=== 3. 手動RDSスナップショット ==="
aws rds describe-db-snapshots --region "$REGION" --snapshot-type manual \
  --query 'DBSnapshots[].[DBSnapshotIdentifier,DBInstanceIdentifier,Status]' --output table

read -r -p "boto3-study で始まる手動スナップショットを削除しますか [y/N] " ans
if [[ "$ans" == "y" ]]; then
  for s in $(aws rds describe-db-snapshots --region "$REGION" --snapshot-type manual \
      --query "DBSnapshots[?starts_with(DBSnapshotIdentifier, 'boto3-study')].DBSnapshotIdentifier" \
      --output text); do
    echo "  削除: $s"
    aws rds delete-db-snapshot --region "$REGION" --db-snapshot-identifier "$s"
  done
fi

echo
echo "=== 4. 残っていないことの最終確認 ==="
echo "--- EKS クラスタ（$2.4/日。最重要） ---"
aws eks list-clusters --region "$REGION" --output table
echo "--- Aurora / RDS クラスタ ---"
aws rds describe-db-clusters --region "$REGION" --query 'DBClusters[].DBClusterIdentifier' --output table
echo "--- 未割り当て EIP ---"
aws ec2 describe-addresses --region "$REGION" \
  --query 'Addresses[?AssociationId==null].[PublicIp,AllocationId]' --output table
echo "--- IAM ユーザ ---"
aws iam list-users --query "Users[?starts_with(UserName, 'boto3-study')].UserName" --output table
echo "--- NAT Gateway（作っていないはず） ---"
aws ec2 describe-nat-gateways --region "$REGION" \
  --filter Name=state,Values=available \
  --query 'NatGateways[].NatGatewayId' --output table

echo
echo "以上がすべて空なら terraform destroy に進んでください。"
