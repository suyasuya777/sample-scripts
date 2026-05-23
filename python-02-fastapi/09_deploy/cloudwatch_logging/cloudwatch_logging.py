"""
学習ポイント: AWS CloudWatch Logsへのログ送信（α）
- watchtower              : CloudWatch Logs向けのPythonログハンドラー
- JSON形式のログ           : CloudWatch Logs Insightsで検索・集計しやすい形式
- ロググループ・ストリーム : CloudWatch上のログの整理単位

実行前に AWS 認証情報を設定（IAMロール or 環境変数）
必要なIAMポリシー: logs:CreateLogGroup / logs:CreateLogStream / logs:PutLogEvents
"""
import logging
import json
from datetime import datetime
import os
# import watchtower  # pip install watchtower

from fastapi import FastAPI, Request

app = FastAPI()

class CloudWatchJsonFormatter(logging.Formatter):
    """CloudWatch Logs Insights で検索しやすいJSON形式"""
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level":     record.levelname,
            "message":   record.getMessage(),
            "service":   "fastapi-app",
            "environment": os.getenv("APP_ENV", "development"),
        }
        return json.dumps(log_entry, ensure_ascii=False)

def setup_cloudwatch_logger(log_group: str = "/fastapi/app") -> logging.Logger:
    """
    CloudWatchへのログ送信設定（watchtowerを使用）
    実際の使用時は import watchtower のコメントを外す
    """
    logger = logging.getLogger("cloudwatch")
    logger.setLevel(logging.INFO)
    # cw_handler = watchtower.CloudWatchLogHandler(log_group=log_group)
    # cw_handler.setFormatter(CloudWatchJsonFormatter())
    # logger.addHandler(cw_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CloudWatchJsonFormatter())
    logger.addHandler(stream_handler)
    return logger

logger = setup_cloudwatch_logger()

@app.get("/items/{item_id}")
async def get_item(item_id: int, request: Request):
    logger.info(json.dumps({"action": "get_item", "item_id": item_id,
                             "client_ip": request.client.host}))
    return {"id": item_id}
