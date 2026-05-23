"""
18. IAM 管理者ポリシーのアタッチ先確認
AdministratorAccess 付与先のユーザー・ロール・グループを棚卸しする。
"""
import boto3

iam = boto3.client('iam')

ADMIN_POLICY_ARN = 'arn:aws:iam::aws:policy/AdministratorAccess'
paginator = iam.get_paginator('list_entities_for_policy')

print(f"ポリシー: {ADMIN_POLICY_ARN}")
total = 0
for page in paginator.paginate(PolicyArn=ADMIN_POLICY_ARN):
    for user in page['PolicyUsers']:
        print(f"  👤 ユーザー : {user['UserName']}")
        total += 1
    for role in page['PolicyRoles']:
        print(f"  🔑 ロール  : {role['RoleName']}")
        total += 1
    for group in page['PolicyGroups']:
        print(f"  👥 グループ: {group['GroupName']}")
        total += 1

print(f"\n合計: {total} エンティティに管理者権限が付与されています")
