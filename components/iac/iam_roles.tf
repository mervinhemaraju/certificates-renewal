# Create an assumable role for Lambda renew_web_helios
module "renew_web_helios" {

  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "~> 5.0"

  create_role           = true
  role_requires_mfa     = false
  role_name             = "role-lambda-oci-helios-web-ssl-renew"
  trusted_role_services = ["lambda.amazonaws.com"]

  #   # Attach AWS managed policies
  #   role_policy_arns = [
  #     "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
  #     # Optional: Add VPC access if needed
  #     # "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
  #   ]

  #   # Inline policy for custom permissions
  #   inline_policy_statements = [
  #     {
  #       effect = "Allow"
  #       actions = [
  #         "s3:GetObject",
  #         "s3:PutObject"
  #       ]
  #       resources = ["arn:aws:s3:::my-bucket/*"]
  #     },
  #     {
  #       effect = "Allow"
  #       actions = [
  #         "dynamodb:GetItem",
  #         "dynamodb:PutItem",
  #         "dynamodb:Query"
  #       ]
  #       resources = ["arn:aws:dynamodb:*:*:table/my-table"]
  #     },
  #     {
  #       effect = "Allow"
  #       actions = [
  #         "secretsmanager:GetSecretValue"
  #       ]
  #       resources = ["arn:aws:secretsmanager:*:*:secret:my-secret-*"]
  #     }
  #   ]
}
