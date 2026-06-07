from datetime import datetime, timezone

import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Memo(db.Base):
    __tablename__ = "memos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    
    title: Mapped[str] = mapped_column(
        String(50)
    )
    
    description: Mapped[str | None] = mapped_column(
        String(255)
    )
    
    priority: Mapped[str] = mapped_column(
        String(10)
    )
    
    due_date: Mapped[datetime | None]

    is_completed: Mapped[bool] = mapped_column(
        default=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    
    updated_at: Mapped[datetime | None]
