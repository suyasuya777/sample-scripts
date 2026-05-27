import json
import logging
from datetime import datetime, timezone

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("items")


# ── バッチ処理の実装例 ────────────────────────────────────────
def cleanup_old_records(cutoff_date: str) -> int:
    """
    古いレコードの削除（定期クリーンアップ例）。
    cutoff_date: "2024-01-01" 形式
    """
    deleted = 0
    scan_kwargs: dict = {
        "FilterExpression": "created_at < :cutoff",
        "ExpressionAttributeValues": {":cutoff": cutoff_date},
        "ProjectionExpression": "id",
    }

    while True:
        result = table.scan(**scan_kwargs)
        for item in result.get("Items", []):
            table.delete_item(Key={"id": item["id"]})
            deleted += 1

        if "LastEvaluatedKey" not in result:
            break
        scan_kwargs["ExclusiveStartKey"] = result["LastEvaluatedKey"]

    logger.info("削除件数: %d", deleted)
    return deleted


def generate_daily_report() -> dict:
    """日次レポート生成の雛形"""
    result = table.scan(Select="COUNT")
    total = result.get("Count", 0)
    logger.info("レコード総数: %d", total)
    return {"total": total}


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    """
    EventBridge スケジュールから呼び出される。

    cron 式の例（毎日 AM 2:00 JST）: cron(0 17 * * ? *)
    rate 式の例（5分ごと）: rate(5 minutes)

    event["time"] に実行時刻（ISO 8601 形式）が含まれる。
    """
    exec_time = event.get("time", "")
    logger.info("実行時刻: %s", exec_time)

    now = datetime.now(timezone.utc)
    cutoff = now.strftime("%Y-%m-01")  # 当月1日より前を削除対象とする例

    deleted = cleanup_old_records(cutoff)
    report = generate_daily_report()

    return {
        "statusCode": 200,
        "body": json.dumps({"deleted": deleted, "report": report}),
    }
