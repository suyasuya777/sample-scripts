"""
51. SES 送信ドメインのID一覧取得
登録済みドメイン・メールアドレスの棚卸し。検証ステータスも合わせて確認する。
"""
import boto3

ses = boto3.client('ses', region_name='ap-northeast-1')

# ドメインID一覧
domains = ses.list_identities(IdentityType='Domain')['Identities']
emails = ses.list_identities(IdentityType='EmailAddress')['Identities']
all_ids = domains + emails

print(f"登録ID合計: {len(all_ids)} 件  (ドメイン: {len(domains)}, メール: {len(emails)})\n")

# 検証ステータスを一括取得（最大100件）
for i in range(0, len(all_ids), 100):
    chunk = all_ids[i:i+100]
    attrs = ses.get_identity_verification_attributes(Identities=chunk)['VerificationAttributes']
    for identity, attr in attrs.items():
        status = attr['VerificationStatus']
        token = attr.get('VerificationToken', '')
        icon = '✅' if status == 'Success' else '⏳' if status == 'Pending' else '❌'
        id_type = 'ドメイン' if identity in domains else 'メール'
        print(f"{icon} [{id_type}] {identity}  {status}")
