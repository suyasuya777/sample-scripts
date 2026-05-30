from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # 外部キー: usersテーブルのidを参照
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # 多対1: 複数のItemが1人のUserに属する
    owner: Mapped["User"] = relationship("User", back_populates="items")
