from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.item import Item
from schemas.item import ItemCreate, ItemUpdate


async def get_items(
    db: AsyncSession
) -> list[Item]:

    result = await db.execute(
        select(Item)
    )
    return result.scalars().all()


async def get_item(
    db: AsyncSession,
    item_id: int
) -> Item | None:

    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    return result.scalar_one_or_none()


async def get_items_by_user(
    db: AsyncSession,
    user_id: int
) -> list[Item]:
    result = await db.execute(
        select(Item).where(Item.user_id == user_id)
    )
    return result.scalars().all()


async def get_items_paged(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Item]:
    result = await db.execute(
        select(Item).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_user_item(
    db: AsyncSession,
    item_in: ItemCreate,
    user_id: int
) -> Item:

    item = Item(**item_in.model_dump(exclude={"user_id"}), user_id=user_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def patch_item(
    db: AsyncSession,
    item_id: int,
    item_in: ItemUpdate
) -> Item | None:

    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        return None
    for key, value in item_in.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(
    db: AsyncSession,
    item_id: int
) -> bool:

    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True
