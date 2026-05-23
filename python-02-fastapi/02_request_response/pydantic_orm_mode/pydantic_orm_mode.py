"""
学習ポイント: ConfigDict(from_attributes=True) によるORM変換
- from_attributes=True : SQLAlchemyのORMオブジェクトをPydanticスキーマへ直接変換
  （Pydantic v1の orm_mode=True に相当）
- model_validate()     : ORMオブジェクトからスキーマインスタンスを生成
- 変換の流れ: ORM → response_model → JSONレスポンス
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# ── SQLAlchemy ORMモデル ──────────────────────────────
class UserOrm(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)  # ハッシュ済み
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

# ── Pydanticスキーマ ──────────────────────────────────
class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime
    # password と salt はレスポンスに含めない（セキュリティ設計）
    model_config = ConfigDict(from_attributes=True)

# ── 変換の確認 ────────────────────────────────────────
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

with Session() as db:
    user = UserOrm(username="user1", password="hashed", salt="salt123")
    db.add(user)
    db.commit()
    db.refresh(user)

    # ORMオブジェクト → Pydanticスキーマへ変換
    response = UserResponse.model_validate(user)
    print(response.model_dump())
    # password / salt は含まれない
