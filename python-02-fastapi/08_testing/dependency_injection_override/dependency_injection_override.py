"""
学習ポイント: dependency_overrides によるDI差し替え
- app.dependency_overrides[orig_func] = mock_func : 依存関数をモックに差し替え
- テスト後のクリア: app.dependency_overrides.clear()
- 用途: DB接続・認証・外部APIをテスト用のモックに差し替え

実行: pytest dependency_injection_override.py -v
"""
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

# ── 本番用の依存関数 ─────────────────────────────────
def get_db():
    """本番: PostgreSQLセッションを返す"""
    return {"type": "production_db"}

def get_current_user():
    """本番: JWTを検証して認証ユーザーを返す"""
    return {"user_id": 1, "username": "real_user", "role": "admin"}

@app.get("/items")
def get_items(db=Depends(get_db), user=Depends(get_current_user)):
    return {"db": db, "user": user}

# ── テスト ────────────────────────────────────────────
@pytest.fixture()
def client():
    # モック関数でオーバーライド
    app.dependency_overrides[get_db]           = lambda: {"type": "sqlite_memory"}
    app.dependency_overrides[get_current_user] = lambda: {"user_id": 99, "username": "test_user", "role": "user"}
    yield TestClient(app)
    app.dependency_overrides.clear()  # テスト後に必ずクリア

def test_get_items_with_mock(client):
    res = client.get("/items")
    assert res.status_code == 200
    data = res.json()
    assert data["db"]["type"] == "sqlite_memory"
    assert data["user"]["username"] == "test_user"
