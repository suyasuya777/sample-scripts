import json
import logging
import hashlib
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client("sqs")
DLQ_URL = "https://sqs.ap-northeast-1.amazonaws.com/123456789012/my-dlq"


# ── カスタム例外 ──────────────────────────────────────────────
class RetryableError(Exception):
    """再試行可能なエラー（一時的な障害など）"""


class NonRetryableError(Exception):
    """再試行不要なエラー（バリデーションエラーなど）"""


# ── 冪等性チェック ────────────────────────────────────────────
_processed_ids: set = set()  # 本番は DynamoDB 等で管理


def is_already_processed(idempotency_key: str) -> bool:
    """同一リクエストの重複処理を防ぐ"""
    return idempotency_key in _processed_ids


def mark_as_processed(idempotency_key: str) -> None:
    _processed_ids.add(idempotency_key)


# ── DLQ への送信 ──────────────────────────────────────────────
def send_to_dlq(payload: dict, reason: str) -> None:
    """処理不能なメッセージを DLQ に送信"""
    message = json.dumps({"payload": payload, "failure_reason": reason}, ensure_ascii=False)
    try:
        sqs.send_message(QueueUrl=DLQ_URL, MessageBody=message)
        logger.warning("DLQ 送信: reason=%s", reason)
    except ClientError as e:
        logger.error("DLQ 送信失敗: %s", e)


# ── ビジネスロジック ──────────────────────────────────────────
def process(payload: dict) -> dict:
    """
    冪等性を考慮した処理。
    idempotency_key で重複実行を防ぐ。
    """
    idempotency_key = hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    if is_already_processed(idempotency_key):
        logger.info("重複リクエストをスキップ: key=%s", idempotency_key)
        return {"status": "skipped"}

    if not payload.get("id"):
        raise NonRetryableError("id が必要です")

    # 処理本体（例: DB 登録、外部 API 呼び出しなど）
    logger.info("処理実行: id=%s", payload["id"])
    mark_as_processed(idempotency_key)
    return {"status": "success", "id": payload["id"]}


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    """
    Lambda Destinations / maximumRetryAttempts と組み合わせて使用する想定。
    NonRetryableError は DLQ に直接送り、RetryableError は Lambda に再試行させる。
    """
    logger.info("event: %s", json.dumps(event))

    try:
        result = process(event)
        return {"statusCode": 200, "body": json.dumps(result)}

    except NonRetryableError as e:
        # 再試行しても意味がないエラーは DLQ へ
        logger.error("NonRetryableError: %s", e)
        send_to_dlq(event, str(e))
        return {"statusCode": 400, "body": json.dumps({"message": str(e)})}

    except RetryableError as e:
        # 再試行させるために例外を raise して Lambda にリトライを委ねる
        logger.error("RetryableError: %s", e)
        raise

    except Exception as e:
        logger.error("予期しないエラー: %s", e)
        send_to_dlq(event, f"Unexpected: {e}")
        raise
