locals {

  # > Tags for resources
  tags = {
    default = {
      Creator     = "mervin.hemaraju"
      Owner       = "mervin.hemaraju"
      Project     = "https://github.com/mervinhemaraju/certificates-renewal"
      Usage       = "personal"
      Product     = "ssl-renewal"
      Environment = "production"
      Terraform   = "yes"
    }
  }

  constants = {

    # > Lambda default configurations
    lambda = {
      SOURCE_PATH          = "./functions/renew/"
      RETRIES_ATTEMPT      = 0
      TIMEOUT              = "200"
      HANDLER              = "main.main"
      VERSION              = "python3.11"
      MEMORY_SIZE          = 128
      CLOUDWATCH_RETENTION = 7
      TRUSTED_ENTITIES = [
        {
          type = "Service",
          identifiers = [
            "lambda.amazonaws.com"
          ]
        }
      ]
    }
  }
}
