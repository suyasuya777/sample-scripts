"""
38. ECS サービスのローリング再起動
新しいタスク定義をデプロイせずにタスクを再起動する。設定反映・障害復旧時に使う。
"""
import boto3

ecs = boto3.client('ecs', region_name='ap-northeast-1')

CLUSTER = 'my-cluster'
SERVICE = 'my-service'

print(f"ローリング再起動を開始します: {CLUSTER}/{SERVICE}")
ecs.update_service(
    cluster=CLUSTER,
    service=SERVICE,
    forceNewDeployment=True
)

# サービスが安定するまで待機
print("安定するまで待機中...")
waiter = ecs.get_waiter('services_stable')
waiter.wait(
    cluster=CLUSTER,
    services=[SERVICE],
    WaiterConfig={'Delay': 15, 'MaxAttempts': 40}
)
print("再起動完了")
