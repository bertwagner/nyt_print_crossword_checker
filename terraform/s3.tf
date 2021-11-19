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


# Unprocessed user-uploaded crossword images
resource "aws_s3_bucket" "crosschecker_app_uploads" {
  bucket = "crosschecker.app-uploads"
  acl = "private"
}