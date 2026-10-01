variable "region" {
  description = "使用リージョン。1つに固定すること"
  type        = string
  default     = "ap-northeast-1"
}

variable "name_prefix" {
  description = "全リソース名の接頭辞"
  type        = string
  default     = "lambda-study"
}

variable "samples_dir" {
  description = "Lambda 実務サンプル集を展開したディレクトリの絶対パス（末尾スラッシュなし）"
  type        = string
}

variable "notification_email" {
  description = "SNS購読・SES送信先に使う自分のメールアドレス。2月にSESで検証済みのものを使う"
  type        = string
}

variable "allowed_signup_domain" {
  description = "Cognito Pre Sign-up トリガで許可するメールドメイン"
  type        = string
  default     = "example.com"
}

# ------------------------------------------------------------------
# ステージ有効化フラグ（3月の環境タイムラインに対応）
#   3/1 (月)  基盤（フラグなし。apply した時点で作られる）
#   3/4 (木)  enable_s3_sns     = true
#   3/10(水)  enable_apigw      = true
#   3/11(木)  enable_cognito    = true
#   3/15(月)  enable_sqs        = true
#   3/18(木)  enable_dynamodb   = true
#   3/22(月)  enable_integration= true
#   3/25(木)  enable_rds        = true  → 3/26 の作業後に false に戻す
#   3/28(日)  enable_sfn        = true
#   3/29(月)  enable_powertools = true
#   3/31(水)  terraform destroy
# ------------------------------------------------------------------

variable "enable_s3_sns" {
  description = "S3バケット・SNSトピックと s3_event_integration / s3_presigned_url / sns_publisher"
  type        = bool
  default     = false
}

variable "enable_apigw" {
  description = "HTTP API と rest_api"
  type        = bool
  default     = false
}

variable "enable_cognito" {
  description = "Cognito ユーザープールと cognito_pre_signup_trigger"
  type        = bool
  default     = false
}

variable "enable_sqs" {
  description = "SQS メインキュー・DLQ・SNS購読と sqs_sns_integration"
  type        = bool
  default     = false
}

variable "enable_dynamodb" {
  description = "DynamoDB テーブル（Streams有効）・冪等性テーブルと dynamodb_streams_trigger / error_handling_dlq"
  type        = bool
  default     = false
}

variable "enable_integration" {
  description = "api_gateway_dynamodb_ses_integration（3ファイル構成）"
  type        = bool
  default     = false
}

variable "enable_rds" {
  description = "VPC・RDS・RDS Proxy・VPCエンドポイントと vpc_rds_connection。3/26 中に false に戻すこと（約 $1.3/日）"
  type        = bool
  default     = false
}

variable "enable_rds_proxy" {
  description = "RDS Proxy を作るか。約 $0.7/日。省略しても学習は成立する"
  type        = bool
  default     = true
}

variable "enable_sfn" {
  description = "Step Functions ステートマシンと step_functions_trigger"
  type        = bool
  default     = false
}

variable "enable_powertools" {
  description = "powertools_middleware（X-Ray 有効）"
  type        = bool
  default     = false
}

# ------------------------------------------------------------------
# 調整用
# ------------------------------------------------------------------

variable "powertools_layer_version" {
  description = "AWS 提供の Powertools マネージドレイヤーのバージョン番号。最新値は AWS ドキュメントで確認すること"
  type        = number
  default     = 3
}

variable "powertools_layer_account" {
  description = "Powertools マネージドレイヤーの提供アカウント。ほとんどのリージョンで共通"
  type        = string
  default     = "017000801446"
}

variable "db_password" {
  description = "学習用RDSのパスワード。state に平文で入る"
  type        = string
  default     = "StudyOnly12345!"
  sensitive   = true
}

variable "log_retention_days" {
  description = "Lambda ロググループの保持期間"
  type        = number
  default     = 7
}
