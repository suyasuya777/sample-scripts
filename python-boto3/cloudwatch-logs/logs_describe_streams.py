"""
30. CloudWatch Logs ログストリームの一覧取得
特定タスク・インスタンスのログを特定する。ECSタスクIDやEC2インスタンスIDで絞り込む。
"""
import boto3
from datetime import datetime, timezone

logs = boto3.client('logs', region_name='ap-northeast-1')

LOG_GROUP = '/ecs/my-service'
paginator = logs.get_paginator('describe_log_streams')

streams = []
for page in paginator.paginate(
    logGroupName=LOG_GROUP,
    orderBy='LastEventTime',
    descending=True
):
    streams.extend(page['logStreams'])
    if len(streams) >= 20:
        break

print(f"ロングストリーム一覧: {LOG_GROUP}\n")
for s in streams[:20]:
    last_event = s.get('lastEventTimestamp')
    last_ts = datetime.fromtimestamp(last_event / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M') if last_event else '-'
    print(f"  {s['logStreamName']}  最終イベント: {last_ts}")
