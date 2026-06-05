"""
59. RDS Aurora クラスターのフェイルオーバー操作
障害訓練・計画メンテナンス時のフェイルオーバー実行と完了確認。
ライター/リーダーの切り替えをウェイターで安全に待機する。
"""
import boto3
import time

rds = boto3.client('rds', region_name='ap-northeast-1')

CLUSTER_ID = 'my-aurora-cluster'

def get_cluster_members(cluster_id: str) -> dict:
    """クラスターのライター/リーダー情報を返す"""
    resp = rds.describe_db_clusters(DBClusterIdentifier=cluster_id)
    cluster = resp['DBClusters'][0]
    members = cluster['DBClusterMembers']
    writer  = next((m['DBInstanceIdentifier'] for m in members if m['IsClusterWriter']), None)
    readers = [m['DBInstanceIdentifier'] for m in members if not m['IsClusterWriter']]
    return {
        'status' : cluster['Status'],
        'writer' : writer,
        'readers': readers,
        'engine' : cluster['Engine'],
        'version': cluster['EngineVersion'],
    }

# フェイルオーバー前の状態確認
print(f"クラスター: {CLUSTER_ID}")
before = get_cluster_members(CLUSTER_ID)
print(f"フェイルオーバー前")
print(f"  ステータス : {before['status']}")
print(f"  ライター   : {before['writer']}")
print(f"  リーダー   : {', '.join(before['readers']) if before['readers'] else 'なし'}")
print(f"  エンジン   : {before['engine']} {before['version']}")

if not before['readers']:
    print("\n⚠️  リーダーインスタンスがないためフェイルオーバーできません")
    raise SystemExit(1)

# フェイルオーバー実行
# ターゲットを指定することでどのリーダーを昇格させるか制御できる
target = before['readers'][0]
print(f"\nフェイルオーバーを実行します (ターゲット: {target})")

rds.failover_db_cluster(
    DBClusterIdentifier=CLUSTER_ID,
    TargetDBInstanceIdentifier=target
)

# クラスターが failing-over → available になるまでポーリング
print("完了を待機中 ...")
MAX_WAIT   = 300  # 最大5分
INTERVAL   = 15
elapsed    = 0

while elapsed < MAX_WAIT:
    time.sleep(INTERVAL)
    elapsed += INTERVAL
    info = get_cluster_members(CLUSTER_ID)
    print(f"  [{elapsed}s] status={info['status']}  writer={info['writer']}")
    if info['status'] == 'available' and info['writer'] != before['writer']:
        print("\n✅ フェイルオーバー完了")
        print(f"  旧ライター → {before['writer']}")
        print(f"  新ライター → {info['writer']}")
        break
else:
    print(f"\n⚠️  {MAX_WAIT}秒以内に完了しませんでした。AWSコンソールで状態を確認してください。")
