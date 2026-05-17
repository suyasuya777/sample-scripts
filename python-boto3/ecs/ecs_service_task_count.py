"""
37. ECS サービスの desired/running カウント確認
タスク数の不一致を検出する。ヘルスチェック代わりの監視スクリプトとして使う。
"""
import boto3

ecs = boto3.client('ecs', region_name='ap-northeast-1')

clusters = ecs.list_clusters()['clusterArns']
issues = []

for cluster_arn in clusters:
    cluster_name = cluster_arn.split('/')[-1]
    service_arns = ecs.list_services(cluster=cluster_arn)['serviceArns']
    if not service_arns:
        continue
    details = ecs.describe_services(cluster=cluster_arn, services=service_arns)
    for svc in details['services']:
        desired = svc['desiredCount']
        running = svc['runningCount']
        pending = svc['pendingCount']
        if desired != running:
            issues.append((cluster_name, svc['serviceName'], desired, running, pending))
            print(f"⚠️  {cluster_name}/{svc['serviceName']}: desired={desired} running={running} pending={pending}")
        else:
            print(f"✅ {cluster_name}/{svc['serviceName']}: {running}/{desired}")

print(f"\n不一致: {len(issues)} 件")
