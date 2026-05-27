import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── CORS ヘッダー ─────────────────────────────────────────────
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


# ── バリデーション ─────────────────────────────────────────────
def validate_item(body: dict) -> str | None:
    """必須フィールドチェック。エラーメッセージを返す（問題なければ None）"""
    if not body.get("name"):
        return "name は必須です"
    if not isinstance(body.get("price"), (int, float)):
        return "price は数値で指定してください"
    return None


# ── ルーティング ─────────────────────────────────────────────
def handle_get(event: dict) -> dict:
    item_id = event.get("pathParameters", {}) or {}
    item_id = item_id.get("id")
    if item_id:
        # 単件取得（本来は DB 参照）
        return response(200, {"id": item_id, "name": "sample", "price": 1000})
    # 一覧取得
    return response(200, {"items": []})


def handle_post(event: dict) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"message": "リクエストボディが不正です"})

    error = validate_item(body)
    if error:
        return response(400, {"message": error})

    # 本来は DB 登録
    logger.info("POST item: %s", body)
    return response(201, {"message": "登録しました", "item": body})


def handle_put(event: dict) -> dict:
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        return response(400, {"message": "id が指定されていません"})

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"message": "リクエストボディが不正です"})

    logger.info("PUT item id=%s body=%s", item_id, body)
    return response(200, {"message": "更新しました", "id": item_id})


def handle_delete(event: dict) -> dict:
    item_id = (event.get("pathParameters") or {}).get("id")
    if not item_id:
        return response(400, {"message": "id が指定されていません"})

    logger.info("DELETE item id=%s", item_id)
    return response(200, {"message": "削除しました", "id": item_id})


# ── Lambda ハンドラー ─────────────────────────────────────────
def lambda_handler(event: dict, context) -> dict:
    method = event.get("httpMethod", "")
    logger.info("method=%s path=%s", method, event.get("path"))

    if method == "OPTIONS":
        return response(200, {})
    if method == "GET":
        return handle_get(event)
    if method == "POST":
        return handle_post(event)
    if method == "PUT":
        return handle_put(event)
    if method == "DELETE":
        return handle_delete(event)

    return response(405, {"message": f"メソッド {method} は許可されていません"})
