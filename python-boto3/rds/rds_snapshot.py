"""
45. RDS スナップショット作成と世代管理（30日）
定期バックアップの自動化。世代管理ロジックをLambdaで動かすのが定番パターン。
"""
import boto3
from datetime import datetime, timezone, timedelta

rds = boto3.client('rds', region_name='ap-northeast-1')
now = datetime.now(timezone.utc)

DB_IDENTIFIER = 'my-database'
RETENTION_DAYS = 30
snap_id = f"{DB_IDENTIFIER}-{now.strftime('%Y%m%d-%H%M')}"

# スナップショット作成
print(f"スナップショットを作成します: {snap_id}")
rds.create_db_snapshot(DBInstanceIdentifier=DB_IDENTIFIER, DBSnapshotIdentifier=snap_id)

waiter = rds.get_waiter('db_snapshot_completed')
waiter.wait(DBSnapshotIdentifier=snap_id)
print(f"作成完了: {snap_id}")

# 古いスナップショットを削除
snaps = rds.describe_db_snapshots(
    DBInstanceIdentifier=DB_IDENTIFIER,
    SnapshotType='manual'
)['DBSnapshots']

deleted = 0
for s in snaps:
    age = now - s['SnapshotCreateTime']
    if age > timedelta(days=RETENTION_DAYS):
        rds.delete_db_snapshot(DBSnapshotIdentifier=s['DBSnapshotIdentifier'])
        print(f"削除: {s['DBSnapshotIdentifier']} ({age.days}日経過)")
        deleted += 1

print(f"\n削除したスナップショット: {deleted} 件")
