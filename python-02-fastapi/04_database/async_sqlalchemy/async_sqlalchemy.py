"""
学習ポイント: 非同期SQLAlchemy（AsyncSession）
- create_async_engine  : 非同期エンジンの生成（postgresql+asyncpg://）
- AsyncSession         : 非同期セッション
- async_sessionmaker   : 非同期セッションファクトリ
- await db.execute()   : 非同期クエリ実行
- select()             : SQLAlchemy 2.0スタイルのSELECT文
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, select
from fastapi import FastAPI, Depends

# 非同期URL: postgresql+asyncpg:// or sqlite+aiosqlite://
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./async_sample.db"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/items")
async def find_all(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items

@app.post("/items")
async def create(name: str, db: AsyncSession = Depends(get_async_db)):
    item = Item(name=name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
