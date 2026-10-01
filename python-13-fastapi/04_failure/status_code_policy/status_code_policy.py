"""
学習ポイント: 4xx と 5xx の切り分けが SLI の分母と分子になる
- 4xx : クライアント起因。自分のサービスは正常に動いている
- 5xx : サーバ起因。自分の責任

SRE 的な論点:
  本来 4xx のものを 500 で返していると、可用性 SLO が実態より悪く出る。
  逆に、自分の不具合を 400 で返していると SLO が実態より良く出る。
  どちらも「数値を見ても状態が分からない」状態を作る。

  判断に迷う代表例と方針:
  ┌──────────────────────────┬──────────────────────────────────┐
  │ 状況                       │ 返すもの                          │
  ├──────────────────────────┼──────────────────────────────────┤
  │ 下流APIが404を返した        │ 業務的に「見つからない」なら404      │
  │                            │ 下流の設定ミスが原因なら502          │
  │ 下流APIがタイムアウト        │ 504（自分は正常だが完遂できない）     │
  │ 下流APIが500を返した        │ 502（bad gateway）                 │
  │ 自分のDBに繋がらない         │ 503（依存が復旧すれば直る）          │
  │ コードのバグでNoneエラー     │ 500                              │
  │ レート制限に到達            │ 429（Retry-After を付ける）         │
  │ 認証なし / 期限切れ          │ 401                              │
  │ 認証済みだが権限なし         │ 403                              │
  └──────────────────────────┴──────────────────────────────────┘
"""
from fastapi import FastAPI, HTTPException, Response, status

app = FastAPI()


@app.get("/rate-limited")
async def rate_limited(response: Response):
    """429 には必ず Retry-After を付ける。付けないとクライアントが即リトライする"""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="rate limit exceeded",
        headers={"Retry-After": "30"},
    )


@app.get("/depends-on-db")
async def depends_on_db():
    db_ok = False
    if not db_ok:
        # 依存が復旧すれば直る種類の失敗は 503
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"ok": True}


# ── 可用性 SLI の定義（この分類がそのまま効く） ──────────
# 分母: ヘルスチェックを除く全リクエスト
# 分子: ステータスが 5xx 以外のリクエスト
#   → 4xx はサービスとしては正常に応答しているので成功に数える
#   → ただし 429 を大量に返している状態は「正常」ではないので、
#     別途レート制限の発火率を監視する
