# ==================================================================
# Step Functions（3/28）/ Powertools・X-Ray（3/29〜3/30）  削除 3/31
#   enable_sfn = true / enable_powertools = true
# ==================================================================

locals {
  sfn = var.enable_sfn ? 1 : 0
  pt  = var.enable_powertools ? 1 : 0
}

# ------------------------------------------------------------------
# step_functions_trigger
#   同期タスクと waitForTaskToken の両方を1本の関数で扱う。
#   send_task_success / send_task_failure の権限が要る。
# ------------------------------------------------------------------

data "aws_iam_policy_document" "sfn_callback" {
  count = local.sfn

  statement {
    actions   = ["states:SendTaskSuccess", "states:SendTaskFailure", "states:SendTaskHeartbeat"]
    resources = ["*"]
  }
}

module "fn_sfn_task" {
  count  = local.sfn
  source = "./modules/lambda_fn"

  name               = "${local.name}-step-functions-trigger"
  source_dir         = "${local.src}/step_functions_trigger"
  handler            = "step_functions_trigger.lambda_handler"
  timeout            = 60
  policy_json        = data.aws_iam_policy_document.sfn_callback[0].json
  log_retention_days = var.log_retention_days
}

data "aws_iam_policy_document" "sfn_assume" {
  count = local.sfn
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sfn" {
  count              = local.sfn
  name               = "${local.name}-sfn"
  assume_role_policy = data.aws_iam_policy_document.sfn_assume[0].json
}

resource "aws_iam_role_policy" "sfn" {
  count = local.sfn
  name  = "invoke-lambda"
  role  = aws_iam_role.sfn[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["lambda:InvokeFunction"]
      Resource = [module.fn_sfn_task[0].arn, "${module.fn_sfn_task[0].arn}:*"]
    }]
  })
}

# 直列2タスク。前のタスクの出力が次のタスクの入力になることを確認する（3/28）
resource "aws_sfn_state_machine" "sequential" {
  count    = local.sfn
  name     = "${local.name}-sequential"
  role_arn = aws_iam_role.sfn[0].arn

  definition = jsonencode({
    Comment = "3/28 : 同期タスクの直列実行"
    StartAt = "First"
    States = {
      First = {
        Type     = "Task"
        Resource = module.fn_sfn_task[0].arn
        Next     = "Second"
        Retry = [{
          ErrorEquals     = ["States.TaskFailed"]
          IntervalSeconds = 2
          MaxAttempts     = 2
          BackoffRate     = 2.0
        }]
      }
      Second = {
        Type     = "Task"
        Resource = module.fn_sfn_task[0].arn
        End      = true
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next        = "Failed"
        }]
      }
      Failed = {
        Type  = "Fail"
        Cause = "second task failed"
      }
    }
  })
}

# waitForTaskToken。taskToken を渡して待機し、
# send_task_success が呼ばれるまで進まないことを確認する（3/28）
resource "aws_sfn_state_machine" "callback" {
  count    = local.sfn
  name     = "${local.name}-callback"
  role_arn = aws_iam_role.sfn[0].arn

  definition = jsonencode({
    Comment = "3/28 : waitForTaskToken パターン"
    StartAt = "WaitForCallback"
    States = {
      WaitForCallback = {
        Type       = "Task"
        Resource   = "arn:aws:states:::lambda:invoke.waitForTaskToken"
        TimeoutSeconds = 900
        Parameters = {
          FunctionName = module.fn_sfn_task[0].arn
          Payload = {
            "taskToken.$" = "$$.Task.Token"
            "params.$"    = "$"
          }
        }
        End = true
      }
    }
  })
}

# ------------------------------------------------------------------
# powertools_middleware（3/29）+ X-Ray（3/30）
#   Powertools は AWS 提供のマネージドレイヤーを使う。
#   バージョン番号は変わるので、最新値をドキュメントで確認して
#   powertools_layer_version を更新すること。
# ------------------------------------------------------------------

module "fn_powertools" {
  count  = local.pt
  source = "./modules/lambda_fn"

  name               = "${local.name}-powertools-middleware"
  source_dir         = "${local.src}/powertools_middleware"
  handler            = "powertools_middleware.lambda_handler"
  timeout            = 30
  tracing_mode       = "Active" # X-Ray 有効。IAM も自動で付く
  log_retention_days = var.log_retention_days

  layers = [
    "arn:aws:lambda:${local.region}:${var.powertools_layer_account}:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:${var.powertools_layer_version}"
  ]

  environment = {
    POWERTOOLS_SERVICE_NAME      = local.name
    POWERTOOLS_METRICS_NAMESPACE = "LambdaStudy"
    LOG_LEVEL                    = "INFO"
  }
}

# 3/10 の HTTP API に /powertools ルートを足して、
# APIGatewayProxyEvent データクラスの動作を実トリガで確認する
resource "aws_apigatewayv2_integration" "powertools" {
  count                  = local.pt * local.apigw
  api_id                 = aws_apigatewayv2_api.http[0].id
  integration_type       = "AWS_PROXY"
  integration_uri        = module.fn_powertools[0].invoke_arn
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_route" "powertools" {
  count     = local.pt * local.apigw
  api_id    = aws_apigatewayv2_api.http[0].id
  route_key = "ANY /powertools"
  target    = "integrations/${aws_apigatewayv2_integration.powertools[0].id}"
}

resource "aws_lambda_permission" "powertools_apigw" {
  count         = local.pt * local.apigw
  statement_id  = "AllowApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.fn_powertools[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http[0].execution_arn}/*/*"
}
