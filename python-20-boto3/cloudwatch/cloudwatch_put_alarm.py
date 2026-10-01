"""
24. CloudWatch アラームの作成・更新と状態遷移の観測

ALB の RequestCount にアラームを置き、
INSUFFICIENT_DATA -> OK -> ALARM の3状態をすべて観測する。

--------------------------------------------------------------------
実行前に置き換えること:

  terraform output -raw sns_topic_arn    -> SNS_TOPIC_ARN

SNS の購読確認メール（件名: AWS Notification - Subscription Confirmation）
のリンクを踏んでいないと、ALARM になってもメールは届かない。

【重要1】閾値を「1リクエスト以上」にすると OK 状態は観測できない。
ALB は、リクエストが1件も無い期間には RequestCount のデータポイントを
そもそも発行しない（ヘルスチェックは RequestCount に計上されない）。
OK になるには「データポイントが存在し、かつ閾値未満」という期間が要るが、
閾値1ではその条件を満たす値（Sum = 0）が発行されないため、状態は
  INSUFFICIENT_DATA -> ALARM
としか動かない。そこで閾値を 100 に置き、
  フェーズ1: 無通信            -> データなし    -> INSUFFICIENT_DATA
  フェーズ2: 1分間に 10 リクエスト -> Sum=10  (<100) -> OK
  フェーズ3: 一気に 300 リクエスト -> Sum>=100       -> ALARM
の3段階でトラフィックを作り、3状態すべてを通す。

【注意】このスクリプトを流す前の5分間は ALB にトラフィックを流さないこと。
put_metric_alarm 直後の状態は必ず INSUFFICIENT_DATA になるが、直前の
トラフィックが評価期間に残っていると CloudWatch がすぐ OK / ALARM に
動かしてしまい、フェーズ2・3 の境目が見えにくくなる。
（フェーズが時間内に目的の状態に届かなくても、次のフェーズへ進むだけで
  スクリプトは止まらない。）

【重要2】TreatMissingData の選び方でこの演習は成立したりしなくなる。
  'missing'      … 欠測を無視し、直前の状態を保持する  -> 遷移を追うならこれ
  'breaching'    … 欠測を閾値超え扱い -> いきなり ALARM に飛ぶ
  'notBreaching' … 欠測を正常扱い     -> 常に OK に寄る
--------------------------------------------------------------------
"""
import time
import urllib.error
import urllib.request
import boto3
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
LB_NAME = "boto3-study"

# terraform output -raw sns_topic_arn
SNS_TOPIC_ARN = "arn:aws:sns:ap-northeast-1:REPLACEME:boto3-study"

ALARM_NAME = "boto3-study-alb-requestcount"
PERIOD = 60             # 1分。短いほど遷移が早く見える
EVALUATION_PERIODS = 1
THRESHOLD = 100.0       # 1分間に100リクエスト以上で ALARM

LIGHT_REQUESTS = 10     # フェーズ2（OK を作る）
BURST_REQUESTS = 300    # フェーズ3（ALARM を作る）
                        # 300 にしているのは、送信が2つの評価期間にまたがっても
                        # どちらかが 100 を超えるようにするため

POLL_INTERVAL = 20      # 状態確認の間隔（秒）
PHASE_TIMEOUT = 600     # 1フェーズあたりの待ち上限（秒）
# ==================================================

cw = boto3.client("cloudwatch", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)


def resolve_alb() -> tuple[dict, str]:
    """
    CloudWatch の LoadBalancer 次元（ARN 末尾の app/<名前>/<ID>）と
    トラフィック生成用の DNS 名を取得する。
    """
    lb = elbv2.describe_load_balancers(Names=[LB_NAME])["LoadBalancers"][0]
    dim_value = lb["LoadBalancerArn"].split("loadbalancer/")[1]
    print(f"LoadBalancer 次元: {dim_value}")
    print(f"ALB DNS 名       : {lb['DNSName']}")
    return {"Name": "LoadBalancer", "Value": dim_value}, lb["DNSName"]


