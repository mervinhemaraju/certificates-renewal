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
      RETRIES_ATTEMPT      = 0
      TIMEOUT              = "200"
      HANDLER              = "main.main"
      VERSION              = "python3.13"
      MEMORY_SIZE          = 256
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

    scheduler = {

      group_name = "certificates-renewal"
    }

    ecr = {
      helios_web_renew = {
        name = "python/oci/renew-web-helios"
      }
    }
  }
}
