"""
03. 全リージョン一覧取得
マルチリージョンスキャンの前処理として必須。有効リージョンを動的に取得する。
"""
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')
response = ec2.describe_regions(Filters=[{'Name': 'opt-in-status', 'Values': ['opt-in-not-required', 'opted-in']}])

regions = [r['RegionName'] for r in response['Regions']]
regions.sort()

print(f"有効なリージョン数: {len(regions)}")
for region in regions:
    print(region)
