resource "aws_s3_bucket" "crosschecker_app" {
  bucket = "crosschecker.app"
  acl    = "public-read"
  policy = file("policies/s3-public-website.json")


  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "crosschecker.app-state"
  acl = "private"
  versioning {
    enabled = true
  }
}
