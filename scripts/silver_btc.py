import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, to_timestamp

# =============================================================================
# 1. INICIALIZAÇÃO DO MOTOR SPARK E VARIÁVEIS
# =============================================================================
# Lê os argumentos passados pelo Terraform
args = getResolvedOptions(
    sys.argv,
    [
        'JOB_NAME',
        'bronze_bucket',
        'silver_bucket',
        'silver_database'
    ]
)

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BRONZE_BUCKET = args['bronze_bucket']
SILVER_BUCKET = args['silver_bucket']
SILVER_DB = args['silver_database']
TABLE_NAME = "btc"

bronze_path = f"s3://{BRONZE_BUCKET}/btc/btc/"
silver_path = f"s3://{SILVER_BUCKET}/btc/{TABLE_NAME}"

table_identifier = f"glue_catalog.{SILVER_DB}.{TABLE_NAME}"

print("Reading bronze data...")
# Pandas: pd.read_parquet(bronze_path)
# Spark: spark.read.parquet(bronze_path)
df_bronze = spark.read.parquet(bronze_path)

print("Converting/cleaning data...")
# pandas:`df['col'] = ...`
# spark: `.withColumn("nome_da_coluna", nova_logica)`
# `.cast("double")` = `.astype(float)`

df_silver = df_bronze \
    .withColumn("open", col("open").cast("double")) \
    .withColumn("high", col("high").cast("double")) \
    .withColumn("low", col("low").cast("double")) \
    .withColumn("close", col("close").cast("double")) \
    .withColumn("volume", col("volume").cast("double")) \
    .withColumn("candle_time", to_timestamp(col("open_time") / 1000))

# df[['col1', 'col2']] on Pandas
df_final = df_silver.select(
    col("symbol"),
    col("candle_time"),
    col("open"),
    col("high"),
    col("low"),
    col("close"),
    col("volume"),
    col("ingestion_timestamp")
)

# Upsert w/ iceberg
# turn the DataFrame into a temp view

df_final.createOrReplaceTempView("vw_new_data")

# Iceberg core query, merge statement, udpates if the records exists, insert if it does not
merge_query = f"""
MERGE INTO {table_identifier} target
USING vw_new_data source
ON target.symbol = source.symbol AND target.candle_time = source.candle_time
WHEN MATCHED THEN
    UPDATE SET 
        target.open = source.open,
        target.high = source.high,
        target.low = source.low,
        target.close = source.close,
        target.volume = source.volume,
        target.ingestion_timestamp = source.ingestion_timestamp
WHEN NOT MATCHED THEN
    INSERT (symbol, candle_time, open, high, low, close, volume, ingestion_timestamp)
    VALUES (source.symbol, source.candle_time, source.open, source.high, source.low, source.close, source.volume, source.ingestion_timestamp)
"""

# Check if the table already exists on athena/glue catalog
table_exists_query = f"SHOW TABLES IN glue_catalog.{SILVER_DB} LIKE '{TABLE_NAME}'"
tables = spark.sql(table_exists_query).collect()

if len(tables) == 0:
    print("First execution, table does not exist yet...")
    # .writeTo() is the native function of spark to store iceberg tables (V2 allows UPDATE/DELETE statemtns)
    df_final.writeTo(table_identifier) \
        .tableProperty("format-version", "2") \
        .tableProperty("location", silver_path) \
        .create()
else:
    print("Tabela já existe. Executando MERGE INTO para evitar duplicidade...")
    spark.sql(merge_query)

print("Silver layer successfully ran.")
job.commit()