"""
57. Cost Explorer サービス別コスト取得・異常コスト検出
先月 vs 今月のサービス別コストを比較し、急増サービスを検出する。SREのコスト監視の基本。
"""
import boto3
from datetime import datetime, date, timedelta

ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer は us-east-1 固定

today      = date.today()
# 今月の開始日〜昨日
month_start = today.replace(day=1).isoformat()
yesterday   = (today - timedelta(days=1)).isoformat()
# 先月の開始日〜終了日
last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1).isoformat()
last_month_end   = today.replace(day=1).isoformat()

THRESHOLD_PCT = 20  # 前月比でこの%以上増加したサービスを警告

def get_cost_by_service(start: str, end: str) -> dict:
    """期間内のサービス別コスト(USD)を返す"""
    resp = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    result = {}
    for group in resp['ResultsByTime'][0]['Groups']:
        svc  = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        if cost > 0:
            result[svc] = cost
    return result

print(f"先月  : {last_month_start} 〜 {last_month_end}")
print(f"今月  : {month_start} 〜 {yesterday}\n")

last_costs = get_cost_by_service(last_month_start, last_month_end)
curr_costs = get_cost_by_service(month_start, yesterday)

# 全サービスをマージして比較
all_services = sorted(
    set(last_costs) | set(curr_costs),
    key=lambda s: curr_costs.get(s, 0),
    reverse=True
)

total_last = sum(last_costs.values())
total_curr = sum(curr_costs.values())

print(f"{'サービス':<45} {'先月(USD)':>10} {'今月(USD)':>10} {'増減%':>8}  判定")
print("-" * 85)

alerts = []
for svc in all_services:
    last = last_costs.get(svc, 0.0)
    curr = curr_costs.get(svc, 0.0)
    if last == 0 and curr == 0:
        continue
    pct  = ((curr - last) / last * 100) if last > 0 else float('inf')
    flag = ""
    if pct > THRESHOLD_PCT and curr > 1.0:   # 1USD 未満の誤差は無視
        flag = "⚠️  急増"
        alerts.append((svc, last, curr, pct))
    elif pct < -THRESHOLD_PCT:
        flag = "📉 急減"
    print(f"{svc:<45} {last:>10.2f} {curr:>10.2f} {pct:>7.1f}%  {flag}")

print("-" * 85)
print(f"{'合計':<45} {total_last:>10.2f} {total_curr:>10.2f}")

# 警告サマリ
if alerts:
    print(f"\n⚠️  急増サービス ({THRESHOLD_PCT}%超) : {len(alerts)} 件")
    for svc, last, curr, pct in alerts:
        print(f"  {svc}: {last:.2f} → {curr:.2f} USD (+{pct:.1f}%)")
else:
    print(f"\n✅ {THRESHOLD_PCT}%超の急増サービスはありません")
