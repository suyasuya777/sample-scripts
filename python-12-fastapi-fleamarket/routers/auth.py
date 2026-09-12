from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from cruds import auth as auth_cruds
from database import get_db
from models import User
from schemas import Token, UserCreate

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Auth"])

DbDependency = Annotated[
    AsyncSession,
    Depends(get_db)
]

FormDependency = Annotated[
    OAuth2PasswordRequestForm,
    Depends()
]


def _issue_token(user: User) -> Token:
    token = auth_cruds.create_access_token(
        user.username,
        user.id,
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=token, token_type="bearer")


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_user(db: DbDependency, user_in: UserCreate):
    """ユーザーを作成し、そのままログイン済みにするためのトークンを返す"""
    user = await auth_cruds.create_user(db, user_in)
    await db.commit()
    return _issue_token(user)


@router.post("/login", response_model=Token)
async def login_user(
    db: DbDependency,
    form_in: FormDependency
):
    user = await auth_cruds.authenticate_user(db, form_in.username, form_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return _issue_token(user)
