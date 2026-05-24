"""
学習ポイント: パーシャルアップデートパターン（部分更新）
- Optional フィールド: 全フィールドをOptionalにして送信されたもののみ更新
- None チェック      : item_update.name is None なら既存値を維持
- PATCH的な設計      : 送信されたフィールドのみ上書き、未送信は変更しない
"""
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import FastAPI, Depends, HTTPException, Path

Base = declarative_base()

class ItemOrm(Base):
    __tablename__ = "items"
    id          = Column(Integer, primary_key=True)
    name        = Column(String)
    price       = Column(Integer)
    description = Column(String)
    status      = Column(String, default="ON_SALE")

# 全フィールドが Optional → 更新したいフィールドだけ送信できる
class ItemUpdate(BaseModel):
    name:        Optional[str] = Field(None, min_length=2, max_length=20)
    price:       Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    status:      Optional[str] = None

def crud_update(db: Session, item_id: int, update_data: ItemUpdate) -> Optional[ItemOrm]:
    item = db.query(ItemOrm).filter(ItemOrm.id == item_id).first()
    if not item:
        return None
    # None チェック: 送信されたフィールドのみ上書き
    item.name        = item.name        if update_data.name        is None else update_data.name
    item.price       = item.price       if update_data.price       is None else update_data.price
    item.description = item.description if update_data.description is None else update_data.description
    item.status      = item.status      if update_data.status      is None else update_data.status
    db.commit()
    db.refresh(item)
    return item

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.put("/items/{item_id}")
async def update(
    item_update: ItemUpdate,
    item_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    updated = crud_update(db, item_id, item_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated
