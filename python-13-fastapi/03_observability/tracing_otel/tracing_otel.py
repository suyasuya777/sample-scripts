"""
学習ポイント: サービスをまたいだ1本の処理を追う
- トレース  : 1リクエストの全体。trace_id で識別
- スパン    : その中の1区間（DB問い合わせ、外部API呼び出し等）。span_id で識別
- 伝搬     : traceparent ヘッダで下流に引き継ぐ（W3C Trace Context）

三者の役割分担:
| 種類       | 得意なこと                     | 苦手なこと            |
|-----------|-------------------------------|----------------------|
| メトリクス | 全体の傾向、SLI の計算、アラート | 個別の原因特定        |
| ログ       | 個別リクエストの詳細            | 集計、横断の追跡      |
| トレース   | どの区間が遅いかの特定          | 全件保持（サンプリング前提） |

SRE 的な論点:
  「遅い」という報告に対して、DNS / 接続 / TLS / サーバ処理 / 下流呼び出しの
  どこが伸びたかを分解できるかが分岐点。トレースがないと、各サービスの
  ログを時刻で突き合わせる作業になり、数時間かかる。

  サンプリングは必須（全件保持はコストが合わない）。ただしエラーは
  必ず残す設定（tail-based sampling）にしないと、肝心のときに残っていない。
"""
# pip install opentelemetry-distro opentelemetry-instrumentation-fastapi \
#             opentelemetry-instrumentation-httpx opentelemetry-exporter-otlp
#
# from opentelemetry import trace
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from fastapi import FastAPI

app = FastAPI()

# ── 自動計装 ──────────────────────────────────────────
# FastAPIInstrumentor.instrument_app(app)   # 受信側のスパンを自動生成
# HTTPXClientInstrumentor().instrument()    # 送信側に traceparent を自動付与


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    # ── 手動でスパンを切る例 ──────────────────────────
    # tracer = trace.get_tracer(__name__)
    # with tracer.start_as_current_span("load_order") as span:
    #     span.set_attribute("order.id", order_id)
    #     ...
    return {"order_id": order_id}


# ── AWS で動かす場合 ─────────────────────────────────
# ADOT Collector をサイドカーとして同一タスクに置き、
# アプリは OTLP で localhost:4317 に送る。Collector が X-Ray へ変換する。
# ALB の X-Amzn-Trace-Id と OTel の traceparent は別物なので、
# 両方をログに残して突き合わせられるようにしておく。
#
# ── ログとの接続 ──────────────────────────────────────
# ログの JSON に trace_id / span_id を含めると、トレースから該当ログへ、
# ログから該当トレースへ双方向に飛べるようになる。これをやるかどうかで
# 調査速度が大きく変わる。
