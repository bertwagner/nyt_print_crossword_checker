resource "aws_lambda_function" "image_uploader_signature" {
  function_name = "crosschecker-image-uploader-generate-signature"
  role          = aws_iam_role.iam_for_lambda.arn

  runtime = "python3.9"
  s3_bucket = aws_s3_bucket.lambda_functions.bucket
  s3_key = "image-uploader-generate-signature.zip"
  handler       = "calculate_upload_signature.lambda_handler"
}