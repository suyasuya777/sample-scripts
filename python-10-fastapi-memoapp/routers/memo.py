from typing import Annotated

import cruds.memo as memo_crud
import db
import schemas.memo as memo_schema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Memos"], prefix="/memos")

DbSession = Annotated[AsyncSession, Depends(db.get_db)]


@router.post("/", response_model=memo_schema.ResponseSchema)
async def create_memo(
    memo_data: memo_schema.BaseSchema,
    db_session: DbSession
):

    try:
        await memo_crud.create_memo(db_session, memo_data)
        return memo_schema.ResponseSchema(message="メモが正常に登録されました")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[memo_schema.Schema])
async def get_memos(
    db_session: DbSession
):

    memos = await memo_crud.get_memos(db_session)
    return [memo_schema.Schema.model_validate(memo) for memo in memos]


@router.get("/{id}", response_model=memo_schema.Schema)
async def get_memo_by_id(
    id: int,
    db_session: DbSession
):

    memo = await memo_crud.get_memo_by_id(db_session, id)
    if not memo:
        raise HTTPException(status_code=404, detail="メモが見つかりません")
    return memo_schema.Schema.model_validate(memo)


@router.put("/{id}", response_model=memo_schema.ResponseSchema)
async def update_memo(
    id: int,
    memo_data: memo_schema.BaseSchema,
    db_session: DbSession
):

    memo = await memo_crud.update_memo(db_session, id, memo_data)
    if not memo:
        raise HTTPException(status_code=404, detail="更新対象が見つかりません")
    return memo_schema.ResponseSchema(message="メモが正常に更新されました")


@router.delete("/{id}", response_model=memo_schema.ResponseSchema)
async def delete_memo(
    id: int,
    db_session: DbSession
):

    memo = await memo_crud.delete_memo(db_session, id)
    if not memo:
        raise HTTPException(status_code=404, detail="削除対象が見つかりません")
    return memo_schema.ResponseSchema(message="メモが正常に削除されました")