"""
学習ポイント: 構造化ログに必須フィールドを揃える
- 必須      : timestamp / level / message / request_id / path / method / status / duration_ms
- ContextVar : ログ出力時に request_id を自動で差し込む（Filter を使う）
- 出力先    : 標準出力に出すだけ。CloudWatch へは awslogs ドライバが運ぶ

SRE 的な論点:
  アプリから直接 CloudWatch API を叩く方式（watchtower 等）は failure mode を増やす。
    - IAM 権限が必要になる
    - CloudWatch API 障害時にアプリ側で詰まる/例外が出る
    - プロセス強制終了でバッファが飛ぶ
  ECS なら awslogs / FireLens ドライバに任せ、アプリは標準出力に出すだけにする。
  これが「アプリはログを書く、運ぶのは基盤の仕事」という分離。
"""
import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# ログに常に含めたい固定値
SERVICE = "sample-api"
ENV = "dev"


class RequestIdFilter(logging.Filter):
    """全レコードに request_id を差し込む"""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "service": SERVICE,
            "env": ENV,
            "request_id": getattr(record, "request_id", "-"),
        }
        # extra= で渡した任意フィールドを取り込む
        for k, v in getattr(record, "fields", {}).items():
            payload[k] = v
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    return logging.getLogger(SERVICE)


if __name__ == "__main__":
    log = setup_logging()
    request_id_var.set("abc123")
    log.info("order created", extra={"fields": {"order_id": "ord_1", "amount": 1200}})
    try:
        1 / 0
    except ZeroDivisionError:
        log.error("unexpected error", exc_info=True)


# ── CloudWatch Logs Insights のクエリ例 ────────────────
# fields @timestamp, request_id, path, status, duration_ms
# | filter status >= 500
# | sort @timestamp desc
# | limit 50
#
# stats count(*) as n, pct(duration_ms, 99) as p99 by path
# | sort p99 desc
