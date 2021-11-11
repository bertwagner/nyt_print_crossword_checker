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
  region  = "us-east-1"
}

resource "aws_s3_bucket" "crosschecker_app" {
  bucket = "crosschecker.app"
  acl    = "public-read"
  policy = file("policies/s3-public-website.json")


  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}
