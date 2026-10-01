"""
08. EC2 インスタンスタイプ変更
停止 → タイプ変更 → 起動 の三点セット。スペック変更時の定番操作。

--------------------------------------------------------------------
実行前に INSTANCE_ID を置き換えること:

  terraform output -raw ec2_instance_id    -> INSTANCE_ID

【重要】Terraform 側は aws_instance に ignore_changes = [instance_type]
が入っているため、terraform apply しても t3.micro には戻りません。
その日のうちに RESTORE_TYPE へ戻すこと（t3.small のままだと課金が倍）。
このスクリプトは最後の「戻す」まで通しで実行します。
--------------------------------------------------------------------
"""
import time
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"

# terraform output -raw ec2_instance_id
INSTANCE_ID = "i-REPLACEME"

NEW_TYPE = "t3.small"      # 2/9 の演習で一時的に上げるタイプ
RESTORE_TYPE = "t3.micro"  # 必ずこれに戻す（Terraform は戻してくれない）
# ==================================================

ec2 = boto3.client("ec2", region_name=REGION)


def current_type() -> str:
    r = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
    return r["Reservations"][0]["Instances"][0]["InstanceType"]


def change_type(new_type: str) -> None:
    """停止 → タイプ変更 → 起動。各フェーズの所要時間を計測する。"""
    print(f"\n=== {current_type()} -> {new_type} ===")

    t0 = time.time()
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])
    ec2.get_waiter("instance_stopped").wait(InstanceIds=[INSTANCE_ID])
    print(f"[1/3] 停止完了  {time.time() - t0:.1f} 秒")

    ec2.modify_instance_attribute(
        InstanceId=INSTANCE_ID,
        InstanceType={"Value": new_type},
    )
    print(f"[2/3] タイプ変更  {new_type}")

    t1 = time.time()
    ec2.start_instances(InstanceIds=[INSTANCE_ID])
    ec2.get_waiter("instance_running").wait(InstanceIds=[INSTANCE_ID])
    print(f"[3/3] 起動完了  {time.time() - t1:.1f} 秒  （合計 {time.time() - t0:.1f} 秒）")


def try_modify_while_running() -> None:
    """
    起動中のインスタンスに直接 modify を投げると何が返るかを確認する。
    IncorrectInstanceState になるのが正しい挙動。
    """
    print("\n=== 起動中に modify を投げてみる（状態遷移の確認） ===")
    try:
        ec2.modify_instance_attribute(
            InstanceId=INSTANCE_ID,
            InstanceType={"Value": NEW_TYPE},
        )
        print("[?] 想定外: エラーになりませんでした（既に停止中かもしれません）")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        print(f"[OK] 想定どおり拒否されました: {code}")
        print(f"     {e.response['Error']['Message']}")


def main() -> None:
    if "REPLACEME" in INSTANCE_ID:
        print("[ERROR] INSTANCE_ID を置き換えてください")
        print("        terraform output -raw ec2_instance_id")
        return

    try:
        print(f"現在のタイプ: {current_type()}")

        # 1) 起動中に modify を投げて IncorrectInstanceState を確認
        try_modify_while_running()

        # 2) 正規手順で t3.small へ
        change_type(NEW_TYPE)
        print(f"変更後: {current_type()}")

        # 3) その日のうちに戻す（課金が倍になるため必須）
        input("\n確認が終わったら Enter を押すと t3.micro に戻します > ")
        change_type(RESTORE_TYPE)

        final = current_type()
        print(f"\n最終状態: {final}")
        if final != RESTORE_TYPE:
            print(f"[警告] {RESTORE_TYPE} に戻っていません。手で戻してください")
        else:
            print("[OK] 戻し完了")

    except ClientError as e:
        print(f"[ERROR] {e.response['Error']['Code']}: {e}")
        print(f"        中断した場合は必ずタイプを確認し、{RESTORE_TYPE} に戻すこと")


if __name__ == "__main__":
    main()
