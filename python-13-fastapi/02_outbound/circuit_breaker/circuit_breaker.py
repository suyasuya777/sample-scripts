"""
学習ポイント: 連続失敗時に呼び出し自体を止める
- Closed    : 通常。失敗をカウントする
- Open      : 遮断中。呼び出さずに即失敗を返す
- Half-Open : 試験的に1本だけ通し、成功すれば Closed へ戻る

SRE 的な論点:
  リトライは「相手はすぐ直る」前提。サーキットブレーカは「相手は当分直らない」
  前提。両方ないと、障害が長引いたときに自分のスレッド/接続が呼び出し待ちで
  埋まり、相手の障害が自分の障害に変わる（カスケード障害）。

  Open 中に何を返すかは設計判断:
    - 即 503 を返す（速く失敗する）
    - キャッシュ済みの古い値を返す（縮退運転）
    - 機能を落として処理を続ける（フォールバック）
"""
import asyncio
import time
from enum import Enum


class State(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_seconds: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.state = State.CLOSED
        self.failures = 0
        self.opened_at = 0.0
        self._lock = asyncio.Lock()

    async def call(self, fn, *args, **kwargs):
        async with self._lock:
            if self.state is State.OPEN:
                if time.monotonic() - self.opened_at >= self.recovery_seconds:
                    self.state = State.HALF_OPEN
                else:
                    raise RuntimeError("circuit open: call skipped")

        try:
            result = await fn(*args, **kwargs)
        except Exception:
            async with self._lock:
                self.failures += 1
                if self.state is State.HALF_OPEN or self.failures >= self.failure_threshold:
                    self.state = State.OPEN
                    self.opened_at = time.monotonic()
            raise

        async with self._lock:
            self.failures = 0
            self.state = State.CLOSED
        return result


# ── 使い方 ────────────────────────────────────────────
# breaker = CircuitBreaker(failure_threshold=5, recovery_seconds=30)
# try:
#     r = await breaker.call(client.get, url)
# except RuntimeError:
#     return fallback_response()
#
# ── 監視 ──────────────────────────────────────────────
# state が OPEN になった回数と継続時間はメトリクス化しておく。
# 「気づいたら半日遮断されていた」を防ぐため、OPEN はアラート対象にする。
