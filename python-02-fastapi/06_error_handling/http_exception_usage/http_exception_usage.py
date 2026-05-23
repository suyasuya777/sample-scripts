"""
学習ポイント: HTTPExceptionの使い方
- HTTPException      : FastAPI標準のHTTPエラー
- status_code        : 4xx/5xxのHTTPステータスコード
- detail             : エラー詳細（文字列またはdict）
- headers            : レスポンスヘッダーの追加（認証エラー時のWWW-Authenticate等）
- starlette.status   : ステータスコード定数（HTTP_404_NOT_FOUND等）
"""
from fastapi import FastAPI, HTTPException, Path
from starlette import status

app = FastAPI()

ITEMS = {1: {"name": "PC"}, 2: {"name": "スマホ"}}

@app.get("/items/{item_id}")
async def get_item(item_id: int = Path(gt=0)):
    if item_id not in ITEMS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ITEM_NOT_FOUND", "item_id": item_id},
        )
    return ITEMS[item_id]

@app.get("/protected")
async def protected(token: str = ""):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "OK"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    del ITEMS[item_id]
    return {"message": "deleted"}
