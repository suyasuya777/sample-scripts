"""
学習ポイント: ページネーションの実装
- offset/limit方式    : skip件スキップしてlimit件取得
- カーソル方式        : 最後に取得したIDを基点に次ページを取得
- Depends でページネーション共通パラメーターを再利用
"""
from typing import List, Optional
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel

app = FastAPI()

class PaginationParams:
    def __init__(self, page: int = Query(1, ge=1),
                 limit: int = Query(10, ge=1, le=100)):
        self.skip = (page - 1) * limit
        self.limit = limit
        self.page = page

class Item(BaseModel):
    id: int
    name: str

DUMMY_ITEMS = [Item(id=i, name=f"Item{i}") for i in range(1, 51)]

@app.get("/items/offset", response_model=dict)
async def offset_pagination(params: PaginationParams = Depends()):
    """offset/limit方式: ?page=2&limit=10"""
    items = DUMMY_ITEMS[params.skip: params.skip + params.limit]
    return {"total": len(DUMMY_ITEMS), "page": params.page, "items": items}

@app.get("/items/cursor", response_model=dict)
async def cursor_pagination(
    cursor: Optional[int] = Query(None, description="最後に取得したアイテムID"),
    limit: int = Query(10, ge=1, le=100),
):
    """カーソル方式: ?cursor=20&limit=10"""
    if cursor:
        items = [i for i in DUMMY_ITEMS if i.id > cursor][:limit]
    else:
        items = DUMMY_ITEMS[:limit]
    next_cursor = items[-1].id if items else None
    return {"items": items, "next_cursor": next_cursor}
