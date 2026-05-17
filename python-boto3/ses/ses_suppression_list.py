"""
55. SES サプレッションリストの管理
バウンス・苦情メールアドレスの管理。SESv2 APIを使用。送信停止アドレスの確認・追加・削除。
"""
import boto3
from datetime import datetime, timezone

sesv2 = boto3.client('sesv2', region_name='ap-northeast-1')

# サプレッションリスト一覧取得
print("=== サプレッションリスト ===")
paginator = sesv2.get_paginator('list_suppressed_destinations')
suppressed = []
for page in paginator.paginate():
    suppressed.extend(page.get('SuppressedDestinationSummaries', []))

print(f"合計: {len(suppressed)} 件\n")
for s in sorted(suppressed, key=lambda x: x['LastUpdateTime'], reverse=True)[:20]:
    reason = s['Reason']
    ts = s['LastUpdateTime'].strftime('%Y-%m-%d')
    print(f"  {s['EmailAddress']:<40}  理由={reason}  日時={ts}")

# 特定アドレスの詳細確認
CHECK_EMAIL = 'bounced@example.com'
try:
    detail = sesv2.get_suppressed_destination(EmailAddress=CHECK_EMAIL)
    dest = detail['SuppressedDestination']
    print(f"\n詳細: {CHECK_EMAIL}")
    print(f"  理由: {dest['Reason']}")
    print(f"  登録日時: {dest['LastUpdateTime']}")
    print(f"  属性: {dest.get('Attributes', {})}")
except sesv2.exceptions.NotFoundException:
    print(f"\n{CHECK_EMAIL} はリストにありません")

# アドレスの手動追加（コメントアウトを外す）:
# sesv2.put_suppressed_destination(EmailAddress='block@example.com', Reason='BOUNCE')
# print("リストに追加しました")

# アドレスの削除（コメントアウトを外す）:
# sesv2.delete_suppressed_destination(EmailAddress='block@example.com')
# print("リストから削除しました")
