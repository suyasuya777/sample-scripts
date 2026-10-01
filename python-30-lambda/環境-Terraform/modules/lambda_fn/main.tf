# ==================================================================
# Lambda 関数 1本ぶんの型
#   関数 + 実行ロール + ロググループ をセットで作る。
#
# ロググループを明示的に作るのは、Lambda に自動生成させると
# 保持期間が「無期限」になり、消し忘れると課金が積み上がるため。
# （2月 2/11 の「保持期間未設定のロググループ」の話と同じ論点）
# ==================================================================

data "archive_file" "this" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.root}/.build/${var.name}.zip"
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "this" {
  name               = "${var.name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

# 最小の出発点。ここから AccessDenied を読みながら policy_json で足していく
resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# VPC に入れる場合は ENI の作成・削除権限が要る
resource "aws_iam_role_policy_attachment" "vpc" {
  count      = var.vpc_config == null ? 0 : 1
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "xray" {
  count      = var.tracing_mode == "Active" ? 1 : 0
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

resource "aws_iam_role_policy" "extra" {
  count  = var.policy_json == null ? 0 : 1
  name   = "${var.name}-extra"
  role   = aws_iam_role.this.id
  policy = var.policy_json
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "this" {
  function_name = var.name
  role          = aws_iam_role.this.arn
  handler       = var.handler
  runtime       = var.runtime
  timeout       = var.timeout
  memory_size   = var.memory_size
  layers        = var.layers

  filename         = data.archive_file.this.output_path
  source_code_hash = data.archive_file.this.output_base64sha256

  reserved_concurrent_executions = var.reserved_concurrency

  dynamic "environment" {
    for_each = length(var.environment) > 0 ? [1] : []
    content {
      variables = var.environment
    }
  }

  dynamic "vpc_config" {
    for_each = var.vpc_config == null ? [] : [var.vpc_config]
    content {
      subnet_ids         = vpc_config.value.subnet_ids
      security_group_ids = vpc_config.value.security_group_ids
    }
  }

  dynamic "dead_letter_config" {
    for_each = var.dlq_target_arn == null ? [] : [var.dlq_target_arn]
    content {
      target_arn = dead_letter_config.value
    }
  }

  tracing_config {
    mode = var.tracing_mode
  }

  # 3/21 の冪等性改造など、学習中にコンソールから設定を触ることがある。
  # 意図せず巻き戻さないよう環境変数の差分は無視する。
  lifecycle {
    ignore_changes = [environment]
  }

  depends_on = [aws_cloudwatch_log_group.this]
}
