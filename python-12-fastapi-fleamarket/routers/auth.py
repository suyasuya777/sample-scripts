from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cruds import auth as auth_cruds
from database import get_db
from schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

DbDependency = Annotated[
    AsyncSession,
    Depends(get_db)
]

FormDependency = Annotated[
    OAuth2PasswordRequestForm,
    Depends()
]


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: DbDependency, user_in: UserCreate):
    try:
        user = await auth_cruds.create_user(db, user_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    await db.commit()
    return user

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

    token = auth_cruds.create_access_token(
        user.username, user.id, timedelta(minutes=20)
    )
    return {"access_token": token, "token_type": "bearer"}
