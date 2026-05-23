"""
53. SES メール送信（テキスト・HTML両対応）
アプリからのトランザクションメール送信。テキストとHTMLを同時に指定できる。
"""
import boto3
from botocore.exceptions import ClientError

ses = boto3.client('ses', region_name='ap-northeast-1')

SENDER = 'noreply@example.com'
RECIPIENT = 'user@example.com'
CC = []
BCC = []

# テキスト＋HTML両形式で送信
try:
    response = ses.send_email(
        Source=SENDER,
        Destination={
            'ToAddresses': [RECIPIENT],
            'CcAddresses': CC,
            'BccAddresses': BCC,
        },
        Message={
            'Subject': {
                'Data': '【確認】ご登録ありがとうございます',
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': 'この度はご登録いただきありがとうございます。\n\nログインURL: https://example.com/login',
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': '''
                        <html><body>
                        <h2>ご登録ありがとうございます</h2>
                        <p>以下のURLからログインしてください。</p>
                        <a href="https://example.com/login">ログイン</a>
                        </body></html>
                    ''',
                    'Charset': 'UTF-8'
                }
            }
        },
        ReplyToAddresses=['support@example.com'],
    )
    print(f"送信成功: MessageId={response['MessageId']}")
except ClientError as e:
    print(f"送信失敗: {e.response['Error']['Message']}")
