"""
学習ポイント: pytest + TestClientによるユニットテスト
- TestClient      : FastAPIアプリにHTTPリクエストを送るテスト用クライアント
- pytest          : テストフレームワーク（test_で始まる関数を自動収集）
- assert          : レスポンスのstatusコード・JSONボディの検証
- 正常系・異常系  : 成功ケースと失敗ケースを両方テスト

実行: pytest unit_test_with_pytest_and_test_client.py -v
"""
from fastapi import FastAPI, HTTPException, Path
from fastapi.testclient import TestClient

app = FastAPI()

ITEMS = {1: {"id": 1, "name": "PC", "price": 50000},
         2: {"id": 2, "name": "スマホ", "price": 30000}}

@app.get("/items", status_code=200)
def find_all():
    return list(ITEMS.values())

@app.get("/items/{item_id}", status_code=200)
def find_by_id(item_id: int = Path(gt=0)):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return ITEMS[item_id]

client = TestClient(app)

# ── テスト ────────────────────────────────────────────
def test_find_all():
    res = client.get("/items")
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_find_by_id_success():
    res = client.get("/items/1")
    assert res.status_code == 200
    assert res.json()["name"] == "PC"

def test_find_by_id_not_found():
    res = client.get("/items/99")
    assert res.status_code == 404
    assert res.json()["detail"] == "Item not found"

def test_find_by_id_invalid_path():
    res = client.get("/items/0")  # Path(gt=0) で弾かれる
    assert res.status_code == 422
