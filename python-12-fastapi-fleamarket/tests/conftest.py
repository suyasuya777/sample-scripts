import os
import sys

app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(app_dir)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import storage
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


def _override_db(session):
    async def override_get_db():
        yield session

    return override_get_db


@pytest_asyncio.fixture
async def client_fixture(session_fixture):
    """user_id=1 として認証済みのクライアント（PC1 の所有者）"""

    def override_get_current_user():
        return DecodedToken(username="user1", user_id=1)

    app.dependency_overrides[get_db] = _override_db(session_fixture)
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def other_client_fixture(session_fixture):
    """user_id=2 として認証済みのクライアント（PC1 の所有者ではない）"""

    def override_get_current_user():
        return DecodedToken(username="user2", user_id=2)

    app.dependency_overrides[get_db] = _override_db(session_fixture)
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client_fixture(session_fixture):
    """認証をオーバーライドしないクライアント（401 と実際の認証フローの検証用）"""
    app.dependency_overrides[get_db] = _override_db(session_fixture)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def image_dir(tmp_path, monkeypatch):
    """画像の保存先を一時ディレクトリに差し替える（実際の uploads/ を汚さない）"""
    items_dir = tmp_path / "items"
    items_dir.mkdir(parents=True)
    monkeypatch.setattr(storage, "ITEMS_DIR", items_dir)
    return items_dir
