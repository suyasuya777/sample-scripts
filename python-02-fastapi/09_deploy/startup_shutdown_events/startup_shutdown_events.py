"""
学習ポイント: lifespan によるアプリ起動・終了イベント管理（α）
- lifespan (推奨)    : FastAPI 0.93+ の推奨パターン。contextmanager で起動・終了を管理
- @app.on_event      : 旧パターン（非推奨だが互換性のために残存）
- 用途               : DB接続プール初期化・Redis接続・外部サービス疎通確認・クリーンアップ
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

# ── 推奨パターン: lifespan ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup（yield より前） ────────────────────────
    print("[startup] DB接続プール初期化")
    print("[startup] Redis接続確認")
    print("[startup] アプリ起動完了")
    yield
    # ── shutdown（yield より後） ───────────────────────
    print("[shutdown] DB接続プールクローズ")
    print("[shutdown] Redis接続クローズ")
    print("[shutdown] クリーンアップ完了")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "running"}

# ── 旧パターン（参考）: on_event ───────────────────────
legacy_app = FastAPI()

@legacy_app.on_event("startup")
async def startup_event():
    print("[legacy startup]")

@legacy_app.on_event("shutdown")
async def shutdown_event():
    print("[legacy shutdown]")
