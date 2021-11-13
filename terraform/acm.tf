resource "aws_acm_certificate" "cert" {
  domain_name       = "crosschecker.app"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cname_validation: record.fqdn]
}

resource "aws_acm_certificate" "cert2" {
  domain_name       = "*.crosschecker.app"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "cert2" {
  certificate_arn         = aws_acm_certificate.cert2.arn
  validation_record_fqdns = [for record in aws_route53_record.cname_validation2: record.fqdn]
}
