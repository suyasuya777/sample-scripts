"""
46. SQS キューの属性取得（滞留数確認）
ApproximateNumberOfMessages でメッセージ滞留数を監視する。DLQの監視に特に有効。
"""
import boto3

sqs = boto3.client('sqs', region_name='ap-northeast-1')

queue_urls = sqs.list_queues().get('QueueUrls', [])
print(f"キュー数: {len(queue_urls)}\n")
print(f"{'キュー名':<40}  {'待機':>6}  {'処理中':>6}  {'遅延':>6}  DLQ警告")
print("-" * 70)

for url in queue_urls:
    name = url.split('/')[-1]
    attrs = sqs.get_queue_attributes(
        QueueUrl=url,
        AttributeNames=[
            'ApproximateNumberOfMessages',
            'ApproximateNumberOfMessagesNotVisible',
            'ApproximateNumberOfMessagesDelayed',
        ]
    )['Attributes']
    visible = int(attrs['ApproximateNumberOfMessages'])
    in_flight = int(attrs['ApproximateNumberOfMessagesNotVisible'])
    delayed = int(attrs['ApproximateNumberOfMessagesDelayed'])
    is_dlq = 'dlq' in name.lower() or 'dead' in name.lower()
    alert = '🔴 滞留あり' if (is_dlq and visible > 0) else ''
    print(f"{name:<40}  {visible:>6}  {in_flight:>6}  {delayed:>6}  {alert}")
