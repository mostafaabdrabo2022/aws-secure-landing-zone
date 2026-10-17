# VPC Module Call for Prod
module "prod_vpc" {
  source      = "../../modules/vpc"
  vpc_cidr    = "10.20.0.0/16"
  environment = "prod"
}

# Invoking the Log Bucket module for Prod
module "prod_logs" {
  source      = "../../modules/log_bucket"
  bucket_name = "depi-prod-secure-logs-bucket-2026"
}