"""
学習ポイント: BackgroundTasks は落ちたら消える
- 実行場所 : レスポンス返却後、同じプロセス内
- 失われる条件 : デプロイ、スケールイン、タスク異常終了、SIGKILL
- 再実行 : されない。失敗しても誰も気づかない

SRE 的な論点:
  「レスポンスを速く返す」ために BackgroundTasks を使うのは正しい。
  問題は、失われて困る処理まで載せてしまうこと。
  ローリング更新のたびに数件ずつ消えるので、障害として気づきにくく、
  数か月後に「データが合わない」形で表面化する。

  判断基準:
  | 処理                     | BackgroundTasks | キュー（SQS等） |
  |-------------------------|-----------------|----------------|
  | アクセスログの追記        | ○               | 不要           |
  | キャッシュの温め直し       | ○               | 不要           |
  | 通知メールの送信          | △               | ○              |
  | 決済の確定・在庫引当       | ×               | ○              |
  | 外部システムへの連携       | ×               | ○              |
"""
import asyncio

from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


async def write_cache(key: str) -> None:
    await asyncio.sleep(5)
    print(f"[bg] cache warmed: {key}")


# ── ○ 失われてよい処理 ────────────────────────────────
@app.post("/items/{item_id}/view")
async def record_view(item_id: int, tasks: BackgroundTasks):
    tasks.add_task(write_cache, f"item:{item_id}")
    return {"accepted": True}


# ── × 失われては困る処理 ──────────────────────────────
@app.post("/orders/{order_id}/confirm")
async def confirm_order(order_id: int, tasks: BackgroundTasks):
    # tasks.add_task(charge_payment, order_id)   ← これをやってはいけない
    #
    # 正しくは: DB に「確定待ち」で書き、キューへ投げる。
    #   1. トランザクション内で outbox テーブルに書く
    #   2. 別プロセスが outbox を読んで SQS へ送る（transactional outbox）
    #   3. ワーカーが SQS から取り出して処理し、冪等キーで二重実行を防ぐ
    return {"order_id": order_id, "status": "queued"}


# ── 再現手順 ──────────────────────────────────────────
# 1. /items/1/view を叩く（即座に応答が返る）
# 2. 5秒以内に Ctrl+C でプロセスを落とす
# 3. "[bg] cache warmed" が出力されないことを確認する
