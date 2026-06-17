from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _create_user(name: str, email: str) -> int:
    """テスト用ユーザーを作成してIDを返す"""
    res = client.post("/users", json={"name": name, "email": email})
    return res.json()["id"]


def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_items_paged():
    response = client.get("/items/paged?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_item():
    user_id = _create_user("Item Owner", "item_owner@example.com")

    response = client.post(
        "/items",
        json={"title": "Sample Item", "description": "A test item", "user_id": user_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Sample Item"
    assert data["description"] == "A test item"
    assert "id" in data


def test_get_item():
    user_id = _create_user("Get Item User", "get_item_user@example.com")

    create_res = client.post(
        "/items",
        json={"title": "Get Test", "description": "desc", "user_id": user_id},
    )
    item_id = create_res.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_get_items_by_user():
    user_id = _create_user("Items By User", "items_by_user@example.com")

    client.post(
        "/items",
        json={"title": "User Item", "description": "desc", "user_id": user_id},
    )

    response = client.get(f"/items/user/{user_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_patch_item():
    user_id = _create_user("Patch Item User", "patch_item_user@example.com")

    create_res = client.post(
        "/items",
        json={"title": "Patch Target", "description": "old", "user_id": user_id},
    )
    item_id = create_res.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        json={"title": "Patched Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Patched Title"
    assert response.json()["description"] == "old"  # 変更されていない


def test_patch_item_not_found():
    response = client.patch(
        "/items/99999",
        json={"title": "No Item"},
    )
    assert response.status_code == 404


def test_delete_item():
    user_id = _create_user("Delete Item User", "delete_item_user@example.com")

    create_res = client.post(
        "/items",
        json={"title": "To Delete", "description": "bye", "user_id": user_id},
    )
    item_id = create_res.json()["id"]

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() is True

    # 削除後は404
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404


def test_delete_item_not_found():
    response = client.delete("/items/99999")
    assert response.status_code == 404
