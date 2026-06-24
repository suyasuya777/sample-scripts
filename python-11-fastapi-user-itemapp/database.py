from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

import config


class Base(DeclarativeBase):
    pass


engine = create_async_engine(config.get_settings().database_url, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
