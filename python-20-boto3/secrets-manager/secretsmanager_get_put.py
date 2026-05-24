"""
50. Secrets Manager シークレットの取得と更新
DBパスワード・APIキーを安全に取得・ローテーションする。
"""
import boto3
import json
from datetime import datetime, timezone

sm = boto3.client('secretsmanager', region_name='ap-northeast-1')

SECRET_NAME = 'myapp/production/db-credentials'

# シークレットの取得
try:
    response = sm.get_secret_value(SecretId=SECRET_NAME)
    if 'SecretString' in response:
        secret = json.loads(response['SecretString'])
        print(f"シークレット取得成功: {SECRET_NAME}")
        print(f"キー一覧: {list(secret.keys())}")
        # 使用例: db_host = secret['host']
    else:
        print("バイナリシークレット")
except sm.exceptions.ResourceNotFoundException:
    print(f"シークレットが見つかりません: {SECRET_NAME}")

# シークレット一覧の棚卸し
print("\n=== シークレット一覧 ===")
paginator = sm.get_paginator('list_secrets')
for page in paginator.paginate():
    for s in page['SecretList']:
        last_rotated = s.get('LastRotatedDate', '未ローテーション')
        last_changed = s.get('LastChangedDate', '-')
        print(f"  {s['Name']}  最終変更={last_changed}  ローテーション={last_rotated}")

# シークレットの更新例（コメントアウトを外す）:
# new_secret = json.dumps({'host': 'new-host.rds.amazonaws.com', 'password': 'new-password'})
# sm.put_secret_value(SecretId=SECRET_NAME, SecretString=new_secret)
# print("シークレットを更新しました")
