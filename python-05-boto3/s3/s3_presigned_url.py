"""
15. S3 署名付きURL生成
一時的なダウンロード / アップロードリンクを発行する。
"""
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    region_name='ap-northeast-1',
    config=Config(signature_version='s3v4')
)
BUCKET = 'your-bucket-name'

# ダウンロード用署名付きURL（1時間有効）
download_url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={'Bucket': BUCKET, 'Key': 'reports/report.csv'},
    ExpiresIn=3600
)
print(f"ダウンロードURL（1時間有効）:\n{download_url}\n")

# アップロード用署名付きURL（10分有効）
upload_url = s3.generate_presigned_url(
    ClientMethod='put_object',
    Params={
        'Bucket': BUCKET,
        'Key': 'uploads/new_file.csv',
        'ContentType': 'text/csv'
    },
    ExpiresIn=600
)
print(f"アップロードURL（10分有効）:\n{upload_url}")
