
data "aws_ecr_image" "renew_web_helios" {
  repository_name = local.constants.ecr.helios_web_renew
  most_recent     = true
}
