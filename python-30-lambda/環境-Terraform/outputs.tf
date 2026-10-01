output "fn_scheduled" {
  description = "3/2 : EventBridge 定期実行"
  value       = module.fn_scheduled.function_name
}

output "fn_secrets" {
  description = "3/3 : コールドスタートとキャッシュの実測対象"
  value       = module.fn_secrets.function_name
}

output "s3_bucket" {
  description = "3/4・3/5 : uploads/ にファイルを置くとトリガされる"
  value       = try(aws_s3_bucket.data[0].id, null)
}

output "sns_topic_arn" {
  value = try(aws_sns_topic.main[0].arn, null)
}

output "api_endpoint" {
  description = "3/10 : curl で叩く先。/items /items/{id} /records /powertools"
  value       = try(aws_apigatewayv2_api.http[0].api_endpoint, null)
}

output "cognito_user_pool_id" {
  value = try(aws_cognito_user_pool.this[0].id, null)
}

output "cognito_client_id" {
  description = "3/12 : aws cognito-idp sign-up に渡す"
  value       = try(aws_cognito_user_pool_client.this[0].id, null)
}

output "sqs_main_url" {
  description = "3/15〜3/17 : ここにメッセージを送って部分失敗を確認する"
  value       = try(aws_sqs_queue.main[0].url, null)
}

output "sqs_dlq_url" {
  value = try(aws_sqs_queue.dlq[0].url, null)
}

output "sqs_from_sns_url" {
  description = "3/16 : SNS経由で届いた body の入れ子を確認する"
  value       = try(aws_sqs_queue.from_sns[0].url, null)
}

output "dynamodb_items_table" {
  description = "3/18 : 項目を追加・更新・削除して Streams を確認する"
  value       = try(aws_dynamodb_table.items[0].name, null)
}

output "dynamodb_idempotency_table" {
  description = "3/21 : set() をここに置き換える"
  value       = try(aws_dynamodb_table.idempotency[0].name, null)
}

output "integration_table" {
  value = try(aws_dynamodb_table.integration[0].name, null)
}

output "rds_endpoint" {
  value = try(aws_db_instance.this[0].address, null)
}

output "rds_proxy_endpoint" {
  value = try(aws_db_proxy.this[0].endpoint, null)
}

output "sfn_sequential_arn" {
  description = "3/28 : 直列2タスク"
  value       = try(aws_sfn_state_machine.sequential[0].arn, null)
}

output "sfn_callback_arn" {
  description = "3/28 : waitForTaskToken"
  value       = try(aws_sfn_state_machine.callback[0].arn, null)
}

output "lambda_log_groups" {
  description = "ログを見るときの一覧"
  value = compact([
    module.fn_scheduled.log_group,
    module.fn_secrets.log_group,
    try(module.fn_s3_event[0].log_group, ""),
    try(module.fn_presigned[0].log_group, ""),
    try(module.fn_sns_publisher[0].log_group, ""),
    try(module.fn_rest_api[0].log_group, ""),
    try(module.fn_cognito[0].log_group, ""),
    try(module.fn_sqs[0].log_group, ""),
    try(module.fn_streams[0].log_group, ""),
    try(module.fn_error_handling[0].log_group, ""),
    try(module.fn_integration[0].log_group, ""),
    try(module.fn_vpc_rds[0].log_group, ""),
    try(module.fn_sfn_task[0].log_group, ""),
    try(module.fn_powertools[0].log_group, ""),
  ])
}
