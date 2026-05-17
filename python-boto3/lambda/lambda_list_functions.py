"""
31. Lambda 関数一覧とランタイム確認
EOLランタイムの棚卸し・定期監査に。ランタイム・最終更新日を一覧表示する。
"""
import boto3

lmb = boto3.client('lambda', region_name='ap-northeast-1')
paginator = lmb.get_paginator('list_functions')

functions = []
for page in paginator.paginate():
    functions.extend(page['Functions'])

print(f"Lambda関数数: {len(functions)}\n")
print(f"{'関数名':<40}  {'ランタイム':<15}  {'最終更新':<25}  メモリ(MB)")
print("-" * 95)
for f in sorted(functions, key=lambda x: x['LastModified'], reverse=True):
    print(f"{f['FunctionName']:<40}  {f.get('Runtime','N/A'):<15}  {f['LastModified']:<25}  {f['MemorySize']}")
