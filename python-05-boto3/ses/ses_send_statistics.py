"""
54. SES 送信統計・バウンス率の確認
送信レート・バウンス率を監視してレピュテーション管理に役立てる。
"""
import boto3
from datetime import datetime, timezone

ses = boto3.client('ses', region_name='ap-northeast-1')

# 送信クォータ確認
quota = ses.get_send_quota()
print("=== 送信クォータ ===")
print(f"  24時間の上限: {quota['Max24HourSend']:,.0f} 通")
print(f"  1秒あたりの上限: {quota['MaxSendRate']:,.0f} 通/秒")
print(f"  直近24時間の送信数: {quota['SentLast24Hours']:,.0f} 通")
usage_pct = quota['SentLast24Hours'] / quota['Max24HourSend'] * 100 if quota['Max24HourSend'] > 0 else 0
print(f"  使用率: {usage_pct:.1f}%")

# 送信統計（直近2週間）
print("\n=== 送信統計 ===")
stats = ses.get_send_statistics()['SendDataPoints']
stats_sorted = sorted(stats, key=lambda x: x['Timestamp'], reverse=True)

total_sent = sum(s['DeliveryAttempts'] for s in stats)
total_bounces = sum(s['Bounces'] for s in stats)
total_complaints = sum(s['Complaints'] for s in stats)
total_rejects = sum(s['Rejects'] for s in stats)

bounce_rate = total_bounces / total_sent * 100 if total_sent > 0 else 0
complaint_rate = total_complaints / total_sent * 100 if total_sent > 0 else 0

print(f"  合計送信: {total_sent:,} 通")
print(f"  バウンス: {total_bounces:,} 通 ({bounce_rate:.2f}%)  ⚠️ 5%以上で要注意")
print(f"  苦情: {total_complaints:,} 通 ({complaint_rate:.4f}%)  ⚠️ 0.1%以上で要注意")
print(f"  拒否: {total_rejects:,} 通")

if bounce_rate >= 5:
    print("\n🔴 バウンス率が高すぎます！サプレッションリストを確認してください")
elif bounce_rate >= 2:
    print("\n⚠️  バウンス率に注意が必要です")
