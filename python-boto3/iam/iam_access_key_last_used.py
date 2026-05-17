"""
20. IAM アクセスキー最終使用日時の確認
未使用キーを特定して定期監査・自動無効化の基礎データとして使う。
"""
import boto3
from datetime import datetime, timezone, timedelta

iam = boto3.client('iam')
now = datetime.now(timezone.utc)

paginator = iam.get_paginator('list_users')
rows = []
for page in paginator.paginate():
    for user in page['Users']:
        name = user['UserName']
        for key in iam.list_access_keys(UserName=name)['AccessKeyMetadata']:
            key_id = key['AccessKeyId']
            status = key['Status']
            detail = iam.get_access_key_last_used(AccessKeyId=key_id)
            last_used = detail['AccessKeyLastUsed'].get('LastUsedDate')
            last_region = detail['AccessKeyLastUsed'].get('Region', '-')
            last_service = detail['AccessKeyLastUsed'].get('ServiceName', '-')
            unused_days = (now - last_used).days if last_used else 9999
            rows.append((unused_days, name, key_id, status, last_used, last_region, last_service))

rows.sort(reverse=True)
print(f"{'未使用日数':>8}  {'ユーザー':<20}  {'キーID':<20}  {'状態':<8}  最終使用サービス")
print("-" * 80)
for unused_days, name, key_id, status, last_used, region, service in rows:
    days_str = f"{unused_days}日" if unused_days < 9999 else "未使用"
    print(f"{days_str:>8}  {name:<20}  {key_id:<20}  {status:<8}  {service}")
