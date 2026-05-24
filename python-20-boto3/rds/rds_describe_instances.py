"""
44. RDS DBインスタンス一覧と状態確認
ストレージ使用量・エンジンバージョンの棚卸し。EOLバージョンの検出にも使う。
"""
import boto3

rds = boto3.client('rds', region_name='ap-northeast-1')
paginator = rds.get_paginator('describe_db_instances')

instances = []
for page in paginator.paginate():
    instances.extend(page['DBInstances'])

print(f"DBインスタンス数: {len(instances)}\n")
print(f"{'識別子':<30}  {'エンジン':<15}  {'クラス':<15}  {'状態':<12}  ストレージ(GB)")
print("-" * 90)
for db in instances:
    ident = db['DBInstanceIdentifier']
    engine = f"{db['Engine']} {db['EngineVersion']}"
    cls = db['DBInstanceClass']
    status = db['DBInstanceStatus']
    storage = db['AllocatedStorage']
    multi_az = '(Multi-AZ)' if db.get('MultiAZ') else ''
    print(f"{ident:<30}  {engine:<15}  {cls:<15}  {status:<12}  {storage} {multi_az}")
