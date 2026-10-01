# ==================================================================
# API Gateway（3/10）/ Cognito（3/11）  削除 3/31
#   enable_apigw = true / enable_cognito = true
# ==================================================================

locals {
  apigw   = var.enable_apigw ? 1 : 0
  cognito = var.enable_cognito ? 1 : 0
}

# ------------------------------------------------------------------
# HTTP API + rest_api
#
# 教材の rest_api.py は event["httpMethod"] を読んでいる。これは
# ペイロード形式 1.0（REST API と同じ形）なので、HTTP API を使いつつ
# payload_format_version を "1.0" に指定して合わせている。
#
# 3/8 の「REST API と HTTP API で event の形式が違う」を体験するには、
# 下の payload_format_version を "2.0" に変えて apply し、
# event が {requestContext: {http: {method: ...}}} に変わることと、
# コードが 405 を返すようになることを確認するとよい。
# ------------------------------------------------------------------

module "fn_rest_api" {
  count  = local.apigw
  source = "./modules/lambda_fn"

  name               = "${local.name}-rest-api"
  source_dir         = "${local.src}/rest_api"
  handler            = "rest_api.lambda_handler"
  timeout            = 10
  log_retention_days = var.log_retention_days
}

resource "aws_apigatewayv2_api" "http" {
  count         = local.apigw
  name          = "${local.name}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
  }
}

resource "aws_apigatewayv2_integration" "rest_api" {
  count                  = local.apigw
  api_id                 = aws_apigatewayv2_api.http[0].id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.fn_rest_api[0].invoke_arn
  payload_format_version = "1.0" # 教材のコードに合わせる。2.0 に変えると event の形が変わる
}

resource "aws_apigatewayv2_route" "items_collection" {
  count     = local.apigw
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "ANY /items"
  target    = "integrations/${aws_apigatewayv2_integration.rest_api[0].id}"
}

resource "aws_apigatewayv2_route" "items_item" {
  count     = local.apigw
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "ANY /items/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.rest_api[0].id}"
}

resource "aws_cloudwatch_log_group" "apigw" {
  count             = local.apigw
  name              = "/aws/apigateway/${local.name}-http-api"
  retention_in_days = var.log_retention_days
}

resource "aws_apigatewayv2_stage" "default" {
  count       = local.apigw
  api_id      = aws_apigatewayv2_api.http[0].id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigw[0].arn
    format = jsonencode({
      requestId       = "$context.requestId"
      routeKey        = "$context.routeKey"
      status          = "$context.status"
      integrationErr  = "$context.integrationErrorMessage"
      responseLatency = "$context.responseLatency"
    })
  }
}

resource "aws_lambda_permission" "apigw" {
  count         = local.apigw
  statement_id  = "AllowApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.fn_rest_api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http[0].execution_arn}/*/*"
}

# ------------------------------------------------------------------
# Cognito + Pre Sign-up トリガ
#   このトリガだけは「event を書き換えて返す」型である点が他と違う
# ------------------------------------------------------------------

module "fn_cognito" {
  count  = local.cognito
  source = "./modules/lambda_fn"

  name               = "${local.name}-cognito-pre-signup"
  source_dir         = "${local.src}/cognito_pre_signup_trigger"
  handler            = "cognito_pre_signup_trigger.lambda_handler"
  log_retention_days = var.log_retention_days

  environment = {
    ALLOWED_DOMAIN = var.allowed_signup_domain
  }
}

resource "aws_cognito_user_pool" "this" {
  count = local.cognito
  name  = "${local.name}-pool"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  lambda_config {
    pre_sign_up = module.fn_cognito[0].arn
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
}

resource "aws_cognito_user_pool_client" "this" {
  count        = local.cognito
  name         = "${local.name}-client"
  user_pool_id = aws_cognito_user_pool.this[0].id

  generate_secret = false
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
  ]
}

resource "aws_lambda_permission" "cognito" {
  count         = local.cognito
  statement_id  = "AllowCognito"
  action        = "lambda:InvokeFunction"
  function_name = module.fn_cognito[0].function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.this[0].arn
}
