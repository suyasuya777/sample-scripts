import json
import logging
import boto3
from boto3.dynamodb.types import TypeDeserializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

deserializer = TypeDeserializer()


def deserialize(record: dict) -> dict:
    """DynamoDB 形式 → 通常の Python dict に変換"""
    return {k: deserializer.deserialize(v) for k, v in record.items()}


# ── イベント種別ごとの処理 ────────────────────────────────────
def on_insert(new_image: dict) -> None:
    """INSERT: 新規レコード追加時の処理"""
    logger.info("INSERT: %s", new_image)
    # 例: 検索インデックスへの追加、Slack 通知など


def on_modify(old_image: dict, new_image: dict) -> None:
    """MODIFY: レコード更新時の処理（変更差分の検知）"""
    diff = {
        k: {"before": old_image.get(k), "after": new_image.get(k)}
        for k in set(old_image) | set(new_image)
        if old_image.get(k) != new_image.get(k)
    }
    logger.info("MODIFY diff: %s", diff)
    # 例: 監査ログ記録、検索インデックスの更新など


def on_remove(old_image: dict) -> None:
    """REMOVE: レコード削除時の処理"""
    logger.info("REMOVE: %s", old_image)
    # 例: 検索インデックスからの削除など


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    logger.info("Records count: %d", len(event.get("Records", [])))

    for record in event.get("Records", []):
        event_name = record["eventName"]  # INSERT / MODIFY / REMOVE
        dynamodb = record.get("dynamodb", {})

        new_image = deserialize(dynamodb.get("NewImage", {}))
        old_image = deserialize(dynamodb.get("OldImage", {}))

        logger.info("eventName=%s", event_name)

        if event_name == "INSERT":
            on_insert(new_image)
        elif event_name == "MODIFY":
            on_modify(old_image, new_image)
        elif event_name == "REMOVE":
            on_remove(old_image)

    return {"statusCode": 200, "body": "OK"}
