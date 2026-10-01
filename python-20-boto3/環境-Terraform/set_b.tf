# ==================================================================
# セットB : S3（1200オブジェクト）/ IAM / SSM Parameter Store / Secrets Manager
# 構築 1/19  削除 2/28
# enable_set_b = true で作られる
# ==================================================================

locals {
  b = var.enable_set_b ? 1 : 0
}

# ------------------------------------------------------------------
# S3 : 2バケット。paginator 確認用に1200オブジェクトを投入する
# ------------------------------------------------------------------

resource "aws_s3_bucket" "a" {
  count         = local.b
  bucket        = "${local.name}-a-${local.account}"
  force_destroy = true
}

resource "aws_s3_bucket" "b" {
  count         = local.b
  bucket        = "${local.name}-b-${local.account}"
  force_destroy = true
}

# バケットAは4項目すべてブロック
resource "aws_s3_bucket_public_access_block" "a" {
  count  = local.b
  bucket = aws_s3_bucket.a[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# バケットBはわざと2項目だけ。s3_public_access_block.py で差が出る題材
resource "aws_s3_bucket_public_access_block" "b" {
  count  = local.b
  bucket = aws_s3_bucket.b[0].id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

# 1200オブジェクトを aws_s3_object で作ると state が肥大し apply も遅いので、
# ローカルにファイルを生成して aws s3 sync で一括投入する。
# AWS CLI v2 がローカルにあることが前提。
resource "terraform_data" "seed_objects" {
  count = local.b

  triggers_replace = [
    aws_s3_bucket.a[0].id,
    var.s3_object_count,
  ]

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      DIR=$(mktemp -d)
      for i in $(seq 1 ${var.s3_object_count}); do
        printf 'sample object %s\n' "$i" > "$DIR/file$i.txt"
      done
      aws s3 sync "$DIR" "s3://${aws_s3_bucket.a[0].id}/objects/" \
        --region ${var.region} --only-show-errors
      rm -rf "$DIR"
      echo "seeded ${var.s3_object_count} objects"
    EOT
  }
}

# ------------------------------------------------------------------
# IAM : user1（キー使用済み・インラインポリシーあり）
#        user2（キー未使用・AdministratorAccess 付き）
# ------------------------------------------------------------------

resource "aws_iam_user" "u1" {
  count         = local.b
  name          = "${local.name}-user1"
  force_destroy = true # アクセスキーごと消す
}

resource "aws_iam_user" "u2" {
  count         = local.b
  name          = "${local.name}-user2"
  force_destroy = true
}

# 注意: シークレットアクセスキーは state に平文で入る。学習用アカウント限定。
resource "aws_iam_access_key" "u1" {
  count = local.b
  user  = aws_iam_user.u1[0].name
}

resource "aws_iam_access_key" "u2" {
  count = local.b
  user  = aws_iam_user.u2[0].name
}

# iam_inline_policies.py の題材
resource "aws_iam_user_policy" "u1_inline" {
  count = local.b
  name  = "inline-sample"
  user  = aws_iam_user.u1[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:ListBucket"]
      Resource = "*"
    }]
  })
}

# iam_admin_policy_entities.py の題材。2/5 に detach して検出されなくなることを確認する
resource "aws_iam_user_policy_attachment" "u2_admin" {
  count      = local.b
  user       = aws_iam_user.u2[0].name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"

  lifecycle {
    ignore_changes = all # 2/5 に detach するので差分を無視
  }
}

# iam_access_key_last_used.py で「使用済み／未使用」の差を出すため、
# user1 のキーだけ1回だけ API を叩いておく。反映まで数分かかる。
resource "terraform_data" "u1_key_use" {
  count = local.b

  triggers_replace = [aws_iam_access_key.u1[0].id]

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      # IAM の伝播待ち
      sleep 15
      AWS_ACCESS_KEY_ID='${aws_iam_access_key.u1[0].id}' \
      AWS_SECRET_ACCESS_KEY='${aws_iam_access_key.u1[0].secret}' \
      AWS_SESSION_TOKEN= \
      aws sts get-caller-identity --region ${var.region} >/dev/null
      echo "user1 key used once"
    EOT
  }
}

# クロスアカウント許可の検出対象（iam_roles_trust_policy.py）
data "aws_iam_policy_document" "cross_account_assume" {
  count = local.b

  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${local.account}:root"]
    }
  }
}

resource "aws_iam_role" "cross_account_sample" {
  count              = local.b
  name               = "${local.name}-cross-account-sample"
  assume_role_policy = data.aws_iam_policy_document.cross_account_assume[0].json
}

resource "aws_iam_role_policy_attachment" "cross_account_sample" {
  count      = local.b
  role       = aws_iam_role.cross_account_sample[0].name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# ------------------------------------------------------------------
# SSM Parameter Store
# ------------------------------------------------------------------

resource "aws_ssm_parameter" "db_host" {
  count = local.b
  name  = "/${local.name}/app/db-host"
  type  = "String"
  value = "db.example.internal"
}

resource "aws_ssm_parameter" "db_user" {
  count = local.b
  name  = "/${local.name}/app/db-user"
  type  = "String"
  value = "appuser"
}

# WithDecryption の有無で差が出る題材
resource "aws_ssm_parameter" "db_password" {
  count = local.b
  name  = "/${local.name}/app/db-password"
  type  = "SecureString"
  value = "dummy-password"
}

# ------------------------------------------------------------------
# Secrets Manager（$0.40/月）
# ------------------------------------------------------------------

resource "aws_secretsmanager_secret" "db" {
  count = local.b
  name  = "${local.name}/db"

  # 既定は30日の復旧待機。学習用なので即時削除にする
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db" {
  count     = local.b
  secret_id = aws_secretsmanager_secret.db[0].id

  secret_string = jsonencode({
    username = "appuser"
    password = "dummy"
    host     = "db.example.internal"
  })

  # 2/7 に put_secret_value で更新するため差分を無視
  lifecycle {
    ignore_changes = [secret_string]
  }
}
