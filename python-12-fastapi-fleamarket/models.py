from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from enums import ItemStatusEnum


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )


class Item(TimestampMixin, Base):
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

    image_url: Mapped[str | None] = mapped_column(
        String(255)
    )

    status: Mapped[ItemStatusEnum] = mapped_column(
        SAEnum(ItemStatusEnum, native_enum=False, length=20),
        default=ItemStatusEnum.ON_SALE
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    user: Mapped[User] = relationship(
        back_populates="items",
        lazy="raise_on_sql"
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    items: Mapped[list[Item]] = relationship(
        back_populates="user",
        lazy="raise_on_sql",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
