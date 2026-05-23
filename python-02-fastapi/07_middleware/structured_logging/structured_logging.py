"""
学習ポイント: 構造化ログ（JSON形式）の実装
- python-json-logger : ログをJSON形式で出力するライブラリ
- ログフィールド      : timestamp / level / message / request_id / user_id 等
- CloudWatch対応     : JSON形式にすることでAWS CloudWatch Logs Insightsで検索可能
"""
import logging
import json
from datetime import datetime
from fastapi import FastAPI, Request

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level":     record.levelname,
            "message":   record.getMessage(),
            "module":    record.module,
            "function":  record.funcName,
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data, ensure_ascii=False)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(item_id: int, request: Request):
    logger.info("Item retrieved", extra={
        "extra": {"item_id": item_id, "path": str(request.url.path), "method": request.method}
    })
    return {"id": item_id}
