"""リクエストスコープの値を保持する（03_observability/request_id）"""
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
