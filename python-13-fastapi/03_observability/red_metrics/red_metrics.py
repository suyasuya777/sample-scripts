"""
学習ポイント: RED メトリクスを公開する
- Rate     : 単位時間あたりのリクエスト数
- Errors   : そのうち失敗した数
- Duration : 処理時間の分布（平均ではなくヒストグラム）

SRE 的な論点:
  ログからの集計でメトリクスを代用すると、次の問題が出る。
    - コスト  : Logs Insights のスキャン量課金
    - 遅延    : 集計に時間がかかり、アラートが遅れる
    - 保持    : ログは数週間で消すが、メトリクスは年単位で持ちたい
  SLI を計算する母数はメトリクスで持ち、ログは個別調査に使う、と役割を分ける。

  平均を使ってはいけない理由:
    1%のリクエストが10秒かかっていても、99%が50msなら平均は約150ms。
    平均だけ見ていると「正常」に見える。p99 を見て初めて気づく。

  ヒストグラムのバケットは後から変えにくい（過去データと比較できなくなる）。
  SLO の閾値をバケット境界に含めておくのが定石。
"""
import time

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI()

REQUESTS = Counter(
    "http_requests_total", "リクエスト総数", ["method", "path", "status"]
)
# SLO が「p99 < 500ms」なら 0.5 をバケット境界に含めておく
LATENCY = Histogram(
    "http_request_duration_seconds", "処理時間",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

EXCLUDE = {"/metrics", "/livez", "/readyz"}


def route_template(request: Request) -> str:
    """path をそのまま使うとIDごとに系列が増える（カーディナリティ爆発）"""
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


@app.middleware("http")
async def observe(request: Request, call_next):
    if request.url.path in EXCLUDE:
        return await call_next(request)

    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        path = route_template(request)
        REQUESTS.labels(request.method, path, str(status)).inc()
        LATENCY.labels(request.method, path).observe(time.perf_counter() - start)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id}


# ── カーディナリティに注意 ────────────────────────────
# ラベルに item_id のような可変値を入れると系列数が無限に増え、
# メトリクスのストレージとクエリが破綻する。ルートのテンプレート
# （/items/{item_id}）を使うこと。
