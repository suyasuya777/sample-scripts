"""
02. EC2 インスタンス起動 / 停止 / 再起動
緊急対応・メンテナンスウィンドウで多用するインスタンス操作。
"""
import boto3

ec2 = boto3.client('ec2', region_name='ap-northeast-1')

INSTANCE_IDS = ['i-xxxxxxxxxxxxxxxxx']

# 起動
ec2.start_instances(InstanceIds=INSTANCE_IDS)
print(f"起動開始: {INSTANCE_IDS}")

# 停止
# ec2.stop_instances(InstanceIds=INSTANCE_IDS)
# print(f"停止開始: {INSTANCE_IDS}")

# 再起動
# ec2.reboot_instances(InstanceIds=INSTANCE_IDS)
# print(f"再起動: {INSTANCE_IDS}")

# 起動完了まで待機
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=INSTANCE_IDS)
print("インスタンスが running 状態になりました")
