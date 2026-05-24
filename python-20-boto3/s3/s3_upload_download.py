"""
11. S3 ファイルアップロード / ダウンロード
ログ収集・成果物配布で日常的に使用する基本操作。
"""
import boto3
import os

s3 = boto3.client('s3')
BUCKET = 'your-bucket-name'

# アップロード
local_upload = '/tmp/report.csv'
s3_key_upload = 'reports/report.csv'
s3.upload_file(local_upload, BUCKET, s3_key_upload)
print(f"アップロード完了: s3://{BUCKET}/{s3_key_upload}")

# ダウンロード
s3_key_download = 'reports/report.csv'
local_download = '/tmp/downloaded_report.csv'
s3.download_file(BUCKET, s3_key_download, local_download)
print(f"ダウンロード完了: {local_download}")

# ディレクトリ内のファイルを一括アップロード
local_dir = '/tmp/logs'
s3_prefix = 'logs/'
if os.path.isdir(local_dir):
    for filename in os.listdir(local_dir):
        local_path = os.path.join(local_dir, filename)
        s3.upload_file(local_path, BUCKET, f"{s3_prefix}{filename}")
        print(f"アップロード: {filename}")
