# ==================================================================
# セットD : Lambda / SQS / SNS / SES
# 構築 2/14  削除 2/28
# enable_set_d = true で作られる
# ==================================================================

locals {
  d = var.enable_set_d ? 1 : 0
}

# ------------------------------------------------------------------
# Lambda : 3関数
#   ok      … 正常系
#   canary  … publish_version / alias / routing_config の題材
#   config  … update_function_configuration の題材
# {"fail": true} を渡すと例外を投げる。FunctionError の観測用。
# ------------------------------------------------------------------

data "archive_file" "lambda" {
  count       = local.d
  type        = "zip"
  output_path = "${path.module}/.build/lambda.zip"

  source {
    filename = "lambda_function.py"
    content  = <<-PY
      import os


      def lambda_handler(event, context):
          if event.get("fail"):
              raise RuntimeError("intentional failure for FunctionError check")
          return {
              "ok": True,
              "stage": os.environ.get("STAGE", "unset"),
              "version": context.function_version,
          }
    PY
  }
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  count              = local.d
  name               = "${local.name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  count      = local.d
  role       = aws_iam_role.lambda[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "fn" {
  for_each = var.enable_set_d ? toset(["ok", "canary", "config"]) : toset([])

  function_name    = "${local.name}-${each.key}"
  role             = aws_iam_role.lambda[0].arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda[0].output_path
  source_code_hash = data.archive_file.lambda[0].output_base64sha256
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      STAGE = "dev"
    }
  }

  # 2/16 に update_function_configuration で書き換えるため差分を無視
  lifecycle {
    ignore_changes = [environment, timeout, memory_size]
  }
}

# ------------------------------------------------------------------
# SQS : メインキュー + DLQ（maxReceiveCount = 2）
# ------------------------------------------------------------------

resource "aws_sqs_queue" "dlq" {
  count                     = local.d
  name                      = "${local.name}-dlq"
  message_retention_seconds = 345600 # 4日
}

resource "aws_sqs_queue" "main" {
  count                      = local.d
  name                       = "${local.name}-main"
  visibility_timeout_seconds = 30

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq[0].arn
    maxReceiveCount     = 2
  })
}

# sqs_dlq_reprocess.py の題材。DLQ にメッセージを3件仕込む
resource "terraform_data" "seed_dlq" {
  count = local.d

  triggers_replace = [aws_sqs_queue.dlq[0].id]

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -euo pipefail
      for i in 1 2 3; do
        aws sqs send-message \
          --region ${var.region} \
          --queue-url "${aws_sqs_queue.dlq[0].url}" \
          --message-body "stuck-message-$i" >/dev/null
      done
      echo "seeded 3 messages into DLQ"
    EOT
  }
}

# ------------------------------------------------------------------
# SNS : メール購読（確認メールのリンクを手で踏む必要がある）
# ------------------------------------------------------------------

resource "aws_sns_topic" "this" {
  count = local.d
  name  = local.name
}

# 注意: protocol = "email" は確認が手動なので、apply 直後は
# PendingConfirmation のままになる。届いたメールのリンクを踏むこと。
resource "aws_sns_topic_subscription" "email" {
  count     = local.d
  topic_arn = aws_sns_topic.this[0].arn
  protocol  = "email"
  endpoint  = var.notification_email

  lifecycle {
    ignore_changes = [id]
  }
}

# ------------------------------------------------------------------
# SES : サンドボックスのまま。検証済みアドレス宛にのみ送れる
# ------------------------------------------------------------------

resource "aws_sesv2_email_identity" "self" {
  count          = local.d
  email_identity = var.notification_email
}

# ses_send_email.py で使う設定セット（イベント追跡の題材）
resource "aws_sesv2_configuration_set" "this" {
  count                  = local.d
  configuration_set_name = local.name

  reputation_options {
    reputation_metrics_enabled = true
  }

  sending_options {
    sending_enabled = true
  }
}
