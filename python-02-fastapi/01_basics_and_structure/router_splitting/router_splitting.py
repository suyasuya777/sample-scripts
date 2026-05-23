"""
学習ポイント: APIRouterによるルーターの分割
- prefix  : URLプレフィックス（例: /items, /auth）
- tags    : Swagger UIでのグルーピング名
- include_router: アプリへの組み込み
"""
from fastapi import FastAPI, APIRouter

# ── アイテムルーター ──────────────────────────────────
item_router = APIRouter(prefix="/items", tags=["Items"])

@item_router.get("", summary="全アイテム取得")
async def find_all_items():
    return [{"id": 1, "name": "PC"}]

@item_router.get("/{item_id}", summary="ID指定で取得")
async def find_item(item_id: int):
    return {"id": item_id, "name": "PC"}

# ── 認証ルーター ──────────────────────────────────────
auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/signup", status_code=201, summary="ユーザー登録")
async def signup():
    return {"message": "created"}

@auth_router.post("/login", summary="ログイン")
async def login():
    return {"access_token": "dummy_token", "token_type": "bearer"}

# ── アプリへの登録 ────────────────────────────────────
app = FastAPI()
app.include_router(item_router)
app.include_router(auth_router)

# uvicorn router_splitting:app --reload で起動
# http://localhost:8000/docs で確認
