"""
学習ポイント: APIレスポンスの統一フォーマット
- Generic型でデータ型を柔軟に対応
- 成功・失敗・一覧すべて同じ構造で返す
- status / message / data の3フィールド構成
"""
from typing import Generic, TypeVar, Optional, List
from fastapi import FastAPI
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    status: str = "success"
    message: str = ""
    data: Optional[T] = None

class PagedResponse(BaseModel, Generic[T]):
    status: str = "success"
    total: int
    page: int
    limit: int
    data: List[T]

class ItemOut(BaseModel):
    id: int
    name: str

app = FastAPI()

@app.get("/items/{item_id}", response_model=ApiResponse[ItemOut])
async def get_item(item_id: int):
    return ApiResponse(data=ItemOut(id=item_id, name="PC"))

@app.get("/items", response_model=PagedResponse[ItemOut])
async def list_items(page: int = 1, limit: int = 10):
    items = [ItemOut(id=i, name=f"Item{i}") for i in range(1, 4)]
    return PagedResponse(total=3, page=page, limit=limit, data=items)
