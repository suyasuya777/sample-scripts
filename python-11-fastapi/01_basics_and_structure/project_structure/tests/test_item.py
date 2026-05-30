from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_items_paged():
    response = client.get("/items/paged?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_item():
    response = client.post(
        "/items",
        json={"title": "Sample Item", "description": "A test item", "user_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Sample Item"
    assert data["description"] == "A test item"
    assert "id" in data


def test_get_item():
    # 事前にアイテムを作成
    create_res = client.post(
        "/items",
        json={"title": "Get Test", "description": "desc", "user_id": 1},
    )
    item_id = create_res.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_get_items_by_user():
    response = client.get("/items/user/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_item():
    create_res = client.post(
        "/items",
        json={"title": "Before Update", "description": "old", "user_id": 1},
    )
    item_id = create_res.json()["id"]

    response = client.put(
        f"/items/{item_id}",
        json={"title": "After Update", "description": "new", "user_id": 1},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "After Update"


def test_patch_item():
    create_res = client.post(
        "/items",
        json={"title": "Patch Target", "description": "old", "user_id": 1},
    )
    item_id = create_res.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        json={"title": "Patched Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Patched Title"
    assert response.json()["description"] == "old"  # 変更されていない


def test_delete_item():
    create_res = client.post(
        "/items",
        json={"title": "To Delete", "description": "bye", "user_id": 1},
    )
    item_id = create_res.json()["id"]

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() is True

    # 削除後は404
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404


def test_update_item_not_found():
    response = client.put(
        "/items/99999",
        json={"title": "No Item", "description": "none", "user_id": 1},
    )
    assert response.status_code == 404


def test_delete_item_not_found():
    response = client.delete("/items/99999")
    assert response.status_code == 404
