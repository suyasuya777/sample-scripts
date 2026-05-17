"""
48. SNS トピックへのメッセージ発行
アラート通知・イベント連携の発火点。JSON形式のペイロードも送れる。
"""
import boto3
import json
from datetime import datetime, timezone

sns = boto3.client('sns', region_name='ap-northeast-1')

TOPIC_ARN = 'arn:aws:sns:ap-northeast-1:123456789012:my-alert-topic'

# シンプルなテキスト通知
sns.publish(
    TopicArn=TOPIC_ARN,
    Subject='[ALERT] サービス障害を検出',
    Message='APIサーバーのエラー率が5%を超えました。調査してください。'
)
print("テキスト通知を送信しました")

# 構造化JSON通知（Lambda等で受け取る場合）
payload = {
    'level': 'ERROR',
    'service': 'api-server',
    'message': 'Error rate exceeded 5%',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'detail': {'error_rate': 5.3, 'threshold': 5.0}
}
sns.publish(
    TopicArn=TOPIC_ARN,
    Message=json.dumps(payload),
    MessageAttributes={
        'level': {'DataType': 'String', 'StringValue': 'ERROR'},
        'service': {'DataType': 'String', 'StringValue': 'api-server'},
    }
)
print("JSON通知を送信しました")
