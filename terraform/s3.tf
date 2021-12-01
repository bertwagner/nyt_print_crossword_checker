# Keeps track of Terraform State
resource "aws_s3_bucket" "terraform_state" {
  bucket = "crosschecker.app-state"
  acl = "private"
  versioning {
    enabled = true
  }
}


#Bucket for hosting the static web app
resource "aws_s3_bucket" "crosschecker_app" {
  bucket = "crosschecker.app"
  acl    = "public-read"
  policy = file("policies/s3-public-website.json")

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "aws_s3_bucket_public_access_block" "crosschecker_app_public_access" {
  bucket = aws_s3_bucket.crosschecker_app.id

  block_public_policy = false
}


# Unprocessed user-uploaded crossword images
resource "aws_s3_bucket" "crosschecker_app_data" {
  bucket = "crosschecker.app-data"
  acl = "private"
}


# Lambda source code
resource "aws_s3_bucket" "lambda_functions" {
  bucket = "crosschecker.app-lambda-functions"
  acl = "private"
}