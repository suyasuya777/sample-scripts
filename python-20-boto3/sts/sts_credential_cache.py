"""
sts_credential_cache.py ― 一時クレデンシャルのキャッシュと自動更新

assume_role のたびに STS を叩くとレイテンシと API コールが増えるため、
取得した一時クレデンシャルを期限まで再利用し、期限が近づいたら
自動で再取得するキャッシュを実装する。

方式は 2 つ紹介する:
  A) 手動キャッシュ: 仕組みが分かる素朴な実装
  B) botocore の自動更新: RefreshableCredentials を使う実務的な実装
     （client を作り直さずに、期限切れ直前で裏側で自動リフレッシュされる）

--------------------------------------------------------------------
実行前に SUB_ACCOUNT_ID を置き換えること:

  aws organizations list-create-account-status \
    --query 'CreateAccountStatuses[?State==`SUCCEEDED`].[AccountName,AccountId]' \
    --output table

DURATION_SECONDS = 900 は AssumeRole の下限（15分）。
安全マージン _REFRESH_MARGIN を 5 分にしてあるので、
「取得から10分でキャッシュが無効になる」という短いサイクルを
その場で観測できる。
--------------------------------------------------------------------
"""
import time
from datetime import datetime, timezone, timedelta

import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"

# 2/28 に作ったサブアカウントの AccountId
SUB_ACCOUNT_ID = "REPLACEME000"

# Organizations が自動作成するロール名
ROLE_NAME = "OrganizationAccountAccessRole"

# AssumeRole の最小値。下限は 900 秒（15分）
DURATION_SECONDS = 900
# ==================================================

# 期限のどれくらい前に再取得するか（安全マージン）
_REFRESH_MARGIN = timedelta(minutes=5)


# ============================================================
# A) 手動キャッシュ（仕組み理解用）
# ============================================================
class SimpleAssumeRoleCache:
    """1 ロール分の一時クレデンシャルをメモリにキャッシュする素朴な実装。"""

    def __init__(
        self,
        role_arn: str,
        session_name: str,
        duration_seconds: int = DURATION_SECONDS,
    ):
        self.role_arn = role_arn
        self.session_name = session_name
        self.duration_seconds = duration_seconds
        self._creds: dict | None = None
        self._expiry: datetime | None = None
        self._sts = boto3.client("sts", region_name=REGION)

    def _is_valid(self) -> bool:
        if self._creds is None or self._expiry is None:
            return False
        # 期限までマージンを残して有効かどうか
        return datetime.now(timezone.utc) < self._expiry - _REFRESH_MARGIN

    def get_credentials(self) -> dict:
        """有効なら再利用、期限が近ければ再取得してクレデンシャルを返す。"""
        if self._is_valid():
            print("[CACHE] ヒット（再利用）")
            return self._creds

        print("[CACHE] ミス → assume_role で再取得")
        resp = self._sts.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=self.duration_seconds,
        )["Credentials"]
        self._creds = {
            "aws_access_key_id": resp["AccessKeyId"],
            "aws_secret_access_key": resp["SecretAccessKey"],
            "aws_session_token": resp["SessionToken"],
        }
        self._expiry = resp["Expiration"]  # tz-aware datetime
        remain = self._expiry - datetime.now(timezone.utc)
        print(f"        有効期限 {self._expiry:%H:%M:%S}"
              f"（残り {remain.total_seconds():.0f} 秒 / "
              f"マージン {_REFRESH_MARGIN.total_seconds():.0f} 秒）")
        return self._creds

    def session(self) -> boto3.Session:
        return boto3.Session(region_name=REGION, **self.get_credentials())


