terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-east-2"
}

resource "aws_s3_bucket" "crosscheck_app" {
  bucket = "crosscheck-app"
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}
