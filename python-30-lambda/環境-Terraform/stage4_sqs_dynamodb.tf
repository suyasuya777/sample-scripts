# ==================================================================
# SQS（3/15）/ DynamoDB（3/18）  削除 3/31
#   enable_sqs = true / enable_dynamodb = true
#
#   3月の山場。部分失敗（3/17）と冪等性（3/21）の実測がここ。
# ==================================================================

locals {
  sqs = var.enable_sqs ? 1 : 0
  ddb = var.enable_dynamodb ? 1 : 0
}

# ------------------------------------------------------------------
# SQS : メインキュー + DLQ + SNS→SQS 購読
# ------------------------------------------------------------------

resource "aws_sqs_queue" "dlq" {
  count                     = local.sqs
  name                      = "${local.name}-dlq"
  message_retention_seconds = 345600
}

resource "aws_sqs_queue" "main" {
  count                      = local.sqs
  name                       = "${local.name}-main"
  visibility_timeout_seconds = 60 # Lambda のタイムアウト以上にすること

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq[0].arn
    maxReceiveCount     = 3
  })
}

# SNS → SQS 購読。3/16 の「body に SNS の JSON が入れ子になる」の題材。
# raw_message_delivery = false のままにしておくのが重要（true にすると入れ子が消える）
resource "aws_sqs_queue" "from_sns" {
  count                      = local.sqs * local.s3sns
  name                       = "${local.name}-from-sns"
  visibility_timeout_seconds = 60
}

resource "aws_sqs_queue_policy" "from_sns" {
  count     = local.sqs * local.s3sns
  queue_url = aws_sqs_queue.from_sns[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "sns.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.from_sns[0].arn
      Condition = {
        ArnEquals = { "aws:SourceArn" = aws_sns_topic.main[0].arn }
      }
    }]
  })
}

resource "aws_sns_topic_subscription" "to_sqs" {
  count                = local.sqs * local.s3sns
  topic_arn            = aws_sns_topic.main[0].arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.from_sns[0].arn
  raw_message_delivery = false
}

data "aws_iam_policy_document" "sqs_consumer" {
  count = local.sqs

  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ChangeMessageVisibility",
    ]
    resources = compact([
      aws_sqs_queue.main[0].arn,
      local.s3sns == 1 ? aws_sqs_queue.from_sns[0].arn : "",
    ])
  }
}

module "fn_sqs" {
  count  = local.sqs
  source = "./modules/lambda_fn"

  name               = "${local.name}-sqs-sns-integration"
  source_dir         = "${local.src}/sqs_sns_integration"
  handler            = "sqs_sns_integration.lambda_handler"
  timeout            = 30
  policy_json        = data.aws_iam_policy_document.sqs_consumer[0].json
  log_retention_days = var.log_retention_days
}

# 3/17 の演習の中心。
# function_response_types を一度コメントアウトして apply し、
# バッチ10件中1件失敗させると10件すべてが再試行されることを確認する。
# そのあと戻して、失敗した1件だけになることを見る。
resource "aws_lambda_event_source_mapping" "sqs_main" {
  count            = local.sqs
  event_source_arn = aws_sqs_queue.main[0].arn
  function_name    = module.fn_sqs[0].arn
  batch_size       = 10

  function_response_types = ["ReportBatchItemFailures"]
}

resource "aws_lambda_event_source_mapping" "sqs_from_sns" {
  count            = local.sqs * local.s3sns
  event_source_arn = aws_sqs_queue.from_sns[0].arn
  function_name    = module.fn_sqs[0].arn
  batch_size       = 5

  function_response_types = ["ReportBatchItemFailures"]
}

# ------------------------------------------------------------------
# DynamoDB : Streams 有効テーブル + 冪等性テーブル
# ------------------------------------------------------------------

resource "aws_dynamodb_table" "items" {
  count        = local.ddb
  name         = "${local.name}-items"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}

# 3/21 の改造先。set() による冪等性判定をここに置き換える。
# TTL で古いキーが自動削除されるようにしてある。
resource "aws_dynamodb_table" "idempotency" {
  count        = local.ddb
  name         = "${local.name}-idempotency"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}

data "aws_iam_policy_document" "streams_consumer" {
  count = local.ddb

  statement {
    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:DescribeStream",
      "dynamodb:ListStreams",
    ]
    resources = [aws_dynamodb_table.items[0].stream_arn]
  }
}

module "fn_streams" {
  count  = local.ddb
  source = "./modules/lambda_fn"

  name               = "${local.name}-dynamodb-streams-trigger"
  source_dir         = "${local.src}/dynamodb_streams_trigger"
  handler            = "dynamodb_streams_trigger.lambda_handler"
  timeout            = 30
  policy_json        = data.aws_iam_policy_document.streams_consumer[0].json
  log_retention_days = var.log_retention_days
}

# 失敗したバッチでシャードが止まるのを防ぐ設定。
# 3/18 に一度これらを外して、詰まる挙動を見てから戻すとよい。
resource "aws_lambda_event_source_mapping" "streams" {
  count             = local.ddb
  event_source_arn  = aws_dynamodb_table.items[0].stream_arn
  function_name     = module.fn_streams[0].arn
  starting_position = "LATEST"
  batch_size        = 10

  maximum_retry_attempts             = 2
  bisect_batch_on_function_error     = true
  maximum_record_age_in_seconds      = 3600
  function_response_types            = ["ReportBatchItemFailures"]
}

# ------------------------------------------------------------------
# error_handling_dlq（3/19・3/21）
#   関数設定の DLQ（dead_letter_config）と、
#   コードが自分で send_message する DLQ の両方を用意して差を見る
# ------------------------------------------------------------------

data "aws_iam_policy_document" "error_handling" {
  count = local.ddb * local.sqs

  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.dlq[0].arn]
  }
  # 3/21 の冪等性改造で使う
  statement {
    actions   = ["dynamodb:PutItem", "dynamodb:GetItem"]
    resources = [aws_dynamodb_table.idempotency[0].arn]
  }
}

module "fn_error_handling" {
  count  = local.ddb * local.sqs
  source = "./modules/lambda_fn"

  name               = "${local.name}-error-handling-dlq"
  source_dir         = "${local.src}/error_handling_dlq"
  handler            = "error_handling_dlq.lambda_handler"
  timeout            = 30
  policy_json        = data.aws_iam_policy_document.error_handling[0].json
  log_retention_days = var.log_retention_days

  # 関数設定としての DLQ。非同期呼び出しが2回のリトライで失敗したあと AWS が自動で送る
  dlq_target_arn = aws_sqs_queue.dlq[0].arn

  environment = {
    DLQ_URL            = aws_sqs_queue.dlq[0].url
    IDEMPOTENCY_TABLE  = aws_dynamodb_table.idempotency[0].name
    IDEMPOTENCY_TTL    = "86400"
  }
}

# Destinations（OnFailure）。関数設定のDLQとの違いを見る題材。
# 失敗した「呼び出しの文脈ごと」送られる点がDLQと異なる。
resource "aws_lambda_function_event_invoke_config" "error_handling" {
  count         = local.ddb * local.sqs
  function_name = module.fn_error_handling[0].function_name

  maximum_retry_attempts = 2

  destination_config {
    on_failure {
      destination = aws_sqs_queue.dlq[0].arn
    }
  }
}
