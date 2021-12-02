resource "aws_route53_zone" "primary" {
  name = "crosschecker.app"
}

resource "aws_route53_record" "cname_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.primary.zone_id
}

resource "aws_route53_record" "cloudfront_alias" {
  zone_id = aws_route53_zone.primary.zone_id
  name = "crosschecker.app"
  type = "A"
  
  alias {
    name = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
    evaluate_target_health = false 
  }
}

resource "aws_route53_record" "apigateway_cname" {
  zone_id = aws_route53_zone.primary.zone_id
  name = "api.crosschecker.app"
  type = "CNAME"
  ttl = "300"
  
  records = [aws_apigatewayv2_domain_name.image_uploader_signature_api.domain_name_configuration[0].target_domain_name]
}
