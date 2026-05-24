"""
14. S3 ライフサイクルルール設定
古いオブジェクトの自動削除・Glacier移行でストレージコストを削減する。
"""
import boto3

s3 = boto3.client('s3')
BUCKET = 'your-bucket-name'

lifecycle_config = {
    'Rules': [
        {
            'ID': 'log-lifecycle',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'logs/'},
            'Transitions': [
                {'Days': 30, 'StorageClass': 'STANDARD_IA'},
                {'Days': 90, 'StorageClass': 'GLACIER'},
            ],
            'Expiration': {'Days': 365},
        },
        {
            'ID': 'tmp-cleanup',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'tmp/'},
            'Expiration': {'Days': 7},
        },
        {
            'ID': 'incomplete-multipart-cleanup',
            'Status': 'Enabled',
            'Filter': {'Prefix': ''},
            'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 3},
        },
    ]
}

s3.put_bucket_lifecycle_configuration(Bucket=BUCKET, LifecycleConfiguration=lifecycle_config)
print(f"ライフサイクルルールを設定しました: {BUCKET}")

# 確認
current = s3.get_bucket_lifecycle_configuration(Bucket=BUCKET)
for rule in current['Rules']:
    print(f"  ルール: {rule['ID']}  状態: {rule['Status']}")
