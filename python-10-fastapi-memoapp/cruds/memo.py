from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import schemas.memo as memo_schema
import models.memo as memo_model
from datetime import datetime, timezone


# ==================================================
# 非同期CRUD処理
# ==================================================
# 新規登録
async def create_memo(
    db_session: AsyncSession, memo_data: memo_schema.CreateAndUpdateMemoSchema
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


# 全件取得
async def get_memos(db_session: AsyncSession) -> list[memo_model.Memo]:

    result = await db_session.execute(select(memo_model.Memo))
    memos = result.scalars().all()
    return memos


# 1件取得
async def get_memo_by_id(
    db_session: AsyncSession, memo_id: int
) -> memo_model.Memo | None:

    result = await db_session.execute(
        select(memo_model.Memo).where(memo_model.Memo.memo_id == memo_id)
    )
    memo = result.scalars().first()
    return memo


# 更新処理
async def update_memo(
    db_session: AsyncSession,
    memo_id: int,
    memo_data: memo_schema.CreateAndUpdateMemoSchema,
) -> memo_model.Memo | None:

    memo = await get_memo_by_id(db_session, memo_id)
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


# 削除処理
async def delete_memo(db_session: AsyncSession, memo_id: int) -> memo_model.Memo | None:

    memo = await get_memo_by_id(db_session, memo_id)
    if memo:
        await db_session.delete(memo)
        await db_session.commit()

    return memo
