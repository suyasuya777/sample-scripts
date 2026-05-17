"""
36. ECS クラスター・サービス一覧取得
ECS環境の全体把握。クラスターをまたいでサービス一覧を取得する棚卸し起点。
"""
import boto3

ecs = boto3.client('ecs', region_name='ap-northeast-1')

clusters = ecs.list_clusters()['clusterArns']
print(f"クラスター数: {len(clusters)}\n")

for cluster_arn in clusters:
    cluster_name = cluster_arn.split('/')[-1]
    print(f"クラスター: {cluster_name}")
    service_arns = ecs.list_services(cluster=cluster_arn)['serviceArns']
    if not service_arns:
        print("  サービスなし")
        continue
    details = ecs.describe_services(cluster=cluster_arn, services=service_arns)
    for svc in details['services']:
        print(f"  サービス: {svc['serviceName']}  "
              f"desired={svc['desiredCount']}  running={svc['runningCount']}  "
              f"status={svc['status']}")
