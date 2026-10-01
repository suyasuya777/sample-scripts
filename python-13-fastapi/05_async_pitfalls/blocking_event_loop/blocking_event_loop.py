"""
学習ポイント: async def の中で同期処理を呼ぶとワーカー全体が止まる
- イベントループは1スレッド。await しない処理の間、他のリクエストは進まない
- 症状 : 特定のエンドポイントを叩くと、無関係なリクエストまで遅くなる
- 原因になりやすいもの: time.sleep / requests / 同期DBドライバ / 重いCPU処理

SRE 的な論点:
  この障害は「アプリのログには何も出ない」。エラーにならず、ただ遅くなる。
  CPU 使用率も上がらない（sleep や同期 I/O 待ちなら）。
  ALB のアクセスログで target_processing_time だけが伸び、
  原因のエンドポイントと被害を受けたエンドポイントが別物なので、
  「なぜこの API が遅いのか」を追っても答えが出ない。

  見分け方: 遅くなった時刻に、同一タスクへ届いた別のリクエストを調べる。
  重い同期処理が走っていれば、そこが犯人。
"""
import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


# ── ❌ 悪い例: イベントループを止める ─────────────────
@app.get("/blocking")
async def blocking():
    time.sleep(3)          # ここで全リクエストが止まる
    return {"mode": "blocking"}


# ── ✅ 良い例1: 非同期で待つ ──────────────────────────
@app.get("/non-blocking")
async def non_blocking():
    await asyncio.sleep(3)  # 他のリクエストは進む
    return {"mode": "non-blocking"}


# ── ✅ 良い例2: 同期処理はスレッドへ逃がす ────────────
@app.get("/offloaded")
async def offloaded():
    await asyncio.to_thread(time.sleep, 3)
    return {"mode": "offloaded"}


# ── ✅ 良い例3: そもそも def で書く（FastAPI がスレッドへ回す）
@app.get("/sync-def")
def sync_def():
    time.sleep(3)
    return {"mode": "sync-def"}


# ── 再現手順 ──────────────────────────────────────────
# 1. uvicorn blocking_event_loop:app --workers 1
# 2. 別ターミナルで:  curl localhost:8000/blocking &
# 3. すぐに:          time curl localhost:8000/sync-def
#    → /blocking の3秒が終わるまで応答が返らないことを確認する
# 4. /blocking を /non-blocking に変えて同じことをすると、待たされない
