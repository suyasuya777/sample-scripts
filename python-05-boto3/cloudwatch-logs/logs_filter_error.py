"""
27. CloudWatch Logs エラーログのフィルタ取得
障害調査で最初に実行するログ検索。直近1時間のERRORログを抽出する。
"""
import boto3
from datetime import datetime, timezone, timedelta

logs = boto3.client('logs', region_name='ap-northeast-1')

LOG_GROUP = '/aws/lambda/my-function'
FILTER_PATTERN = 'ERROR'
HOURS = 1

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=HOURS)

paginator = logs.get_paginator('filter_log_events')
count = 0
for page in paginator.paginate(
    logGroupName=LOG_GROUP,
    startTime=int(start_time.timestamp() * 1000),
    endTime=int(end_time.timestamp() * 1000),
    filterPattern=FILTER_PATTERN
):
    for event in page['events']:
        ts = datetime.fromtimestamp(event['timestamp'] / 1000, tz=timezone.utc)
        print(f"[{ts.strftime('%H:%M:%S')}] {event['message'].strip()}")
        count += 1

print(f"\n{FILTER_PATTERN} ログ: {count} 件（直近{HOURS}時間）")
