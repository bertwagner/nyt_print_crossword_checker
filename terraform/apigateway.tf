resource "aws_apigatewayv2_api" "image_uploader_signature_api" {
  name          = "crosschecker.app-image-uploader-signature"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["https://crosschecker.app"]
  }
}

resource "aws_apigatewayv2_route" "image_uploader_signature_api" {
  api_id    = aws_apigatewayv2_api.image_uploader_signature_api.id
  route_key = "GET /signature"
  target = "integrations/${aws_apigatewayv2_integration.image_uploader_signature_api.id}"
}

resource "aws_apigatewayv2_stage" "image_uploader_signature_api" {
  api_id = aws_apigatewayv2_api.image_uploader_signature_api.id
  name   = "v1"
  auto_deploy = "true"

  default_route_settings {
    throttling_burst_limit = 20
    throttling_rate_limit  = 50
  }

  access_log_settings {
     destination_arn = aws_cloudwatch_log_group.apigateway_image_uploader_signature.arn
     format = "{ \"requestId\":\"$context.requestId\",\"extendedRequestId\":\"$context.extendedRequestId\",\"ip\": \"$context.identity.sourceIp\",\"caller\":\"$context.identity.caller\",\"user\":\"$context.identity.user\",\"requestTime\":\"$context.requestTime\",\"httpMethod\":\"$context.httpMethod\",\"resourcePath\":\"$context.resourcePath\",\"status\":\"$context.status\",\"protocol\":\"$context.protocol\", \"responseLength\":\"$context.responseLength\" }"
  }
}

resource "aws_apigatewayv2_integration" "image_uploader_signature_api" {
  api_id           = aws_apigatewayv2_api.image_uploader_signature_api.id
  integration_type = "AWS_PROXY"

  connection_type           = "INTERNET"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.image_uploader_signature.invoke_arn
}


resource "aws_apigatewayv2_domain_name" "image_uploader_signature_api" {
  domain_name = "api.crosschecker.app"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate.cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "image_uploader_signature_api" {
  api_id      = aws_apigatewayv2_api.image_uploader_signature_api.id
  domain_name = aws_apigatewayv2_domain_name.image_uploader_signature_api.id
  stage       = aws_apigatewayv2_stage.image_uploader_signature_api.id
}


