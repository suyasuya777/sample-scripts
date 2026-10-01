variable "name" {
  description = "関数名"
  type        = string
}

variable "source_dir" {
  description = "zip 化するソースディレクトリ"
  type        = string
}

variable "handler" {
  description = "ハンドラ。<ファイル名>.lambda_handler"
  type        = string
}

variable "runtime" {
  type    = string
  default = "python3.12"
}

variable "timeout" {
  type    = number
  default = 10
}

variable "memory_size" {
  type    = number
  default = 128
}

variable "environment" {
  description = "環境変数"
  type        = map(string)
  default     = {}
}

variable "policy_json" {
  description = "実行ロールに追加するインラインポリシー（JSON）。null なら基本権限のみ"
  type        = string
  default     = null
}

variable "layers" {
  type    = list(string)
  default = []
}

variable "vpc_config" {
  description = "VPC に入れる場合のサブネットとSG"
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}

variable "tracing_mode" {
  description = "PassThrough または Active（X-Ray）"
  type        = string
  default     = "PassThrough"
}

variable "dlq_target_arn" {
  description = "非同期呼び出し失敗時の DLQ。関数設定としての DLQ であり、アプリが自分で送るものとは別"
  type        = string
  default     = null
}

variable "reserved_concurrency" {
  description = "予約済み同時実行数。-1 で未設定"
  type        = number
  default     = -1
}

variable "log_retention_days" {
  type    = number
  default = 7
}
