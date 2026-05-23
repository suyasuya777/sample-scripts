from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # 1対多: 1人のUserが複数のItemを持つ
    items: Mapped[list["Item"]] = relationship(
        "Item", back_populates="owner", cascade="all, delete-orphan"
    )
