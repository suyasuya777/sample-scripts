"""共有 httpx クライアント + リトライ（02_outbound）"""
import asyncio
import random

import httpx

TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=3.0)
LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)

MAX_ATTEMPTS = 3
BASE_DELAY = 0.5
MAX_DELAY = 4.0
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIMEOUT, limits=LIMITS)


def _retryable(exc: Exception) -> bool:
    if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS
    return False


async def get_with_retry(client: httpx.AsyncClient, url: str, request_id: str) -> httpx.Response:
    headers = {"x-request-id": request_id}   # 下流へ伝搬
    last: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return r
        except Exception as exc:
            last = exc
            if not _retryable(exc) or attempt == MAX_ATTEMPTS - 1:
                raise
            await asyncio.sleep(random.uniform(0, min(MAX_DELAY, BASE_DELAY * 2 ** attempt)))
    raise RuntimeError("unreachable") from last
