"""
56. Auto Scaling グループ一覧・状態確認
スケール状態の把握とインスタンス数の異常検出。SREの日常監視・障害対応の起点。
"""
import boto3

asg = boto3.client('autoscaling', region_name='ap-northeast-1')
ec2 = boto3.client('ec2', region_name='ap-northeast-1')

paginator = asg.get_paginator('describe_auto_scaling_groups')

groups = []
for page in paginator.paginate():
    groups.extend(page['AutoScalingGroups'])

print(f"Auto Scaling グループ数: {len(groups)}\n")

for g in groups:
    name   = g['AutoScalingGroupName']
    min_s  = g['MinSize']
    max_s  = g['MaxSize']
    desire = g['DesiredCapacity']
    instances = g['Instances']

    # 状態別にカウント
    in_service  = sum(1 for i in instances if i['LifecycleState'] == 'InService')
    pending     = sum(1 for i in instances if i['LifecycleState'] == 'Pending')
    terminating = sum(1 for i in instances if i['LifecycleState'] == 'Terminating')
    unhealthy   = sum(1 for i in instances if i['HealthStatus'] != 'Healthy')

    # desired との乖離を検出
    gap = desire - in_service
    status = '⚠️  乖離あり' if gap != 0 else '✅ 正常'

    print(f"グループ名  : {name}")
    print(f"サイズ設定  : Min={min_s}  Desired={desire}  Max={max_s}")
    print(f"InService   : {in_service}  Pending={pending}  Terminating={terminating}")
    print(f"Unhealthy   : {unhealthy}")
    print(f"ステータス  : {status}" + (f"  (不足: {gap}台)" if gap > 0 else ""))

    # スケーリングポリシーの有無
    policies = asg.describe_policies(AutoScalingGroupName=name)['ScalingPolicies']
    policy_types = [p['PolicyType'] for p in policies]
    print(f"スケーリング: {', '.join(policy_types) if policy_types else 'なし'}")

    # 起動テンプレート or 起動設定
    if 'LaunchTemplate' in g:
        lt = g['LaunchTemplate']
        print(f"起動テンプレート: {lt['LaunchTemplateName']}  バージョン={lt.get('Version', '$Default')}")
    elif 'LaunchConfigurationName' in g:
        print(f"起動設定 : {g['LaunchConfigurationName']}  ※LaunchTemplateへの移行を推奨")

    print()

# サマリ
total_desired    = sum(g['DesiredCapacity'] for g in groups)
total_in_service = sum(
    sum(1 for i in g['Instances'] if i['LifecycleState'] == 'InService')
    for g in groups
)
anomaly = sum(
    1 for g in groups
    if g['DesiredCapacity'] != sum(1 for i in g['Instances'] if i['LifecycleState'] == 'InService')
)

print(f"--- サマリ ---")
print(f"総 Desired     : {total_desired}")
print(f"総 InService   : {total_in_service}")
print(f"乖離グループ数 : {anomaly}")
