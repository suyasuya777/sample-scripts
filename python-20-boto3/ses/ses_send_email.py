"""
53. SES メール送信（テキスト・HTML両対応）

--------------------------------------------------------------------
実行前に VERIFIED_EMAIL を置き換えること:

  grep '^notification_email' ~/boto3-study-tf/terraform.tfvars

【重要】SES はサンドボックスのままなので、
**送信元も宛先も「検証済みアドレス」でなければ送れません。**
セットD（set_d.tf の aws_sesv2_email_identity）で検証されているのは
terraform.tfvars の notification_email ただ1つです。
したがって SENDER と RECIPIENT は同じアドレスになります。

検証メール（件名: Amazon Web Services – Email Address Verification Request）
のリンクを踏んでいないと MessageRejected になります。状態の確認:

  aws ses list-identities
  aws ses get-identity-verification-attributes --identities <アドレス>
--------------------------------------------------------------------
"""
import boto3
from botocore.exceptions import ClientError

# ====================== 設定 ======================
REGION = "ap-northeast-1"

# terraform.tfvars の notification_email と同じアドレス
VERIFIED_EMAIL = "REPLACEME@example.com"

SENDER = VERIFIED_EMAIL
RECIPIENT = VERIFIED_EMAIL
CC: list[str] = []
BCC: list[str] = []

# 未検証アドレス宛で MessageRejected を確認するための宛先（実在しなくてよい）
UNVERIFIED_RECIPIENT = "not-verified@example.com"

# 3/7 の ses_send_statistics.py で統計に出すため、まとまった通数を送っておく
EXTRA_SENDS = 3
# ==================================================

ses = boto3.client("ses", region_name=REGION)


def send(recipient: str, subject: str) -> str | None:
    """テキスト＋HTML の両形式で1通送る。MessageId を返す。"""
    try:
        resp = ses.send_email(
            Source=SENDER,
            Destination={
                "ToAddresses": [recipient],
                "CcAddresses": CC,
                "BccAddresses": BCC,
            },
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {
                        "Data": (
                            "boto3 学習環境からのテスト送信です。\n\n"
                            "このメールはテキスト形式の本文です。"
                        ),
                        "Charset": "UTF-8",
                    },
                    "Html": {
                        "Data": (
                            "<html><body>"
                            "<h2>boto3 学習環境からのテスト送信</h2>"
                            "<p>このメールは <b>HTML形式</b> の本文です。</p>"
                            "<p>メールクライアントがどちらを表示したか確認してください。</p>"
                            "</body></html>"
                        ),
                        "Charset": "UTF-8",
                    },
                },
            },
            ReplyToAddresses=[SENDER],
        )
        print(f"  [OK] 送信成功 -> {recipient}  MessageId={resp['MessageId']}")
        return resp["MessageId"]
    except ClientError as e:
        code = e.response["Error"]["Code"]
        print(f"  [NG] {code} -> {recipient}")
        print(f"       {e.response['Error']['Message']}")
        return None


def main() -> None:
    if "REPLACEME" in VERIFIED_EMAIL:
        print("[ERROR] VERIFIED_EMAIL を置き換えてください")
        print("        grep '^notification_email' ~/boto3-study-tf/terraform.tfvars")
        return

    # 検証状態を先に確認しておく（ここで未検証なら以降は全部落ちる）
    attrs = ses.get_identity_verification_attributes(
        Identities=[VERIFIED_EMAIL]
    )["VerificationAttributes"]
    status = attrs.get(VERIFIED_EMAIL, {}).get("VerificationStatus", "NotFound")
    print(f"{VERIFIED_EMAIL} の検証状態: {status}")
    if status != "Success":
        print("[ERROR] 検証が完了していません。")
        print("        件名 'Amazon Web Services – Email Address Verification Request'")
        print("        のメールのリンクを踏んでから再実行してください。")
        return

    # 1) 検証済みアドレス宛（テキスト＋HTML）
    print("\n=== 検証済みアドレス宛 ===")
    send(RECIPIENT, "【boto3学習】テキスト+HTML の送信テスト")

    # 2) 未検証アドレス宛 -> MessageRejected になるのが正しい
    print("\n=== 未検証アドレス宛（MessageRejected の確認） ===")
    send(UNVERIFIED_RECIPIENT, "【boto3学習】届かないはずのメール")
    print("  → サンドボックスでは宛先も検証済みである必要がある。")
    print("     本番では Production access を申請してこの制限を外す。")

    # 3) 3/7 の送信統計用に数通送っておく
    print(f"\n=== 送信統計用に {EXTRA_SENDS} 通追加送信（3/7 で使う） ===")
    for i in range(1, EXTRA_SENDS + 1):
        send(RECIPIENT, f"【boto3学習】統計用テスト {i}/{EXTRA_SENDS}")
    print("  → 3/7 の ses_send_statistics.py でこの送信数が見えるか確認する")


if __name__ == "__main__":
    main()
