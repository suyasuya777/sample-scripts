"""
04. 未使用EIP（Elastic IP）の検出
アタッチされていないEIPを特定してコスト削減につなげる。
"""
import boto3

ec2 = boto3.client('ec2', region_name='ap-northeast-1')
addresses = ec2.describe_addresses()['Addresses']

unused = [a for a in addresses if 'InstanceId' not in a and 'NetworkInterfaceId' not in a]

if not unused:
    print("未使用のEIPはありません")
else:
    print(f"未使用EIP: {len(unused)} 件")
    for a in unused:
        print(f"  PublicIp: {a['PublicIp']}  AllocationId: {a['AllocationId']}")
        # 解放する場合（コメントアウトを外す）:
        # ec2.release_address(AllocationId=a['AllocationId'])
        # print(f"  -> 解放しました")
