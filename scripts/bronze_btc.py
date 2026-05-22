import time
import requests
import pandas as pd
import awswrangler as wr
from datetime import datetime, timedelta

OUTPUT_BUCKET = "datashi-data-sample"
PROJECT = "crypto_market"
OUTPUT_DATABASE = "bronze"
OUTPUT_TABLE_NAME = f"tbl_{PROJECT}_raw"
OUTPUT_S3_PATH = f"s3://{OUTPUT_BUCKET}/{PROJECT}/{OUTPUT_TABLE_NAME}/"
TEMP_PATH = f"s3://{OUTPUT_BUCKET}/temp-athena/"


SYMBOL = "BTCUSDT"
INTERVAL = "1h"   
LIMIT = 1000      
ENDPOINT = "https://api.binance.com/api/v3/klines"

def get_binance_data(symbol, interval, limit, days_back):
    print(f"Iniciando extração de {symbol} dos ultimos {days_back} dias...")
    
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

print(f"Extração concluída. {len(df)} registros obtidos.")

print("Gravando camada Bronze no S3 e registrando no Athena...")
wr.athena.to_iceberg(
    df=df,
    database=OUTPUT_DATABASE,
    table=OUTPUT_TABLE_NAME,
    table_location=OUTPUT_S3_PATH,
    temp_path=TEMP_PATH,
    mode="overwrite"
)

print("Pipeline Bronze finalizada com sucesso!")