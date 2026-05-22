locals {
  project_prefix = "lakehouse-portfolio"
  
  unique_suffix  = "datashi" 

  # Geração dinâmica dos nomes dos buckets (Padrão corporativo)
  artifacts_bucket_name = "${local.project_prefix}-artifacts-${local.unique_suffix}"
  bronze_bucket_name    = "${local.project_prefix}-bronze-${local.unique_suffix}"
  silver_bucket_name    = "${local.project_prefix}-silver-${local.unique_suffix}"
  gold_bucket_name      = "${local.project_prefix}-gold-${local.unique_suffix}"

  common_default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    
    "--artifacts_bucket" = local.artifacts_bucket_name
    "--bronze_bucket"    = local.bronze_bucket_name
    "--silver_bucket"    = local.silver_bucket_name
    "--gold_bucket"      = local.gold_bucket_name
    
    "--bronze_database" = "bronze"
    "--silver_database" = "silver"
    "--gold_database"   = "gold"
  }
}