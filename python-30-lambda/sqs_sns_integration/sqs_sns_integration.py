import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_message(body: dict) -> None:
    """
    メッセージ1件の処理。
    例外を raise するとそのメッセージを batchItemFailures に含める。
    """
    logger.info("処理中: %s", body)
    # ここに実際のビジネスロジックを実装
    # 例: DB 登録、外部 API 呼び出しなど


def parse_body(record: dict) -> dict:
    """
    SNS → SQS 経由の場合、SQS body の中に SNS の Message が入る。
    直接 SQS の場合はそのまま JSON パースする。
    """
    raw = json.loads(record["body"])
    # SNS → SQS サブスクリプション構成の場合
    if "Message" in raw and "Type" in raw:
        return json.loads(raw["Message"])
    return raw


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    """
    SQS イベントソースのバッチ処理。
    失敗したメッセージのみ batchItemFailures に含めて返す（部分的失敗）。
    """
    failures = []

    for record in event.get("Records", []):
        message_id = record["messageId"]
        try:
            body = parse_body(record)
            process_message(body)
            logger.info("成功: messageId=%s", message_id)
        except Exception as e:
            logger.error("失敗: messageId=%s error=%s", message_id, e)
            failures.append({"itemIdentifier": message_id})

    logger.info("合計=%d 失敗=%d", len(event["Records"]), len(failures))

    # batchItemFailures に含めたメッセージのみ再試行される
    return {"batchItemFailures": failures}
