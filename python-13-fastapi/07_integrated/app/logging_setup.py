"""構造化ログ（03_observability/json_logging + log_masking）"""
import json
import logging
import sys
from datetime import datetime, timezone

from .context import request_id_var

SERVICE = "integrated-sample"
SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "authorization"}


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def _mask(obj):
    if isinstance(obj, dict):
        return {k: ("***" if k.lower() in SENSITIVE_KEYS else _mask(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_mask(v) for v in obj]
    return obj


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "service": SERVICE,
            "request_id": getattr(record, "request_id", "-"),
        }
        payload.update(_mask(getattr(record, "fields", {})))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
