from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Item
from schemas import ItemCreate, ItemUpdate


async def get_items(
    db: AsyncSession
) -> list[Item]:
    result = await db.execute(
        select(Item)
    )
    items = result.scalars().all()
    return items


async def get_items_by_name(
    db: AsyncSession,
    name: str
) -> list[Item]:
    result = await db.execute(
        select(Item).where(Item.name.like(f"%{name}%"))
    )
    items = result.scalars().all()
    return items


async def get_item(
    db: AsyncSession,
    item_id: int,
    user_id: int
) -> Item | None:
    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        return None
    return item


async def create_item(
    db: AsyncSession,
    item_in: ItemCreate,
    user_id: int
) -> Item:
    item = Item(**item_in.model_dump(), user_id=user_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_item(
    db: AsyncSession,
    item_id: int,
    item_in: ItemUpdate,
    user_id: int
) -> Item | None:
    item = await get_item(db, item_id, user_id)
    if item is None:
        return None

    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(
    db: AsyncSession,
    item_id: int,
    user_id: int
) -> bool:
    item = await get_item(db, item_id, user_id)
    if item is None:
        return False
    await db.delete(item)
    await db.commit()
    return True
