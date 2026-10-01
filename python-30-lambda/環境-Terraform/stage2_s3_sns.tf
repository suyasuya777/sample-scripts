# ==================================================================
# S3 / SNS（3/4 構築）  削除 3/31
#   enable_s3_sns = true
#
#   - s3_event_integration : S3イベントの構造とトリガ（3/4・3/5）
#   - s3_presigned_url     : 署名付きURL（3/7）
#   - sns_publisher        : SNS発行とフィルタ（3/7）
# ==================================================================

locals {
  s3sns = var.enable_s3_sns ? 1 : 0
}

# ------------------------------------------------------------------
# S3 バケット
#   uploads/ に置かれたものだけを処理する。
#   出力を同じプレフィックスに書くと無限ループになるため out/ を分けてある（3/5）
# ------------------------------------------------------------------

resource "aws_s3_bucket" "data" {
  count         = local.s3sns
  bucket        = "${local.name}-data-${local.account}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "data" {
  count  = local.s3sns
  bucket = aws_s3_bucket.data[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "s3_event" {
  count = local.s3sns

  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.data[0].arn}/*"]
  }
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.data[0].arn}/out/*"]
  }
}

module "fn_s3_event" {
  count  = local.s3sns
  source = "./modules/lambda_fn"

  name               = "${local.name}-s3-event-integration"
  source_dir         = "${local.src}/s3_event_integration"
  handler            = "s3_event_integration.lambda_handler"
  timeout            = 30
  memory_size        = 256
  policy_json        = data.aws_iam_policy_document.s3_event[0].json
  log_retention_days = var.log_retention_days

  environment = {
    OUTPUT_PREFIX = "out/"
  }
}

resource "aws_lambda_permission" "s3_event" {
  count         = local.s3sns
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = module.fn_s3_event[0].function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data[0].arn
}

resource "aws_s3_bucket_notification" "data" {
  count  = local.s3sns
  bucket = aws_s3_bucket.data[0].id

  lambda_function {
    lambda_function_arn = module.fn_s3_event[0].arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_permission.s3_event]
}

# ------------------------------------------------------------------
# 署名付きURL（3/7）
#   発行されるURLの権限は「この実行ロールの権限」になる点が論点
# ------------------------------------------------------------------

data "aws_iam_policy_document" "presign" {
  count = local.s3sns

  statement {
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${aws_s3_bucket.data[0].arn}/*"]
  }
}

module "fn_presigned" {
  count  = local.s3sns
  source = "./modules/lambda_fn"

  name               = "${local.name}-s3-presigned-url"
  source_dir         = "${local.src}/s3_presigned_url"
  handler            = "s3_presigned_url.lambda_handler"
  policy_json        = data.aws_iam_policy_document.presign[0].json
  log_retention_days = var.log_retention_days

  environment = {
    BUCKET_NAME = aws_s3_bucket.data[0].id
    EXPIRES_IN  = "300"
  }
}

# ------------------------------------------------------------------
# SNS（3/7）
#   標準トピックとFIFOトピックの両方を用意する
# ------------------------------------------------------------------

resource "aws_sns_topic" "main" {
  count = local.s3sns
  name  = "${local.name}-topic"
}

resource "aws_sns_topic" "fifo" {
  count                       = local.s3sns
  name                        = "${local.name}-topic.fifo"
  fifo_topic                  = true
  content_based_deduplication = true
}

# protocol = "email" は確認が手動。届いたメールのリンクを踏むこと
resource "aws_sns_topic_subscription" "email" {
  count     = local.s3sns
  topic_arn = aws_sns_topic.main[0].arn
  protocol  = "email"
  endpoint  = var.notification_email

  lifecycle {
    ignore_changes = [id]
  }
}

data "aws_iam_policy_document" "sns_publish" {
  count = local.s3sns

  statement {
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.main[0].arn, aws_sns_topic.fifo[0].arn]
  }
}

module "fn_sns_publisher" {
  count  = local.s3sns
  source = "./modules/lambda_fn"

  name               = "${local.name}-sns-publisher"
  source_dir         = "${local.src}/sns_publisher"
  handler            = "sns_publisher.lambda_handler"
  policy_json        = data.aws_iam_policy_document.sns_publish[0].json
  log_retention_days = var.log_retention_days

  environment = {
    TOPIC_ARN      = aws_sns_topic.main[0].arn
    FIFO_TOPIC_ARN = aws_sns_topic.fifo[0].arn
  }
}
