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