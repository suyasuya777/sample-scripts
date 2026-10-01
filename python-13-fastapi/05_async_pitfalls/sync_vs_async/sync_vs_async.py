"""
学習ポイント: async def と def の使い分け
- async def : イベントループで実行。await で明示的に譲る必要がある
- def       : FastAPI が自動でスレッドプールへ回す（anyio のワーカースレッド）
- スレッドプールには上限があり、既定では 40 スレッド程度

判断基準:
| 処理の中身                        | 書き方     |
|----------------------------------|-----------|
| 非同期ライブラリ（httpx, asyncpg） | async def |
| 同期ライブラリ（requests, psycopg2）| def       |
| CPU 負荷が高い処理                 | def（または別プロセス） |
| 何も待たない軽い処理               | どちらでも |

SRE 的な論点:
  最悪の組み合わせは「async def の中で同期ライブラリを呼ぶ」。
  イベントループを止めるうえ、スレッドプールにも逃がされない。
  次に危ないのは「def で書いた重い処理が多い」状態。
  スレッドプールの上限に達すると、以降のリクエストは待ち行列に入る。
  スレッド枯渇はアプリ側にエラーが出ず、レイテンシだけが伸びる。
"""
import anyio
from fastapi import FastAPI

app = FastAPI()


@app.get("/threadpool-limit")
async def threadpool_limit():
    """現在のスレッドプールの設定を確認する"""
    limiter = anyio.to_thread.current_default_thread_limiter()
    return {
        "total_tokens": limiter.total_tokens,       # 上限
        "borrowed_tokens": limiter.borrowed_tokens,  # 使用中
    }


# ── 上限を変える ──────────────────────────────────────
# 同期エンドポイントが多く、かつ処理が長い場合は増やす選択もある。
# ただし増やせば増やすほどメモリと下流への同時接続が増える。
# 「増やす前に、なぜそんなに同期処理があるのか」を先に考える。
#
# @app.on_event("startup")
# async def _tune():
#     anyio.to_thread.current_default_thread_limiter().total_tokens = 80
