
data "aws_ecr_image" "renew_web_helios" {
  repository_name = "python/oci/renew-web-helios"
  most_recent     = true
}
