from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from schemas.user import UserCreate, UserUpdate


async def get_users(
    db: AsyncSession
) -> list[User]:
    result = await db.execute(
        select(User).options(selectinload(User.items))
    )
    users = result.scalars().all()
    return users


async def get_users_paged(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[User]:
    result = await db.execute(
        select(User).options(selectinload(User.items)).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users


async def get_user(
    db: AsyncSession,
    user_id: int
) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    return user


async def create_user(
    db: AsyncSession,
    user_in: UserCreate
) -> User:
    user = User(**user_in.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user, ["items"])
    return user


async def patch_user(
    db: AsyncSession,
    user_in: UserUpdate,
    user_id: int
) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    for key, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user, ["items"])
    return user


async def delete_user(
    db: AsyncSession,
    user_id: int
) -> bool:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True
