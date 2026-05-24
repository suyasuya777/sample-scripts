"""
01. EC2 インスタンス一覧取得
全リージョンのEC2インスタンスを一括取得する。インフラ棚卸し・コスト分析の起点。
"""
import boto3

ec2_global = boto3.client('ec2', region_name='us-east-1')
regions = [r['RegionName'] for r in ec2_global.describe_regions()['Regions']]

for region in regions:
    ec2 = boto3.client('ec2', region_name=region)
    paginator = ec2.get_paginator('describe_instances')
    for page in paginator.paginate():
        for reservation in page['Reservations']:
            for i in reservation['Instances']:
                name = next((t['Value'] for t in i.get('Tags', []) if t['Key'] == 'Name'), '-')
                print(f"[{region}] {i['InstanceId']} {i['InstanceType']} {i['State']['Name']} {name}")
