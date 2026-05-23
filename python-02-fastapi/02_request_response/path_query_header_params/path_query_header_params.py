"""
学習ポイント: パスパラメーター・クエリパラメーター・ヘッダーの受け取り
- Path  : URLパス内のパラメーター（バリデーション付き）
- Query : URLクエリ文字列のパラメーター（バリデーション付き）
- Header: HTTPリクエストヘッダーの取得
"""
from typing import Optional
from fastapi import FastAPI, Path, Query, Header, HTTPException

app = FastAPI()

@app.get("/items/{item_id}")
async def find_by_id(
    item_id: int = Path(gt=0, description="アイテムID（1以上）"),
):
    """パスパラメーター: gt=0 でIDが正の整数であることを保証"""
    return {"item_id": item_id}

@app.get("/items")
async def search(
    name: Optional[str] = Query(None, min_length=2, max_length=20),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """クエリパラメーター: /items?name=PC&page=1&limit=10"""
    return {"name": name, "page": page, "limit": limit}

@app.get("/me")
async def get_me(
    x_token: Optional[str] = Header(None, alias="X-Token"),
    user_agent: Optional[str] = Header(None),
):
    """ヘッダー: X-Token と User-Agent を受け取る"""
    if not x_token:
        raise HTTPException(status_code=401, detail="X-Token required")
    return {"x_token": x_token, "user_agent": user_agent}
