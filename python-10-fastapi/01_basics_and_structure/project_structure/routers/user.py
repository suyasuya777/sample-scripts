from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from cruds import user as user_crud
from schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def find_all(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_users(db)


@router.get("/paged", response_model=list[UserResponse])
async def find_paged(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await user_crud.get_users_paged(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def find_one(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse)
async def create(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_crud.create_user(db, user_in)


@router.put("/{user_id}", response_model=UserResponse)
async def update(user_id: int, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def patch(user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await user_crud.patch_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=bool)
async def delete(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await user_crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted
