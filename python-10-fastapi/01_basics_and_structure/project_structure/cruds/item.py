from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.item import Item
from schemas.item import ItemCreate


async def get_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item))
    return result.scalars().all()


async def get_items_by_user(db: AsyncSession, user_id: int) -> list[Item]:
    result = await db.execute(select(Item).where(Item.user_id == user_id))
    return result.scalars().all()


async def create_item(db: AsyncSession, item_in: ItemCreate) -> Item:
    item = Item(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item