# The Terraform Module
terraform {

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.32.0"
    }

    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}
