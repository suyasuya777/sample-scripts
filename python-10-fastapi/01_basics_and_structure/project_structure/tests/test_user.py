from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_users():
    response = client.get("/users")
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
