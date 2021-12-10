resource "aws_secretsmanager_secret" "iam-image-uploader-secret" {
  name = "crosschecker-image-uploader-user-access-key"
}
resource "aws_secretsmanager_secret" "nyt-login-credentials" {
  name = "crosschecker-nyt-login"
}