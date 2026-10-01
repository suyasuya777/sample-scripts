"""
33. Lambda 同時実行数の確認と予約（書き込みあり）

参照（現状把握）と書き込み（予約の設定・削除）の両方をやる。

--------------------------------------------------------------------
実行前に置き換えること:

  terraform output -json lambda_function_names   -> TARGET_FUNCTION
  （boto3-study-ok / -canary / -config のいずれか。既定は -ok）

【重要】アカウントの同時実行上限に注意。
put_function_concurrency は「未予約の枠を 100 以上残す」制約がある。
新しいアカウントは上限が 10 のままのことがあり、その場合は何を指定しても

  InvalidParameterValueException: Specified ConcurrentExecutions for
  function decreases account's UnreservedConcurrentExecutions below
  its minimum value of [100].

で必ず失敗する。このスクリプトは実行前に上限を確認し、足りなければ
書き込みをスキップして引き上げ申請の案内を出す。
--------------------------------------------------------------------
"""
import time
import boto3
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
TARGET_FUNCTION = "boto3-study-ok"   # 予約を設定する対象
RESERVED = 1                          # 予約する同時実行数
INVOKE_COUNT = 20                     # スロットリングを起こすための非同期呼び出し数
MIN_UNRESERVED = 100                  # AWS が要求する未予約の最小枠
# ==================================================

lmb = boto3.client("lambda", region_name=REGION)
cw = boto3.client("cloudwatch", region_name=REGION)


def account_limits() -> int:
    s = lmb.get_account_settings()["AccountLimit"]
    limit = s["ConcurrentExecutions"]
    unreserved = s["UnreservedConcurrentExecutions"]
    print("=== アカウントの同時実行 ===")
    print(f"  上限            : {limit}")
    print(f"  未予約の残り枠  : {unreserved}")
    return limit


def overview() -> None:
    """全関数の予約状況と直近1時間の実績を並べる。"""
    paginator = lmb.get_paginator("list_functions")
    functions = [f for p in paginator.paginate() for f in p["Functions"]]

    print(f"\n{'関数名':<28}  {'予約':>6}  {'直近最大':>8}  {'スロットル':>10}")
    print("-" * 62)
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)

    for f in functions:
        name = f["FunctionName"]
        try:
            reserved = lmb.get_function_concurrency(
                FunctionName=name
            ).get("ReservedConcurrentExecutions", "-")
        except ClientError:
            reserved = "-"

        def metric(metric_name: str, stat: str, period: int) -> float:
            r = cw.get_metric_statistics(
                Namespace="AWS/Lambda", MetricName=metric_name,
                Dimensions=[{"Name": "FunctionName", "Value": name}],
                StartTime=start, EndTime=end,
                Period=period, Statistics=[stat],
            )
            vals = [d[stat] for d in r["Datapoints"]]
            return max(vals) if (stat == "Maximum" and vals) else sum(vals)

        max_conc = int(metric("ConcurrentExecutions", "Maximum", 300))
        throttles = int(metric("Throttles", "Sum", 3600))
        flag = " <-" if throttles > 0 else ""
        print(f"{name:<28}  {str(reserved):>6}  {max_conc:>8}  {throttles:>10}{flag}")


def set_reservation() -> None:
    print(f"\n=== {TARGET_FUNCTION} に予約 {RESERVED} を設定 ===")
    resp = lmb.put_function_concurrency(
        FunctionName=TARGET_FUNCTION,
        ReservedConcurrentExecutions=RESERVED,
    )
    print(f"  [OK] ReservedConcurrentExecutions = "
          f"{resp['ReservedConcurrentExecutions']}")
    after = lmb.get_account_settings()["AccountLimit"]
    print(f"  未予約の残り枠: {after['UnreservedConcurrentExecutions']}")


def cause_throttles() -> None:
    """非同期で一気に投げ、スロットリングを起こす。"""
    print(f"\n=== 非同期で {INVOKE_COUNT} 回 invoke ===")
    for _ in range(INVOKE_COUNT):
        lmb.invoke(
            FunctionName=TARGET_FUNCTION,
            InvocationType="Event",
            Payload=b'{"burst": true}',
        )
    print("  投げ終わり。Throttles メトリクスは反映まで数分かかる")
    print("  待っている間に別の項目を進めて、あとで overview() を見直すこと")


def clear_reservation() -> None:
    print(f"\n=== 予約を削除して元に戻す ===")
    lmb.delete_function_concurrency(FunctionName=TARGET_FUNCTION)
    print("  [OK] 予約を削除（アカウント共有プールに戻った）")
    try:
        r = lmb.get_function_concurrency(FunctionName=TARGET_FUNCTION)
        print(f"  確認: {r.get('ReservedConcurrentExecutions', '予約なし')}")
    except ClientError as e:
        print(f"  {e.response['Error']['Code']}")


def main() -> None:
    try:
        limit = account_limits()
        overview()

        if limit - RESERVED < MIN_UNRESERVED:
            print(f"\n[スキップ] アカウント上限が {limit} のため、"
                  f"予約を設定すると未予約枠が {MIN_UNRESERVED} を下回ります。")
            print("  put_function_concurrency は必ず "
                  "InvalidParameterValueException になります。")
            print("  Service Quotas から "
                  "'Concurrent executions' の引き上げを申請してください")
            print("  （申請は無料。反映まで数時間〜1営業日）。")
            print("  引き上げない場合は、予約の代わりに get_function_concurrency と")
            print("  Throttles メトリクスの読み方の確認までで止めること。")
            return

        set_reservation()
        cause_throttles()

        input("\n数分待ってから Enter を押すと予約を削除します > ")
        overview()
        clear_reservation()

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")
        print("        予約が残っていないか必ず確認すること:")
        print(f"        aws lambda get-function-concurrency "
              f"--function-name {TARGET_FUNCTION}")


if __name__ == "__main__":
    main()
