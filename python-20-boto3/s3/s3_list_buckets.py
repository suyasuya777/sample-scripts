"""
09. S3 バケット一覧取得
アカウント内全バケットの棚卸し起点。リージョン・作成日も合わせて取得する。
"""
import boto3

s3 = boto3.client('s3')
response = s3.list_buckets()

print(f"バケット数: {len(response['Buckets'])}")
for b in sorted(response['Buckets'], key=lambda x: x['Name']):
    # バケットのリージョンを取得
    try:
        loc = s3.get_bucket_location(Bucket=b['Name'])
        region = loc['LocationConstraint'] or 'us-east-1'
    except Exception:
        region = 'unknown'
    print(f"{b['Name']}  region={region}  created={b['CreationDate'].date()}")
