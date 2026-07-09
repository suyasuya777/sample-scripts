import os
import sys

app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(app_dir)

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from cruds.auth import get_current_user
from database import Base, get_db
from main import app
from models import Item
from schemas import DecodedToken


@pytest_asyncio.fixture
async def session_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        session.add(Item(name="PC1", price=10000, description="test1", user_id=1))
        session.add(Item(name="PC2", price=10000, description="test2", user_id=2))
        await session.commit()
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def client_fixture(session_fixture):
    async def override_get_db():
        yield session_fixture

    def override_get_current_user():
        return DecodedToken(username="user1", user_id=1)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
