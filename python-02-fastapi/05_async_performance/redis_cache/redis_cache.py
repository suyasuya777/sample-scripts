"""
学習ポイント: Redisキャッシュの活用
- redis.asyncio  : 非同期Redisクライアント
- SET / GET / TTL: キャッシュの保存・取得・有効期限設定
- キャッシュパターン: Cache-Aside（読み時にキャッシュがなければDBから取得してキャッシュ保存）
- JSON直列化     : オブジェクトをJSON文字列に変換してRedisに保存

実行前に Redis を起動: docker run -p 6379:6379 redis:alpine
"""
import json
from typing import Optional
from fastapi import FastAPI
import redis.asyncio as aioredis

app = FastAPI()
redis_client: Optional[aioredis.Redis] = None

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()

FAKE_DB = {1: {"id": 1, "name": "PC", "price": 50000},
           2: {"id": 2, "name": "スマホ", "price": 30000}}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    cache_key = f"item:{item_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}
    item = FAKE_DB.get(item_id)
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item not found")
    await redis_client.set(cache_key, json.dumps(item), ex=60)  # TTL: 60秒
    return {"source": "db", "data": item}

@app.delete("/items/{item_id}/cache")
async def invalidate_cache(item_id: int):
    """キャッシュの無効化（更新・削除時に呼び出す）"""
    await redis_client.delete(f"item:{item_id}")
    return {"message": f"Cache for item:{item_id} invalidated"}
