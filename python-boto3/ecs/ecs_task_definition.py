"""
40. ECS タスク定義の最新リビジョン取得
デプロイ内容の確認・差分チェックに。現在のサービスが使っているリビジョンも確認する。
"""
import boto3
import json

ecs = boto3.client('ecs', region_name='ap-northeast-1')

CLUSTER = 'my-cluster'
SERVICE = 'my-service'

# サービスが使っているタスク定義を確認
svc = ecs.describe_services(cluster=CLUSTER, services=[SERVICE])['services'][0]
current_task_def = svc['taskDefinition']
print(f"現在のタスク定義: {current_task_def}")

# タスク定義の詳細を取得
td = ecs.describe_task_definition(taskDefinition=current_task_def)['taskDefinition']
print(f"\nリビジョン: {td['revision']}")
print(f"CPU: {td.get('cpu', '-')}  メモリ: {td.get('memory', '-')}")
print("\nコンテナ定義:")
for c in td['containerDefinitions']:
    print(f"  {c['name']}  image={c['image']}  cpu={c.get('cpu',0)}  memory={c.get('memory',0)}")
    env_list = c.get('environment', [])
    if env_list:
        print(f"    環境変数: {[e['name'] for e in env_list]}")
