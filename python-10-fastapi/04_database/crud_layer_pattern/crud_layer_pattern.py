"""
学習ポイント: CRUDレイヤー分離パターン（routers/cruds/schemas の3層構造）
- routers/ : エンドポイント定義・HTTPレスポンスコード・HTTPException
- cruds/   : DBクエリ・ビジネスロジック（SQLAlchemyの操作）
- schemas/ : リクエスト・レスポンスのPydanticスキーマ

この分離により:
  - ロジックのテストが容易（routerを介さずにcruds関数を単体テスト可能）
  - コードの責務が明確
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi import status as http_status

# ── モデル ────────────────────────────────────────────
Base = declarative_base()
class ItemOrm(Base):
    __tablename__ = "items"
    id    = Column(Integer, primary_key=True)
    name  = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

# ── スキーマ ──────────────────────────────────────────
class ItemCreate(BaseModel):
    name:  str = Field(min_length=1)
    price: int = Field(gt=0)

class ItemResponse(BaseModel):
    id:    int
    name:  str
    price: int
    class Config:
        from_attributes = True

# ── CRUDレイヤー（DBロジックのみ） ──────────────────────
def crud_find_all(db: Session) -> List[ItemOrm]:
    return db.query(ItemOrm).all()

def crud_find_by_id(db: Session, item_id: int) -> Optional[ItemOrm]:
    return db.query(ItemOrm).filter(ItemOrm.id == item_id).first()

def crud_create(db: Session, item_data: ItemCreate) -> ItemOrm:
    item = ItemOrm(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def crud_delete(db: Session, item_id: int) -> Optional[ItemOrm]:
    item = crud_find_by_id(db, item_id)
    if not item:
        return None
    db.delete(item)
    db.commit()
    return item

# ── ルーターレイヤー（HTTPレスポンスのみ） ────────────
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

@app.get("/items", response_model=List[ItemResponse])
async def find_all(db: Session = Depends(get_db)):
    return crud_find_all(db)

@app.get("/items/{item_id}", response_model=ItemResponse)
async def find_by_id(item_id: int = Path(gt=0), db: Session = Depends(get_db)):
    item = crud_find_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=ItemResponse, status_code=http_status.HTTP_201_CREATED)
async def create(item_data: ItemCreate, db: Session = Depends(get_db)):
    return crud_create(db, item_data)
