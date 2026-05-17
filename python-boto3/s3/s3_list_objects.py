"""
10. S3 オブジェクト一覧（paginator必須）
大量オブジェクトの全件取得。paginatorを使わないと1000件上限で打ち切られる。
"""
import boto3

s3 = boto3.client('s3')
BUCKET = 'your-bucket-name'
PREFIX = ''  # フォルダを絞る場合は指定（例: 'logs/2024/'）

paginator = s3.get_paginator('list_objects_v2')
total_size = 0
total_count = 0

for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
    for obj in page.get('Contents', []):
        total_size += obj['Size']
        total_count += 1
        print(f"{obj['Key']}  {obj['Size']:,} bytes  {obj['LastModified'].date()}")

print(f"\n合計: {total_count:,} 件  {total_size / 1024 / 1024:.2f} MB")
