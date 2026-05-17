"""
07. スナップショット一覧と削除
孤立スナップショット（AMI非紐付け）を検出してコスト削減につなげる。
"""
import boto3

ec2 = boto3.client('ec2', region_name='ap-northeast-1')
account_id = boto3.client('sts').get_caller_identity()['Account']

# 自アカウントのスナップショット一覧
paginator = ec2.get_paginator('describe_snapshots')
snapshots = []
for page in paginator.paginate(OwnerIds=[account_id]):
    snapshots.extend(page['Snapshots'])

# 現在のAMIが使用しているスナップショットIDを収集
amis = ec2.describe_images(Owners=[account_id])['Images']
used_snap_ids = set()
for ami in amis:
    for mapping in ami.get('BlockDeviceMappings', []):
        if 'Ebs' in mapping:
            used_snap_ids.add(mapping['Ebs']['SnapshotId'])

# 孤立スナップショットを特定
orphans = [s for s in snapshots if s['SnapshotId'] not in used_snap_ids]
print(f"スナップショット合計: {len(snapshots)} 件  孤立: {len(orphans)} 件")
for s in orphans:
    size_gb = s['VolumeSize']
    print(f"  {s['SnapshotId']}  {size_gb} GB  {s['StartTime'].date()}  {s.get('Description', '')}")
    # 削除する場合（コメントアウトを外す）:
    # ec2.delete_snapshot(SnapshotId=s['SnapshotId'])
