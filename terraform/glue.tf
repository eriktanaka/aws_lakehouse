resource "aws_glue_job" "bronze_btc" {
  name     = join("-", [local.project_prefix, "glue-job", "bronze", "btc"])
  role_arn = aws_iam_role.glue_job_role.arn
  command {
    name            = "pythonshell"
    python_version  = "3.9"
    script_location = "s3://${aws_s3_bucket.artifacts.bucket}/scripts/bronze_btc.py"
  }
  max_capacity = 1.0 
  default_arguments = merge(
    local.common_default_arguments,
    {
      "--job_name" = join("-", [local.project_prefix, "glue-job", "bronze", "btc"])
    }
  )
}

##############################
#########SILVER LAYER#########
##############################

resource "aws_glue_job" "silver_btc" {
  name              = join("-", [local.project_prefix, "glue-job", "silver", "btc"])
  role_arn          = aws_iam_role.glue_job_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2 

  command {
    name            = "glueetl"
    python_version  = "3"
    script_location = "s3://${aws_s3_bucket.artifacts.bucket}/scripts/silver_btc.py"
  }

  default_arguments = merge(
    local.common_default_arguments,
    {
      "--job_name"         = join("-", [local.project_prefix, "glue-job", "silver", "btc"])
      "--datalake-formats" = "iceberg"
      "--conf"             = "spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog --conf spark.sql.catalog.glue_catalog.io-impl=org.apache.iceberg.aws.s3.S3FileIO --conf spark.sql.catalog.glue_catalog.warehouse=s3://${local.silver_bucket_name}/"
    }
)
}