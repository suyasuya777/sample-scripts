# ==================================================================
# セットE-1 : RDS（db.t4g.micro / PostgreSQL）
#   構築 3/7（日）  削除 3/14（日）   約 $0.5/日
# セットE-2 : Aurora Serverless v2（writer + reader）/ EKS
#   構築 Aurora=3/9・EKS=3/10  削除 いずれも当日中   約 $4.8/日 + $2.4/日
#
# E-2 は手順書 §3 のとおり -target で Aurora と EKS を別々の日に作る。
# terraform.tfvars の enable_set_e2 は false のまま触らないこと。
# 作った日のうちに terraform apply（フラグなし）で消す。消し忘れが一番高くつく。
# ==================================================================

locals {
  e1 = var.enable_set_e1 ? 1 : 0
  e2 = var.enable_set_e2 ? 1 : 0
}

# ------------------------------------------------------------------
# 共通 : サブネットグループ（セットAのVPCを流用）
# ------------------------------------------------------------------

resource "aws_db_subnet_group" "this" {
  count      = max(local.e1, local.e2)
  name       = local.name
  subnet_ids = aws_subnet.public[*].id
}

# ------------------------------------------------------------------
# E-1 : RDS インスタンス
# ------------------------------------------------------------------

resource "aws_db_instance" "this" {
  count = local.e1

  identifier             = local.name
  engine                 = "postgres"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  storage_type           = "gp3"
  username               = "postgres"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.this[0].name
  vpc_security_group_ids = [aws_security_group.task.id]

  multi_az                = false
  publicly_accessible     = false
  skip_final_snapshot     = true
  backup_retention_period = 1
  apply_immediately       = true
  deletion_protection     = false

  # 3/8 に create_db_snapshot を実行するので、手動スナップショットは
  # terraform destroy では消えない。3/14 の cleanup_leftovers.sh で削除すること。
}

# ------------------------------------------------------------------
# E-2 : Aurora Serverless v2（フェイルオーバー演習用）
# ------------------------------------------------------------------

# engine_version を未指定にすると、既定が Serverless v2（db.serverless）
# 非対応バージョンだった場合に「クラスタは作れるがインスタンス作成で失敗」
# という形で 10 分走ってから落ちる。3/9 は当日作成・当日削除なので、
# ここでバージョンを明示的に解決しておく。
#
# 固定したい場合は data の参照をやめて直接書いてもよい:
#   engine_version = "16.6"
# 利用可能なバージョンの確認:
#   aws rds describe-db-engine-versions --engine aurora-postgresql \
#     --query 'DBEngineVersions[].EngineVersion' --output table
data "aws_rds_engine_version" "aurora_postgresql" {
  engine = "aurora-postgresql"
  latest = true
}

resource "aws_rds_cluster" "aurora" {
  count = local.e2

  cluster_identifier     = "${local.name}-aurora"
  engine                 = "aurora-postgresql"
  engine_version         = data.aws_rds_engine_version.aurora_postgresql.version_actual
  engine_mode            = "provisioned"
  master_username        = "postgres"
  master_password        = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.this[0].name
  vpc_security_group_ids = [aws_security_group.task.id]

  skip_final_snapshot = true
  apply_immediately   = true
  deletion_protection = false

  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 1.0
  }
}

# フェイルオーバーには writer と reader の2台が要る
resource "aws_rds_cluster_instance" "aurora" {
  count = local.e2 * 2

  identifier         = "${local.name}-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora[0].id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.aurora[0].engine
  engine_version     = aws_rds_cluster.aurora[0].engine_version

  # フェイルオーバー後に writer/reader が入れ替わるので差分を無視
  lifecycle {
    ignore_changes = [promotion_tier]
  }
}

# ------------------------------------------------------------------
# E-2 : EKS（コントロールプレーンのみ。ノードグループは作らない）
#   describe_cluster を叩くだけなのでノードは不要。$0.10/時。
#   作成に約10分、削除に約10分かかる。
# ------------------------------------------------------------------

data "aws_iam_policy_document" "eks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks" {
  count              = local.e2
  name               = "${local.name}-eks"
  assume_role_policy = data.aws_iam_policy_document.eks_assume.json
}

resource "aws_iam_role_policy_attachment" "eks_cluster" {
  count      = local.e2
  role       = aws_iam_role.eks[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_eks_cluster" "this" {
  count = local.e2

  name     = local.name
  role_arn = aws_iam_role.eks[0].arn

  vpc_config {
    subnet_ids = aws_subnet.public[*].id
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster]
}
