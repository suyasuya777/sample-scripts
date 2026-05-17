"""
42. SSM Parameter Store への一括読み書き
環境変数・接続先設定の管理。Terraform apply前の設定準備などに活用。
"""
import boto3

ssm = boto3.client('ssm', region_name='ap-northeast-1')

# 一括書き込み
params = {
    '/myapp/prod/DB_HOST': ('String', 'mydb.cluster.ap-northeast-1.rds.amazonaws.com'),
    '/myapp/prod/DB_PORT': ('String', '5432'),
    '/myapp/prod/DB_NAME': ('String', 'myapp_production'),
    '/myapp/prod/LOG_LEVEL': ('String', 'INFO'),
    '/myapp/prod/DB_PASSWORD': ('SecureString', 'secret-password-here'),
}
for name, (param_type, value) in params.items():
    ssm.put_parameter(Name=name, Value=value, Type=param_type, Overwrite=True)
    print(f"書き込み: {name}")

# パス配下を一括読み込み
print("\n--- 読み込み ---")
paginator = ssm.get_paginator('get_parameters_by_path')
for page in paginator.paginate(Path='/myapp/prod/', WithDecryption=True):
    for p in page['Parameters']:
        display = '****' if 'PASSWORD' in p['Name'] or 'SECRET' in p['Name'] else p['Value']
        print(f"  {p['Name']} = {display}")

# 単一パラメータの取得
single = ssm.get_parameter(Name='/myapp/prod/DB_HOST', WithDecryption=True)
print(f"\nDB_HOST: {single['Parameter']['Value']}")
