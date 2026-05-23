"""
学習ポイント: SQLiteインメモリDBを使った統合テスト
- StaticPool        : テスト用に接続を維持する固定プール（SQLiteインメモリに必須）
- Base.metadata.create_all: テスト用DBにテーブルを作成
- フィクスチャデータ : テスト前に既知のデータを投入
- テスト間の独立性  : 各テストで独立したDBセッションを使用

実行: pytest integration_test_with_db_mock.py -v
"""
import pytest
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()

class ItemOrm(Base):
    __tablename__ = "items"
    id    = Column(Integer, primary_key=True)
    name  = Column(String)
    price = Column(Integer)
    user_id = Column(Integer, default=1)

def get_db():
    pass  # テストでオーバーライド

app = FastAPI()

@app.get("/items")
def find_all(db: Session = Depends(get_db)):
    return db.query(ItemOrm).all()

@app.get("/items/{item_id}")
def find_by_id(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemOrm).filter(ItemOrm.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# ── pytest フィクスチャ ────────────────────────────────
@pytest.fixture()
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # インメモリDBで複数接続を同一にする
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    db.add_all([ItemOrm(name="PC1", price=50000, user_id=1),
                ItemOrm(name="PC2", price=30000, user_id=2)])
    db.commit()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client_fixture(session_fixture):
    app.dependency_overrides[get_db] = lambda: session_fixture
    yield TestClient(app)
    app.dependency_overrides.clear()

# ── テスト ────────────────────────────────────────────
def test_find_all(client_fixture):
    res = client_fixture.get("/items")
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_find_by_id_success(client_fixture):
    res = client_fixture.get("/items/1")
    assert res.status_code == 200

def test_find_by_id_not_found(client_fixture):
    res = client_fixture.get("/items/99")
    assert res.status_code == 404
