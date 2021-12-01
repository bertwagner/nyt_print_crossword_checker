resource "aws_secretsmanager_secret" "iam-image-uploader-secret" {
  name = "crosschecker-image-uploader-user-access-key"
}