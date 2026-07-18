"""
athena_create_projection_table.py ― Partition Projection テーブルの作成（DDL 実行）

ALB アクセスログ用の外部テーブルを Partition Projection 付きで作成する。
Glue Crawler や ADD PARTITION 不要で、追記され続けるログをそのままクエリできる。

ポイント:
  - CREATE DATABASE / CREATE EXTERNAL TABLE も start_query_execution で流す
  - projection.* と storage.location.template を実 S3 パスに一致させる
  - DDL も SELECT と同じくポーリングで完了待ちする
"""
import time
import boto3
from botocore.exceptions import ClientError


def execute_ddl(
    client,
    sql: str,
    database: str | None,
    workgroup: str = "primary",
    output_location: str | None = None,
    timeout: float = 60.0,
) -> str:
    """DDL（CREATE DATABASE / CREATE TABLE 等）を実行し完了まで待つ。"""
    start_args = {"QueryString": sql, "WorkGroup": workgroup}
    if database:
        start_args["QueryExecutionContext"] = {"Database": database}
    if output_location:
        start_args["ResultConfiguration"] = {"OutputLocation": output_location}

    qid = client.start_query_execution(**start_args)["QueryExecutionId"]

    deadline = time.time() + timeout
    while True:
        status = client.get_query_execution(QueryExecutionId=qid)[
            "QueryExecution"
        ]["Status"]
        state = status["State"]
        if state not in ("QUEUED", "RUNNING"):
            break
        if time.time() > deadline:
            client.stop_query_execution(QueryExecutionId=qid)
            raise TimeoutError(f"DDL タイムアウト: {qid}")
        time.sleep(1.0)

    if state != "SUCCEEDED":
        reason = status.get("StateChangeReason", "(理由不明)")
        raise RuntimeError(f"DDL 失敗 state={state}: {reason}")
    return qid


# ALB アクセスログ用テーブル DDL（day を date 型で射影する AWS 推奨形）
# ※ SerDe の正規表現は長いため要点を抜粋。実運用では AWS 公式の最新版を使うこと。
_ALB_TABLE_DDL = """
CREATE EXTERNAL TABLE IF NOT EXISTS {database}.alb_logs (
  type string,
  time string,
  elb string,
  client_ip string,
  client_port int,
  target_ip string,
  target_port int,
  request_processing_time double,
  target_processing_time double,
  response_processing_time double,
  elb_status_code int,
  target_status_code string,
  received_bytes bigint,
  sent_bytes bigint,
  request_verb string,
  request_url string,
  request_proto string,
  user_agent string,
  ssl_cipher string,
  ssl_protocol string,
  target_group_arn string,
  trace_id string,
  domain_name string,
  chosen_cert_arn string,
  matched_rule_priority string,
  request_creation_time string,
  actions_executed string,
  redirect_url string,
  error_reason string
)
PARTITIONED BY (day string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'input.regex' =
  '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \\"([^ ]*) ([^ ]*) (- |[^ ]*)\\" \\"([^\\"]*)\\" ([A-Z0-9-_]+) ([A-Za-z0-9.-]*) ([^ ]*) \\"([^\\"]*)\\" \\"([^\\"]*)\\" \\"([^\\"]*)\\" ([-.0-9]*) ([^ ]*) \\"([^\\"]*)\\" \\"([^\\"]*)\\".*'
)
LOCATION 's3://{bucket}/AWSLogs/{account_id}/elasticloadbalancing/{region}/'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.day.type' = 'date',
  'projection.day.range' = '{range_start},NOW',
  'projection.day.format' = 'yyyy/MM/dd',
  'projection.day.interval' = '1',
  'projection.day.interval.unit' = 'DAYS',
  'storage.location.template' =
    's3://{bucket}/AWSLogs/{account_id}/elasticloadbalancing/{region}/${{day}}'
)
"""


def main() -> None:
    region = "ap-northeast-1"
    database = "log_analysis"
    workgroup = "primary"
    output_location = "s3://your-athena-results-bucket/query-results/"

    # 実環境に合わせて置き換える
    bucket = "your-alb-log-bucket"
    account_id = "123456789012"
    range_start = "2024/01/01"  # ログ蓄積開始日に合わせて絞ると無駄スキャンを防げる

    client = boto3.client("athena", region_name=region)

    try:
        # 1) データベース作成（既存ならスキップされる）
        execute_ddl(
            client,
            sql=f"CREATE DATABASE IF NOT EXISTS {database}",
            database=None,
            workgroup=workgroup,
            output_location=output_location,
        )
        print(f"[OK] database ready: {database}")

        # 2) Partition Projection 付きテーブル作成
        ddl = _ALB_TABLE_DDL.format(
            database=database,
            bucket=bucket,
            account_id=account_id,
            region=region,
            range_start=range_start,
        )
        execute_ddl(
            client,
            sql=ddl,
            database=database,
            workgroup=workgroup,
            output_location=output_location,
        )
        print("[OK] table ready: alb_logs（Partition Projection 有効）")
        print("     → WHERE day='2026/07/18' でスキャン範囲を絞ってクエリ可能")

    except (ClientError, RuntimeError, TimeoutError) as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
