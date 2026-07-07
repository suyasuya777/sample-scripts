from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import ItemStatus


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50)
    )

    price: Mapped[int]

    description: Mapped[str | None] = mapped_column(
        String(255)
    )

    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus),
        default=ItemStatus.ON_SALE
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="items"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    password: Mapped[str] = mapped_column(
        String(255)
    )

    salt: Mapped[str] = mapped_column(
        String(64)
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now
    )

    items: Mapped[list[Item]] = relationship(
        "Item",
        back_populates="user"
    )
