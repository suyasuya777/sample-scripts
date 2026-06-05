"""
58. ALB ターゲットグループのヘルスチェック確認
unhealthy ターゲットを即座に検出する。可用性監視・障害対応の最初の確認コマンド。
"""
import boto3

elb = boto3.client('elbv2', region_name='ap-northeast-1')

paginator_tg  = elb.get_paginator('describe_target_groups')
paginator_alb = elb.get_paginator('describe_load_balancers')

# ロードバランサー情報を先に取得（ARN → 名前のマッピング用）
lb_map = {}
for page in paginator_alb.paginate():
    for lb in page['LoadBalancers']:
        lb_map[lb['LoadBalancerArn']] = lb['LoadBalancerName']

# ターゲットグループを全件取得
tgs = []
for page in paginator_tg.paginate():
    tgs.extend(page['TargetGroups'])

print(f"ターゲットグループ数: {len(tgs)}\n")

total_unhealthy = 0
alert_groups    = []

for tg in tgs:
    tg_arn  = tg['TargetGroupArn']
    tg_name = tg['TargetGroupName']
    proto   = tg['Protocol']
    port    = tg['Port']

    # 紐付くALB名
    lb_names = [lb_map.get(arn, arn) for arn in tg.get('LoadBalancerArns', [])]

    # ターゲットのヘルス取得
    health_resp = elb.describe_target_health(TargetGroupArn=tg_arn)
    targets = health_resp['TargetHealthDescriptions']

    healthy   = [t for t in targets if t['TargetHealth']['State'] == 'healthy']
    unhealthy = [t for t in targets if t['TargetHealth']['State'] == 'unhealthy']
    draining  = [t for t in targets if t['TargetHealth']['State'] == 'draining']
    unused    = [t for t in targets if t['TargetHealth']['State'] == 'unused']

    status = '✅ 正常' if not unhealthy else '🔴 異常あり'
    total_unhealthy += len(unhealthy)

    print(f"TG名        : {tg_name}")
    print(f"プロトコル  : {proto}:{port}")
    print(f"ALB         : {', '.join(lb_names) if lb_names else '未アタッチ'}")
    print(f"ヘルス      : healthy={len(healthy)}  unhealthy={len(unhealthy)}  draining={len(draining)}  unused={len(unused)}")
    print(f"ステータス  : {status}")

    if unhealthy:
        for t in unhealthy:
            tid    = t['Target']['Id']
            reason = t['TargetHealth'].get('Reason', '-')
            desc   = t['TargetHealth'].get('Description', '-')
            print(f"  🔴 {tid}  理由={reason}  詳細={desc}")
        alert_groups.append(tg_name)

    print()

# サマリ
print(f"--- サマリ ---")
print(f"unhealthy ターゲット総数 : {total_unhealthy}")
if alert_groups:
    print(f"⚠️  異常 TG ({len(alert_groups)} 件) : {', '.join(alert_groups)}")
else:
    print("✅ すべてのターゲットグループが正常です")
