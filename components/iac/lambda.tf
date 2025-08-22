# Python lambda for certificate renew
module "lambda_renew_web_helios" {

  source  = "terraform-aws-modules/lambda/aws"
  version = "7.0.0"

  function_name = "oci-certificate-renew-helios"
  description   = "The lambda function that renews the SSL certificates on OCI Helios Web Load Balancer"
  handler       = local.constants.lambda.HANDLER
  runtime       = local.constants.lambda.VERSION

  memory_size                       = local.constants.lambda.MEMORY_SIZE
  cloudwatch_logs_retention_in_days = local.constants.lambda.CLOUDWATCH_RETENTION
  timeout                           = local.constants.lambda.TIMEOUT
  create_async_event_config         = true
  maximum_retry_attempts            = local.constants.lambda.RETRIES_ATTEMPT

  create_lambda_function_url    = false
  attach_cloudwatch_logs_policy = true

  create_role = false
  lambda_role = module.iam_role_renew_web_helios.iam_role_arn

  create_package = false
  package_type   = "Image"
  image_uri      = data.aws_ecr_image.renew_web_helios.image_uri

  environment_variables = {
    DOPPLER_MAIN_TOKEN = var.token_doppler_global
  }

  trusted_entities = local.constants.lambda.TRUSTED_ENTITIES
}
