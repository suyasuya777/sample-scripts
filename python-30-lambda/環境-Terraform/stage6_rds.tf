# ==================================================================
# VPC / RDS / RDS Proxy / VPCエンドポイント（3/25 構築 → 3/26 中に削除）
#   enable_rds = true → 演習後 false に戻して apply
#
#   3月で唯一まとまった費用がかかる。約 $1.3/日。
#     RDS db.t4g.micro        約 $0.5/日
#     RDS Proxy               約 $0.7/日（enable_rds_proxy = false で省略可）
#     Secrets Manager VPCEP   約 $0.34/日
#
#   NAT Gateway は作らない。3/25 の演習が「VPC Lambda はインターネットに
#   出られない」を実測することなので、最初から出口を用意しては意味がない。
# ==================================================================

locals {
  rds   = var.enable_rds ? 1 : 0
  proxy = var.enable_rds && var.enable_rds_proxy ? 1 : 0
}

# ------------------------------------------------------------------
# VPC（プライベートサブネットのみ。IGW も NAT も作らない）
# ------------------------------------------------------------------

resource "aws_vpc" "this" {
  count                = local.rds
  cidr_block           = "10.30.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = local.name }
}

resource "aws_subnet" "private" {
  count             = local.rds * 2
  vpc_id            = aws_vpc.this[0].id
  cidr_block        = cidrsubnet("10.30.0.0/16", 8, count.index)
  availability_zone = local.azs[count.index]

  tags = { Name = "${local.name}-private-${count.index}" }
}

resource "aws_security_group" "lambda" {
  count       = local.rds
  name        = "${local.name}-lambda"
  description = "Lambda in VPC"
  vpc_id      = aws_vpc.this[0].id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db" {
  count       = local.rds
  name        = "${local.name}-db"
  description = "RDS and proxy"
  vpc_id      = aws_vpc.this[0].id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda[0].id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS Proxy から RDS への戻りを許可する（Proxy は db SG に所属させる）
resource "aws_security_group_rule" "db_self" {
  count                    = local.proxy
  type                     = "ingress"
  from_port                = 3306
  to_port                  = 3306
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db[0].id
  source_security_group_id = aws_security_group.db[0].id
}

# ------------------------------------------------------------------
# VPCエンドポイント（3/26）
#   3/25 は「これが無い状態で Secrets Manager 取得が固まる」ことを実測する。
#   3/26 にこれを足して疎通させる。
#
#   3/25 の演習を素直にやるなら、初回 apply 時は下の count を 0 にしておき、
#   3/26 に戻す運用でもよい。
# ------------------------------------------------------------------

resource "aws_security_group" "vpce" {
  count       = local.rds
  name        = "${local.name}-vpce"
  description = "Interface endpoints"
  vpc_id      = aws_vpc.this[0].id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda[0].id]
  }
}

resource "aws_vpc_endpoint" "secretsmanager" {
  count               = local.rds
  vpc_id              = aws_vpc.this[0].id
  service_name        = "com.amazonaws.${local.region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpce[0].id]
  private_dns_enabled = true

  tags = { Name = "${local.name}-secretsmanager" }
}

# ------------------------------------------------------------------
# RDS（MySQL。教材が pymysql を使うため）
# ------------------------------------------------------------------