def put_alarm(dimension: dict) -> None:
    cw.put_metric_alarm(
        AlarmName=ALARM_NAME,
        AlarmDescription=f"ALB のリクエストが1分間に {int(THRESHOLD)} 件以上で ALARM",
        Namespace="AWS/ApplicationELB",
        MetricName="RequestCount",
        Dimensions=[dimension],
        Statistic="Sum",
        Period=PERIOD,
        EvaluationPeriods=EVALUATION_PERIODS,
        Threshold=THRESHOLD,
        ComparisonOperator="GreaterThanOrEqualToThreshold",
        AlarmActions=[SNS_TOPIC_ARN],
        OKActions=[SNS_TOPIC_ARN],
        # 欠測は無視して直前の状態を保持する。
        # 'breaching' だと最初から ALARM に飛び、遷移が観測できない
        TreatMissingData="missing",
    )
    print(f"[OK] アラーム作成/更新: {ALARM_NAME}"
          f"（{PERIOD}秒 × {EVALUATION_PERIODS}回, 閾値 {int(THRESHOLD)}）")


def current_state() -> tuple[str, str]:
    a = cw.describe_alarms(AlarmNames=[ALARM_NAME])["MetricAlarms"][0]
    return a["StateValue"], a.get("StateReason", "")


def send_requests(dns_name: str, count: int) -> None:
    """ALB に HTTP リクエストを投げて RequestCount を作る。"""
    url_base = f"http://{dns_name}/"
    ok = 0
    t0 = time.time()
    for i in range(count):
        try:
            with urllib.request.urlopen(f"{url_base}w{i}", timeout=5):
                ok += 1
        except urllib.error.HTTPError:
            ok += 1           # 404 でも RequestCount には計上される
        except Exception:
            pass
    print(f"  {count} 件送信（成功 {ok}） {time.time() - t0:.1f} 秒")


def wait_for(target: str, label: str) -> bool:
    """
    目的の状態になるまで待つ。状態が変わったときだけ1行出す。
    メトリクスの配信に1〜3分、評価にさらに1分かかるので気長に待つ。
    """
    print(f"\n--- {label}: {target} になるまで待つ（最大 {PHASE_TIMEOUT // 60} 分） ---")
    deadline = time.time() + PHASE_TIMEOUT
    last = None
    while time.time() < deadline:
        state, reason = current_state()
        if state != last:
            stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
            print(f"  [{stamp}] {last or '(開始)'} -> {state}")
            print(f"            {reason}")
            last = state
        if state == target:
            return True
        time.sleep(POLL_INTERVAL)
    print(f"  [タイムアウト] {target} に到達しませんでした（現在 {last}）")
    return False


def show_history() -> None:
    print("\n=== 状態遷移の履歴（describe_alarm_history） ===")
    resp = cw.describe_alarm_history(
        AlarmName=ALARM_NAME,
        HistoryItemType="StateUpdate",
        StartDate=datetime.now(timezone.utc) - timedelta(hours=2),
        EndDate=datetime.now(timezone.utc),
        MaxRecords=20,
    )
    items = sorted(resp["AlarmHistoryItems"], key=lambda x: x["Timestamp"])
    if not items:
        print("  履歴なし（まだ一度も遷移していない）")
        return
    for h in items:
        print(f"  {h['Timestamp'].strftime('%H:%M:%S')}  {h['HistorySummary']}")


def main() -> None:
    if "REPLACEME" in SNS_TOPIC_ARN:
        print("[ERROR] SNS_TOPIC_ARN を置き換えてください")
        print("        terraform output -raw sns_topic_arn")
        return

    try:
        dimension, dns_name = resolve_alb()
        put_alarm(dimension)

        state, reason = current_state()
        print(f"\n作成直後の状態: {state}")
        print(f"  {reason}")

        # --- フェーズ1: 無通信 -> INSUFFICIENT_DATA --------------------
        # 直前まで curl を流していた場合は少し待つ必要がある
        wait_for("INSUFFICIENT_DATA", "フェーズ1（無通信）")

        # --- フェーズ2: 少量のトラフィック -> OK -----------------------
        print(f"\n--- フェーズ2: {LIGHT_REQUESTS} 件送信（閾値 {int(THRESHOLD)} 未満） ---")
        send_requests(dns_name, LIGHT_REQUESTS)
        wait_for("OK", "フェーズ2（少量）")

        # --- フェーズ3: バースト -> ALARM ------------------------------
        print(f"\n--- フェーズ3: {BURST_REQUESTS} 件を一気に送信 ---")
        send_requests(dns_name, BURST_REQUESTS)
        wait_for("ALARM", "フェーズ3（バースト）")

        show_history()

        print("\n3/14 の破棄チェックリストで削除すること:")
        print(f"  aws cloudwatch delete-alarms --alarm-names {ALARM_NAME}")

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")


if __name__ == "__main__":
    main()
