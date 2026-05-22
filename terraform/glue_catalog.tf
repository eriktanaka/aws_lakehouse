resource "aws_glue_catalog_database" "bronze" {
  name = local.common_default_arguments["--bronze_database"]
}

resource "aws_glue_catalog_database" "silver" {
  name = local.common_default_arguments["--silver_database"]
}

resource "aws_glue_catalog_database" "gold" {
  name = local.common_default_arguments["--gold_database"]
}