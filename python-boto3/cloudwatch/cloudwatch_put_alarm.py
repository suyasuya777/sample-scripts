"""
24. CloudWatch アラームの作成・更新
しきい値・アクション設定をコードで管理する。Infrastructure as Codeの一環として。
"""
import boto3

cw = boto3.client('cloudwatch', region_name='ap-northeast-1')
SNS_TOPIC_ARN = 'arn:aws:sns:ap-northeast-1:123456789012:my-alert-topic'
INSTANCE_ID = 'i-xxxxxxxxxxxxxxxxx'

# CPU使用率アラーム
cw.put_metric_alarm(
    AlarmName=f'ec2-cpu-high-{INSTANCE_ID}',
    AlarmDescription='EC2 CPU使用率が80%を超えました',
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
    Statistic='Average',
    Period=300,
    EvaluationPeriods=2,
    Threshold=80.0,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=[SNS_TOPIC_ARN],
    OKActions=[SNS_TOPIC_ARN],
    TreatMissingData='breaching',
)
print(f"CPU高負荷アラームを作成しました: {INSTANCE_ID}")

# ステータスチェックアラーム
cw.put_metric_alarm(
    AlarmName=f'ec2-statuscheck-{INSTANCE_ID}',
    AlarmDescription='EC2 ステータスチェック失敗',
    Namespace='AWS/EC2',
    MetricName='StatusCheckFailed',
    Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
    Statistic='Maximum',
    Period=60,
    EvaluationPeriods=3,
    Threshold=1.0,
    ComparisonOperator='GreaterThanOrEqualToThreshold',
    AlarmActions=[SNS_TOPIC_ARN],
    TreatMissingData='missing',
)
print(f"ステータスチェックアラームを作成しました: {INSTANCE_ID}")
