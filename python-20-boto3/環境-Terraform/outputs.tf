output "alb_dns_name" {
  description = "curl でアクセスして ALB アクセスログを貯める先"
  value       = aws_lb.this.dns_name
}

output "log_bucket" {
  description = "ALBアクセスログ / VPC Flow Logs の保存先。2/14 の Athena で使う"
  value       = aws_s3_bucket.logs.bucket
}

output "athena_alb_log_location" {
  description = "Athena テーブルの LOCATION にそのまま使える S3 パス"
  value       = "s3://${aws_s3_bucket.logs.bucket}/alb/AWSLogs/${local.account}/elasticloadbalancing/${var.region}/"
}

output "ecs_cluster" {
  value = aws_ecs_cluster.this.name
}

output "ecs_service" {
  value = aws_ecs_service.this.name
}

output "ec2_instance_id" {
  description = "1/22 の start/stop、1/26 のタイプ変更、2/24 の send_command の対象"
  value       = aws_instance.this.id
}

output "asg_name" {
  value = aws_autoscaling_group.this.name
}

output "target_group_arn" {
  value = aws_lb_target_group.this.arn
}

output "s3_bucket_a" {
  description = "1200オブジェクトが入ったバケット（paginator 確認用）"
  value       = try(aws_s3_bucket.a[0].id, null)
}

output "s3_bucket_b" {
  description = "パブリックアクセスブロックが2項目だけのバケット"
  value       = try(aws_s3_bucket.b[0].id, null)
}

output "sqs_main_url" {
  value = try(aws_sqs_queue.main[0].url, null)
}

output "sqs_dlq_url" {
  value = try(aws_sqs_queue.dlq[0].url, null)
}

output "sns_topic_arn" {
  value = try(aws_sns_topic.this[0].arn, null)
}

output "lambda_function_names" {
  value = [for f in aws_lambda_function.fn : f.function_name]
}

output "rds_identifier" {
  value = try(aws_db_instance.this[0].identifier, null)
}

output "aurora_cluster_identifier" {
  value = try(aws_rds_cluster.aurora[0].cluster_identifier, null)
}

output "eks_cluster_name" {
  value = try(aws_eks_cluster.this[0].name, null)
}
