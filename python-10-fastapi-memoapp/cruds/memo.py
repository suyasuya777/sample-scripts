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
    """
    新しいメモをデータベースに登録する関数
    Args:
    db_session (AsyncSession): 非同期DBセッション
    memo_data (CreateAndUpdateMemoSchema): 作成するメモのデータ
    Returns:
    Memo: 作成されたメモのモデル
    """
    new_memo = memo_model.Memo(
        title=memo_data.title,
        description=memo_data.description,
        priority=memo_data.priority,
        due_date=memo_data.due_date,
        is_completed=memo_data.is_completed,
    )
    db_session.add(new_memo)
    await db_session.commit()
    await db_session.refresh(new_memo)
    return new_memo


# 全件取得
async def get_memos(db_session: AsyncSession) -> list[memo_model.Memo]:
    """
    データベースから全てのメモを取得する関数
    Args:
        db_session (AsyncSession): 非同期DBセッション
    Returns:
        list[Memo]: 取得された全てのメモのリスト
    """
    result = await db_session.execute(select(memo_model.Memo))
    memos = result.scalars().all()
    return memos


# 1件取得
async def get_memo_by_id(
    db_session: AsyncSession, memo_id: int
) -> memo_model.Memo | None:
    """
    データベースから特定のメモを1件取得する関数
    Args:
        db_session (AsyncSession): 非同期DBセッション
        memo_id (int): 取得するメモのID（プライマリキー）
    Returns:
        Memo | None: 取得されたメモのモデル、メモが存在しない場合はNoneを返す
    """
    result = await db_session.execute(
        select(memo_model.Memo).where(memo_model.Memo.memo_id == memo_id)
    )
    memo = result.scalars().first()
    return memo


# 更新処理
async def update_memo(
    db_session: AsyncSession,
    memo_id: int,
    target_data: memo_schema.CreateAndUpdateMemoSchema,
) -> memo_model.Memo | None:
    """
    データベースのメモを更新する関数
    Args:
        db_session (AsyncSession): 非同期DBセッション
        memo_id (int): 更新するメモのID（プライマリキー）
        target_data (CreateAndUpdateMemoSchema): 更新するデータ
    Returns:
        Memo | None: 更新されたメモのモデル、メモが存在しない場合はNoneを返す
    """
    memo = await get_memo_by_id(db_session, memo_id)
    if memo:
        memo.title = target_data.title
        memo.description = target_data.description
        memo.updated_at = datetime.now(timezone.utc)
        memo.priority = target_data.priority
        memo.due_date = target_data.due_date
        memo.is_completed = target_data.is_completed
        await db_session.commit()
        await db_session.refresh(memo)

    return memo


# 削除処理
async def delete_memo(db_session: AsyncSession, memo_id: int) -> memo_model.Memo | None:
    """
    データベースのメモを削除する関数
    Args:
        db_session (AsyncSession): 非同期DBセッション
        memo_id (int): 削除するメモのID（プライマリキー）
    Returns:
        Memo | None: 削除されたメモのモデル、メモが存在しない場合はNoneを返す
    """
    memo = await get_memo_by_id(db_session, memo_id)
    if memo:
        await db_session.delete(memo)
        await db_session.commit()

    return memo
