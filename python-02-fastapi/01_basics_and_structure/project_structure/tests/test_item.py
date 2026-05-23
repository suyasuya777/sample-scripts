from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_item():
    response = client.post(
        "/items",
        json={"title": "Sample Item", "description": "A test item"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Sample Item"
    assert data["description"] == "A test item"
    assert "id" in data
