"""
35. Lambda エイリアスとバージョン管理
Blue/Greenデプロイ・ロールバック管理に使う。本番エイリアスのトラフィック割合も制御できる。
"""
import boto3

lmb = boto3.client('lambda', region_name='ap-northeast-1')
FUNCTION_NAME = 'my-function'

# バージョン一覧
print("=== バージョン一覧 ===")
paginator = lmb.get_paginator('list_versions_by_function')
for page in paginator.paginate(FunctionName=FUNCTION_NAME):
    for v in page['Versions']:
        print(f"  バージョン: {v['Version']}  最終更新: {v['LastModified']}")

# エイリアス一覧
print("\n=== エイリアス一覧 ===")
aliases = lmb.list_aliases(FunctionName=FUNCTION_NAME)['Aliases']
for a in aliases:
    routing = a.get('RoutingConfig', {}).get('AdditionalVersionWeights', {})
    print(f"  {a['Name']} -> v{a['FunctionVersion']}  追加ルーティング: {routing}")

# 新バージョン発行例（コメントアウトを外す）:
# new_version = lmb.publish_version(FunctionName=FUNCTION_NAME, Description='v2.0 release')
# print(f"新バージョン発行: {new_version['Version']}")

# エイリアス更新例（コメントアウトを外す）:
# lmb.update_alias(FunctionName=FUNCTION_NAME, Name='production', FunctionVersion=new_version['Version'])
# print("productionエイリアスを更新しました")
