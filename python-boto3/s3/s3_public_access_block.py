"""
12. S3 パブリックアクセス設定の確認
全バケットのパブリックアクセスブロック設定を確認するセキュリティ監査。
"""
import boto3

s3 = boto3.client('s3')
buckets = s3.list_buckets()['Buckets']

ok = []
ng = []
for b in buckets:
    name = b['Name']
    try:
        cfg = s3.get_public_access_block(Bucket=name)['PublicAccessBlockConfiguration']
        all_blocked = all([
            cfg.get('BlockPublicAcls', False),
            cfg.get('IgnorePublicAcls', False),
            cfg.get('BlockPublicPolicy', False),
            cfg.get('RestrictPublicBuckets', False),
        ])
        if all_blocked:
            ok.append(name)
            print(f"✅ {name}")
        else:
            ng.append(name)
            print(f"⚠️  {name}  設定不完全: {cfg}")
    except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
        ng.append(name)
        print(f"❌ {name}  ブロック設定なし")

print(f"\n正常: {len(ok)} 件  要確認: {len(ng)} 件")
