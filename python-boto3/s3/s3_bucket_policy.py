"""
13. S3 バケットポリシーの取得・設定
クロスアカウントアクセス設定時に使用。既存ポリシーの確認と更新。
"""
import boto3
import json

s3 = boto3.client('s3')
BUCKET = 'your-bucket-name'

# 現在のポリシーを取得
try:
    response = s3.get_bucket_policy(Bucket=BUCKET)
    policy = json.loads(response['Policy'])
    print("現在のバケットポリシー:")
    print(json.dumps(policy, indent=2, ensure_ascii=False))
except s3.exceptions.NoSuchBucketPolicy:
    print("ポリシーが設定されていません")

# ポリシーを設定する例（特定アカウントからの読み取り許可）
TRUSTED_ACCOUNT_ID = '123456789012'
new_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": f"arn:aws:iam::{TRUSTED_ACCOUNT_ID}:root"},
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": [
                f"arn:aws:s3:::{BUCKET}",
                f"arn:aws:s3:::{BUCKET}/*"
            ]
        }
    ]
}

# 設定する場合（コメントアウトを外す）:
# s3.put_bucket_policy(Bucket=BUCKET, Policy=json.dumps(new_policy))
# print("ポリシーを設定しました")
