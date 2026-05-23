"""
学習ポイント: JWTトークンの生成・検証
- jwt.encode()  : ペイロードをHS256で署名してJWTを生成
- jwt.decode()  : JWTを検証してペイロードを取得
- exp           : 有効期限クレーム（datetime.now() + timedelta）
- JWTError      : 署名不正・期限切れ時の例外
"""
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from jose import jwt, JWTError
from pydantic import BaseModel

SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20

app = FastAPI()

class TokenPayload(BaseModel):
    sub: str        # subject（ユーザー名）
    user_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(username: str, user_id: int) -> str:
    expires = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "id": user_id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"無効なトークン: {e}")

@app.post("/token", response_model=Token)
async def issue_token(username: str = "user1", user_id: int = 1):
    token = create_access_token(username, user_id)
    return Token(access_token=token, token_type="bearer")

@app.get("/verify")
async def verify_token(token: str):
    payload = decode_access_token(token)
    return {"username": payload.get("sub"), "user_id": payload.get("id")}
