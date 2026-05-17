"""
33. Lambda 同時実行数の確認
スロットリングリスクを事前に検知する。予約済み同時実行数と実績を比較する。
"""
import boto3
from datetime import datetime, timezone, timedelta

lmb = boto3.client('lambda', region_name='ap-northeast-1')
cw = boto3.client('cloudwatch', region_name='ap-northeast-1')

paginator = lmb.get_paginator('list_functions')
functions = []
for page in paginator.paginate():
    functions.extend(page['Functions'])

print(f"{'関数名':<35}  {'予約同時実行':>10}  {'直近最大':>8}  {'スロットル':>8}")
print("-" * 70)

for f in functions:
    name = f['FunctionName']
    try:
        reserved = lmb.get_function_concurrency(FunctionName=name).get('ReservedConcurrentExecutions', '-')
    except Exception:
        reserved = '-'

    r = cw.get_metric_statistics(
        Namespace='AWS/Lambda', MetricName='ConcurrentExecutions',
        Dimensions=[{'Name': 'FunctionName', 'Value': name}],
        StartTime=datetime.now(timezone.utc) - timedelta(hours=1),
        EndTime=datetime.now(timezone.utc),
        Period=300, Statistics=['Maximum']
    )
    t = cw.get_metric_statistics(
        Namespace='AWS/Lambda', MetricName='Throttles',
        Dimensions=[{'Name': 'FunctionName', 'Value': name}],
        StartTime=datetime.now(timezone.utc) - timedelta(hours=1),
        EndTime=datetime.now(timezone.utc),
        Period=3600, Statistics=['Sum']
    )
    max_conc = int(max((d['Maximum'] for d in r['Datapoints']), default=0))
    throttles = int(sum(d['Sum'] for d in t['Datapoints']))
    flag = '⚠️' if throttles > 0 else ''
    print(f"{name:<35}  {str(reserved):>10}  {max_conc:>8}  {throttles:>8} {flag}")
