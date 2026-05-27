"""DynamoDB CRUD 操作モジュール"""
import logging
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "items"
table = dynamodb.Table(TABLE_NAME)


def put_item(item: dict) -> dict:
    """アイテムを登録・上書き"""
    try:
        table.put_item(Item=item)
        logger.info("put_item: %s", item.get("id"))
        return item
    except ClientError as e:
        logger.error("put_item error: %s", e)
        raise


def get_item(item_id: str) -> dict | None:
    """アイテムを1件取得"""
    try:
        result = table.get_item(Key={"id": item_id})
        return result.get("Item")
    except ClientError as e:
        logger.error("get_item error: %s", e)
        raise


def query_items(partition_key: str, value: str) -> list:
    """パーティションキーで検索"""
    try:
        result = table.query(
            KeyConditionExpression=Key(partition_key).eq(value)
        )
        return result.get("Items", [])
    except ClientError as e:
        logger.error("query error: %s", e)
        raise


def delete_item(item_id: str) -> None:
    """アイテムを削除"""
    try:
        table.delete_item(Key={"id": item_id})
        logger.info("delete_item: %s", item_id)
    except ClientError as e:
        logger.error("delete_item error: %s", e)
        raise
