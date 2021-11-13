resource "aws_iam_user" "CrossCheckerServiceUser" {
  name = "CrossCheckerServiceUser"
}

resource "aws_iam_policy" "policy" {
  name = "crosschecker-service-policy"
  policy = file("policies/iam-crosschecker-service.json")
}

resource "aws_iam_user_policy_attachment" "policy-attach" {
  user = aws_iam_user.CrossCheckerServiceUser.name
  policy_arn = aws_iam_policy.policy.arn
}
