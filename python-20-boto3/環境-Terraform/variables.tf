variable "region" {
  description = "使用リージョン。1つに固定すること（消し忘れ防止）"
  type        = string
  default     = "ap-northeast-1"
}

variable "name_prefix" {
  description = "全リソース名の接頭辞"
  type        = string
  default     = "boto3-study"
}

variable "notification_email" {
  description = "SNS サブスクリプションと SES 検証に使う自分のメールアドレス"
  type        = string
}

variable "my_ip_cidr" {
  description = "自宅IPなど。S3バケットポリシーの条件付きDenyの題材に使う（例 203.0.113.10/32）"
  type        = string
  default     = "203.0.113.10/32"
}

# ------------------------------------------------------------------
# セットの有効化フラグ
# 環境タイムラインに合わせて terraform.tfvars で true にしていく
# ------------------------------------------------------------------

variable "enable_set_b" {
  description = "S3大量オブジェクト・IAM・SSM・Secrets。1/19 に true"
  type        = bool
  default     = false
}

variable "enable_set_c" {
  description = "CloudWatch Logs のロググループとイベント。2/7 に true"
  type        = bool
  default     = false
}

variable "enable_set_d" {
  description = "Lambda・SQS/SNS・SES。2/14 に true"
  type        = bool
  default     = false
}

variable "enable_set_e1" {
  description = "RDS（db.t4g.micro）。2/21 に true"
  type        = bool
  default     = false
}

variable "enable_set_e2" {
  description = "Aurora・EKS。2/23 の午前に true、当日中に false に戻す"
  type        = bool
  default     = false
}

# ------------------------------------------------------------------
# セットA の調整用
# ------------------------------------------------------------------

variable "ecs_desired_count" {
  description = "ECS サービスの初期タスク数。以降は CLI で変更するので ignore_changes 対象"
  type        = number
  default     = 2
}

variable "s3_object_count" {
  description = "paginator 確認用に投入するオブジェクト数。1000超が必須"
  type        = number
  default     = 1200
}

variable "db_password" {
  description = "学習用RDSのパスワード。state に平文で入る点に注意"
  type        = string
  default     = "StudyOnly12345!"
  sensitive   = true
}
