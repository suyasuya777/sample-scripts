"""
sts_credential_cache.py ― 一時クレデンシャルのキャッシュと自動更新

assume_role のたびに STS を叩くとレイテンシと API コールが増えるため、
取得した一時クレデンシャルを期限まで再利用し、期限が近づいたら
自動で再取得するキャッシュを実装する。

方式は 2 つ紹介する:
  A) 手動キャッシュ: 仕組みが分かる素朴な実装
  B) botocore の自動更新: RefreshableCredentials を使う実務的な実装
     （client を作り直さずに、期限切れ直前で裏側で自動リフレッシュされる）
"""
from datetime import datetime, timezone, timedelta

import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
from botocore.exceptions import ClientError

REGION = "ap-northeast-1"
# 期限のどれくらい前に再取得するか（安全マージン）
_REFRESH_MARGIN = timedelta(minutes=5)


# ============================================================
# A) 手動キャッシュ（仕組み理解用）
# ============================================================
class SimpleAssumeRoleCache:
    """1 ロール分の一時クレデンシャルをメモリにキャッシュする素朴な実装。"""

    def __init__(self, role_arn: str, session_name: str):
        self.role_arn = role_arn
        self.session_name = session_name
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
        )["Credentials"]
        self._creds = {
            "aws_access_key_id": resp["AccessKeyId"],
            "aws_secret_access_key": resp["SecretAccessKey"],
            "aws_session_token": resp["SessionToken"],
        }
        self._expiry = resp["Expiration"]  # tz-aware datetime
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
            RoleArn=role_arn, RoleSessionName=session_name
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
    role_arn = "arn:aws:iam::098891529997:role/devops-agent-investigation-role"

    try:
        # --- A) 手動キャッシュのデモ ---
        print("=== A) 手動キャッシュ ===")
        cache = SimpleAssumeRoleCache(role_arn, "cache-demo")
        s1 = cache.session()  # 1 回目 → ミス
        _ = s1.client("sts").get_caller_identity()
        s2 = cache.session()  # 2 回目 → ヒット（再利用）
        _ = s2.client("sts").get_caller_identity()

        # --- B) 自動更新のデモ ---
        print("\n=== B) botocore 自動更新 ===")
        session = make_refreshable_session(role_arn, "auto-refresh-demo")
        ident = session.client("sts").get_caller_identity()
        print(f"[OK] {ident['Account']}  {ident['Arn']}")
        # このあと長時間ループで使い続けても、期限接近時に自動更新される

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")


if __name__ == "__main__":
    main()
