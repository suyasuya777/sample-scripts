"""
API Gateway → Lambda → DynamoDB → SES の一連のフロー実装

ディレクトリ構成:
  api_gateway_dynamodb_ses_integration/
    ├── handler.py   # Lambda エントリーポイント（ルーティング）
    ├── db.py        # DynamoDB CRUD 操作
    └── mailer.py    # SES メール送信
"""
import json
import logging
import uuid

import db
import mailer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

NOTIFY_EMAIL = "admin@example.com"


# ── レスポンスヘルパー ────────────────────────────────────────
def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False, default=str),
    }


# ── ルーティング ─────────────────────────────────────────────
def handle_post(event: dict) -> dict:
    """アイテム登録 → SES でメール通知"""
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"message": "リクエストボディが不正です"})

    if not body.get("name"):
        return response(400, {"message": "name は必須です"})

    item = {"id": str(uuid.uuid4()), **body}
    db.put_item(item)

    # 登録完了メール通知
    mailer.send_notification(
        to=NOTIFY_EMAIL,
        subject="アイテム登録通知",
        body_text=f"アイテムが登録されました。\nID: {item['id']}\n名前: {item['name']}",
    )
    return response(201, {"message": "登録しました", "item": item})


def handle_get(event: dict) -> dict:
    """アイテム取得"""
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        return response(400, {"message": "id が必要です"})

    item = db.get_item(item_id)
    if not item:
        return response(404, {"message": "アイテムが見つかりません"})
    return response(200, item)


def handle_delete(event: dict) -> dict:
    """アイテム削除"""
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        return response(400, {"message": "id が必要です"})

    db.delete_item(item_id)
    return response(200, {"message": "削除しました", "id": item_id})


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    method = event.get("httpMethod", "")
    logger.info("method=%s", method)

    if method == "POST":
        return handle_post(event)
    if method == "GET":
        return handle_get(event)
    if method == "DELETE":
        return handle_delete(event)

    return response(405, {"message": f"メソッド {method} は許可されていません"})
