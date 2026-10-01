# ==================================================================
# 基盤（3/1）  削除 3/31
#   フラグなし。terraform apply した時点で作られる。
#
#   - eventbridge_scheduled_job : デプロイの型を確認する1本目
#   - secrets_manager_ssm       : コールドスタートとキャッシュの実測用（3/3）
# ==================================================================

# ------------------------------------------------------------------
# 3/2 : EventBridge スケジュール実行
# ------------------------------------------------------------------

# eventbridge_scheduled_job.py は DynamoDB のテーブルを scan / delete する。
# テーブル本体は 4/1（enable_dynamodb）まで存在しないが、モジュールに
# ignore_changes = [environment] が入っているため、環境変数は「作成時」に
# 入れておかないと後から足せない。そこで ARN と名前を文字列で先に渡しておく
# （stage4 のリソースを参照すると 3/15 に apply できなくなるため、あえて文字列）。
# 3/15 は DynamoDB を呼ばない形にコードを直して動かし、4/1 に戻す。手順書 §4 参照。
data "aws_iam_policy_document" "scheduled" {
  statement {
    actions   = ["dynamodb:Scan", "dynamodb:DeleteItem"]
    resources = ["arn:aws:dynamodb:${local.region}:${local.account}:table/${local.name}-items"]
  }
}

module "fn_scheduled" {
  source = "./modules/lambda_fn"

  name               = "${local.name}-eventbridge-scheduled-job"
  source_dir         = "${local.src}/eventbridge_scheduled_job"
  handler            = "eventbridge_scheduled_job.lambda_handler"
  timeout            = 30
  policy_json        = data.aws_iam_policy_document.scheduled.json
  log_retention_days = var.log_retention_days

  environment = {
    STAGE      = "study"
    TABLE_NAME = "${local.name}-items" # 実体は 4/1 に作られる
  }
}

# cron式は UTC で書く。下は JST 10:00（UTC 01:00）に毎日実行する例
resource "aws_cloudwatch_event_rule" "scheduled" {
  name                = "${local.name}-schedule"
  description         = "3/2 の定期実行確認用"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "scheduled" {
  rule = aws_cloudwatch_event_rule.scheduled.name
  arn  = module.fn_scheduled.arn
}

# これを忘れると EventBridge からの起動が拒否される。
# 3/2 の「リソースベースポリシー」の題材。
resource "aws_lambda_permission" "scheduled" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.fn_scheduled.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled.arn
}

# ------------------------------------------------------------------
# 3/3 : Secrets Manager / SSM Parameter Store
# ------------------------------------------------------------------

resource "aws_secretsmanager_secret" "db" {
  name                    = "${local.name}/db"
  recovery_window_in_days = 0 # 学習用。既定の30日待機を無効化
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id
  secret_string = jsonencode({
    username = "appuser"
    password = var.db_password
    host     = "db.example.internal"
    dbname   = "studydb"
  })
}

resource "aws_ssm_parameter" "app_stage" {
  name  = "/${local.name}/app/stage"
  type  = "String"
  value = "dev"
}

resource "aws_ssm_parameter" "app_endpoint" {
  name  = "/${local.name}/app/endpoint"
  type  = "String"
  value = "https://example.internal/api"
}

# WithDecryption=True が KMS 権限を要求することを確認する題材
resource "aws_ssm_parameter" "app_token" {
  name  = "/${local.name}/app/token"
  type  = "SecureString"
  value = "dummy-token-value"
}

data "aws_iam_policy_document" "secrets_reader" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.db.arn]
  }
  statement {
    actions   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
    resources = ["arn:aws:ssm:${local.region}:${local.account}:parameter/${local.name}/*"]
  }
  # SecureString の復号に必要。この statement を外して AccessDenied を出すのが 3/3 の演習
  statement {
    actions   = ["kms:Decrypt"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["ssm.${local.region}.amazonaws.com", "secretsmanager.${local.region}.amazonaws.com"]
    }
  }
}

module "fn_secrets" {
  source = "./modules/lambda_fn"

  name               = "${local.name}-secrets-manager-ssm"
  source_dir         = "${local.src}/secrets_manager_ssm"
  handler            = "secrets_manager_ssm.lambda_handler"
  timeout            = 15
  policy_json        = data.aws_iam_policy_document.secrets_reader.json
  log_retention_days = var.log_retention_days

  environment = {
    SECRET_NAME   = aws_secretsmanager_secret.db.name
    PARAM_PREFIX  = "/${local.name}/app"
    PARAM_STAGE   = aws_ssm_parameter.app_stage.name
    PARAM_TOKEN   = aws_ssm_parameter.app_token.name
  }
}
