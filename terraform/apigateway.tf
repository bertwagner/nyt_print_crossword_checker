resource "aws_apigatewayv2_api" "image-uploader-signature-api" {
  name          = "crosschecker.app-image-uploader-signature"
  protocol_type = "HTTP"
  target = aws_lambda_function.image_uploader_signature.arn
}


