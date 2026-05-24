"""
05. セキュリティグループのルール確認
0.0.0.0/0 開放のインバウンドルールを検出。セキュリティ監査・インシデント調査に。
"""
import boto3

ec2 = boto3.client('ec2', region_name='ap-northeast-1')
paginator = ec2.get_paginator('describe_security_groups')

print("=== 全開放（0.0.0.0/0）のインバウンドルール ===")
for page in paginator.paginate():
    for sg in page['SecurityGroups']:
        for rule in sg.get('IpPermissions', []):
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    port = rule.get('FromPort', 'ALL')
                    proto = rule.get('IpProtocol', '-1')
                    print(f"SG: {sg['GroupId']} ({sg['GroupName']})  Port: {port}  Protocol: {proto}")
