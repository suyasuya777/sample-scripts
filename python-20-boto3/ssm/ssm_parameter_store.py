"""
42. SSM Parameter Store の読み書き

セットB が作った /boto3-study/app/ 配下のパラメータを対象にする。
新しいパスを勝手に作らないので、Terraform の管理外リソースが残らない。

対象（set_b.tf で作成済み）:
  /boto3-study/app/db-host      String
  /boto3-study/app/db-user      String
  /boto3-study/app/db-password  SecureString

--------------------------------------------------------------------
このスクリプトで確認すること:
  1. get_parameters_by_path の WithDecryption 有無で SecureString の
     見え方がどう変わるか
  2. Overwrite を付けずに既存名へ put_parameter すると
     ParameterAlreadyExists になること
  3. Overwrite=True なら通り、Version が増えること

【注意】3 で値を書き換えると Terraform の状態と食い違います
（aws_ssm_parameter に ignore_changes は入っていません）。
このスクリプトは最後に元の値へ戻します。戻さずに終えた場合は、
次の terraform apply が元の値に戻すだけなので実害はありません。
--------------------------------------------------------------------
"""
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"
PREFIX = "/boto3-study/app/"     # name_prefix に合わせる
WRITE_TARGET = PREFIX + "db-host"  # 書き込み演習の対象（String のほう）
# ==================================================

ssm = boto3.client("ssm", region_name=REGION)


def dump_path(with_decryption: bool) -> None:
    label = "WithDecryption=True" if with_decryption else "WithDecryption=False"
    print(f"\n--- get_parameters_by_path（{label}） ---")
    paginator = ssm.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path=PREFIX, WithDecryption=with_decryption):
        for p in page["Parameters"]:
            print(f"  {p['Name']:34} [{p['Type']:12}] v{p['Version']}  = {p['Value']}")


def demo_overwrite() -> None:
    """Overwrite なし -> あり の差を実測する。"""
    before = ssm.get_parameter(Name=WRITE_TARGET)["Parameter"]
    original = before["Value"]
    print(f"\n対象: {WRITE_TARGET}")
    print(f"  現在値 = {original}  (v{before['Version']})")

    # 1) Overwrite を付けずに同名更新 -> 失敗するのが正しい
    print("\n--- Overwrite なしで put_parameter ---")
    try:
        ssm.put_parameter(
            Name=WRITE_TARGET,
            Value=original + "-modified",
            Type="String",
        )
        print("  [?] 想定外: エラーになりませんでした")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        print(f"  [OK] 想定どおり拒否: {code}")
        print(f"       {e.response['Error']['Message']}")

    # 2) Overwrite=True なら通る。Version が増える
    print("\n--- Overwrite=True で put_parameter ---")
    resp = ssm.put_parameter(
        Name=WRITE_TARGET,
        Value=original + "-modified",
        Type="String",
        Overwrite=True,
    )
    print(f"  [OK] 更新成功  Version = {resp['Version']}")
    after = ssm.get_parameter(Name=WRITE_TARGET)["Parameter"]
    print(f"       新しい値 = {after['Value']}")

    # 3) 履歴を見る（Parameter Store は世代を保持している）
    print("\n--- get_parameter_history ---")
    hist = ssm.get_parameter_history(Name=WRITE_TARGET)["Parameters"]
    for h in hist[-5:]:
        print(f"  v{h['Version']}  {h['LastModifiedDate']:%Y-%m-%d %H:%M}  = {h['Value']}")

    # 4) 元に戻す（Terraform の状態と食い違わせない）
    ssm.put_parameter(
        Name=WRITE_TARGET, Value=original, Type="String", Overwrite=True
    )
    restored = ssm.get_parameter(Name=WRITE_TARGET)["Parameter"]
    print(f"\n  [OK] 復元: {restored['Value']}  (v{restored['Version']})")
    print("       ※ Version は戻らず増え続ける。値だけが元に戻る")


def main() -> None:
    try:
        # SecureString の見え方の差
        dump_path(with_decryption=False)
        dump_path(with_decryption=True)
        print("\n→ WithDecryption=False だと SecureString は暗号文のまま返る。"
              "\n  復号には KMS の kms:Decrypt 権限が要る点も押さえておく。")

        demo_overwrite()

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")


if __name__ == "__main__":
    main()
