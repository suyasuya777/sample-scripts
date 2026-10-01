"""
sts_assume_role_client.py ― AssumeRole で別アカウントの client を生成する

管理アカウントから、Organizations で作った2つ目のアカウント（サブ）の
ロールを assume して、その一時クレデンシャルで任意サービスの client を作る
基本形。実務でのクロスアカウント調査のベースになるパターン。

--------------------------------------------------------------------
実行前に SUB_ACCOUNT_ID を置き換えること:

  aws organizations list-create-account-status \
    --query 'CreateAccountStatuses[?State==`SUCCEEDED`].[AccountName,AccountId]' \
    --output table

ロールは Organizations が新規アカウントに自動作成する
OrganizationAccountAccessRole を使う。管理アカウントからは
追加設定なしで assume できる（信頼ポリシーに管理アカウントが入っている）。
--------------------------------------------------------------------
"""
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"

# 2/28 に作ったサブアカウントの AccountId（12桁）
SUB_ACCOUNT_ID = "REPLACEME000"

# Organizations が自動作成するロール名。自前で作ったものではない
ROLE_NAME = "OrganizationAccountAccessRole"
# ==================================================


def assume_role(
    role_arn: str,
    session_name: str,
    external_id: str | None = None,
    duration_seconds: int = 3600,
    region: str = REGION,
) -> boto3.Session:
    """
    指定ロールを assume し、一時クレデンシャルを持つ boto3.Session を返す。

    :param role_arn: assume する対象ロールの ARN
    :param session_name: CloudTrail に記録されるセッション名。
                         誰が・何のために叩いたかを後から追えるよう、
                         意味のある名前を付ける（ここが今日の要点）
    :param external_id: 信頼ポリシーで ExternalId が要求される場合に指定。
                        第三者に権限を渡すときの「混乱した代理人」対策で、
                        Organizations 内のロールでは通常不要
    :param duration_seconds: 一時クレデンシャルの有効秒数。
                             900（15分）〜 ロール側の MaxSessionDuration
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
    print(f"  [assume] {session_name}  有効期限 {creds['Expiration']:%H:%M:%S}")

    # 一時クレデンシャルから新しい Session を組み立てる
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )


def whoami(session: boto3.Session) -> dict:
    """assume 後の実効アイデンティティを確認する（切り分けに便利）。"""
    ident = session.client("sts").get_caller_identity()
    return {"Account": ident["Account"], "Arn": ident["Arn"]}


def main() -> None:
    if "REPLACEME" in SUB_ACCOUNT_ID:
        print("[ERROR] SUB_ACCOUNT_ID を置き換えてください")
        print("        aws organizations list-create-account-status")
        return

    role_arn = f"arn:aws:iam::{SUB_ACCOUNT_ID}:role/{ROLE_NAME}"

    try:
        # 1) assume 前（＝呼び出し元＝管理アカウント）の identity
        base = boto3.client("sts", region_name=REGION).get_caller_identity()
        print(f"[BEFORE] {base['Account']}  {base['Arn']}")

        # 2) サブアカウントのロールを assume
        print("\n=== assume ===")
        session = assume_role(
            role_arn=role_arn,
            session_name="boto3-study-investigation",
        )

        # 3) assume 後の identity（アカウントIDが変わっていること）
        after = whoami(session)
        print(f"[AFTER ] {after['Account']}  {after['Arn']}")
        assert after["Account"] == SUB_ACCOUNT_ID, "アカウントが切り替わっていない"
        print("→ Arn が assumed-role/OrganizationAccountAccessRole/<セッション名> "
              "になっている点に注目")

        # 4) その session で対象アカウントのリソースを操作
        s3 = session.client("s3")
        buckets = s3.list_buckets()["Buckets"]
        print(f"\n[サブアカウントの S3 バケット] {len(buckets)} 件"
              "（作ったばかりなので 0 件が正しい）")
        for b in buckets[:10]:
            print(f"  - {b['Name']}")

        # 5) RoleSessionName を変えて2回叩き、CloudTrail で区別できることを確認
        print("\n=== RoleSessionName を変えて2回 assume ===")
        for name in ("session-alpha", "session-beta"):
            s = assume_role(role_arn=role_arn, session_name=name)
            print(f"  {name} -> {whoami(s)['Arn']}")
        print("\nCloudTrail（サブアカウント側）で AssumeRole イベントを検索し、")
        print("userIdentity.arn の末尾で2つのセッションが区別できることを確認する:")
        print("  aws cloudtrail lookup-events \\")
        print("    --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole \\")
        print("    --query 'Events[].[EventTime,Username]' --output table")

        # 6) DurationSeconds の下限・上限
        print("\n=== DurationSeconds ===")
        print("  下限 900 秒（15分）。上限はロールの MaxSessionDuration（既定 3600）")
        try:
            assume_role(role_arn, "too-long", duration_seconds=7200)
        except ClientError as e:
            print(f"  [OK] 上限超えは拒否される: {e.response['Error']['Code']}")

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "AccessDenied":
            print(f"[ERROR] AssumeRole 拒否。次を確認:")
            print(f"        - SUB_ACCOUNT_ID が正しいか")
            print(f"        - そのアカウントが Organizations 経由で作られたか")
            print(f"          （手動作成のアカウントには {ROLE_NAME} が無い）")
            print(f"        {e}")
        else:
            print(f"[ERROR] {code}: {e}")


if __name__ == "__main__":
    main()
