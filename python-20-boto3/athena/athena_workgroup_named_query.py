"""
athena_workgroup_named_query.py ― ワークグループと名前付きクエリの管理

障害調査でよく使う定番クエリを named query として登録・再利用し、
ワークグループ単位でスキャン量上限やコスト管理を行うためのサンプル。

  - ワークグループ作成（結果出力先・スキャン量上限・コスト制御）
  - 名前付きクエリの登録 / 一覧 / 取得
  - ワークグループ内のクエリ実行履歴の確認

--------------------------------------------------------------------
実行前に下の「設定」を terraform output の値に置き換えること:

  terraform output -raw athena_results_location    -> OUTPUT_LOCATION

ここで作ったワークグループは Terraform 管理外。3/14 の破棄チェックリストで
手動削除すること（aws athena list-work-groups / delete-work-group）。
--------------------------------------------------------------------
"""
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
DATABASE = "boto3_study"          # athena_create_projection_table.py で作ったもの
TABLE = "alb_logs"
WORKGROUP = "boto3-study-incident"

# terraform output -raw athena_results_location
OUTPUT_LOCATION = "s3://REPLACE-ME-athena/query-results/"

# 1 クエリあたりのスキャン量上限（バイト）。学習環境のログは数MBなので 1GB で十分
BYTES_SCANNED_CUTOFF = 1 * 1024 ** 3
# ==================================================


def ensure_workgroup(
    client,
    name: str,
    output_location: str,
    bytes_scanned_cutoff: int | None = None,
) -> None:
    """
    ワークグループを作成（存在すれば何もしない）。

    :param bytes_scanned_cutoff: 1 クエリあたりのスキャン量上限（バイト）。
                                 設定すると上限超過クエリは自動でキャンセルされ、
                                 想定外の高額クエリを防げる。
    """
    config: dict = {
        "ResultConfiguration": {"OutputLocation": output_location},
        # ワークグループ側の設定をクライアント設定より優先させる
        "EnforceWorkGroupConfiguration": True,
        "PublishCloudWatchMetricsEnabled": True,
    }
    if bytes_scanned_cutoff:
        config["BytesScannedCutoffPerQuery"] = bytes_scanned_cutoff

    try:
        client.create_work_group(
            Name=name,
            Configuration=config,
            Description="障害調査・ログ分析用ワークグループ",
        )
        print(f"[OK] ワークグループ作成: {name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidRequestException":
            # 既に存在する場合はここに来る
            print(f"[SKIP] ワークグループは既に存在: {name}")
        else:
            raise


def register_named_query(
    client,
    name: str,
    database: str,
    sql: str,
    workgroup: str,
    description: str = "",
) -> str:
    """名前付きクエリを登録して NamedQueryId を返す。"""
    resp = client.create_named_query(
        Name=name,
        Database=database,
        QueryString=sql,
        WorkGroup=workgroup,
        Description=description,
    )
    qid = resp["NamedQueryId"]
    print(f"[OK] 名前付きクエリ登録: {name} ({qid})")
    return qid


def list_named_queries(client, workgroup: str) -> None:
    """ワークグループ内の名前付きクエリを一覧表示する。"""
    paginator = client.get_paginator("list_named_queries")
    print(f"\n=== 名前付きクエリ一覧（{workgroup}） ===")
    for page in paginator.paginate(WorkGroup=workgroup):
        ids = page.get("NamedQueryIds", [])
        if not ids:
            continue
        # まとめて詳細取得（batch）
        detail = client.batch_get_named_query(NamedQueryIds=ids)
        for nq in detail["NamedQueries"]:
            print(f"  - {nq['Name']}  [{nq['Database']}]")
            if nq.get("Description"):
                print(f"      {nq['Description']}")


def main() -> None:
    if "REPLACE-ME" in OUTPUT_LOCATION:
        print("[ERROR] OUTPUT_LOCATION を terraform output の値に置き換えてください")
        print("        terraform output -raw athena_results_location")
        return

    client = boto3.client("athena", region_name=REGION)

    try:
        # 1) ワークグループ作成（スキャン量上限付き）
        ensure_workgroup(
            client,
            name=WORKGROUP,
            output_location=OUTPUT_LOCATION,
            bytes_scanned_cutoff=BYTES_SCANNED_CUTOFF,
        )

        # 2) 障害調査の定番クエリを登録
        register_named_query(
            client,
            name="alb_5xx_by_day",
            database=DATABASE,
            sql=(
                f"SELECT time, elb_status_code, target_status_code, request_url "
                f"FROM {TABLE} WHERE day = '2027/02/28' AND elb_status_code >= 500 "
                f"ORDER BY time LIMIT 100"
            ),
            workgroup=WORKGROUP,
            description="指定日の ALB 5xx を抽出（day は使う前に書き換える）",
        )
        register_named_query(
            client,
            name="alb_slow_targets",
            database=DATABASE,
            sql=(
                f"SELECT time, target_processing_time, request_url "
                f"FROM {TABLE} WHERE day = '2027/02/28' "
                f"AND target_processing_time > 1.0 "
                f"ORDER BY target_processing_time DESC LIMIT 100"
            ),
            workgroup=WORKGROUP,
            description="ターゲット処理時間 1 秒超の遅いリクエスト",
        )

        # 3) 登録済みクエリの一覧
        list_named_queries(client, WORKGROUP)

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")


if __name__ == "__main__":
    main()
