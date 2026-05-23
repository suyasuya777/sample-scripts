"""
学習ポイント: OAuth2PasswordBearer による認証フロー
- OAuth2PasswordBearer    : Authorization: Bearer ヘッダーからトークンを自動抽出
- OAuth2PasswordRequestForm: username/password をフォーム形式で受け取る
- tokenUrl               : Swagger UIのログインエンドポイント指定
- Depends(get_current_user): 認証済みユーザーを各エンドポイントに自動注入
"""
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel

SECRET_KEY = "change-this-in-production"
ALGORITHM = "HS256"

app = FastAPI()

# tokenUrl はログインエンドポイントのパス。Swagger UIの「Authorize」ボタンが使うURL。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class DecodedToken(BaseModel):
    username: str
    user_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

FAKE_USERS = {"user1": {"user_id": 1, "password": "pass1234"}}

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> DecodedToken:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if not username or not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return DecodedToken(username=username, user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token validation failed")

UserDependency = Annotated[DecodedToken, Depends(get_current_user)]

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    payload = {"sub": form_data.username, "id": user["user_id"],
               "exp": datetime.now() + timedelta(minutes=20)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=token, token_type="bearer")

@app.get("/protected")
async def protected_route(current_user: UserDependency):
    return {"message": f"Hello, {current_user.username}!"}
