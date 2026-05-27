from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from cruds import item as item_crud
from schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("", response_model=list[ItemResponse])
async def find_all(db: AsyncSession = Depends(get_db)):
    return await item_crud.get_items(db)


@router.get("/user/{user_id}", response_model=list[ItemResponse])
async def find_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await item_crud.get_items_by_user(db, user_id)


@router.post("", response_model=ItemResponse)
async def create(item_in: ItemCreate, db: AsyncSession = Depends(get_db)):
    return await item_crud.create_item(db, item_in)