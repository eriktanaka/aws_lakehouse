import awswrangler as wr
from awsglue.utils import getResolvedOptions
import sys
import pandas as pd

args = getResolvedOptions(
    sys.argv,
    [
        "silver_database",
        "silver_bucket",
        "bronze_database",
        "table_name",
    ]
)

INPUT_DATABASE = args['bronze_database']
INPUT_TABLE = args['table_name']
OUTPUT_BUCKET = args['silver_bucket']
PROJECT = "btc"
OUTPUT_DATABASE = args['silver_database']
OUTPUT_TABLE_NAME = f"tbl_{PROJECT}"
OUTPUT_S3_PATH = f"s3://{OUTPUT_BUCKET}/{PROJECT}/{OUTPUT_TABLE_NAME}/"
TEMP_PATH = f"s3://{OUTPUT_BUCKET}/temp-athena/"

query = f"""
SELECT * FROM {INPUT_DATABASE}.{INPUT_TABLE}
"""

df = wr.athena.read_sql_query(
    sql = query,
    database = INPUT_DATABASE,
    ctas_approach = True,
)

wr.s3.to_parquet(
    df = df,
    path = OUTPUT_S3_PATH,
    index = False,
    mode = 'overwrite',
    dataset = True,
    database = OUTPUT_DATABASE,
    table = OUTPUT_TABLE_NAME,
    schema_evolution = True
)