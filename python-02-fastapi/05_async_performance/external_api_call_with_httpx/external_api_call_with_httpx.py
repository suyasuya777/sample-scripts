"""
学習ポイント: httpx による外部API呼び出し
- httpx.AsyncClient : 非同期HTTPクライアント（FastAPIのasync defと相性が良い）
- 接続タイムアウト  : connect / read / write の個別設定
- リトライ処理      : 失敗時の再試行ロジック
- コンテキストマネージャー: with文でセッションを管理してリソースをリーク防止
"""
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI()

TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)

@app.get("/external/posts/{post_id}")
async def get_external_post(post_id: int):
    """外部APIを非同期で呼び出す"""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(
                f"https://jsonplaceholder.typicode.com/posts/{post_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="外部APIタイムアウト")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="外部APIエラー")

@app.get("/external/with-retry/{post_id}")
async def get_with_retry(post_id: int, max_retries: int = 3):
    """リトライ付き外部API呼び出し"""
    for attempt in range(max_retries):
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                response = await client.get(
                    f"https://jsonplaceholder.typicode.com/posts/{post_id}"
                )
                response.raise_for_status()
                return {"attempt": attempt + 1, "data": response.json()}
            except (httpx.TimeoutException, httpx.HTTPStatusError):
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=503, detail="最大リトライ回数超過")
