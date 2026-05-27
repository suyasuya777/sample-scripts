import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns")

STANDARD_TOPIC_ARN = "arn:aws:sns:ap-northeast-1:123456789012:my-topic"
FIFO_TOPIC_ARN = "arn:aws:sns:ap-northeast-1:123456789012:my-topic.fifo"


# ── スタンダードトピックへの発行 ──────────────────────────────
def publish_standard(message: dict, event_type: str) -> str:
    """
    メッセージ属性（MessageAttributes）を付与して発行。
    サブスクリプションのフィルターポリシーと組み合わせて
    特定の属性を持つメッセージだけを配信できる。
    """
    result = sns.publish(
        TopicArn=STANDARD_TOPIC_ARN,
        Message=json.dumps(message, ensure_ascii=False),
        Subject=f"イベント通知: {event_type}",
        MessageAttributes={
            "event_type": {
                "DataType": "String",
                "StringValue": event_type,
            }
        },
    )
    message_id = result["MessageId"]
    logger.info("standard publish: MessageId=%s event_type=%s", message_id, event_type)
    return message_id


# ── FIFO トピックへの発行 ─────────────────────────────────────
def publish_fifo(message: dict, group_id: str, dedup_id: str) -> str:
    """
    FIFO トピックは MessageGroupId / MessageDeduplicationId が必須。
    同じ dedup_id のメッセージは5分間の重複排除ウィンドウ内で1回のみ配信される。
    """
    result = sns.publish(
        TopicArn=FIFO_TOPIC_ARN,
        Message=json.dumps(message, ensure_ascii=False),
        MessageGroupId=group_id,
        MessageDeduplicationId=dedup_id,
    )
    message_id = result["MessageId"]
    logger.info("fifo publish: MessageId=%s group=%s", message_id, group_id)
    return message_id


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    topic_type = event.get("topic_type", "standard")
    message = event.get("message", {})

    if topic_type == "fifo":
        group_id = event.get("group_id", "default")
        dedup_id = event.get("dedup_id", "")
        message_id = publish_fifo(message, group_id, dedup_id)
    else:
        event_type = event.get("event_type", "default")
        message_id = publish_standard(message, event_type)

    return {"statusCode": 200, "messageId": message_id}
