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
resource "aws_iam_role" "iam_lambda_generate_signature" {
  name = "iam_lambda_generate_signature"

  assume_role_policy = jsonencode({
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
  })
}

resource "aws_iam_policy" "iam_lambda_generate-signature" {
  name = "crosschecker-lambda-generate-signature-policy"
  policy = file("policies/iam-lambda-generate-signature.json")
}

resource "aws_iam_role_policy_attachment" "iam_lambda_generate-signature" {
  role = aws_iam_role.iam_lambda_generate_signature.name
  policy_arn = aws_iam_policy.iam_lambda_generate-signature.arn
}
