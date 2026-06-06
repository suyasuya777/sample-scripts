from typing import Annotated

import cruds.memo as memo_crud
import db
from fastapi import APIRouter, Depends, HTTPException
from schemas.memo import CreateAndUpdateMemoSchema, MemoSchema, ResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession

# ルーターを作成し、タグとURLパスのプレフィックスを設定
router = APIRouter(tags=["Memos"], prefix="/memos")

DbSession = Annotated[AsyncSession, Depends(db.get_db)]

# ==================================================
# メモ用のエンドポイント
# ==================================================
# メモ新規登録のエンドポイント
@router.post("/", response_model=ResponseSchema)
async def create_memo(memo_data: CreateAndUpdateMemoSchema, db_session: DbSession):
    try:
        # 新しいメモをデータベースに登録
        await memo_crud.create_memo(db_session, memo_data)
        return ResponseSchema(message="メモが正常に登録されました")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# メモ情報全件取得のエンドポイント
@router.get("/", response_model=list[MemoSchema])
async def get_memos(db_session: DbSession):
    # 全てのメモをデータベースから取得
    memos = await memo_crud.get_memos(db_session)
    return [MemoSchema.model_validate(memo) for memo in memos]

# 特定のメモ情報取得のエンドポイント
@router.get("/{memo_id}", response_model=MemoSchema)
async def get_memo_by_id(memo_id: int, db_session: DbSession):
    # 指定されたIDのメモをデータベースから取得
    memo = await memo_crud.get_memo_by_id(db_session, memo_id)
    if not memo:
        # メモが見つからない場合、HTTP 404エラーを返す
        raise HTTPException(status_code=404, detail="メモが見つかりません")
    return MemoSchema.model_validate(memo)

# 特定のメモを更新するエンドポイント
@router.put("/{memo_id}", response_model=ResponseSchema)
async def update_memo(memo_id: int, memo_data: CreateAndUpdateMemoSchema, db_session: DbSession):
    # 指定されたIDのメモを新しいデータで更新
    memo = await memo_crud.update_memo(db_session, memo_id, memo_data)
    if not memo:
        # 更新対象が見つからない場合、HTTP 404エラーを返す
        raise HTTPException(status_code=404, detail="更新対象が見つかりません")
    return ResponseSchema(message="メモが正常に更新されました")

# 特定のメモを削除するエンドポイント
@router.delete("/{memo_id}", response_model=ResponseSchema)
async def delete_memo(memo_id: int, db_session: DbSession):
    # 指定されたIDのメモをデータベースから削除
    memo = await memo_crud.delete_memo(db_session, memo_id)
    if not memo:
        # 削除対象が見つからない場合、HTTP 404エラーを返す
        raise HTTPException(status_code=404, detail="削除対象が見つかりません")
    return ResponseSchema(message="メモが正常に削除されました")