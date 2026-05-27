from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from cruds import user as user_crud
from schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def find_all(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_users(db)


@router.post("", response_model=UserResponse)
async def create(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_crud.create_user(db, user_in)