"""/auth エンドポイントの検証（認証をオーバーライドしない実フロー）"""

import pytest
from httpx import AsyncClient

VALID_USER = {"username": "alice", "password": "test1234"}


async def signup(client: AsyncClient, **overrides):
    return await client.post("/auth/signup", json={**VALID_USER, **overrides})


async def login(client: AsyncClient, **overrides):
    return await client.post("/auth/login", data={**VALID_USER, **overrides})


# --- signup ------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signup_正常系(unauth_client_fixture: AsyncClient):
    response = await signup(unauth_client_fixture)
    assert response.status_code == 201

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2  # JWT は3パート構成


@pytest.mark.asyncio
async def test_signup_パスワードを返さない(unauth_client_fixture: AsyncClient):
    body = (await signup(unauth_client_fixture)).json()
    assert "password" not in body
    assert "password_hash" not in body


@pytest.mark.asyncio
async def test_signup_のトークンでそのまま出品できる(
    unauth_client_fixture: AsyncClient,
):
    """登録直後にログインし直さずに認証つきリクエストが通ること"""
    token = (await signup(unauth_client_fixture)).json()["access_token"]

    response = await unauth_client_fixture.post(
        "/items",
        data={"name": "スマホ", "price": 30000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_signup_重複は409(unauth_client_fixture: AsyncClient):
    assert (await signup(unauth_client_fixture)).status_code == 201

    response = await signup(unauth_client_fixture)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_signup_短いパスワードは422(unauth_client_fixture: AsyncClient):
    response = await signup(unauth_client_fixture, password="short")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_signup_短いユーザー名は422(unauth_client_fixture: AsyncClient):
    response = await signup(unauth_client_fixture, username="a")
    assert response.status_code == 422


# --- login -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_正常系(unauth_client_fixture: AsyncClient):
    await signup(unauth_client_fixture)

    response = await login(unauth_client_fixture)
    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2  # JWT は3パート構成


@pytest.mark.asyncio
async def test_login_パスワード誤りは401(unauth_client_fixture: AsyncClient):
    await signup(unauth_client_fixture)

    response = await login(unauth_client_fixture, password="wrong-password")
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_login_存在しないユーザーは401(unauth_client_fixture: AsyncClient):
    response = await login(unauth_client_fixture, username="nobody")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_失敗メッセージはユーザーの有無で変わらない(
    unauth_client_fixture: AsyncClient,
):
    """ユーザー名の存在を推測させないため、両者は同じ応答であること"""
    await signup(unauth_client_fixture)

    wrong_password = await login(unauth_client_fixture, password="wrong-password")
    no_such_user = await login(unauth_client_fixture, username="nobody")

    assert wrong_password.status_code == no_such_user.status_code
    assert wrong_password.json() == no_such_user.json()


# --- signup → login → 認証つきリクエスト -------------------------------------

@pytest.mark.asyncio
async def test_発行したトークンで出品できる(unauth_client_fixture: AsyncClient):
    await signup(unauth_client_fixture)
    token = (await login(unauth_client_fixture)).json()["access_token"]

    response = await unauth_client_fixture.post(
        "/items",
        data={"name": "スマホ", "price": 30000},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "スマホ"
