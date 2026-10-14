output "bucket_id" {
  value       = aws_s3_bucket.log_bucket.id
  description = "The ID of the secure log bucket"
}

output "bucket_arn" {
  value       = aws_s3_bucket.log_bucket.arn
  description = "The ARN of the secure log bucket"
}