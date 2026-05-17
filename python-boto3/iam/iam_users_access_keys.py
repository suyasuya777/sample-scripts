"""
16. IAM ユーザー一覧とアクセスキー確認
未使用キー・長期未ローテーションのアクセスキーを検出する定期監査スクリプト。
"""
import boto3
from datetime import datetime, timezone, timedelta

iam = boto3.client('iam')
now = datetime.now(timezone.utc)
THRESHOLD_DAYS = 90

users = iam.list_users()['Users']
print(f"IAMユーザー数: {len(users)}")
print("=== 90日以上未使用または未ローテーションのキー ===")

for user in users:
    name = user['UserName']
    keys = iam.list_access_keys(UserName=name)['AccessKeyMetadata']
    for key in keys:
        key_id = key['AccessKeyId']
        status = key['Status']
        created = key['CreateDate']
        age = (now - created).days
        detail = iam.get_access_key_last_used(AccessKeyId=key_id)
        last_used = detail['AccessKeyLastUsed'].get('LastUsedDate')
        unused_days = (now - last_used).days if last_used else None
        flag = ''
        if age > THRESHOLD_DAYS:
            flag += f'  作成から{age}日経過'
        if unused_days and unused_days > THRESHOLD_DAYS:
            flag += f'  最終使用から{unused_days}日'
        if flag:
            print(f"  {name}  {key_id}  {status}{flag}")
