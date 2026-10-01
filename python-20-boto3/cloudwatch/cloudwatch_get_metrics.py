"""
22. CloudWatch メトリクス統計値の取得
ALB と ECS の SLI を直近1時間・5分粒度で取得する。

--------------------------------------------------------------------
実行前に置き換えること:

  terraform output -raw ecs_cluster    -> ECS_CLUSTER
  terraform output -raw ecs_service    -> ECS_SERVICE

ALB の Dimensions はスクリプト内で自動解決するので指定不要。

【重要】ALB の RequestCount にはヘルスチェックは計上されない。
2/1 に流した curl の分は直近1時間には入らないので、この日の最初に
トラフィックを流してから実行すること（流さないと空配列になり、
下の「Dimensions をわざと間違える」実験と区別がつかない）:

  for i in $(seq 1 50); do
    curl -s -o /dev/null "http://$(terraform output -raw alb_dns_name)/m$i"
  done
--------------------------------------------------------------------
"""
import boto3
from datetime import datetime, timezone, timedelta

# ====================== 設定 ======================
REGION = "ap-northeast-1"
LB_NAME = "boto3-study"       # ALB 名（name_prefix と同じ）
ECS_CLUSTER = "boto3-study"   # terraform output -raw ecs_cluster
ECS_SERVICE = "boto3-study"   # terraform output -raw ecs_service
PERIOD = 300                  # 5分粒度
LOOKBACK_HOURS = 1
# ==================================================

cw = boto3.client("cloudwatch", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)


def alb_dimensions() -> tuple[dict, dict]:
    """
    ALB / ターゲットグループの Dimensions を ARN から組み立てる。

    CloudWatch の LoadBalancer 次元は ARN そのものではなく
    'app/<名前>/<ID>' という ARN の末尾部分を使う。ここを間違えると
    エラーにはならず、ただ空配列が返る。
    """
    lb = elbv2.describe_load_balancers(Names=[LB_NAME])["LoadBalancers"][0]
    lb_dim = lb["LoadBalancerArn"].split("loadbalancer/")[1]

    tgs = elbv2.describe_target_groups(
        LoadBalancerArn=lb["LoadBalancerArn"]
    )["TargetGroups"]
    tg_dim = tgs[0]["TargetGroupArn"].split(":")[-1]

    print(f"LoadBalancer 次元 : {lb_dim}")
    print(f"TargetGroup 次元  : {tg_dim}\n")
    return (
        {"Name": "LoadBalancer", "Value": lb_dim},
        {"Name": "TargetGroup", "Value": tg_dim},
    )


def show(namespace: str, metric: str, dimensions: list[dict],
         stats: list[str], unit_label: str) -> int:
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=LOOKBACK_HOURS)

    resp = cw.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric,
        Dimensions=dimensions,
        StartTime=start,
        EndTime=end,
        Period=PERIOD,
        Statistics=stats,
    )
    points = sorted(resp["Datapoints"], key=lambda x: x["Timestamp"])
    print(f"--- {namespace} / {metric} ({unit_label}) ---")
    if not points:
        print("  データポイントなし")
        print()
        return 0
    for d in points:
        vals = "  ".join(f"{s.lower()}={d[s]:.2f}" for s in stats if s in d)
        print(f"  {d['Timestamp'].strftime('%H:%M')}  {vals}")
    print()
    return len(points)


def main() -> None:
    lb_dim, tg_dim = alb_dimensions()

    # --- ALB ---------------------------------------------------------
    show("AWS/ApplicationELB", "RequestCount", [lb_dim], ["Sum"], "件")
    show("AWS/ApplicationELB", "TargetResponseTime", [lb_dim],
         ["Average", "Maximum"], "秒")
    show("AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", [lb_dim],
         ["Sum"], "件")
    show("AWS/ApplicationELB", "HealthyHostCount", [tg_dim, lb_dim],
         ["Average", "Minimum"], "台")

    # --- ECS ---------------------------------------------------------
    ecs_dims = [
        {"Name": "ClusterName", "Value": ECS_CLUSTER},
        {"Name": "ServiceName", "Value": ECS_SERVICE},
    ]
    show("AWS/ECS", "CPUUtilization", ecs_dims, ["Average", "Maximum"], "%")
    show("AWS/ECS", "MemoryUtilization", ecs_dims, ["Average", "Maximum"], "%")

    # --- Dimensions をわざと1文字間違える ------------------------------
    # 存在しない次元を指定しても ValidationError にはならず、単に
    # Datapoints が空で返る。「取れない」と「無い」が区別できない
    # CloudWatch API の一番の落とし穴。
    print("=== Dimensions を1文字間違えた場合 ===")
    broken = [
        {"Name": "ClusterName", "Value": ECS_CLUSTER},
        {"Name": "ServiceName", "Value": ECS_SERVICE + "x"},
    ]
    n = show("AWS/ECS", "CPUUtilization", broken, ["Average"], "%")
    print(f"→ エラーではなく空配列（{n} 件）が返る。"
          "存在しない次元でも API は成功扱いになる\n")


if __name__ == "__main__":
    main()
