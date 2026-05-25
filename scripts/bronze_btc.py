import time
import sys
import requests
import pandas as pd
import awswrangler as wr
from datetime import datetime, timedelta
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(
    sys.argv,
    [
        'bronze_bucket',
        'bronze_database',
    ]
     )


OUTPUT_BUCKET = args['bronze_bucket']
PROJECT = "btc"
OUTPUT_DATABASE = args['bronze_database']
OUTPUT_TABLE_NAME = f"{PROJECT}"
OUTPUT_S3_PATH = f"s3://{OUTPUT_BUCKET}/{PROJECT}/{OUTPUT_TABLE_NAME}/"
TEMP_PATH = f"s3://{OUTPUT_BUCKET}/temp-athena/"


SYMBOL = "BTCUSDT"
INTERVAL = "1h"   
LIMIT = 1000      
ENDPOINT = "https://api.binance.com/api/v3/klines"

def get_binance_data(symbol, interval, limit, days_back):
    print(f"Starting data extraction for {symbol} for the last {days_back} days...")
    
    start_time = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)
    end_time = int(datetime.now().timestamp() * 1000)
    
    all_data = []
    
    while start_time < end_time:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time
        }
        
        response = requests.get(ENDPOINT, params=params)
        response.raise_for_status() 
        
        data = response.json()
        if not data:
            break 
            
        all_data.extend(data)
        
        start_time = data[-1][6] + 1
        
        time.sleep(0.5)
        
    return all_data

raw_data = get_binance_data(SYMBOL, INTERVAL, LIMIT, days_back=90)

columns = [
    "open_time", "open", "high", "low", "close", "volume", 
    "close_time", "quote_asset_volume", "number_of_trades", 
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
]

df = pd.DataFrame(raw_data, columns=columns)

df = df.astype(str)

df["ingestion_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df["symbol"] = SYMBOL

print(f"Data extraction finished. {len(df)} records stored.")

print("Storing data in s3 + athena...")
wr.athena.to_iceberg(
    df=df,
    database=OUTPUT_DATABASE,
    table=OUTPUT_TABLE_NAME,
    table_location=OUTPUT_S3_PATH,
    temp_path=TEMP_PATH,
    mode="overwrite"
)

print("Bronze process finished")