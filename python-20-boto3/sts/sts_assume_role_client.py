"""
sts_assume_role_client.py ― AssumeRole で別アカウントの client を生成する

運用（ops）アカウントから、対象アカウントのクロスアカウントロールを
assume して、その一時クレデンシャルで任意サービスの client を作る基本形。
DevOps Agent が dev / IDaaS / JWL を横断する際のベースになるパターン。
"""
import boto3
from botocore.exceptions import ClientError


def assume_role(
    role_arn: str,
    session_name: str,
    external_id: str | None = None,
    duration_seconds: int = 3600,
    region: str = "ap-northeast-1",
) -> boto3.Session:
    """
    指定ロールを assume し、一時クレデンシャルを持つ boto3.Session を返す。

    :param role_arn: assume する対象ロールの ARN
                     例: arn:aws:iam::098891529997:role/dev-ope-...-agentspace01
    :param session_name: CloudTrail に記録されるセッション名（追跡用に意味のある名前を）
    :param external_id: 信頼ポリシーで ExternalId が要求される場合に指定
    :param duration_seconds: 一時クレデンシャルの有効秒数（ロール側の最大値以内）
    :return: assume 済みクレデンシャルを持つ Session
    """
    sts = boto3.client("sts", region_name=region)

    assume_args = {
        "RoleArn": role_arn,
        "RoleSessionName": session_name,
        "DurationSeconds": duration_seconds,
    }
    if external_id:
        assume_args["ExternalId"] = external_id

    resp = sts.assume_role(**assume_args)
    creds = resp["Credentials"]

    # 一時クレデンシャルから新しい Session を組み立てる
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )
    return session


def whoami(session: boto3.Session) -> dict:
    """assume 後の実効アイデンティティを確認する（切り分けに便利）。"""
    ident = session.client("sts").get_caller_identity()
    return {"Account": ident["Account"], "Arn": ident["Arn"]}


def main() -> None:
    # 例: ops アカウントから dev アカウントのロールを assume
    dev_role_arn = "arn:aws:iam::098891529997:role/cross-account-readonly-role"

    try:
        # 1) assume 前（＝呼び出し元）の identity を確認
        base = boto3.client("sts").get_caller_identity()
        print(f"[BEFORE] {base['Account']}  {base['Arn']}")

        # 2) 別アカウントのロールを assume
        session = assume_role(
            role_arn=dev_role_arn,
            session_name="devops-agent-investigation",
        )

        # 3) assume 後の identity を確認（別アカウントになっていること）
        after = whoami(session)
        print(f"[AFTER ] {after['Account']}  {after['Arn']}")

        # 4) その session で対象アカウントのリソースを操作
        s3 = session.client("s3")
        buckets = s3.list_buckets()["Buckets"]
        print(f"\n[dev アカウントの S3 バケット] {len(buckets)} 件")
        for b in buckets[:10]:
            print(f"  - {b['Name']}")

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "AccessDenied":
            print(f"[ERROR] AssumeRole 拒否。信頼ポリシー/権限を確認: {e}")
        else:
            print(f"[ERROR] {code}: {e}")


if __name__ == "__main__":
    main()
