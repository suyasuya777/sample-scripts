from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Item
from schemas import ItemCreate, ItemUpdate


async def get_items(
    db: AsyncSession
) -> list[Item]:
    result = await db.execute(
        select(Item)
        .order_by(Item.id.desc())
    )
    items = result.scalars().all()
    return list(items)


async def get_items_by_name(
    db: AsyncSession,
    name: str
) -> list[Item]:
    escaped = name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await db.execute(
        select(Item)
        .where(Item.name.ilike(f"%{escaped}%", escape="\\"))
        .order_by(Item.id.desc())
    )
    items = result.scalars().all()
    return list(items)


async def get_item(
    db: AsyncSession,
    item_id: int,
    user_id: int
) -> Item | None:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    return item


async def get_item_public(
    db: AsyncSession,
    item_id: int
) -> Item | None:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id)
    )
    return result.scalar_one_or_none()


async def create_item(
    db: AsyncSession,
    item_in: ItemCreate,
    user_id: int
) -> Item:
    item = Item(**item_in.model_dump(), user_id=user_id)
    db.add(item)
    await db.flush()
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

    await db.flush()
    await db.refresh(item)
    return item


async def delete_item(
    db: AsyncSession,
    item_id: int,
    user_id: int
) -> tuple[bool, str | None]:
    item = await get_item(db, item_id, user_id)
    if item is None:
        return False, None
    image_url = item.image_url
    await db.delete(item)
    await db.flush()
    return True, image_url


async def set_item_image(
    db: AsyncSession,
    item: Item,
    image_url: str
) -> Item:
    item.image_url = image_url
    await db.flush()
    await db.refresh(item)
    return item
