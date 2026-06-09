#!/bin/bash
# ============================================================
# jq サンプル集 - SRE向け
# ============================================================

# ── 前提：サンプルJSONファイルを作成 ─────────────────────
cat > /tmp/pods.json << 'EOF'
{
  "items": [
    {
      "metadata": { "name": "web-pod-1", "namespace": "production", "labels": {"app": "web"} },
      "status": { "phase": "Running", "podIP": "10.0.0.1" },
      "spec": { "nodeName": "node01", "containers": [{"name": "web", "image": "nginx:1.25", "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}}}] }
    },
    {
      "metadata": { "name": "web-pod-2", "namespace": "production", "labels": {"app": "web"} },
      "status": { "phase": "Running", "podIP": "10.0.0.2" },
      "spec": { "nodeName": "node02", "containers": [{"name": "web", "image": "nginx:1.25", "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}}}] }
    },
    {
      "metadata": { "name": "api-pod-1", "namespace": "production", "labels": {"app": "api"} },
      "status": { "phase": "CrashLoopBackOff", "podIP": "10.0.0.3" },
      "spec": { "nodeName": "node01", "containers": [{"name": "api", "image": "myapp:2.1.0", "resources": {"requests": {"cpu": "200m", "memory": "256Mi"}}}] }
    },
    {
      "metadata": { "name": "db-pod-1", "namespace": "staging", "labels": {"app": "db"} },
      "status": { "phase": "Running", "podIP": "10.0.1.1" },
      "spec": { "nodeName": "node03", "containers": [{"name": "db", "image": "postgres:15", "resources": {"requests": {"cpu": "500m", "memory": "512Mi"}}}] }
    }
  ]
}
EOF

cat > /tmp/alerts.json << 'EOF'
[
  {"alertname": "HighCPU",       "severity": "warning",  "instance": "node01", "value": 85.2, "fired_at": "2024-01-15T10:00:00Z"},
  {"alertname": "HighMemory",    "severity": "critical", "instance": "node02", "value": 92.1, "fired_at": "2024-01-15T10:01:00Z"},
  {"alertname": "DiskFull",      "severity": "critical", "instance": "node03", "value": 91.2, "fired_at": "2024-01-15T10:02:00Z"},
  {"alertname": "HighCPU",       "severity": "warning",  "instance": "node03", "value": 78.5, "fired_at": "2024-01-15T10:03:00Z"},
  {"alertname": "PodCrashLoop",  "severity": "critical", "instance": "node01", "value": 0,    "fired_at": "2024-01-15T10:04:00Z"}
]
EOF

echo "=== Pod一覧 ==="
cat /tmp/pods.json | jq .
echo ""

# ============================================================
# 1. 基本：特定フィールドを取得
# ============================================================
echo "=== 1. Podの名前一覧 ==="
jq '.items[].metadata.name' /tmp/pods.json

# ============================================================
# 2. 配列の展開（[]）と複数フィールド取得
# ============================================================
echo ""
echo "=== 2. Pod名・ステータス・ノードを一覧表示 ==="
jq '.items[] | {name: .metadata.name, phase: .status.phase, node: .spec.nodeName}' /tmp/pods.json

# ============================================================
# 3. フィルタ：特定条件に一致する要素だけ抽出（select）
# ============================================================
echo ""
echo "=== 3. Running 状態の Pod のみ ==="
jq '.items[] | select(.status.phase == "Running") | .metadata.name' /tmp/pods.json

echo ""
echo "=== 3b. CrashLoopBackOff の Pod ==="
jq '.items[] | select(.status.phase == "CrashLoopBackOff") | {name: .metadata.name, node: .spec.nodeName, image: .spec.containers[0].image}' /tmp/pods.json

# ============================================================
# 4. 配列の変換（map）
# ============================================================
echo ""
echo "=== 4. 全Podの名前を配列で取得 ==="
jq '[.items[].metadata.name]' /tmp/pods.json

echo ""
echo "=== 4b. production namespace の Pod を map でフィルタ ==="
jq '[.items[] | select(.metadata.namespace == "production") | .metadata.name]' /tmp/pods.json

# ============================================================
# 5. 文字列補間（\()）と -r（rawモード）
# ============================================================
echo ""
echo "=== 5. Pod名: フェーズ の形式で表示 ==="
jq -r '.items[] | "\(.metadata.name): \(.status.phase)"' /tmp/pods.json

# ============================================================
# 6. 長さ・件数（length）
# ============================================================
echo ""
echo "=== 6. Podの総数 ==="
jq '.items | length' /tmp/pods.json

echo ""
echo "=== 6b. Running Pod の件数 ==="
jq '[.items[] | select(.status.phase == "Running")] | length' /tmp/pods.json

# ============================================================
# 7. グループ化・集計（group_by）
# ============================================================
echo ""
echo "=== 7. Podをステータスでグループ化して件数を集計 ==="
jq '[.items[] | {phase: .status.phase}] | group_by(.phase) | map({phase: .[0].phase, count: length})' /tmp/pods.json

# ============================================================
# 8. ソート（sort_by）
# ============================================================
echo ""
echo "=== 8. アラートをvalueの降順でソート ==="
jq 'sort_by(-.value) | .[] | {alertname, instance, value}' /tmp/alerts.json

# ============================================================
# 9. unique・重複除去
# ============================================================
echo ""
echo "=== 9. アラートの種類（重複除去） ==="
jq '[.[].alertname] | unique' /tmp/alerts.json

# ============================================================
# 10. フィルタ（select + 比較演算子）
# ============================================================
echo ""
echo "=== 10. severity が critical のアラート ==="
jq '.[] | select(.severity == "critical") | {alertname, instance, value}' /tmp/alerts.json

echo ""
echo "=== 10b. value が 80 超のアラート ==="
jq '.[] | select(.value > 80) | {alertname, instance, value}' /tmp/alerts.json

# ============================================================
# 11. キー一覧の取得（keys）
# ============================================================
echo ""
echo "=== 11. アラートオブジェクトのキー一覧 ==="
jq '.[0] | keys' /tmp/alerts.json

# ============================================================
# 12. 実用例：kubectl get pods -o json の簡易サマリー
# ============================================================
echo ""
echo "=== 12. Pod状態サマリー（kubectl風） ==="
jq -r '.items[] | [.metadata.name, .metadata.namespace, .status.phase, .spec.nodeName, .spec.containers[0].image] | @tsv' /tmp/pods.json \
  | column -t -s $'\t'

# ============================================================
# 13. 実用例：criticalアラートのinstanceリストをカンマ区切りで出力
# ============================================================
echo ""
echo "=== 13. criticalアラートのインスタンス一覧（カンマ区切り） ==="
jq -r '[.[] | select(.severity == "critical") | .instance] | unique | join(", ")' /tmp/alerts.json

# ============================================================
# 14. 実用例：JSONをCSVに変換（@csv）
# ============================================================
echo ""
echo "=== 14. アラートをCSV形式に変換 ==="
jq -r '["alertname","severity","instance","value"], (.[] | [.alertname, .severity, .instance, (.value | tostring)]) | @csv' /tmp/alerts.json
