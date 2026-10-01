"""
athena_create_projection_table.py ― Partition Projection テーブルの作成（DDL 実行）

ALB アクセスログ用の外部テーブルを Partition Projection 付きで作成する。
Glue Crawler や ADD PARTITION 不要で、追記され続けるログをそのままクエリできる。

ポイント:
  - CREATE DATABASE / CREATE EXTERNAL TABLE も start_query_execution で流す
  - projection.* と storage.location.template を実 S3 パスに一致させる
  - DDL も SELECT と同じくポーリングで完了待ちする

--------------------------------------------------------------------
実行前に下の「設定」を terraform output の値に置き換えること:

  terraform output -raw athena_alb_log_location    -> ALB_LOG_LOCATION
  terraform output -raw athena_results_location    -> OUTPUT_LOCATION
--------------------------------------------------------------------
"""
import time
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
DATABASE = "boto3_study"
TABLE = "alb_logs"
WORKGROUP = "primary"

# terraform output -raw athena_alb_log_location
# 例: s3://boto3-study-logs-123456789012/alb/AWSLogs/123456789012/elasticloadbalancing/ap-northeast-1/
# 末尾のスラッシュは必須（storage.location.template で ${day} を直接つなげるため）
ALB_LOG_LOCATION = "s3://REPLACE-ME/alb/AWSLogs/000000000000/elasticloadbalancing/ap-northeast-1/"

# terraform output -raw athena_results_location
OUTPUT_LOCATION = "s3://REPLACE-ME-athena/query-results/"

# 射影の開始日。ログが無い日を含めても害はないが、狭いほど無駄スキャンが減る
PROJECTION_RANGE_START = "2027/02/01"
# ==================================================


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


# ------------------------------------------------------------------
# ALB アクセスログ用テーブル DDL
#
# AWS 公式（Athena ユーザーガイド「Create the table for ALB access logs
# in Athena using partition projection」）のものをそのまま使う。
#
# 【重要】列と input.regex のキャプチャグループは必ず対応させること。
#   RegexSerDe は「N 番目のグループ → N 番目の列」で機械的に割り当てるので、
#   途中で1つでもズレると以降の列がすべて1つずつ後ろにずれ、型が合わない列
#   （elb_status_code は int など）は NULL になる。「検索結果が NULL だらけ」
#   の原因はほぼこれ。
#   - 列: 34（client:port と target:port をそれぞれ ip / port の2列に分解、
#          "request" を verb / url / proto の3列に分解）
#   - グループ: 35。最後の ?( .*)? は列を持たない意図的な余り。
#     ALB のログ形式に将来フィールドが追加されても壊れないようにするための
#     もので、AWS も「常に残しておくこと」と明記している。
#     末尾の余りグループは無視されるだけなので列ズレは起きない。
# ------------------------------------------------------------------
_ALB_TABLE_DDL = r"""
CREATE EXTERNAL TABLE IF NOT EXISTS {database}.{table} (
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
  lambda_error_reason string,
  target_port_list string,
  target_status_code_list string,
  classification string,
  classification_reason string,
  conn_trace_id string
)
PARTITIONED BY (day string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1',
  'input.regex' = '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) (.*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-_]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^ ]*)\" \"([^\\s]+?)\" \"([^\\s]+)\" \"([^ ]*)\" \"([^ ]*)\" ?([^ ]*)? ?( .*)?'
)
LOCATION '{location}'
TBLPROPERTIES (
  'projection.enabled' = 'true',
  'projection.day.type' = 'date',
  'projection.day.range' = '{range_start},NOW',
  'projection.day.format' = 'yyyy/MM/dd',
  'projection.day.interval' = '1',
  'projection.day.interval.unit' = 'DAYS',
  'storage.location.template' = '{location}${{day}}'
)
"""


def main() -> None:
    if "REPLACE-ME" in ALB_LOG_LOCATION or "REPLACE-ME" in OUTPUT_LOCATION:
        print("[ERROR] ALB_LOG_LOCATION / OUTPUT_LOCATION を terraform output の値に置き換えてください")
        print("        terraform output -raw athena_alb_log_location")
        print("        terraform output -raw athena_results_location")
        return

    if not ALB_LOG_LOCATION.endswith("/"):
        print("[ERROR] ALB_LOG_LOCATION は必ず '/' で終わらせること")
        return

    client = boto3.client("athena", region_name=REGION)

    try:
        # 1) データベース作成（既存ならスキップされる）
        execute_ddl(
            client,
            sql=f"CREATE DATABASE IF NOT EXISTS {DATABASE}",
            database=None,
            workgroup=WORKGROUP,
            output_location=OUTPUT_LOCATION,
        )
        print(f"[OK] database ready: {DATABASE}")

        # 2) Partition Projection 付きテーブル作成
        ddl = _ALB_TABLE_DDL.format(
            database=DATABASE,
            table=TABLE,
            location=ALB_LOG_LOCATION,
            range_start=PROJECTION_RANGE_START,
        )
        execute_ddl(
            client,
            sql=ddl,
            database=DATABASE,
            workgroup=WORKGROUP,
            output_location=OUTPUT_LOCATION,
        )
        print(f"[OK] table ready: {DATABASE}.{TABLE}（Partition Projection 有効）")
        print("     → WHERE day='2027/02/14' でスキャン範囲を絞ってクエリ可能")
        print("        （ログがあるのは 2/1・2/11・2/14・2/23。2/28 当日の分は無い）")

    except (ClientError, RuntimeError, TimeoutError) as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
