"""
学習ポイント: OpenAPI（Swagger UI）のカスタマイズ
- FastAPI()のパラメーター : title / description / version / docs_url
- タグのメタデータ        : タグごとの説明文・外部ドキュメントリンク
- セキュリティスキーマ    : Swagger UIの「Authorize」ボタンの設定
- レスポンス例の追加      : responses パラメーターで複数のレスポンス例を定義
"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Fleamarket API",
    description="""
## フリーマーケットAPI

FastAPI + PostgreSQL で構築したフリーマーケット向け REST API です。

### 機能
- 🔐 JWT認証
- 📦 アイテム出品・検索・更新・削除
- 👤 ユーザー登録・ログイン
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Auth",  "description": "ユーザー認証・JWT発行"},
        {"name": "Items", "description": "アイテムのCRUD操作"},
    ],
)

@app.get("/items", tags=["Items"],
         summary="全アイテム取得",
         description="出品中の全アイテムを一覧取得します",
         responses={200: {"description": "取得成功"}, 500: {"description": "サーバーエラー"}})
async def get_items():
    return []
