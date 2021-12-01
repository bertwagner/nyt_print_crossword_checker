resource "aws_lambda_function" "image_uploader_signature" {
  function_name = "crosschecker-image-uploader-generate-signature"
  role          = aws_iam_role.iam_lambda_generate_signature.arn

  runtime = "python3.9"
  s3_bucket = aws_s3_bucket.lambda_functions.bucket
  s3_key = "image-uploader-generate-signature.zip"
  handler       = "calculate_upload_signature.lambda_handler"
  
}

resource "aws_lambda_permission" "image_uploader_signature" {
	action        = "lambda:InvokeFunction"
	function_name = aws_lambda_function.image_uploader_signature.arn
	principal     = "apigateway.amazonaws.com"

	source_arn = "${aws_apigatewayv2_api.image_uploader_signature_api.execution_arn}/*/*/*"
}