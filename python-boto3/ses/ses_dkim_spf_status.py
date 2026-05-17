"""
52. SES DKIM・SPF 検証ステータス確認
ドメイン認証の状態確認。Terraform/Route53設定後の疎通確認に必須。
"""
import boto3

ses = boto3.client('ses', region_name='ap-northeast-1')

DOMAIN = 'example.com'

# DKIM検証ステータス
dkim_attrs = ses.get_identity_dkim_attributes(Identities=[DOMAIN])['DkimAttributes']
dkim = dkim_attrs.get(DOMAIN, {})
print(f"=== DKIM ステータス: {DOMAIN} ===")
print(f"  DKIM有効: {dkim.get('DkimEnabled', False)}")
print(f"  検証状態: {dkim.get('DkimVerificationStatus', '-')}")
print(f"  DKIMトークン:")
for token in dkim.get('DkimTokens', []):
    print(f"    {token}._domainkey.{DOMAIN}  (CNAME先: {token}.dkim.amazonses.com)")

# 送信認証（SPF/DMARC相当）
mail_from_attrs = ses.get_identity_mail_from_domain_attributes(Identities=[DOMAIN])
mail_from = mail_from_attrs['MailFromDomainAttributes'].get(DOMAIN, {})
print(f"\n=== MAIL FROM ドメイン ===")
print(f"  ドメイン: {mail_from.get('MailFromDomain', '未設定')}")
print(f"  MXレコード状態: {mail_from.get('MailFromDomainStatus', '-')}")
print(f"  検証失敗時の動作: {mail_from.get('BehaviorOnMXFailure', '-')}")

# 送信通知設定
notif_attrs = ses.get_identity_notification_attributes(Identities=[DOMAIN])
notif = notif_attrs['NotificationAttributes'].get(DOMAIN, {})
print(f"\n=== 通知設定 ===")
print(f"  バウンス通知SNS: {notif.get('BounceTopic', '未設定')}")
print(f"  苦情通知SNS: {notif.get('ComplaintTopic', '未設定')}")
