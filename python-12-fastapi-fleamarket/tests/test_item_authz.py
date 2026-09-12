"""所有者チェックと認証の検証（PC1=user_id:1 / PC2=user_id:2）"""

import pytest
from httpx import AsyncClient

from tests.helpers import png_bytes


# --- 他人のアイテムへの操作は 404 -------------------------------------------

@pytest.mark.asyncio
async def test_patch_他人のアイテムは404(other_client_fixture: AsyncClient):
    response = await other_client_fixture.patch("/items/1", json={"price": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_patch_他人のアイテムは変更されない(
    other_client_fixture: AsyncClient,
):
    await other_client_fixture.patch("/items/1", json={"price": 1})

    response = await other_client_fixture.get("/items/1")
    assert response.status_code == 200
    assert response.json()["price"] == 10000


@pytest.mark.asyncio
async def test_delete_他人のアイテムは404(other_client_fixture: AsyncClient):
    response = await other_client_fixture.delete("/items/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_delete_他人のアイテムは削除されない(
    other_client_fixture: AsyncClient,
):
    await other_client_fixture.delete("/items/1")

    response = await other_client_fixture.get("/items")
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_image_他人のアイテムは404(
    other_client_fixture: AsyncClient, image_dir
):
    response = await other_client_fixture.post(
        "/items/1/image",
        files={"file": ("a.png", png_bytes(), "image/png")},
    )
    assert response.status_code == 404
    assert list(image_dir.glob("*")) == []


@pytest.mark.asyncio
async def test_自分のアイテムは操作できる(other_client_fixture: AsyncClient):
    """所有者チェックが単に全部404にしているわけではないことの確認"""
    response = await other_client_fixture.patch("/items/2", json={"price": 20000})
    assert response.status_code == 200
    assert response.json()["price"] == 20000


# --- 認証なしアクセスは 401 --------------------------------------------------

@pytest.mark.asyncio
async def test_create_認証なしは401(unauth_client_fixture: AsyncClient):
    response = await unauth_client_fixture.post(
        "/items", data={"name": "スマホ", "price": 30000}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_認証なしは401(unauth_client_fixture: AsyncClient):
    response = await unauth_client_fixture.patch("/items/1", json={"price": 1})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_認証なしは401(unauth_client_fixture: AsyncClient):
    response = await unauth_client_fixture.delete("/items/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_image_認証なしは401(unauth_client_fixture: AsyncClient):
    response = await unauth_client_fixture.post(
        "/items/1/image",
        files={"file": ("a.png", png_bytes(), "image/png")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_不正なトークンは401(unauth_client_fixture: AsyncClient):
    response = await unauth_client_fixture.patch(
        "/items/1",
        json={"price": 1},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


# --- 閲覧系は認証不要 --------------------------------------------------------

@pytest.mark.asyncio
async def test_一覧は認証不要(unauth_client_fixture: AsyncClient):
    response = await unauth_client_fixture.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_詳細は認証不要かつ他人のものも見られる(
    unauth_client_fixture: AsyncClient,
):
    response = await unauth_client_fixture.get("/items/2")
    assert response.status_code == 200
    assert response.json()["name"] == "PC2"
