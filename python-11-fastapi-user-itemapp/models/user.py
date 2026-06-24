from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.item import Item


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50)
    )

    email: Mapped[str] = mapped_column(
        String(254)
    )

    items: Mapped[list[Item]] = relationship(
        "Item",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
