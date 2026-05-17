"""
43. SSM パッチコンプライアンス確認
未適用パッチのあるインスタンスを検出する。定期的なセキュリティ監査に使う。
"""
import boto3

ssm = boto3.client('ssm', region_name='ap-northeast-1')
paginator = ssm.get_paginator('describe_instance_patch_states')

non_compliant = []
for page in paginator.paginate():
    for state in page['InstancePatchStates']:
        instance_id = state['InstanceId']
        missing = state.get('MissingCount', 0)
        failed = state.get('FailedCount', 0)
        not_applicable = state.get('NotApplicableCount', 0)
        installed = state.get('InstalledCount', 0)
        compliance = state.get('PatchGroup', '-')

        status = '✅' if missing == 0 and failed == 0 else '⚠️'
        print(f"{status} {instance_id}  インストール済={installed}  未適用={missing}  失敗={failed}  グループ={compliance}")

        if missing > 0 or failed > 0:
            non_compliant.append(instance_id)

print(f"\n非準拠インスタンス: {len(non_compliant)} 件")