resource "aws_db_subnet_group" "this" {
  count      = local.rds
  name       = local.name
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "this" {
  count = local.rds

  identifier             = local.name
  engine                 = "mysql"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  storage_type           = "gp3"
  db_name                = "studydb"
  username               = "appuser"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.this[0].name
  vpc_security_group_ids = [aws_security_group.db[0].id]

  multi_az                = false
  publicly_accessible     = false
  skip_final_snapshot     = true
  backup_retention_period = 0
  apply_immediately       = true
  deletion_protection     = false
}

# RDS Proxy は認証情報を Secrets Manager から読む
resource "aws_secretsmanager_secret" "rds" {
  count                   = local.rds
  name                    = "${local.name}/rds"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "rds" {
  count     = local.rds
  secret_id = aws_secretsmanager_secret.rds[0].id
  secret_string = jsonencode({
    username = aws_db_instance.this[0].username
    password = var.db_password
    host     = aws_db_instance.this[0].address
    port     = 3306
    dbname   = "studydb"
  })
}

# ------------------------------------------------------------------
# RDS Proxy（3/26）
#   同時実行数ぶんの接続がDBに殺到する問題への対処。
#   1/6 と 2月の「ワーカー数 × タスク数 × プール上限 ≦ max_connections」と同じ論点。
# ------------------------------------------------------------------

data "aws_iam_policy_document" "proxy_assume" {
  count = local.proxy
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "proxy" {
  count              = local.proxy
  name               = "${local.name}-rds-proxy"
  assume_role_policy = data.aws_iam_policy_document.proxy_assume[0].json
}

resource "aws_iam_role_policy" "proxy" {
  count = local.proxy
  name  = "read-secret"
  role  = aws_iam_role.proxy[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = aws_secretsmanager_secret.rds[0].arn
    }]
  })
}

resource "aws_db_proxy" "this" {
  count = local.proxy

  name                   = local.name
  engine_family          = "MYSQL"
  role_arn               = aws_iam_role.proxy[0].arn
  vpc_subnet_ids         = aws_subnet.private[*].id
  vpc_security_group_ids = [aws_security_group.db[0].id]
  require_tls            = false
  idle_client_timeout    = 1800

  auth {
    auth_scheme = "SECRETS"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.rds[0].arn
  }

  depends_on = [aws_secretsmanager_secret_version.rds]
}

resource "aws_db_proxy_default_target_group" "this" {
  count         = local.proxy
  db_proxy_name = aws_db_proxy.this[0].name

  connection_pool_config {
    max_connections_percent      = 100
    connection_borrow_timeout    = 120
  }
}

resource "aws_db_proxy_target" "this" {
  count                  = local.proxy
  db_proxy_name          = aws_db_proxy.this[0].name
  target_group_name      = aws_db_proxy_default_target_group.this[0].name
  db_instance_identifier = aws_db_instance.this[0].identifier
}

# ------------------------------------------------------------------
# vpc_rds_connection
#   pymysql は Lambda に同梱されていないので Layer が必要。
#   apply の前に scripts/build_layers.sh を実行しておくこと。
# ------------------------------------------------------------------

resource "aws_lambda_layer_version" "pymysql" {
  count = local.rds

  layer_name          = "${local.name}-pymysql"
  filename            = "${path.module}/.build/pymysql-layer.zip"
  source_code_hash    = filebase64sha256("${path.module}/.build/pymysql-layer.zip")
  compatible_runtimes = ["python3.12"]
  description         = "pymysql for vpc_rds_connection"
}

data "aws_iam_policy_document" "vpc_rds" {
  count = local.rds

  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.rds[0].arn]
  }
}

module "fn_vpc_rds" {
  count  = local.rds
  source = "./modules/lambda_fn"

  name               = "${local.name}-vpc-rds-connection"
  source_dir         = "${local.src}/vpc_rds_connection"
  handler            = "vpc_rds_connection.lambda_handler"
  timeout            = 30
  memory_size        = 256
  layers             = [aws_lambda_layer_version.pymysql[0].arn]
  policy_json        = data.aws_iam_policy_document.vpc_rds[0].json
  log_retention_days = var.log_retention_days

  vpc_config = {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda[0].id]
  }

  environment = {
    SECRET_ARN = aws_secretsmanager_secret.rds[0].arn
    DB_HOST    = local.proxy == 1 ? aws_db_proxy.this[0].endpoint : aws_db_instance.this[0].address
    DB_NAME    = "studydb"
    DB_PORT    = "3306"
  }
}
