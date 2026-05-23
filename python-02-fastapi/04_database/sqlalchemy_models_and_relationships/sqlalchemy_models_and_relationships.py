"""
学習ポイント: SQLAlchemyのORMモデル定義とリレーションシップ
- Column型        : Integer / String / Enum / DateTime / ForeignKey
- relationship    : ORM レベルの結合定義（back_populates で双方向）
- ondelete=CASCADE: 親レコード削除時に子レコードも連動削除
- Enum型          : Pythonのenumと連動するDBカラム
- default/onupdate: created_at / updated_at の自動設定
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum as SaEnum
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class ItemStatus(PyEnum):
    ON_SALE  = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True)
    username   = Column(String, nullable=False, unique=True)
    password   = Column(String, nullable=False)
    salt       = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # User.items でそのユーザーの全アイテムにアクセス可能
    items = relationship("Item", back_populates="user")

class Item(Base):
    __tablename__ = "items"

    id          = Column(Integer, primary_key=True)
    name        = Column(String, nullable=False)
    price       = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    status      = Column(SaEnum(ItemStatus), nullable=False, default=ItemStatus.ON_SALE)
    created_at  = Column(DateTime, default=datetime.now)
    updated_at  = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # ForeignKey: users.id を参照。ondelete=CASCADE でユーザー削除時にアイテムも削除
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # item.user で出品者の User オブジェクトにアクセス可能
    user = relationship("User", back_populates="items")
