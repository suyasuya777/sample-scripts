from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import cruds.memo as memo_crud
import db
from schemas.memo import CreateAndUpdateMemoSchema, MemoSchema, ResponseSchema

router = APIRouter(tags=["Memos"], prefix="/memos")

DbSession = Annotated[AsyncSession, Depends(db.get_db)]


@router.post("/", response_model=ResponseSchema)
async def create_memo(
    memo_data: CreateAndUpdateMemoSchema,
    db_session: DbSession
):

    try:
        await memo_crud.create_memo(db_session, memo_data)
        return ResponseSchema(message="メモが正常に登録されました")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

ト
@router.get("/", response_model=list[MemoSchema])
async def get_memos(
    db_session: DbSession
):

    memos = await memo_crud.get_memos(db_session)
    return [MemoSchema.model_validate(memo) for memo in memos]


@router.get("/{memo_id}", response_model=MemoSchema)
async def get_memo_by_id(
    memo_id: int,
    db_session: DbSession
):

    memo = await memo_crud.get_memo_by_id(db_session, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="メモが見つかりません")
    return MemoSchema.model_validate(memo)


@router.put("/{memo_id}", response_model=ResponseSchema)
async def update_memo(
    memo_id: int,
    memo_data: CreateAndUpdateMemoSchema,
    db_session: DbSession
):

    memo = await memo_crud.update_memo(db_session, memo_id, memo_data)
    if not memo:
        raise HTTPException(status_code=404, detail="更新対象が見つかりません")
    return ResponseSchema(message="メモが正常に更新されました")


@router.delete("/{memo_id}", response_model=ResponseSchema)
async def delete_memo(
    memo_id: int,
    db_session: DbSession
):

    memo = await memo_crud.delete_memo(db_session, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="削除対象が見つかりません")
    return ResponseSchema(message="メモが正常に削除されました")