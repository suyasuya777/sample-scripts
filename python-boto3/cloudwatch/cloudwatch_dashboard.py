"""
25. CloudWatch ダッシュボードのJSON取得・更新
監視ダッシュボードをコード管理・バックアップする。
"""
import boto3
import json

cw = boto3.client('cloudwatch', region_name='ap-northeast-1')
DASHBOARD_NAME = 'my-production-dashboard'

# 既存ダッシュボードの取得
try:
    response = cw.get_dashboard(DashboardName=DASHBOARD_NAME)
    body = json.loads(response['DashboardBody'])
    print(f"ダッシュボード取得: {DASHBOARD_NAME}")
    print(json.dumps(body, indent=2, ensure_ascii=False))
except cw.exceptions.DashboardNotFoundError:
    print("ダッシュボードが存在しないため新規作成します")
    body = {'widgets': []}

# ウィジェット追加例（CPUメトリクス）
new_widget = {
    'type': 'metric',
    'x': 0, 'y': 0, 'width': 12, 'height': 6,
    'properties': {
        'title': 'EC2 CPU使用率',
        'metrics': [['AWS/EC2', 'CPUUtilization', 'InstanceId', 'i-xxxxxxxxxxxxxxxxx']],
        'period': 300,
        'stat': 'Average',
        'region': 'ap-northeast-1',
        'view': 'timeSeries',
    }
}
body.setdefault('widgets', []).append(new_widget)

cw.put_dashboard(DashboardName=DASHBOARD_NAME, DashboardBody=json.dumps(body))
print(f"ダッシュボードを更新しました: {DASHBOARD_NAME}")
