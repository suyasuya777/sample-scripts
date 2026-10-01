# ==================================================================
# セットA : ネットワーク / ALB / ECS Fargate / EC2 / ASG / ログS3
# 構築 1/18（初日）  削除 2/28
# NAT Gateway は作らない（$1.4/日 + データ処理料金の節約）。
# Fargate タスクは公開サブネットに assign_public_ip = true で置く。
# ==================================================================

# ------------------------------------------------------------------
# VPC / サブネット / ルーティング
# ------------------------------------------------------------------

resource "aws_vpc" "this" {
  cidr_block           = "10.20.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = local.name }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = { Name = local.name }
}

resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(aws_vpc.this.cidr_block, 8, count.index)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true

  tags = { Name = "${local.name}-public-${count.index}" }
}

# vpc_describe_network.py の「プライベート判定」の題材。IGW 向きルートを持たない
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(aws_vpc.this.cidr_block, 8, 10)
  availability_zone = local.azs[0]

  tags = { Name = "${local.name}-private" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = { Name = "${local.name}-public" }
}

resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ------------------------------------------------------------------
# セキュリティグループ
# ------------------------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "${local.name}-alb"
  description = "ALB ingress"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${local.name}-alb" }
}

# 1/31 にこのルールを一時的に外して unhealthy を再現する。
# CLI で触るので ingress の差分は無視する。
resource "aws_security_group" "task" {
  name        = "${local.name}-task"
  description = "ECS task and EC2"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    ignore_changes = [ingress]
  }

  tags = { Name = "${local.name}-task" }
}

# ec2_security_groups.py の「全開放ルール検出」の題材。
# どのリソースにもアタッチしないこと。
resource "aws_security_group" "intentionally_open" {
  name        = "${local.name}-intentionally-open"
  description = "Detection target only. DO NOT attach to any resource."
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${local.name}-intentionally-open" }
}

# ------------------------------------------------------------------
# ログ用 S3（ALBアクセスログ / VPC Flow Logs）
# 2/14 の Athena はここに貯まったデータを見るので、期間中は消さない
# ------------------------------------------------------------------

resource "aws_s3_bucket" "logs" {
  bucket = "${local.name}-logs-${local.account}"

  # これがないと destroy がオブジェクト残存で失敗する
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "logs" {
  # ALB アクセスログ（ap-northeast-1 は旧リージョンなので ELB アカウントID を使う）
  statement {
    sid = "AlbAccessLogs"
    principals {
      type        = "AWS"
      identifiers = [data.aws_elb_service_account.this.arn]
    }
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.logs.arn}/alb/*"]
  }

  # VPC Flow Logs
  statement {
    sid = "FlowLogsPut"
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.logs.arn}/*"]
  }

  statement {
    sid = "FlowLogsAcl"
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.logs.arn]
  }
}

resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = data.aws_iam_policy_document.logs.json
}

resource "aws_flow_log" "this" {
  vpc_id               = aws_vpc.this.id
  traffic_type         = "ALL"
  log_destination_type = "s3"
  log_destination      = "${aws_s3_bucket.logs.arn}/flowlogs/"

  depends_on = [aws_s3_bucket_policy.logs]
}

# ------------------------------------------------------------------
# ALB / ターゲットグループ
# ------------------------------------------------------------------

resource "aws_lb" "this" {
  name               = local.name
  load_balancer_type = "application"
  subnets            = aws_subnet.public[*].id
  security_groups    = [aws_security_group.alb.id]

  idle_timeout = 60

  access_logs {
    bucket  = aws_s3_bucket.logs.bucket
    prefix  = "alb"
    enabled = true
  }

  depends_on = [aws_s3_bucket_policy.logs]
}

resource "aws_lb_target_group" "this" {
  name        = local.name
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.this.id
  target_type = "ip"

  # 1/29 のローリング再起動でドレイニングを観測するため短めにしてある
  deregistration_delay = 30

  health_check {
    path                = "/"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }
}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

# ------------------------------------------------------------------
# ECS / Fargate
# ------------------------------------------------------------------

resource "aws_ecs_cluster" "this" {
  name = local.name

  setting {
    name  = "containerInsights"
    value = "disabled" # 有効にすると課金が乗るので off
  }
}

data "aws_iam_policy_document" "ecs_tasks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_exec" {
  name               = "${local.name}-ecs-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
}

resource "aws_iam_role_policy_attachment" "ecs_exec" {
  role       = aws_iam_role.ecs_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name}"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "this" {
  family                   = local.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_exec.arn

  container_definitions = jsonencode([
    {
      name        = "web"
      image       = "public.ecr.aws/nginx/nginx:alpine"
      essential   = true
      stopTimeout = 60
      portMappings = [
        {
          containerPort = 80
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "STAGE", value = "study" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "web"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "this" {
  name            = local.name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.task.id]
    assign_public_ip = true # NAT Gateway を作らないので必須
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = "web"
    container_port   = 80
  }

  # 1/27 と 1/29 に CLI / boto3 で台数とデプロイを操作するため差分を無視する
  lifecycle {
    ignore_changes = [desired_count, task_definition]
  }

  depends_on = [aws_lb_listener.this]
}

# ------------------------------------------------------------------
# EC2（SSM 管理対象。2/24 の send_command で使う）
# ------------------------------------------------------------------

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = "${local.name}-ec2"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${local.name}-ec2"
  role = aws_iam_role.ec2.name
}

# 1/22 の start/stop、1/26 のタイプ変更で状態が変わるため差分を無視する
resource "aws_instance" "this" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.task.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  lifecycle {
    ignore_changes = [instance_type, ami]
  }

  tags = {
    Name = "${local.name}-ec2"
    Env  = "study"
    Role = "ssm-target"
  }
}

# ec2_unused_eip.py の題材。どこにも関連付けない（$0.12/日）
resource "aws_eip" "unused" {
  domain = "vpc"

  tags = { Name = "${local.name}-unused" }
}

# ec2_snapshots.py の題材。
# 「孤立スナップショット（元ボリュームが存在しない）」は Terraform の依存関係では
# 作れないため、1/26 に scripts/make_orphan_snapshot.sh で別途作成する。
resource "aws_ebs_snapshot" "sample" {
  volume_id   = aws_instance.this.root_block_device[0].volume_id
  description = "${local.name} sample snapshot"

  tags = { Name = "${local.name}-sample" }
}

# ------------------------------------------------------------------
# Auto Scaling（既定 0 台。1/31 に CLI で 2 に上げて戻す）
# ------------------------------------------------------------------

resource "aws_launch_template" "asg" {
  name_prefix   = "${local.name}-"
  image_id      = data.aws_ssm_parameter.al2023.value
  instance_type = "t3.micro"

  vpc_security_group_ids = [aws_security_group.task.id]

  tag_specifications {
    resource_type = "instance"
    tags          = { Name = "${local.name}-asg" }
  }
}

resource "aws_autoscaling_group" "this" {
  name                = local.name
  vpc_zone_identifier = aws_subnet.public[*].id
  min_size            = 0
  max_size            = 2
  desired_capacity    = 0
  health_check_type   = "EC2"

  launch_template {
    id      = aws_launch_template.asg.id
    version = "$Latest"
  }

  lifecycle {
    ignore_changes = [desired_capacity]
  }

  tag {
    key                 = "Project"
    value               = "boto3-study"
    propagate_at_launch = true
  }
}
