output "prod_vpc_id" {
  value       = module.prod_vpc.vpc_id
  description = "Production VPC ID"
}

output "prod_log_bucket_id" {
  value       = module.prod_logs.bucket_id
  description = "Production Secure Log Bucket ID"
}