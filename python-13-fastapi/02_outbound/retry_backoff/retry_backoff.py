"""
学習ポイント: 何をリトライし、どう間隔を空けるか
- リトライ対象の選別 : 接続失敗・タイムアウト・429・一部の 5xx のみ
- 指数バックオフ     : 1回目 0.5s, 2回目 1s, 3回目 2s ...
- ジッタ             : 再試行の時刻を散らし、波が揃うのを防ぐ
- 予算               : 総試行回数だけでなく、総所要時間にも上限を置く

SRE 的な論点:
  リトライは「相手が一時的に不調」を前提にした対策。相手が過負荷で落ちている
  ときにリトライすると、負荷をさらに増やして復旧を妨げる（リトライストーム）。
  多段構成では掛け算になる。3層がそれぞれ3回なら、最悪 27 倍。
  対策はバックオフ・ジッタ・上限・サーキットブレーカの組み合わせ。

  4xx をリトライしてはいけない理由:
    400/401/403/404 はリクエスト内容が原因。何度送っても結果は変わらない。
    例外は 429（Retry-After に従う）と 408。
"""
import asyncio
import random

import httpx

MAX_ATTEMPTS = 3
BASE_DELAY = 0.5      # 秒
MAX_DELAY = 8.0       # 1回の待機の上限
TOTAL_BUDGET = 10.0   # リトライ全体に使ってよい時間の上限

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def is_retryable(exc: Exception) -> bool:
    if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS
    return False


def backoff_delay(attempt: int) -> float:
    """指数バックオフ + フルジッタ"""
    capped = min(MAX_DELAY, BASE_DELAY * (2 ** attempt))
    return random.uniform(0, capped)


async def get_with_retry(client: httpx.AsyncClient, url: str) -> httpx.Response:
    spent = 0.0
    last_exc: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            r = await client.get(url)
            r.raise_for_status()
            return r
        except Exception as exc:
            last_exc = exc
            if not is_retryable(exc):
                raise                      # 4xx 等はここで即座に諦める
            if attempt == MAX_ATTEMPTS - 1:
                break

            delay = backoff_delay(attempt)
            if isinstance(exc, httpx.HTTPStatusError):
                # 429 は Retry-After があれば従う
                ra = exc.response.headers.get("retry-after")
                if ra and ra.isdigit():
                    delay = max(delay, float(ra))
            if spent + delay > TOTAL_BUDGET:
                break                      # 時間予算を超えるなら打ち切る
            await asyncio.sleep(delay)
            spent += delay

    raise RuntimeError(f"retry exhausted after {MAX_ATTEMPTS} attempts") from last_exc


# ── 掛け算の検算 ──────────────────────────────────────
def amplification(layers: list[int]) -> int:
    """各層のリトライ回数から、最悪時の総リクエスト数を求める"""
    total = 1
    for n in layers:
        total *= n
    return total


if __name__ == "__main__":
    print("3層 x 各3回 =", amplification([3, 3, 3]), "倍")
    print("2層 x 各2回 =", amplification([2, 2]), "倍")
