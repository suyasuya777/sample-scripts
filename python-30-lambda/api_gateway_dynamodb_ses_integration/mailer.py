"""SES メール送信モジュール"""
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

ses = boto3.client("ses", region_name="ap-northeast-1")

SENDER = "no-reply@example.com"


def send_notification(to: str, subject: str, body_text: str, body_html: str = "") -> str:
    """
    SES でメール送信する。
    HTML 本文が指定された場合はマルチパートで送信する。
    戻り値: MessageId
    """
    message_body: dict = {"Text": {"Data": body_text, "Charset": "UTF-8"}}
    if body_html:
        message_body["Html"] = {"Data": body_html, "Charset": "UTF-8"}

    try:
        result = ses.send_email(
            Source=SENDER,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": message_body,
            },
        )
        message_id = result["MessageId"]
        logger.info("メール送信完了: to=%s MessageId=%s", to, message_id)
        return message_id
    except ClientError as e:
        logger.error("メール送信失敗: %s", e)
        raise
