"""
22. CloudWatch メトリクス統計値の取得
CPU・メモリ・レイテンシのSLI計測。直近1時間を5分粒度で取得する。
"""
import boto3
from datetime import datetime, timezone, timedelta

cw = boto3.client('cloudwatch', region_name='ap-northeast-1')

INSTANCE_ID = 'i-xxxxxxxxxxxxxxxxx'
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=1)

metrics = [
    ('AWS/EC2', 'CPUUtilization', 'Percent', [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]),
    ('AWS/EC2', 'NetworkIn', 'Bytes', [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]),
    ('AWS/EC2', 'StatusCheckFailed', 'Count', [{'Name': 'InstanceId', 'Value': INSTANCE_ID}]),
]

for namespace, metric_name, unit, dimensions in metrics:
    response = cw.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average', 'Maximum']
    )
    datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
    print(f"\n{metric_name} ({unit}):")
    for d in datapoints:
        print(f"  {d['Timestamp'].strftime('%H:%M')}  avg={d['Average']:.2f}  max={d['Maximum']:.2f}")
