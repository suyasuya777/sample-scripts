from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cruds import user as user_crud
from database import get_db
from schemas.user import UserCreate, UserResponse, UserUpdate


router = APIRouter(prefix="/users", tags=["Users"])

DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("", response_model=list[UserResponse])
async def get_users(
    db: DBSession
):
    return await user_crud.get_users(db)


@router.get("/paged", response_model=list[UserResponse])
async def get_users_paged(
    db: DBSession,
    skip: int = 0,
    limit: int = 100
):
    return await user_crud.get_users_paged(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: DBSession
):
    user = await user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="見つかりません")
    return user


@router.post("", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: DBSession
):
    return await user_crud.create_user(db, user_in)


@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_in: UserUpdate,
    user_id: int,
    db: DBSession
):
    user = await user_crud.patch_user(db, user_in, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="見つかりません")
    return user


@router.delete("/{user_id}", response_model=bool)
async def delete_user(
    user_id: int,
    db: DBSession
):
    deleted = await user_crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="見つかりません")
    return True
