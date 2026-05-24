"""
49. VPC・サブネット・ルートテーブル確認
ネットワーク構成の確認・変更前後の比較に使う。インフラ棚卸しの基本操作。
"""
import boto3

ec2 = boto3.client('ec2', region_name='ap-northeast-1')

# VPC一覧
vpcs = ec2.describe_vpcs()['Vpcs']
print(f"VPC数: {len(vpcs)}")
for vpc in vpcs:
    name = next((t['Value'] for t in vpc.get('Tags', []) if t['Key'] == 'Name'), '-')
    print(f"\nVPC: {vpc['VpcId']}  CIDR={vpc['CidrBlock']}  名前={name}  Default={vpc['IsDefault']}")

    # サブネット
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}])['Subnets']
    for sn in sorted(subnets, key=lambda x: x['AvailabilityZone']):
        sn_name = next((t['Value'] for t in sn.get('Tags', []) if t['Key'] == 'Name'), '-')
        print(f"  サブネット: {sn['SubnetId']}  {sn['CidrBlock']}  {sn['AvailabilityZone']}  Public={sn['MapPublicIpOnLaunch']}  名前={sn_name}")

    # ルートテーブル
    rts = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}])['RouteTables']
    for rt in rts:
        rt_name = next((t['Value'] for t in rt.get('Tags', []) if t['Key'] == 'Name'), '-')
        print(f"  ルートテーブル: {rt['RouteTableId']}  名前={rt_name}")
        for route in rt['Routes']:
            dest = route.get('DestinationCidrBlock', route.get('DestinationIpv6CidrBlock', '-'))
            gw = route.get('GatewayId', route.get('NatGatewayId', route.get('TransitGatewayId', '-')))
            print(f"    {dest} -> {gw}  状態={route['State']}")
