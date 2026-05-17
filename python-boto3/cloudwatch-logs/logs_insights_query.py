"""
28. CloudWatch Logs Insights クエリ実行
大量ログの集計・分析。SLO違反の原因調査やパフォーマンス分析に使う。
"""
import boto3
import time
from datetime import datetime, timezone, timedelta

logs = boto3.client('logs', region_name='ap-northeast-1')

LOG_GROUP = '/aws/apigateway/my-api'
QUERY = """
    fields @timestamp, status, @duration
    | filter status >= 500
    | stats count(*) as error_count, avg(@duration) as avg_ms by bin(5m)
    | sort @timestamp desc
    | limit 20
"""

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=3)

response = logs.start_query(
    logGroupName=LOG_GROUP,
    startTime=int(start_time.timestamp()),
    endTime=int(end_time.timestamp()),
    queryString=QUERY
)
query_id = response['queryId']
print(f"クエリ実行中... ID={query_id}")

while True:
    result = logs.get_query_results(queryId=query_id)
    if result['status'] == 'Complete':
        break
    elif result['status'] in ('Failed', 'Cancelled'):
        print(f"クエリ失敗: {result['status']}")
        break
    time.sleep(1)

print(f"\n結果: {len(result['results'])} 行")
for row in result['results']:
    print({f['field']: f['value'] for f in row})
