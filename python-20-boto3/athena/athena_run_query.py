"""
athena_run_query.py ― Athena クエリ実行と結果取得（ポーリング）

ALB / VPC Flow Logs / CloudTrail のログ分析で、SELECT クエリを実行し
完了までポーリングして結果を取得する実用パターン。
CloudWatch Logs Insights の start_query / get_query_results と同じ考え方。

--------------------------------------------------------------------
実行前に下の「設定」を terraform output の値に置き換えること:

  terraform output -raw athena_results_location    -> OUTPUT_LOCATION

ワークグループ primary は結果出力先が未設定なので、OUTPUT_LOCATION を
渡さないと InvalidRequestException: No output location provided. になる。
--------------------------------------------------------------------
"""
import time
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
DATABASE = "boto3_study"          # athena_create_projection_table.py で作ったもの
TABLE = "alb_logs"
WORKGROUP = "primary"

# terraform output -raw athena_results_location
OUTPUT_LOCATION = "s3://REPLACE-ME-athena/query-results/"

# 調べたい日（Partition Projection のキー。yyyy/MM/dd）
# ALB アクセスログはリクエストがあった日にしか作られない。この環境で
# トラフィックを流すのは 2/1・2/11・2/14・2/23 の4日だけで、2/28 当日の
# ログは存在しない。既定は 2/14（意図的に 503 を出した日）。
DAY = "2027/02/14"
# ==================================================

# 完了とみなさない（＝まだ実行中の）ステートの集合
_RUNNING_STATES = {"QUEUED", "RUNNING"}


def run_query(
    sql: str,
    database: str,
    workgroup: str = "primary",
    output_location: str | None = None,
    poll_interval: float = 1.0,
    timeout: float = 120.0,
    region: str = "ap-northeast-1",
) -> dict:
    """
    Athena クエリを実行し、完了まで待ってから結果行を返す。

    :param sql: 実行する SQL（SELECT / DDL いずれも可）
    :param database: 対象の Glue データベース名
    :param workgroup: 使用するワークグループ（結果出力先が設定済みなら output_location 省略可）
    :param output_location: s3://... 形式のクエリ結果出力先。ワークグループ側で
                            指定済みの場合は None でよい
    :param poll_interval: ポーリング間隔（秒）
    :param timeout: タイムアウト（秒）
    :return: {"columns": [...], "rows": [[...], ...], "query_execution_id": "..."}
    """
    client = boto3.client("athena", region_name=region)

    # 1) クエリ開始 --------------------------------------------------------
    start_args = {
        "QueryString": sql,
        "QueryExecutionContext": {"Database": database},
        "WorkGroup": workgroup,
    }
    # ワークグループに出力先が未設定なら ResultConfiguration で明示指定する
    if output_location:
        start_args["ResultConfiguration"] = {"OutputLocation": output_location}

    resp = client.start_query_execution(**start_args)
    qid = resp["QueryExecutionId"]
    print(f"[START] QueryExecutionId = {qid}")

    # 2) 完了までポーリング -----------------------------------------------
    deadline = time.time() + timeout
    while True:
        exec_info = client.get_query_execution(QueryExecutionId=qid)
        status = exec_info["QueryExecution"]["Status"]
        state = status["State"]

        if state not in _RUNNING_STATES:
            break
        if time.time() > deadline:
            # 実行中のまま時間切れ → 明示的に停止しておく
            client.stop_query_execution(QueryExecutionId=qid)
            raise TimeoutError(f"クエリがタイムアウトしました: {qid}")

        time.sleep(poll_interval)

    # 3) 成否判定 ----------------------------------------------------------
    if state != "SUCCEEDED":
        reason = status.get("StateChangeReason", "(理由不明)")
        raise RuntimeError(f"クエリ失敗 state={state}: {reason}")

    # スキャン量（課金に直結するので運用上重要）
    scanned = exec_info["QueryExecution"]["Statistics"].get(
        "DataScannedInBytes", 0
    )
    print(f"[DONE ] state={state}  scanned={scanned / 1024 / 1024:.2f} MB")

    # 4) 結果取得（paginator で全件） -------------------------------------
    paginator = client.get_paginator("get_query_results")
    columns: list[str] = []
    rows: list[list[str]] = []

    for page_idx, page in enumerate(
        paginator.paginate(QueryExecutionId=qid)
    ):
        result_set = page["ResultSet"]
        # 列名は最初のページのメタデータから取得
        if not columns:
            columns = [
                c["Label"]
                for c in result_set["ResultSetMetadata"]["ColumnInfo"]
            ]

        for row_idx, row in enumerate(result_set["Rows"]):
            # 最初のページの先頭行はヘッダー行なのでスキップ
            if page_idx == 0 and row_idx == 0:
                continue
            # VarCharValue が無いセル（NULL）は None として扱う
            rows.append([cell.get("VarCharValue") for cell in row["Data"]])

    return {"columns": columns, "rows": rows, "query_execution_id": qid}


def main() -> None:
    if "REPLACE-ME" in OUTPUT_LOCATION:
        print("[ERROR] OUTPUT_LOCATION を terraform output の値に置き換えてください")
        print("        terraform output -raw athena_results_location")
        return

    # ALB が返した 5xx と、ALB とターゲットでステータスが食い違う行を抽出する。
    # target_status_code は文字列（'-' が入りうる）なので、比較の前に除外する。
    sql = f"""
        SELECT time,
               elb_status_code,
               target_status_code,
               request_url,
               target_processing_time
        FROM {TABLE}
        WHERE day = '{DAY}'
          AND (elb_status_code >= 500
               OR (target_status_code <> '-'
                   AND CAST(elb_status_code AS varchar) <> target_status_code))
        ORDER BY time
        LIMIT 50
    """
    try:
        result = run_query(
            sql=sql,
            database=DATABASE,
            workgroup=WORKGROUP,
            output_location=OUTPUT_LOCATION,
        )
    except (ClientError, RuntimeError, TimeoutError) as e:
        print(f"[ERROR] {e}")
        return

    print("\n" + " | ".join(result["columns"]))
    print("-" * 60)
    for row in result["rows"]:
        print(" | ".join("" if v is None else v for v in row))
    print(f"\n{len(result['rows'])} 件")

    if not result["rows"]:
        print("0 件のときの確認順序:")
        print("  1. day の指定が正しいか（ログは UTC 日付でパーティションされる）")
        print(f"     aws s3 ls {DAY.replace('/', '/')}/ を含むパスで実際のファイルを確認")
        print("  2. SELECT * FROM " + TABLE + f" WHERE day='{DAY}' LIMIT 5 で生の行が引けるか")
        print("  3. 引けた行が NULL だらけなら input.regex と列の対応ズレ")


if __name__ == "__main__":
    main()
