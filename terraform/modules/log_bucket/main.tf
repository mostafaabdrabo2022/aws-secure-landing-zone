variable "bucket_name" {
  type        = string
  description = "Name of the secure S3 log bucket"
}

resource "aws_s3_bucket" "log_bucket" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Name        = var.bucket_name
    Environment = "Security-Logging"
  }
}

# تفعيل الـ Versioning
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.log_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# تفعيل التشفير باستخدام الشكل المحدث والمدعوم في AWS Provider v5+
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.log_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# حجب أي وصول عام خارجي للسلة
resource "aws_s3_bucket_public_access_block" "public_block" {
  bucket                  = aws_s3_bucket.log_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}