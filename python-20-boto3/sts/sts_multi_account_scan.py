"""
sts_multi_account_scan.py ― 複数アカウントを横断して同一処理を回す

管理アカウントとサブアカウントを順に見て、同じ調査処理
（ECS サービスの desired/running 乖離チェック）を実行し、結果を集約する。

  - 自分のアカウントは assume せずそのまま使う
  - 他アカウントは assume してから client を作る
  - 1 アカウントで失敗しても全体を止めず、エラーを記録して継続

--------------------------------------------------------------------
実行前に SUB_ACCOUNT_ID を置き換えること:

  aws organizations list-create-account-status \
    --query 'CreateAccountStatuses[?State==`SUCCEEDED`].[AccountName,AccountId]' \
    --output table

部分失敗の確認用に、存在しないアカウントID を1件だけ混ぜてある。
AccessDenied になるが、そこで止まらず集約レポートに記録されることを見る。
--------------------------------------------------------------------
"""
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"

# 2/28 に作ったサブアカウントの AccountId
SUB_ACCOUNT_ID = "REPLACEME000"

# Organizations が自動作成するロール名
CROSS_ACCOUNT_ROLE_NAME = "OrganizationAccountAccessRole"

# 部分失敗の題材。実在しないアカウントID（触らないこと）
BOGUS_ACCOUNT_ID = "000000000000"
# ==================================================


def build_session(account_id: str, own_account_id: str) -> boto3.Session:
    """
    対象アカウント用の Session を返す。
    自分のアカウントなら assume せず既定のクレデンシャルを使う。
    """
    if account_id == own_account_id:
        return boto3.Session(region_name=REGION)

    role_arn = f"arn:aws:iam::{account_id}:role/{CROSS_ACCOUNT_ROLE_NAME}"
    sts = boto3.client("sts", region_name=REGION)
    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="multi-account-scan",
    )["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION,
    )


def check_ecs_desired_running(session: boto3.Session) -> list[dict]:
    """
    そのアカウント内の全 ECS サービスについて desired/running の乖離を検出する。
    （各アカウントで実行したい「同一処理」の一例）
    """
    ecs = session.client("ecs")
    findings: list[dict] = []

    cluster_arns = ecs.list_clusters()["clusterArns"]
    for cluster_arn in cluster_arns:
        service_arns = ecs.list_services(cluster=cluster_arn)["serviceArns"]
        if not service_arns:
            continue
        # describe_services は最大 10 件ずつ
        for i in range(0, len(service_arns), 10):
            chunk = service_arns[i : i + 10]
            services = ecs.describe_services(
                cluster=cluster_arn, services=chunk
            )["services"]
            for svc in services:
                desired = svc["desiredCount"]
                running = svc["runningCount"]
                if desired != running:
                    findings.append(
                        {
                            "cluster": cluster_arn.split("/")[-1],
                            "service": svc["serviceName"],
                            "desired": desired,
                            "running": running,
                        }
                    )
    return findings


def main() -> None:
    if "REPLACEME" in SUB_ACCOUNT_ID:
        print("[ERROR] SUB_ACCOUNT_ID を置き換えてください")
        print("        aws organizations list-create-account-status")
        return

    own = boto3.client("sts", region_name=REGION).get_caller_identity()["Account"]
    targets = [
        {"name": "main", "account_id": own},
        {"name": "sub", "account_id": SUB_ACCOUNT_ID},
        {"name": "missing(意図的な失敗)", "account_id": BOGUS_ACCOUNT_ID},
    ]
    print(f"実行元アカウント: {own}\n")

    all_findings: dict[str, list[dict]] = {}
    scanned: dict[str, str] = {}
    errors: dict[str, str] = {}

    for acct in targets:
        name = acct["name"]
        try:
            session = build_session(acct["account_id"], own)
            findings = check_ecs_desired_running(session)
            all_findings[name] = findings
            scanned[name] = acct["account_id"]
            print(f"[OK] {name} ({acct['account_id']}): "
                  f"{len(findings)} 件の乖離を検出")
        except ClientError as e:
            # 1 アカウントの失敗で全体を止めない。ここが今日の要点
            code = e.response["Error"]["Code"]
            errors[name] = f"{code}: {e.response['Error']['Message']}"
            print(f"[ERROR] {name} ({acct['account_id']}): {code} "
                  f"→ 続行します")

    # 集約レポート
    print("\n" + "=" * 60)
    print("ECS desired/running 乖離 集約レポート")
    print("=" * 60)
    print(f"調査できた: {len(all_findings)} / {len(targets)} アカウント")

    for name, findings in all_findings.items():
        if not findings:
            print(f"\n[{name}] 乖離なし")
            continue
        print(f"\n[{name}]")
        for f in findings:
            print(
                f"  {f['cluster']}/{f['service']}: "
                f"desired={f['desired']} running={f['running']}"
            )

    if errors:
        print("\n--- 調査できなかったアカウント ---")
        for name, msg in errors.items():
            print(f"  {name}: {msg}")
        print("\n例外で全体を止めるのではなく、"
              "「調査できた範囲」と「できなかった理由」を")
        print("両方返すのが横断調査の基本形。")


if __name__ == "__main__":
    main()
