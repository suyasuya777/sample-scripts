import json
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent, event_source

# ── Powertools 初期化 ─────────────────────────────────────────
logger = Logger(service="my-lambda-service")   # 構造化 JSON ログ
tracer = Tracer(service="my-lambda-service")   # X-Ray トレーシング
metrics = Metrics(namespace="MyApp", service="my-lambda-service")  # カスタムメトリクス


# ── サブ処理（トレースセグメント追加）────────────────────────
@tracer.capture_method
def fetch_data(item_id: str) -> dict:
    """X-Ray でこのメソッドのサブセグメントが自動作成される"""
    logger.info("データ取得", extra={"item_id": item_id})
    # 本来は DB / 外部 API 呼び出しなど
    return {"id": item_id, "name": "sample"}


# ── Lambda ハンドラー ─────────────────────────────────────────
@logger.inject_lambda_context(log_event=True)         # コールドスタート情報・イベントをログ出力
@tracer.capture_lambda_handler                         # ハンドラー全体を X-Ray トレース
@metrics.log_metrics(capture_cold_start_metric=True)  # コールドスタートメトリクスを自動送信
@event_source(data_class=APIGatewayProxyEvent)         # イベントを型付きオブジェクトに変換
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext) -> dict:
    item_id = (event.path_parameters or {}).get("id", "default")

    # カスタムメトリクスの送信
    metrics.add_metric(name="ItemRequested", unit=MetricUnit.Count, value=1)

    # 構造化ログ（JSON 形式で CloudWatch Logs に出力される）
    logger.info("リクエスト受信", extra={"item_id": item_id, "path": event.path})

    try:
        data = fetch_data(item_id)
        # レスポンスをトレースに追加
        tracer.put_annotation(key="item_id", value=item_id)
        tracer.put_metadata(key="response", value=data)

        return {
            "statusCode": 200,
            "body": json.dumps(data, ensure_ascii=False),
        }
    except Exception as e:
        logger.exception("処理エラー")
        metrics.add_metric(name="ItemError", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "内部エラーが発生しました"}),
        }
