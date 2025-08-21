# Terraform Provider for AWS for the connection
provider "aws" {

  # The AWS Environment Configurations
  region = var.region

  # The Default Tags
  default_tags {
    tags = local.tags.default
  }
}

