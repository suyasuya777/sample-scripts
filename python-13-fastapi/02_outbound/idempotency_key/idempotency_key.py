"""
学習ポイント: 非冪等な処理を安全にリトライする
- 冪等     : 同じ操作を何度実行しても結果が同じ。GET / PUT / DELETE
- 非冪等   : POST。2回実行すると2件できる
- 冪等キー : クライアントが採番した一意キーで重複実行を弾く

SRE 的な論点:
  最も危険なのは「タイムアウトしたが、実は成功していた」ケース。
  クライアントは失敗と判断してリトライし、サーバ側では2回実行される。
  決済や在庫引当でこれが起きると、金銭的な被害になる。

  タイムアウト = 失敗ではない。「結果が不明」である。
  結果が不明な非冪等処理は、冪等キーなしにリトライしてはいけない。
"""
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# 実運用では Redis や DynamoDB に置く（TTL 付き）
_STORE: dict[str, dict[str, Any]] = {}
TTL_SECONDS = 24 * 60 * 60


class OrderIn(BaseModel):
    item_id: int
    quantity: int


def _get(key: str):
    rec = _STORE.get(key)
    if rec and time.time() - rec["at"] < TTL_SECONDS:
        return rec
    _STORE.pop(key, None)
    return None


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderIn,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")

    cached = _get(idempotency_key)
    if cached:
        # 同じキーでの再送。処理は行わず、前回と同じ結果を返す
        if cached["body"] != body.model_dump():
            # キーは同じだが中身が違う = クライアント側の不具合
            raise HTTPException(status_code=409, detail="key reused with different body")
        return cached["result"]

    # ── 実処理 ────────────────────────────────────────
    result = {"order_id": f"ord_{len(_STORE) + 1}", "item_id": body.item_id}

    _STORE[idempotency_key] = {"at": time.time(), "body": body.model_dump(), "result": result}
    return result


# ── 動作確認 ──────────────────────────────────────────
# curl -X POST localhost:8000/orders -H 'Idempotency-Key: abc' \
#      -H 'content-type: application/json' -d '{"item_id":1,"quantity":2}'
# 同じコマンドを2回打っても order_id が変わらないことを確認する