# ============================================================
# B) botocore の自動更新（実務向け）
# ============================================================
def make_refreshable_session(
    role_arn: str, session_name: str
) -> boto3.Session:
    """
    RefreshableCredentials を使い、期限切れ直前に裏側で自動 assume し直す
    Session を返す。client を作り直す必要がなく、長時間バッチに向く。
    """
    sts = boto3.client("sts", region_name=REGION)

    def _refresh() -> dict:
        # botocore が期限接近時に自動で呼ぶコールバック
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            DurationSeconds=DURATION_SECONDS,
        )["Credentials"]
        print("[AUTO] クレデンシャルを自動リフレッシュ")
        return {
            "access_key": resp["AccessKeyId"],
            "secret_key": resp["SecretAccessKey"],
            "token": resp["SessionToken"],
            # ISO8601 文字列で渡す必要がある
            "expiry_time": resp["Expiration"].isoformat(),
        }

    refreshable = RefreshableCredentials.create_from_metadata(
        metadata=_refresh(),
        refresh_using=_refresh,
        method="sts-assume-role",
    )

    botocore_session = get_session()
    botocore_session._credentials = refreshable
    botocore_session.set_config_variable("region", REGION)
    return boto3.Session(botocore_session=botocore_session)


def main() -> None:
    if "REPLACEME" in SUB_ACCOUNT_ID:
        print("[ERROR] SUB_ACCOUNT_ID を置き換えてください")
        print("        aws organizations list-create-account-status")
        return

    role_arn = f"arn:aws:iam::{SUB_ACCOUNT_ID}:role/{ROLE_NAME}"

    try:
        # --- A) 手動キャッシュのデモ -----------------------------------
        print(f"=== A) 手動キャッシュ（DurationSeconds={DURATION_SECONDS}） ===")
        cache = SimpleAssumeRoleCache(role_arn, "cache-demo")

        s1 = cache.session()                      # 1 回目 → ミス
        print(f"  {s1.client('sts').get_caller_identity()['Arn']}")

        s2 = cache.session()                      # 2 回目 → ヒット（再利用）
        print(f"  {s2.client('sts').get_caller_identity()['Arn']}")

        # --- 期限切れ前後の挙動 ----------------------------------------
        # 900 秒の期限に対しマージン 5 分なので、取得から 10 分経つと
        # キャッシュは無効と判定され、次の session() で再取得が走る。
        print("\n=== 期限切れ前後の挙動 ===")
        print(f"  残り時間は最大でも {DURATION_SECONDS} 秒。")
        print("  マージンを 20 分（=1200秒）に広げると、取得直後でも")
        print("  「期限が近い」と判定され、必ず再取得が走る")
        globals()["_REFRESH_MARGIN"] = timedelta(minutes=20)
        s3 = cache.session()                      # → ミスになる
        print(f"  {s3.client('sts').get_caller_identity()['Arn']}")
        globals()["_REFRESH_MARGIN"] = timedelta(minutes=5)
        print("  → キャッシュの有効判定は「残り時間 > マージン」だけで決まる。")
        print("    15分クレデンシャルに5分マージンなら、実質10分で作り直される")

        # --- 下限未満は拒否される --------------------------------------
        print("\n=== DurationSeconds の下限 ===")
        try:
            boto3.client("sts", region_name=REGION).assume_role(
                RoleArn=role_arn,
                RoleSessionName="too-short",
                DurationSeconds=600,   # 900 未満
            )
            print("  [?] 想定外: 通ってしまいました")
        except ClientError as e:
            print(f"  [OK] 900 未満は拒否される: {e.response['Error']['Code']}")

        # --- B) 自動更新のデモ -----------------------------------------
        print("\n=== B) botocore 自動更新（RefreshableCredentials） ===")
        session = make_refreshable_session(role_arn, "auto-refresh-demo")
        client = session.client("sts")
        ident = client.get_caller_identity()
        print(f"[OK] {ident['Account']}  {ident['Arn']}")
        print("  同じ client のまま繰り返し呼んでも、期限接近時に")
        print("  裏で自動リフレッシュされる（[AUTO] の行が出る）")
        for i in range(3):
            time.sleep(2)
            client.get_caller_identity()
            print(f"  呼び出し {i + 1} 回目 OK（client は作り直していない）")

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")


if __name__ == "__main__":
    main()
