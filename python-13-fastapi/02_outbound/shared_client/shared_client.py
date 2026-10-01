"""
学習ポイント: httpx クライアントはアプリで1つだけ持つ
- 悪い例: リクエストごとに AsyncClient を生成する
- 良い例: lifespan で1つ生成し、app.state 経由で使い回す
- Limits : max_connections（同時接続上限）/ max_keepalive_connections（維持する数）

SRE 的な論点:
  リクエストごとにクライアントを作ると、毎回 TCP + TLS ハンドシェイクが走り、
  接続はすぐ捨てられる。結果として起きるのは次の3つ。
    1. レイテンシ増（TLS ハンドシェイクは往復2回分）
    2. エフェメラルポート枯渇（同一宛先への 5 タプルを使い切る）
    3. NAT Gateway 経由なら SNAT ポート枯渇（ErrorPortAllocation）
  いずれも「アプリのバグ」ではなく「ネットワーク層の枯渇」として現れるため、
  アプリログには何も出ず、調査が難しくなる。
"""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request

TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=3.0)

# max_connections     : このクライアントが同時に張る接続の上限
# max_keepalive_connections : アイドル時に維持しておく接続数
LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)


# ── ❌ 悪い例 ─────────────────────────────────────────
async def bad_call(post_id: int):
    """リクエストごとにプールごと作って捨てている"""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(f"https://example.invalid/posts/{post_id}")
        return r.json()


# ── ✅ 良い例 ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(
        timeout=TIMEOUT,
        limits=LIMITS,
        headers={"user-agent": "sre-sample/1.0"},
    )
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/posts/{post_id}")
async def get_post(post_id: int, request: Request):
    client: httpx.AsyncClient = request.app.state.http
    r = await client.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
    r.raise_for_status()
    return r.json()


# ── 検算 ──────────────────────────────────────────────
# タスク数 × max_connections が、呼び出し先の受け入れ能力を超えていないか。
#   例) 20 タスク × 100 = 2,000 同時接続
#   呼び出し先が 500 しか捌けないなら、こちらが相手を落とす側になる。
#
# ── 確認方法 ──────────────────────────────────────────
#   ss -tan state established | wc -l      # 接続数の推移を見る
#   悪い例では負荷に比例して TIME_WAIT が積み上がる
