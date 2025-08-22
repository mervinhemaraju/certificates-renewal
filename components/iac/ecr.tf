module "ecr_renew_web_helios" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "1.6.0"

  repository_name = "python/oci/renew-web-helios"

  repository_lambda_read_access_arns = [
    module.renew_web_helios.lambda_function_arn
  ]

  repository_force_delete = true

  repository_lifecycle_policy = jsonencode(
    {
      rules = [
        {
          rulePriority = 1,
          description  = "Keep last 3 images",
          selection = {
            tagStatus   = "any",
            countType   = "imageCountMoreThan",
            countNumber = 3
          },
          action = {
            type = "expire"
          }
        }
      ]
    }
  )

  depends_on = [
    module.renew_web_helios
  ]
}
