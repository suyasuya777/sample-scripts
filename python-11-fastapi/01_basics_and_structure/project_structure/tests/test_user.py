from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_users_paged():
    response = client.get("/users/paged?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user():
    response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_get_user():
    create_res = client.post(
        "/users",
        json={"name": "Bob", "email": "bob@example.com"},
    )
    user_id = create_res.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_not_found():
    response = client.get("/users/99999")
    assert response.status_code == 404


def test_patch_user():
    create_res = client.post(
        "/users",
        json={"name": "Patch Target", "email": "patch@example.com"},
    )
    user_id = create_res.json()["id"]

    response = client.patch(
        f"/users/{user_id}",
        json={"name": "Patched Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Patched Name"
    assert response.json()["email"] == "patch@example.com"  # 変更されていない


def test_patch_user_not_found():
    response = client.patch(
        "/users/99999",
        json={"name": "No User"},
    )
    assert response.status_code == 404


def test_delete_user():
    create_res = client.post(
        "/users",
        json={"name": "To Delete", "email": "delete@example.com"},
    )
    user_id = create_res.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() is True

    # 削除後は404
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


def test_delete_user_not_found():
    response = client.delete("/users/99999")
    assert response.status_code == 404
