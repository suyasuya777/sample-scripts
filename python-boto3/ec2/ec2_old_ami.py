"""
06. AMI一覧と古いイメージの特定
自社AMIの棚卸し。90日以上古いものを削除候補として抽出する。
"""
import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client('ec2', region_name='ap-northeast-1')
account_id = boto3.client('sts').get_caller_identity()['Account']

amis = ec2.describe_images(Owners=[account_id])['Images']
threshold = datetime.now(timezone.utc) - timedelta(days=90)

print(f"自社AMI 合計: {len(amis)} 件")
print("=== 90日以上前に作成されたAMI ===")
old_amis = []
for ami in sorted(amis, key=lambda x: x['CreationDate']):
    created = datetime.fromisoformat(ami['CreationDate'].replace('Z', '+00:00'))
    age = (datetime.now(timezone.utc) - created).days
    if created < threshold:
        old_amis.append(ami)
        print(f"{ami['ImageId']}  {age}日経過  {ami['Name']}")

print(f"\n削除候補: {len(old_amis)} 件")
