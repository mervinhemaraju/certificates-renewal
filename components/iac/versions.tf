# The Terraform Module
terraform {

  # AWS Provider
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.32.0"
    }
  }
}
