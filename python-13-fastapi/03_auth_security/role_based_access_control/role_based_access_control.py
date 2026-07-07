"""
学習ポイント: ロールベースアクセス制御（RBAC）
- JWTペイロードにroleを含める
- Dependsで役割チェック関数を注入してエンドポイントを保護
- admin / user / guest の3ロールを例示
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt  # PyJWT
from enum import Enum

SECRET_KEY = "rbac-sample-secret"
ALGORITHM = "HS256"

class Role(str, Enum):
    ADMIN = "admin"
    USER  = "user"
    GUEST = "guest"

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:  # 期限切れ・改ざん等をまとめて捕捉（ExpiredSignatureError等の基底）
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(*roles: Role):
    """指定ロールのいずれかを持つユーザーのみ許可するファクトリ関数"""
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in [r.value for r in roles]:
            raise HTTPException(status_code=403,
                                detail=f"Roles {[r.value for r in roles]} required")
        return user
    return checker

@app.get("/admin/dashboard")
async def admin_dashboard(user: dict = Depends(require_role(Role.ADMIN))):
    return {"message": "管理者専用ダッシュボード", "user": user}

@app.get("/users/profile")
async def user_profile(user: dict = Depends(require_role(Role.ADMIN, Role.USER))):
    return {"message": "ユーザープロフィール", "user": user}

@app.post("/login")
async def login(username: str = "admin", role: Role = Role.ADMIN):
    payload = {"sub": username, "role": role.value,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
