# ==================================================================
# api_gateway_dynamodb_ses_integration（3/22 構築）  削除 3/31
#   enable_integration = true
#
#   3ファイル構成（handler.py / db.py / mailer.py）。
#   source_dir でディレクトリごと zip 化するので、モジュール側は変更不要。
#
#   前提: enable_apigw = true（HTTP API に /records ルートを足すため）。
#   DynamoDB テーブルはこのファイルが自前で作るので enable_dynamodb は不要。
# ==================================================================

locals {
  integ = var.enable_integration ? 1 : 0
}

resource "aws_dynamodb_table" "integration" {
  count        = local.integ
  name         = "${local.name}-integration-items"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

data "aws_iam_policy_document" "integration" {
  count = local.integ

  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:DeleteItem",
      "dynamodb:UpdateItem",
    ]
    resources = [aws_dynamodb_table.integration[0].arn]
  }

  # SES はサンドボックスのまま。検証済みアドレス宛にのみ送れる
  statement {
    actions   = ["ses:SendEmail", "ses:SendRawEmail"]
    resources = ["*"]
  }
}

module "fn_integration" {
  count  = local.integ
  source = "./modules/lambda_fn"

  name               = "${local.name}-apigw-dynamodb-ses"
  source_dir         = "${local.src}/api_gateway_dynamodb_ses_integration"
  handler            = "handler.lambda_handler"
  timeout            = 30
  memory_size        = 256
  policy_json        = data.aws_iam_policy_document.integration[0].json
  log_retention_days = var.log_retention_days

  environment = {
    TABLE_NAME   = aws_dynamodb_table.integration[0].name
    NOTIFY_EMAIL = var.notification_email
    SES_SOURCE   = var.notification_email
  }
}

# ------------------------------------------------------------------
# 3/10 で作った HTTP API に /records ルートを追加する
# ------------------------------------------------------------------

resource "aws_apigatewayv2_integration" "integration" {
  count                  = local.integ * local.apigw
  api_id                 = aws_apigatewayv2_api.http[0].id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.fn_integration[0].invoke_arn
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_route" "records_collection" {
  count     = local.integ * local.apigw
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "ANY /records"
  target    = "integrations/${aws_apigatewayv2_integration.integration[0].id}"
}

resource "aws_apigatewayv2_route" "records_item" {
  count     = local.integ * local.apigw
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "ANY /records/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.integration[0].id}"
}

resource "aws_lambda_permission" "integration_apigw" {
  count         = local.integ * local.apigw
  statement_id  = "AllowApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.fn_integration[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http[0].execution_arn}/*/*"
}
