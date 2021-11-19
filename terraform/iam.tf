# User for uploading/downloading Terraform state via backened
resource "aws_iam_user" "terraform_state" {
  name = "crosschecker-terraform-state-user"
}

resource "aws_iam_policy" "terraform_state" {
  name = "crosschecker-terraform-state-policy"
  policy = file("policies/iam-terraform-state.json")
}

resource "aws_iam_user_policy_attachment" "terraform_state" {
  user = aws_iam_user.terraform_state.name
  policy_arn = aws_iam_policy.terraform_state.arn
}


# User for uploading images to S3 bucket
resource "aws_iam_user" "image_uploader" {
  name = "crosschecker-image-uploader-user"
}

resource "aws_iam_policy" "image_uploader" {
  name = "crosschecker-image-uploader-policy"
  policy = file("policies/iam-image-uploader.json")
}

resource "aws_iam_user_policy_attachment" "image_uploader" {
  user = aws_iam_user.image_uploader.name
  policy_arn = aws_iam_policy.image_uploader.arn
}

# iam for lambdas
resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}