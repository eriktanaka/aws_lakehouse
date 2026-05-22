resource "aws_s3_bucket" "artifacts" {
  bucket        = local.artifacts_bucket_name
  force_destroy = true 
}

resource "aws_s3_bucket_public_access_block" "artifacts_security" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "bronze" {
  bucket        = local.bronze_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "bronze_security" {
  bucket                  = aws_s3_bucket.bronze.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "silver" {
  bucket        = local.silver_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "silver_security" {
  bucket                  = aws_s3_bucket.silver.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "gold" {
  bucket        = local.gold_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "gold_security" {
  bucket                  = aws_s3_bucket.gold.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}