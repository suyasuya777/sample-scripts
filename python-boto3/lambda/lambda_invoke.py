"""
34. Lambda 関数の手動実行（同期・非同期）
テスト実行・手動トリガーに使う。レスポンスのログも確認できる。
"""
import boto3
import json

lmb = boto3.client('lambda', region_name='ap-northeast-1')
FUNCTION_NAME = 'my-function'

# 同期実行（レスポンスを受け取る）
payload = {'action': 'test', 'data': {'key': 'value'}}
response = lmb.invoke(
    FunctionName=FUNCTION_NAME,
    InvocationType='RequestResponse',
    LogType='Tail',
    Payload=json.dumps(payload).encode()
)

status = response['StatusCode']
result = json.loads(response['Payload'].read())
print(f"ステータス: {status}")
print(f"レスポンス: {json.dumps(result, indent=2, ensure_ascii=False)}")

# 非同期実行（レスポンスを待たない）
lmb.invoke(
    FunctionName=FUNCTION_NAME,
    InvocationType='Event',
    Payload=json.dumps({'action': 'batch_process'}).encode()
)
print("非同期実行を発火しました")
