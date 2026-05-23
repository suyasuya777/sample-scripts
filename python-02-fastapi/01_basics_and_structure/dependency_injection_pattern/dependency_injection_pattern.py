"""
学習ポイント: FastAPIの依存性注入（Depends）パターン
- Depends        : 関数の引数に依存関係を注入する仕組み
- get_db()       : リクエストごとにDBセッションを生成・クローズするジェネレーター
- get_current_user(): JWTを検証して認証済みユーザー情報を返す
- Annotated      : 型ヒントにメタ情報を付与して依存関係をシンプルに記述
"""
from typing import Annotated, Generator
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ── DBセッションの依存関係 ─────────────────────────────
engine = create_engine("sqlite:///./sample.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """
    yieldジェネレーターによりリクエスト終了後に必ずdb.close()が呼ばれる。
    try/finally で例外発生時もセッションがリークしない。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── 認証ユーザーの依存関係 ────────────────────────────
class CurrentUser:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username

def get_current_user(token: str = "dummy") -> CurrentUser:
    """
    実際はJWTを検証してユーザーを返す（cruds/auth.pyパターン参照）
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return CurrentUser(user_id=1, username="user1")

# ── 型エイリアスで依存関係をシンプルに記述 ───────────────
DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[CurrentUser, Depends(get_current_user)]

app = FastAPI()

@app.get("/items")
async def find_all(db: DbDependency):
    """db: DbDependency だけでDBセッションが自動注入される"""
    return {"message": "DBセッション注入済み"}

@app.get("/me")
async def get_me(user: UserDependency):
    """user: UserDependency だけで認証済みユーザーが自動注入される"""
    return {"user_id": user.user_id, "username": user.username}

@app.get("/items/secure")
async def secure_items(db: DbDependency, user: UserDependency):
    """DB + 認証の両方を同時に注入"""
    return {"user": user.username, "db_injected": True}
