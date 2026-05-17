"""
47. SQS DLQメッセージの再処理
DLQに滞留したメッセージを元キューへ差し戻す。インシデント後のリカバリに必須。
"""
import boto3
import json

sqs = boto3.client('sqs', region_name='ap-northeast-1')

DLQ_URL = 'https://sqs.ap-northeast-1.amazonaws.com/123456789012/my-queue-dlq'
SRC_URL = 'https://sqs.ap-northeast-1.amazonaws.com/123456789012/my-queue'

moved = 0
errors = 0

while True:
    response = sqs.receive_message(
        QueueUrl=DLQ_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1,
        AttributeNames=['All'],
        MessageAttributeNames=['All']
    )
    messages = response.get('Messages', [])
    if not messages:
        break

    for msg in messages:
        try:
            sqs.send_message(
                QueueUrl=SRC_URL,
                MessageBody=msg['Body'],
                MessageAttributes=msg.get('MessageAttributes', {})
            )
            sqs.delete_message(QueueUrl=DLQ_URL, ReceiptHandle=msg['ReceiptHandle'])
            moved += 1
            print(f"移動: MessageId={msg['MessageId']}")
        except Exception as e:
            errors += 1
            print(f"エラー: {msg['MessageId']} - {e}")

print(f"\n再処理完了: 成功={moved}  失敗={errors}")
