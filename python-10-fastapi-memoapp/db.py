import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


base_dir = os.path.dirname(__file__)
DATABASE_URL = "sqlite+aiosqlite:///" + os.path.join(base_dir, "memodb.sqlite")
engine = create_async_engine(DATABASE_URL, echo=True)


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_db():
    async with async_session() as session:
        yield session
