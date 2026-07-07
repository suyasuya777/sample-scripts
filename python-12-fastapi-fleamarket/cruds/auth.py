import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models import User
from schemas import DecodedToken, UserCreate

ALGORITHM = "HS256"
SECRET_KEY = get_settings().secret_key

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def create_user(
    db: AsyncSession,
    user_in: UserCreate
) -> User:
    salt = base64.b64encode(os.urandom(32))
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256",
        user_in.password.encode(),
        salt,
        600000
    ).hex()

    user = User(
        username=user_in.username,
        password=hashed_password,
        salt=salt.decode()
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None

    hashed_password = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        user.salt.encode(),
        600000
    ).hex()
    if user.password != hashed_password:
        return None

    return user


def create_access_token(
    username: str,
    user_id: int,
    expires_delta: timedelta
) -> str:
    expires = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": username, "id": user_id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)]
) -> DecodedToken:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return DecodedToken(username=username, user_id=user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
