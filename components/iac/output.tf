output "ssl_renew_current_image_url" {
  value = data.aws_ecr_image.renew_web_helios.image_uri
}
