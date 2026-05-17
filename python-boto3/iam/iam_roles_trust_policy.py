"""
17. IAM ロール一覧と信頼ポリシー確認
外部アカウントへの信頼設定を棚卸しする。クロスアカウント侵害リスクの確認に。
"""
import boto3
import json

iam = boto3.client('iam')
paginator = iam.get_paginator('list_roles')
account_id = boto3.client('sts').get_caller_identity()['Account']

print(f"自アカウント: {account_id}")
print("=== 外部アカウントへの信頼があるロール ===")

for page in paginator.paginate():
    for role in page['Roles']:
        trust = role['AssumeRolePolicyDocument']
        for stmt in trust.get('Statement', []):
            principal = stmt.get('Principal', {})
            aws = principal.get('AWS', '')
            if isinstance(aws, str):
                aws = [aws]
            for arn in aws:
                if account_id not in arn and 'amazonaws.com' not in arn:
                    print(f"  ロール: {role['RoleName']}")
                    print(f"    信頼先: {arn}")
