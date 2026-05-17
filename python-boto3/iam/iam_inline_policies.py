"""
19. IAM インラインポリシーの一覧確認
管理ポリシー外のインラインポリシーを洗い出す。権限の全体把握に必須。
"""
import boto3
import json

iam = boto3.client('iam')

# ロールのインラインポリシー
print("=== ロールのインラインポリシー ===")
role_paginator = iam.get_paginator('list_roles')
for page in role_paginator.paginate():
    for role in page['Roles']:
        inline = iam.list_role_policies(RoleName=role['RoleName'])['PolicyNames']
        if inline:
            print(f"  ロール: {role['RoleName']}")
            for policy_name in inline:
                detail = iam.get_role_policy(RoleName=role['RoleName'], PolicyName=policy_name)
                doc = detail['PolicyDocument']
                print(f"    インラインポリシー: {policy_name}")
                for stmt in doc.get('Statement', []):
                    print(f"      Action: {stmt.get('Action')}  Effect: {stmt.get('Effect')}")

# ユーザーのインラインポリシー
print("\n=== ユーザーのインラインポリシー ===")
user_paginator = iam.get_paginator('list_users')
for page in user_paginator.paginate():
    for user in page['Users']:
        inline = iam.list_user_policies(UserName=user['UserName'])['PolicyNames']
        if inline:
            print(f"  ユーザー: {user['UserName']}  インラインポリシー: {inline}")
