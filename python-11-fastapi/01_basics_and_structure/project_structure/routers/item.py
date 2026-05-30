from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from cruds import item as item_crud
from schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("", response_model=list[ItemResponse])
async def find_all(db: AsyncSession = Depends(get_db)):
    return await item_crud.get_items(db)


@router.get("/paged", response_model=list[ItemResponse])
async def find_paged(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await item_crud.get_items_paged(db, skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=list[ItemResponse])
async def find_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await item_crud.get_items_by_user(db, user_id)


@router.get("/{item_id}", response_model=ItemResponse)
async def find_one(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await item_crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemResponse)
async def create(item_in: ItemCreate, db: AsyncSession = Depends(get_db)):
    return await item_crud.create_user_item(db, item_in, item_in.user_id)


@router.put("/{item_id}", response_model=ItemResponse)
async def update(item_id: int, item_in: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = await item_crud.update_item(db, item_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def patch(item_id: int, item_in: ItemUpdate, db: AsyncSession = Depends(get_db)):
    item = await item_crud.patch_item(db, item_id, item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", response_model=bool)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await item_crud.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted
