"""
08. EC2 インスタンスタイプ変更
停止 → タイプ変更 → 起動 の三点セット。スペック変更時の定番操作。
"""
import boto3

ec2 = boto3.client('ec2', region_name='ap-northeast-1')

INSTANCE_ID = 'i-xxxxxxxxxxxxxxxxx'
NEW_TYPE = 't3.medium'

# 停止
print(f"インスタンスを停止します: {INSTANCE_ID}")
ec2.stop_instances(InstanceIds=[INSTANCE_ID])
waiter = ec2.get_waiter('instance_stopped')
waiter.wait(InstanceIds=[INSTANCE_ID])
print("停止完了")

# タイプ変更
ec2.modify_instance_attribute(
    InstanceId=INSTANCE_ID,
    InstanceType={'Value': NEW_TYPE}
)
print(f"インスタンスタイプを {NEW_TYPE} に変更しました")

# 起動
ec2.start_instances(InstanceIds=[INSTANCE_ID])
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[INSTANCE_ID])
print("起動完了")
