# ==================================================================
# Athena クエリ結果の出力先（2/28 で使用）
# 構築 2/1（セットAと同時。フラグなし）  削除 3/14
#
# ワークグループ primary は既定で結果出力先が未設定のため、これが無いと
# start_query_execution が即エラーになる:
#   InvalidRequestException: No output location provided.
#     An output location is required either through the Workgroup
#     result configuration setting or as an API input.
#
# バケット自体は無料。結果ファイルは1クエリ数KB程度なので実質 $0。
# destroy 時は force_destroy = true で結果ごと消える。
# ==================================================================

resource "aws_s3_bucket" "athena_results" {
  bucket        = "${local.name}-athena-${local.account}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "athena_results_bucket" {
  description = "Athena クエリ結果の保存先バケット"
  value       = aws_s3_bucket.athena_results.bucket
}

output "athena_results_location" {
  description = "athena 3本の OUTPUT_LOCATION にそのまま貼る値（s3://.../query-results/）"
  value       = "s3://${aws_s3_bucket.athena_results.bucket}/query-results/"
}
