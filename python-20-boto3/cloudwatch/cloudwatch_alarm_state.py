"""
21. CloudWatch ALARM状態のアラーム一覧
インシデント対応時の最初の確認コマンド。ALARM状態のアラームを即座に洗い出す。
"""
import boto3

cw = boto3.client('cloudwatch', region_name='ap-northeast-1')
paginator = cw.get_paginator('describe_alarms')

alarms = []
for page in paginator.paginate(StateValue='ALARM'):
    alarms.extend(page['MetricAlarms'])

if not alarms:
    print("ALARM状態のアラームはありません")
else:
    print(f"🔴 ALARM状態: {len(alarms)} 件\n")
    for a in sorted(alarms, key=lambda x: x['StateUpdatedTimestamp'], reverse=True):
        print(f"アラーム名 : {a['AlarmName']}")
        print(f"メトリクス : {a['Namespace']} / {a['MetricName']}")
        print(f"理由       : {a['StateReason']}")
        print(f"更新時刻   : {a['StateUpdatedTimestamp']}")
        print()
