"""教材のリトライ／サーキットブレーカを、下流ダミーに対して動かすドライバ。

教材の `retry_backoff.py` と `circuit_breaker.py` は関数とクラスだけで、
呼び出し側が無い（`__main__` は掛け算の検算を表示するだけ）。
挙動を目で見るには呼び出し側が要るので、それをここに置く。

前提: 下流ダミーが起動していること
    docker compose -f sandbox/docker-compose.yml up -d downstream

使い方:
    python sandbox/drive.py retry   http://localhost:9001/status/503   # 3回で打ち切り
    python sandbox/drive.py retry   http://localhost:9001/status/404   # 即座に諦める
    python sandbox/drive.py retry   http://localhost:9001/throttle     # Retry-After に従う
    python sandbox/drive.py retry   http://localhost:9001/slow?seconds=8  # read タイムアウト
    python sandbox/drive.py breaker                                    # 5回失敗で OPEN
"""
from __future__ import annotations

import asyncio
import importlib.util
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent


def load(rel: str, name: str):
    """教材のファイルをパッケージ化せずに読み込む"""
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


retry_mod = load("02_outbound/retry_backoff/retry_backoff.py", "retry_backoff")
cb_mod = load("02_outbound/circuit_breaker/circuit_breaker.py", "circuit_breaker")


async def run_retry(url: str) -> None:
    timeout = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=3.0)
    started = time.monotonic()
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            r = await retry_mod.get_with_retry(client, url)
            print(f"成功 status={r.status_code} 経過={time.monotonic() - started:.1f}s")
        except Exception as exc:
            print(f"{type(exc).__name__}: {exc}")
            print(f"経過={time.monotonic() - started:.1f}s")
            print("※4xx なら HTTPStatusError が1回で、5xx や 429 なら RuntimeError が"
                  "MAX_ATTEMPTS 回ぶんの待ち時間のあとに出る")


async def run_breaker() -> None:
    """Closed → Open → Half-Open → Closed の一巡を見る。

    下流ダミーの /control で障害を入れたり戻したりして、復旧まで通す。
    """
    breaker = cb_mod.CircuitBreaker(failure_threshold=5, recovery_seconds=5.0)
    url = "http://localhost:9001/ok"

    async with httpx.AsyncClient(timeout=5.0) as client:
        async def call():
            r = await client.get(url)
            r.raise_for_status()
            return r

        async def outage(on: bool):
            await client.post(f"http://localhost:9001/control?outage={str(on).lower()}")

        try:
            await outage(True)
        except httpx.ConnectError:
            print("下流ダミーに接続できない。先に起動すること: "
                  "docker compose -f sandbox/docker-compose.yml up -d downstream")
            return

        print("-- 下流を障害状態にして、失敗を重ねる（threshold=5） --")
        for i in range(1, 8):
            try:
                await breaker.call(call)
                print(f"{i:2d} 成功  state={breaker.state.value}")
            except RuntimeError as exc:
                print(f"{i:2d} 遮断  state={breaker.state.value}  ({exc})")
            except httpx.HTTPStatusError as exc:
                print(f"{i:2d} 失敗  state={breaker.state.value}  "
                      f"failures={breaker.failures} status={exc.response.status_code}")

        print("\n-- recovery_seconds(5秒) 待つ。下流はまだ壊れたまま --")
        await asyncio.sleep(5.1)
        try:
            await breaker.call(call)
        except httpx.HTTPStatusError:
            print(f"HALF_OPEN の試行が失敗 → state={breaker.state.value}"
                  "（1回の失敗で即 OPEN に戻る）")

        print("\n-- 下流を復旧させて、もう一度 recovery を待つ --")
        await outage(False)
        await asyncio.sleep(5.1)
        r = await breaker.call(call)
        print(f"成功 status={r.status_code} → state={breaker.state.value}（CLOSED に戻る）")
        await outage(False)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"retry", "breaker"}:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "retry":
        url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:9001/status/503"
        asyncio.run(run_retry(url))
    else:
        asyncio.run(run_breaker())


if __name__ == "__main__":
    main()
