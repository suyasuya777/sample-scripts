from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from schemas import ItemStatus


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), nullable=False, default=ItemStatus.ON_SALE
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), onupdate=datetime.now()
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="items")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    salt: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), onupdate=datetime.now()
    )

    items: Mapped[list["Item"]] = relationship("Item", back_populates="user")