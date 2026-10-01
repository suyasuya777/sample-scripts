# ==================================================================
# セットC : CloudWatch Logs
# 構築 2/21（日）  削除 3/14（日）
# enable_set_c = true で作られる
#
# 保持期間「未設定」と「設定済み」を混在させ、
# logs_list_log_groups.py の検出と logs_retention_policy.py の一括設定を
# 実際に動かせるようにする。
# ==================================================================

locals {
  c = var.enable_set_c ? 1 : 0
}

# retention_in_days を指定しない = 保持期間未設定（＝無期限）
# logs_list_log_groups.py の検出対象。2/25 に一括設定して消える
resource "aws_cloudwatch_log_group" "no_retention" {
  count = local.c
  name  = "/${local.name}/no-retention"

  lifecycle {
    ignore_changes = [retention_in_days]
  }
}

resource "aws_cloudwatch_log_group" "no_retention_2" {
  count = local.c
  name  = "/${local.name}/no-retention-2"

  lifecycle {
    ignore_changes = [retention_in_days]
  }
}

resource "aws_cloudwatch_log_group" "with_retention" {
  count             = local.c
  name              = "/${local.name}/with-retention"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_stream" "app" {
  count          = local.c
  name           = "app-stream"
  log_group_name = aws_cloudwatch_log_group.no_retention[0].name
}

# 古いストリーム検出（logs_describe_streams.py）の題材。イベントを入れない
resource "aws_cloudwatch_log_stream" "stale" {
  count          = local.c
  name           = "stale-stream"
  log_group_name = aws_cloudwatch_log_group.no_retention[0].name
}

# put_log_events は Terraform のリソースにないので CLI で投入する。
# 構造化ログ（JSON）にしておくと Logs Insights のクエリ練習になる。
#
# 【重要】--log-events にショートハンド構文（timestamp=...,message=...）は使えない。
# message の中身が JSON でカンマを含むため、CLI のショートハンドパーサが
#   Error parsing parameter '--log-events': Expected: '=', received: '"'
# で必ず失敗する。JSON ファイルを作って file:// で渡すこと。
resource "terraform_data" "seed_log_events" {
  count = local.c

  triggers_replace = [aws_cloudwatch_log_stream.app[0].name]

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      GROUP="${aws_cloudwatch_log_group.no_retention[0].name}"
      STREAM="${aws_cloudwatch_log_stream.app[0].name}"

      EVENTS_FILE=$(mktemp /tmp/boto3-study-log-events-XXXXXX.json)
      trap 'rm -f "$EVENTS_FILE"' EXIT

      # 40件。7の倍数の行だけ ERROR かつ高レイテンシにしておく（=5件）。
      # timestamp は昇順でなければ PutLogEvents に拒否される。
      python3 -c 'import json, sys, time
now = int(time.time() * 1000)
events = []
for i in range(1, 41):
    level, latency = ("ERROR", 2500 + i * 20) if i % 7 == 0 else ("INFO", 30 + i)
    events.append({
        "timestamp": now - (41 - i) * 1000,
        "message": json.dumps({
            "level": level,
            "request_id": "r-%03d" % i,
            "path": "/api/items",
            "latency_ms": latency,
        }),
    })
json.dump(events, sys.stdout)' > "$EVENTS_FILE"

      aws logs put-log-events \
        --region ${var.region} \
        --log-group-name "$GROUP" \
        --log-stream-name "$STREAM" \
        --log-events "file://$EVENTS_FILE" >/dev/null

      echo "seeded 40 log events (ERROR x5) into $GROUP/$STREAM"
    EOT
  }
}
