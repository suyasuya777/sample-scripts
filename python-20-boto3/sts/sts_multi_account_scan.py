"""
sts_multi_account_scan.py ― 複数アカウントを横断して同一処理を回す

複数の対象アカウントを順に assume し、それぞれで同じ調査処理
（例: ECS サービスの desired/running 乖離チェック）を実行して結果を集約する。
DevOps Agent の 4 アカウント（dev / ops / IDaaS / JWL）横断調査の雛形。

  - アカウントごとに assume → client 生成 → 処理 → 結果集約
  - 1 アカウントで失敗しても全体を止めず、エラーを記録して継続
"""
import boto3
from botocore.exceptions import ClientError

# 対象アカウント定義（実環境のロール名・アカウント ID に合わせる）
TARGET_ACCOUNTS = [
    {"name": "dev", "account_id": "098891529997"},
    {"name": "ops", "account_id": "545677447333"},
    {"name": "idaas", "account_id": "585082902798"},
    {"name": "jwl", "account_id": "344256453631"},
]
# 各アカウントに用意した共通ロール名（クロスアカウント調査用）
CROSS_ACCOUNT_ROLE_NAME = "devops-agent-investigation-role"
REGION = "ap-northeast-1"


def build_session(account_id: str, role_name: str) -> boto3.Session:
    """account_id と role_name から assume して Session を返す。"""
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
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
    all_findings: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}

    for acct in TARGET_ACCOUNTS:
        name = acct["name"]
        try:
            session = build_session(
                acct["account_id"], CROSS_ACCOUNT_ROLE_NAME
            )
            findings = check_ecs_desired_running(session)
            all_findings[name] = findings
            print(f"[OK] {name}: {len(findings)} 件の乖離を検出")
        except ClientError as e:
            # 1 アカウントの失敗で全体を止めない
            code = e.response["Error"]["Code"]
            errors[name] = f"{code}: {e.response['Error']['Message']}"
            print(f"[ERROR] {name}: {code}")

    # 集約レポート
    print("\n" + "=" * 60)
    print("ECS desired/running 乖離 集約レポート")
    print("=" * 60)
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


if __name__ == "__main__":
    main()
