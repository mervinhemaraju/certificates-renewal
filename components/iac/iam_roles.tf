# Create an assumable role for Lambda renew_web_helios
module "iam_role_scheduler_renew_web_helios" {

  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "~> 5.0"

  create_role           = true
  role_requires_mfa     = false
  role_name             = "role-scheduler-oci-helios-web-ssl-renew"
  trusted_role_services = ["scheduler.amazonaws.com"]

  # Inline policy for custom permissions
  # inline_policy_statements = [
  #   {
  #     sid    = "AllowLambdaInvoke"
  #     effect = "Allow"

  #     actions = [
  #       "lambda:InvokeFunction"
  #     ]

  #     resources = [
  #       module.lambda_renew_web_helios.lambda_function_arn
  #     ]
  #   },
  #   {
  #     sid    = "AllowIamPassRoleOnLambdaRole"
  #     effect = "Allow"

  #     actions = [
  #       "iam:PassRole"
  #     ]

  #     resources = [
  #       module.lambda_renew_web_helios.lambda_role_arn
  #     ]
  #   }
  # ]
}
