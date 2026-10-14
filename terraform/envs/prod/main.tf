# استدعاء موديول الـ VPC للـ Prod
module "prod_vpc" {
  source      = "../../modules/vpc"
  vpc_cidr    = "10.20.0.0/16"
  environment = "prod"
}

# استدعاء موديول الـ Log Bucket للـ Prod
module "prod_logs" {
  source      = "../../modules/log_bucket"
  bucket_name = "depi-prod-secure-logs-bucket-2026"
}