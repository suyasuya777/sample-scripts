from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.item import ItemCreate, ItemUpdate, ItemResponse
from cruds import item as item_crud
from database import get_db


router = APIRouter(prefix="/items", tags=["Items"])

DBSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[ItemResponse])
async def get_items(
    db: DBSession
):
    items = await item_crud.get_items(db)
    return items


@router.get("/paged", response_model=list[ItemResponse])
async def get_items_paged(
    db: DBSession,
    skip: int = 0,
    limit: int =100
):
    items = await item_crud.get_items_paged(db, skip=skip, limit=limit)
    return items


@router.get("/user/{user_id}", response_model=list[ItemResponse])
async def get_items_by_user(
    user_id: int,
    db: DBSession
):
    items = await item_crud.get_items_by_user(db, user_id)
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: DBSession
):
    item = await item_crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="見つかりません")
    return item


@router.post("", response_model=ItemResponse)
async def create_item(
    item_in: ItemCreate,
    db: DBSession
):
    item = await item_crud.create_item(db, item_in)
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
async def patch_item(
    item_in: ItemUpdate,
    item_id: int,
    db: DBSession
):
    item = await item_crud.patch_item(db, item_in, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="見つかりません")
    return item


@router.delete("/{item_id}", response_model=bool)
async def delete_item(
    item_id: int,
    db: DBSession
):
    deleted = await item_crud.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="見つかりません")
    return True
