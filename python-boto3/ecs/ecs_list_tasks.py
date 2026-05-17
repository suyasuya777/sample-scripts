"""
39. ECS タスク一覧と詳細確認
実行中タスクのIPアドレス・コンテナ状態を確認する。インシデント調査の起点。
"""
import boto3

ecs = boto3.client('ecs', region_name='ap-northeast-1')
ec2 = boto3.client('ec2', region_name='ap-northeast-1')

CLUSTER = 'my-cluster'

task_arns = ecs.list_tasks(cluster=CLUSTER)['taskArns']
if not task_arns:
    print("実行中のタスクはありません")
else:
    tasks = ecs.describe_tasks(cluster=CLUSTER, tasks=task_arns)['tasks']
    for task in tasks:
        task_id = task['taskArn'].split('/')[-1]
        status = task['lastStatus']
        print(f"タスク: {task_id}  ステータス: {status}")
        for attachment in task.get('attachments', []):
            for detail in attachment.get('details', []):
                if detail['name'] == 'privateIPv4Address':
                    print(f"  プライベートIP: {detail['value']}")
        for container in task['containers']:
            print(f"  コンテナ: {container['name']}  {container['lastStatus']}")
