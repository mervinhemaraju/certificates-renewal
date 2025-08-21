
#  Terraform AWS providers vars
variable "region" {
  type        = string
  description = "The AWS target region."
  default     = "eu-west-1"
}

variable "bucket_key_prefix_iac" {
  type        = string
  description = "The prefix for the bucket key."
}

variable "bucket_name" {
  type        = string
  description = "The name of the bucket."
}

variable "bucket_region" {
  type        = string
  description = "The region of the bucket."
}
