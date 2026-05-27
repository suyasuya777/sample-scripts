from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas import ItemCreate, ItemUpdate
from models import Item


async def find_all(db: AsyncSession):
    result = await db.execute(select(Item))
    return result.scalars().all()


async def find_by_id(db: AsyncSession, id: int, user_id: int):
    result = await db.execute(
        select(Item).where(Item.id == id, Item.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def find_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Item).where(Item.name.like(f"%{name}%")))
    return result.scalars().all()


async def create(db: AsyncSession, item_create: ItemCreate, user_id: int):
    new_item = Item(**item_create.model_dump(), user_id=user_id)
    db.add(new_item)
    await db.commit()
    return new_item


async def update(db: AsyncSession, id: int, item_update: ItemUpdate, user_id: int):
    item = await find_by_id(db, id, user_id)
    if item is None:
        return None

    item.name = item.name if item_update.name is None else item_update.name
    item.price = item.price if item_update.price is None else item_update.price
    item.description = (
        item.description if item_update.description is None else item_update.description
    )
    item.status = item.status if item_update.status is None else item_update.status
    db.add(item)
    await db.commit()
    return item


async def delete(db: AsyncSession, id: int, user_id: int):
    item = await find_by_id(db, id, user_id)
    if item is None:
        return None
    db.delete(item)
    await db.commit()
    return item
