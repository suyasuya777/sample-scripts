from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from db import Base
from datetime import datetime


# ==================================================
# モデル
# ==================================================
# memosテーブル用：モデル
class Memo(Base):
    # テーブル名
    __tablename__ = "memos"
    # メモID：PK：自動インクリメント
    memo_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # タイトル：未入力不可
    title: Mapped[str] = mapped_column(String(50))
    # 詳細：未入力可
    description: Mapped[str | None] = mapped_column(String(255))
    # 作成日時
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    # 更新日時
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    # ▽▽▽ MemoStatusSchemaのフィールド ▽▽▽
    # 優先度
    priority: Mapped[str] = mapped_column(String(10))
    # 期限日
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    # 完了フラグ
    is_completed: Mapped[bool] = mapped_column(Boolean)
    # △△△ MemoStatusSchemaのフィールド △△△