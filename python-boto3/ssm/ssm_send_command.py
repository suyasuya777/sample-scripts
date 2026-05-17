"""
41. SSM Session Manager でコマンドをリモート実行
SSH不要でEC2に任意コマンドを実行する。踏み台サーバー不要なSRE定番操作。
"""
import boto3
import time

ssm = boto3.client('ssm', region_name='ap-northeast-1')

INSTANCE_ID = 'i-xxxxxxxxxxxxxxxxx'
COMMANDS = ['df -h', 'free -m', 'uptime', 'ps aux --sort=-%cpu | head -10']

response = ssm.send_command(
    InstanceIds=[INSTANCE_ID],
    DocumentName='AWS-RunShellScript',
    Parameters={'commands': COMMANDS},
    TimeoutSeconds=60,
)
command_id = response['Command']['CommandId']
print(f"コマンド実行中... ID={command_id}")

# 完了まで待機
for _ in range(30):
    time.sleep(2)
    result = ssm.get_command_invocation(CommandId=command_id, InstanceId=INSTANCE_ID)
    if result['Status'] in ('Success', 'Failed', 'TimedOut', 'Cancelled'):
        break

print(f"ステータス: {result['Status']}")
print("=== 標準出力 ===")
print(result['StandardOutputContent'])
if result['StandardErrorContent']:
    print("=== 標準エラー ===")
    print(result['StandardErrorContent'])
