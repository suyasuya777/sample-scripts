"""
25. CloudWatch ダッシュボードのJSON取得・更新
ALB と ECS のウィジェットを持つダッシュボードをコードで組み立てる。

--------------------------------------------------------------------
実行前に置き換えること:

  terraform output -raw ecs_cluster    -> ECS_CLUSTER
  terraform output -raw ecs_service    -> ECS_SERVICE

ALB の次元は自動解決する。

ダッシュボードの本体は「JSON 文字列」で、put_dashboard には dict では
なく json.dumps() した文字列を渡す。ここが他の API と違う点。
--------------------------------------------------------------------
"""
import json
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
LB_NAME = "boto3-study"
ECS_CLUSTER = "boto3-study"   # terraform output -raw ecs_cluster
ECS_SERVICE = "boto3-study"   # terraform output -raw ecs_service
DASHBOARD_NAME = "boto3-study"
# ==================================================

cw = boto3.client("cloudwatch", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)


def alb_dimensions() -> tuple[str, str]:
    lb = elbv2.describe_load_balancers(Names=[LB_NAME])["LoadBalancers"][0]
    lb_dim = lb["LoadBalancerArn"].split("loadbalancer/")[1]
    tg = elbv2.describe_target_groups(
        LoadBalancerArn=lb["LoadBalancerArn"]
    )["TargetGroups"][0]
    tg_dim = tg["TargetGroupArn"].split(":")[-1]
    return lb_dim, tg_dim


def metric_widget(title, x, y, metrics, stat="Average", period=300,
                  width=12, height=6) -> dict:
    return {
        "type": "metric",
        "x": x, "y": y, "width": width, "height": height,
        "properties": {
            "title": title,
            "metrics": metrics,
            "period": period,
            "stat": stat,
            "region": REGION,
            "view": "timeSeries",
        },
    }


def build_body(lb_dim: str, tg_dim: str) -> dict:
    alb = "AWS/ApplicationELB"
    return {
        "widgets": [
            metric_widget(
                "ALB リクエスト数", 0, 0,
                [[alb, "RequestCount", "LoadBalancer", lb_dim]],
                stat="Sum", period=60,
            ),
            metric_widget(
                "ALB レスポンスタイム / 5xx", 12, 0,
                [
                    [alb, "TargetResponseTime", "LoadBalancer", lb_dim],
                    [alb, "HTTPCode_ELB_5XX_Count", "LoadBalancer", lb_dim,
                     {"stat": "Sum", "yAxis": "right"}],
                ],
                period=60,
            ),
            metric_widget(
                "ターゲット healthy / unhealthy", 0, 6,
                [
                    [alb, "HealthyHostCount", "TargetGroup", tg_dim,
                     "LoadBalancer", lb_dim],
                    [alb, "UnHealthyHostCount", "TargetGroup", tg_dim,
                     "LoadBalancer", lb_dim],
                ],
                period=60,
            ),
            metric_widget(
                "ECS CPU / メモリ", 12, 6,
                [
                    ["AWS/ECS", "CPUUtilization",
                     "ClusterName", ECS_CLUSTER, "ServiceName", ECS_SERVICE],
                    ["AWS/ECS", "MemoryUtilization",
                     "ClusterName", ECS_CLUSTER, "ServiceName", ECS_SERVICE],
                ],
            ),
        ]
    }


def main() -> None:
    try:
        # 1) 既存ダッシュボードの取得（バックアップ・差分管理の入口）
        try:
            resp = cw.get_dashboard(DashboardName=DASHBOARD_NAME)
            existing = json.loads(resp["DashboardBody"])
            print(f"[取得] 既存ダッシュボード: {DASHBOARD_NAME}")
            print(f"       ウィジェット数: {len(existing.get('widgets', []))}")
        except cw.exceptions.DashboardNotFoundError:
            print("[取得] 未作成なので新規に組み立てます")

        # 2) ALB の次元を解決して本体を組み立て
        lb_dim, tg_dim = alb_dimensions()
        print(f"LoadBalancer 次元: {lb_dim}")
        print(f"TargetGroup 次元 : {tg_dim}")
        body = build_body(lb_dim, tg_dim)

        # 3) put_dashboard は「JSON 文字列」を渡す
        result = cw.put_dashboard(
            DashboardName=DASHBOARD_NAME,
            DashboardBody=json.dumps(body),
        )
        warnings = result.get("DashboardValidationMessages", [])
        if warnings:
            print("[警告] 検証メッセージ:")
            for w in warnings:
                print(f"  {w.get('DataPath')}: {w.get('Message')}")
        print(f"[OK] ダッシュボード更新: {DASHBOARD_NAME}"
              f"（ウィジェット {len(body['widgets'])} 個）")
        print("マネジメントコンソール > CloudWatch > ダッシュボード で表示を確認")

        # 4) 確認後に削除
        input("\n確認が終わったら Enter で削除します > ")
        cw.delete_dashboards(DashboardNames=[DASHBOARD_NAME])
        print(f"[OK] 削除: {DASHBOARD_NAME}")

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")


if __name__ == "__main__":
    main()
