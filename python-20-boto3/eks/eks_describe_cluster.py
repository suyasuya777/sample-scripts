"""
60. EKS クラスター情報取得・ノードグループ状態確認
クラスターのバージョン・エンドポイント・ノードグループの稼働状況を確認する。
ECS から EKS への移行を見据えた基礎操作。
"""
import boto3

eks = boto3.client('eks', region_name='ap-northeast-1')
ec2 = boto3.client('ec2', region_name='ap-northeast-1')

# クラスター一覧
clusters = eks.list_clusters()['clusters']
print(f"EKS クラスター数: {len(clusters)}\n")

for cluster_name in clusters:
    # クラスター詳細
    c = eks.describe_cluster(name=cluster_name)['cluster']

    print(f"クラスター名    : {c['name']}")
    print(f"ステータス      : {c['status']}")
    print(f"Kubernetes      : {c['version']}")
    print(f"エンドポイント  : {c['endpoint']}")
    print(f"プラットフォーム: {c.get('platformVersion', '-')}")
    print(f"ロールARN       : {c['roleArn']}")

    # ネットワーク設定
    resources = c.get('resourcesVpcConfig', {})
    print(f"VPC             : {resources.get('vpcId', '-')}")
    print(f"サブネット       : {', '.join(resources.get('subnetIds', []))}")
    print(f"パブリックアクセス: {resources.get('endpointPublicAccess', '-')}")
    print(f"プライベートアクセス: {resources.get('endpointPrivateAccess', '-')}")

    # ログ設定
    log_types = [
        lt['types']
        for lt in c.get('logging', {}).get('clusterLogging', [])
        if lt.get('enabled')
    ]
    enabled_logs = [t for types in log_types for t in types]
    print(f"有効ログ        : {', '.join(enabled_logs) if enabled_logs else '未設定'}")

    # アドオン一覧
    addons = eks.list_addons(clusterName=cluster_name)['addons']
    if addons:
        print(f"アドオン        : {', '.join(addons)}")

    # ノードグループ一覧
    ng_names = eks.list_nodegroups(clusterName=cluster_name)['nodegroups']
    print(f"\nノードグループ数: {len(ng_names)}")

    for ng_name in ng_names:
        ng = eks.describe_nodegroup(clusterName=cluster_name, nodegroupName=ng_name)['nodegroup']
        scaling  = ng['scalingConfig']
        health   = ng.get('health', {})
        issues   = health.get('issues', [])
        status   = ng['status']
        flag     = '✅' if status == 'ACTIVE' and not issues else '⚠️ '

        print(f"\n  {flag} NG名      : {ng_name}")
        print(f"     ステータス  : {status}")
        print(f"     インスタンス: {ng.get('instanceTypes', ['-'])[0]}")
        print(f"     スケール    : Min={scaling['minSize']}  Desired={scaling['desiredSize']}  Max={scaling['maxSize']}")
        print(f"     AMI タイプ  : {ng.get('amiType', '-')}")
        print(f"     ディスク容量: {ng.get('diskSize', '-')} GB")
        print(f"     リリースVer : {ng.get('releaseVersion', '-')}")

        # ノードグループの問題がある場合
        if issues:
            for issue in issues:
                print(f"     ⚠️  問題: [{issue['code']}] {issue['message']}")

    print("\n" + "=" * 60 + "\n")
