terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = "lambda-study"
      ManagedBy = "terraform"
    }
  }
}

data "aws_caller_identity" "this" {}
data "aws_region" "this" {}
data "aws_availability_zones" "this" { state = "available" }

locals {
  name    = var.name_prefix
  account = data.aws_caller_identity.this.account_id
  region  = data.aws_region.this.name
  azs     = slice(data.aws_availability_zones.this.names, 0, 2)

  # 教材を展開したディレクトリ。各サンプルはこの直下のサブディレクトリに入っている
  src = var.samples_dir
}
