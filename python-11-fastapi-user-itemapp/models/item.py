from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

import database

if TYPE_CHECKING:
    from models.user import User


class Item(database.Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(50)
    )

    description: Mapped[str | None] = mapped_column(
        String(255)
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    owner: Mapped[User] = relationship(
        "User",
        back_populates="items"
    )

