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
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = "boto3-study"
      ManagedBy = "terraform"
    }
  }
}

data "aws_caller_identity" "this" {}
data "aws_availability_zones" "this" { state = "available" }
data "aws_elb_service_account" "this" {}

data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

locals {
  name    = var.name_prefix
  account = data.aws_caller_identity.this.account_id
  azs     = slice(data.aws_availability_zones.this.names, 0, 2)
}
