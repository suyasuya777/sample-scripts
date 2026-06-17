"""
学習ポイント: response_model によるレスポンスフィールドのフィルタリング
- response_model        : エンドポイントの戻り値をスキーマで絞り込む
- response_model_exclude: 特定フィールドを除外する（パスワード等）
- response_model_include: 特定フィールドのみ含める
- セキュリティ設計      : DBモデルに password/salt があっても漏洩しない
"""
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from typing import Optional

app = FastAPI()

# ── 内部データ（DBから取得したイメージ） ─────────────
class UserInternal(BaseModel):
    id: int
    username: str
    password: str   # ハッシュ済みパスワード（外部に出してはいけない）
    salt: str       # ソルト（外部に出してはいけない）

# ── 外部レスポンス用スキーマ（password/salt を含まない） ──
class UserResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

# ── response_model で自動フィルタリング ──────────────
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # DBから取得したデータ（password/saltを含む）
    user = UserInternal(id=user_id, username="user1",
                        password="$pbkdf2-sha256$...", salt="abc123")
    # response_model=UserResponse により password/salt は自動除外される
    return user

# ── response_model_exclude を使う方法 ────────────────
@app.get("/users/{user_id}/exclude", response_model=UserInternal,
         response_model_exclude={"password", "salt"})
async def get_user_exclude(user_id: int):
    return UserInternal(id=user_id, username="user1",
                        password="$pbkdf2-sha256$...", salt="abc123")
