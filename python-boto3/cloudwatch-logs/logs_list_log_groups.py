"""
26. CloudWatch Logs ロググループ一覧取得
全ロググループの棚卸し。保持期間未設定のグループを検出してコスト管理に役立てる。
"""
import boto3

logs = boto3.client('logs', region_name='ap-northeast-1')
paginator = logs.get_paginator('describe_log_groups')

groups = []
for page in paginator.paginate():
    groups.extend(page['logGroups'])

no_retention = [g for g in groups if 'retentionInDays' not in g]
print(f"ロググループ合計: {len(groups)} 件")
print(f"保持期間未設定: {len(no_retention)} 件\n")

print(f"{'グループ名':<50}  {'保持期間':>8}  {'サイズ(MB)':>10}")
print("-" * 75)
for g in sorted(groups, key=lambda x: x.get('storedBytes', 0), reverse=True):
    retention = g.get('retentionInDays', '未設定')
    size_mb = g.get('storedBytes', 0) / 1024 / 1024
    print(f"{g['logGroupName']:<50}  {str(retention):>8}日  {size_mb:>10.2f}")
