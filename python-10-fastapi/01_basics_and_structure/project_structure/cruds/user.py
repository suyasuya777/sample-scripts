from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import UserCreate, UserUpdate


# 一覧取得
async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).options(selectinload(User.items)))
    return result.scalars().all()


# 1件取得（id）
async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


# 1件取得（email）
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.email == email)
    )
    return result.scalar_one_or_none()


# ページネーション
async def get_users_paged(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[User]:
    result = await db.execute(
        select(User).options(selectinload(User.items)).offset(skip).limit(limit)
    )
    return result.scalars().all()


# 作成
async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(**user_in.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user, ["items"])
    return user


# 全フィールド更新（PUT）
async def update_user(
    db: AsyncSession, user_id: int, user_in: UserCreate
) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    for key, value in user_in.model_dump().items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user, ["items"])
    return user


# 部分更新（PATCH）
async def patch_user(
    db: AsyncSession, user_id: int, user_in: UserUpdate
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


# 削除
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True