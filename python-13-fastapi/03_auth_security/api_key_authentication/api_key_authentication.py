"""
学習ポイント: APIキー認証
- APIKeyHeader : Headerからキーを取得する認証スキーム
- APIKeyQuery  : クエリパラメーターからキーを取得
- 用途         : バックエンド間通信や外部サービス連携時の認証
"""
from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery

app = FastAPI()

VALID_API_KEYS = {"secret-key-123", "another-valid-key"}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query  = APIKeyQuery(name="api_key", auto_error=False)

def get_api_key(
    header_key: str = Security(api_key_header),
    query_key:  str = Security(api_key_query),
) -> str:
    key = header_key or query_key
    if key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key

@app.get("/data")
async def get_data(api_key: str = Security(get_api_key)):
    return {"message": "認証成功", "api_key": api_key[:8] + "..."}
