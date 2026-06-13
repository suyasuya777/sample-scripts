from __future__ import annotations

from typing import TYPE_CHECKING

import database
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.item import Item


class User(database.Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(50)
    )

    email: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    items: Mapped[list[Item]] = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
