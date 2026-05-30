"""
学習ポイント: ヘルスチェックエンドポイントの実装
- /health     : コンテナオーケストレーター（ECS/K8s）が死活監視に使用
- /ready      : アプリが受け付け可能な状態かを確認（DB接続確認等）
- /live       : プロセスが生きているかを確認
- レスポンス  : status / version / db_status 等を返す
"""
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
START_TIME = time.time()

@app.get("/health", tags=["Health"])
async def health_check():
    """ALB/ECSヘルスチェック用。DB接続は確認しない（軽量）"""
    return {"status": "healthy"}

@app.get("/ready", tags=["Health"])
async def readiness_check():
    """起動準備完了確認。DB接続・必要リソースの確認を行う"""
    db_ok = True  # 実際はDBへの接続確認
    if not db_ok:
        return JSONResponse(status_code=503, content={"status": "not ready", "db": "unavailable"})
    return {
        "status": "ready",
        "uptime_seconds": int(time.time() - START_TIME),
        "db": "connected",
    }

@app.get("/live", tags=["Health"])
async def liveness_check():
    """プロセス生存確認"""
    return {"status": "alive", "uptime_seconds": int(time.time() - START_TIME)}
