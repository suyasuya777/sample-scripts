"""
23. CloudWatch カスタムメトリクスの送信
アプリ独自のSLIをCloudWatchへ記録する。Prometheus exporter代替としても活用。
"""
import boto3
import time
from datetime import datetime, timezone

cw = boto3.client('cloudwatch', region_name='ap-northeast-1')

def put_metric(namespace, metric_name, value, unit='Count', dimensions=None):
    cw.put_metric_data(
        Namespace=namespace,
        MetricData=[{
            'MetricName': metric_name,
            'Dimensions': dimensions or [],
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.now(timezone.utc),
        }]
    )

# アプリのエラー率を記録
put_metric('MyApp/Production', 'ErrorRate', 0.5, 'Percent',
           [{'Name': 'Service', 'Value': 'api-server'}])

# レイテンシを記録
put_metric('MyApp/Production', 'ResponseTime', 123.4, 'Milliseconds',
           [{'Name': 'Endpoint', 'Value': '/api/v1/users'}])

# アクティブユーザー数を記録
put_metric('MyApp/Production', 'ActiveUsers', 42, 'Count')

print("カスタムメトリクスを送信しました")
