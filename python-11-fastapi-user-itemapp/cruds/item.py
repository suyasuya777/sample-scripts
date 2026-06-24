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
    items = result.scalars().all()
    return items


async def get_items_paged(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Item]:
    result = await db.execute(
        select(Item).offset(skip).limit(limit)
    )
    items = result.scalars().all()
    return items


async def get_items_by_user(
    db: AsyncSession,
    user_id: int
) -> list[Item]:
    result = await db.execute(
        select(Item).where(Item.user_id == user_id)
    )
    items = result.scalars().all()
    return items


async def get_item(
    db: AsyncSession,
    item_id: int
) -> Item | None:
    result = await db.execute(
        select(Item).where(Item.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        return None
    return item


async def create_item(
    db: AsyncSession,
    item_in: ItemCreate
) -> Item:
    item = Item(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def patch_item(
    db: AsyncSession,
    item_in: ItemUpdate,
    item_id: int
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
