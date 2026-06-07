from datetime import datetime, timezone

import models.memo as memo_model
import schemas.memo as memo_schema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_memo(
    db_session: AsyncSession,
    memo_data: memo_schema.MemoBase
) -> memo_model.Memo:

    memo = memo_model.Memo(
        title=memo_data.title,
        description=memo_data.description,
        priority=memo_data.priority,
        due_date=memo_data.due_date,
        is_completed=memo_data.is_completed,
    )
    db_session.add(memo)
    await db_session.commit()
    await db_session.refresh(memo)
    return memo


async def get_memos(
    db_session: AsyncSession
) -> list[memo_model.Memo]:

    result = await db_session.execute(
        select(memo_model.Memo)
    )
    memos = result.scalars().all()
    return memos


async def get_memo_by_id(
    db_session: AsyncSession,
    id: int
) -> memo_model.Memo | None:

    result = await db_session.execute(
        select(memo_model.Memo).where(memo_model.Memo.id == id)
    )
    memo = result.scalars().first()
    return memo


async def update_memo(
    db_session: AsyncSession,
    id: int,
    memo_data: memo_schema.MemoBase,
) -> memo_model.Memo | None:

    memo = await get_memo_by_id(db_session, id)
    if memo:
        memo.title = memo_data.title
        memo.description = memo_data.description
        memo.updated_at = datetime.now(timezone.utc)
        memo.priority = memo_data.priority
        memo.due_date = memo_data.due_date
        memo.is_completed = memo_data.is_completed
        await db_session.commit()
        await db_session.refresh(memo)
    return memo


async def delete_memo(
    db_session: AsyncSession,
    id: int
) -> memo_model.Memo | None:

    memo = await get_memo_by_id(db_session, id)
    if memo:
        await db_session.delete(memo)
        await db_session.commit()
    return memo
