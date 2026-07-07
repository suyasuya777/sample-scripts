from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from cruds import auth as auth_cruds
from cruds import item as item_cruds
from database import get_db
from schemas import DecodedToken, ItemCreate, ItemResponse, ItemUpdate

DbDependency = Annotated[
    AsyncSession,
    Depends(get_db)
]

UserDependency = Annotated[
    DecodedToken,
    Depends(auth_cruds.get_current_user)
]

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("", response_model=list[ItemResponse])
async def get_items(
    db: DbDependency,
    name: str | None = Query(default=None, min_length=2, max_length=20),
):
    if name is None:
        return await item_cruds.get_items(db)
    return await item_cruds.get_items_by_name(db, name)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    db: DbDependency,
    user: UserDependency,
    item_id: int = Path(gt=0)
):
    item = await item_cruds.get_item(db, item_id, user.user_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    db: DbDependency,
    user: UserDependency,
    item_in: ItemCreate
):
    return await item_cruds.create_item(db, item_in, user.user_id)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    db: DbDependency,
    user: UserDependency,
    item_in: ItemUpdate,
    item_id: int = Path(gt=0),
):
    item = await item_cruds.update_item(db, item_id, item_in, user.user_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.delete("/{item_id}", response_model=bool)
async def delete(
    db: DbDependency,
    user: UserDependency,
    item_id: int = Path(gt=0)
):
    item = await item_cruds.delete_item(db, item_id, user.user_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return True
