from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from cruds import user as user_crud
from schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def find_all(db: Session = Depends(get_db)):
    return user_crud.get_users(db)


@router.post("", response_model=UserResponse)
async def create(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user_in)
