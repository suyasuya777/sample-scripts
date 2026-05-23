"""
29. CloudWatch Logs 保持期間の一括設定
保持期間未設定のロググループにまとめて保持期間を設定してコスト削減する。
"""
import boto3

logs = boto3.client('logs', region_name='ap-northeast-1')
paginator = logs.get_paginator('describe_log_groups')

DEFAULT_RETENTION_DAYS = 30
updated = 0

for page in paginator.paginate():
    for group in page['logGroups']:
        name = group['logGroupName']
        if 'retentionInDays' not in group:
            logs.put_retention_policy(
                logGroupName=name,
                retentionInDays=DEFAULT_RETENTION_DAYS
            )
            print(f"設定: {name}  -> {DEFAULT_RETENTION_DAYS}日")
            updated += 1

print(f"\n{updated} 件のロググループに保持期間を設定しました")
