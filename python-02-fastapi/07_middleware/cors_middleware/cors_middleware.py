"""
学習ポイント: CORSMiddleware の設定
- allow_origins      : 許可するオリジン（フロントエンドURL）
- allow_methods      : 許可するHTTPメソッド
- allow_headers      : 許可するリクエストヘッダー
- allow_credentials  : Cookie/認証情報の送信を許可するか
- "*" の注意         : allow_credentials=True と組み合わせる場合は具体的なオリジンが必要
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 開発環境: フロントエンド開発サーバーを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Token"],
)

@app.get("/api/data")
async def get_data():
    return {"data": "CORSが設定されたレスポンス"}

# ── 本番環境での設定例 ──────────────────────────────
ALLOWED_ORIGINS_PROD = [
    "https://example.com",
    "https://www.example.com",
]

def create_production_app() -> FastAPI:
    prod_app = FastAPI()
    prod_app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS_PROD,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return prod_app
