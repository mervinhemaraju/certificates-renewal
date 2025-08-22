
data "aws_ecr_image" "renew_web_helios" {
  repository_name = local.constants.ecr.helios_web_renew.name
  image_digest    = null
  image_tag       = null
  most_recent     = true
}
