import time
import requests
import pandas as pd
import awswrangler as wr
from datetime import datetime, timedelta

# 1. Variáveis de Configuração AWS
OUTPUT_BUCKET = "datashi-data-sample" # Substitua pelo seu bucket se necessário
PROJECT = "crypto_market"
OUTPUT_DATABASE = "bronze"
OUTPUT_TABLE_NAME = f"tbl_{PROJECT}_raw"
OUTPUT_S3_PATH = f"s3://{OUTPUT_BUCKET}/{PROJECT}/{OUTPUT_TABLE_NAME}/"
TEMP_PATH = f"s3://{OUTPUT_BUCKET}/temp-athena/"

# 2. Configuração da API Binance
SYMBOL = "BTCUSDT"
INTERVAL = "1h"   # Granularidade: de hora em hora
LIMIT = 1000      # Limite máximo por requisição da Binance
ENDPOINT = "https://api.binance.com/api/v3/klines"

def get_binance_data(symbol, interval, limit, days_back):
    print(f"Iniciando extração de {symbol} dos ultimos {days_back} dias...")
    
    # Calcula a janela de tempo em milissegundos (formato exigido pela API)
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
        response.raise_for_status() # Interrompe o script se a API retornar erro HTTP (ex: 429 Rate Limit)
        
        data = response.json()
        if not data:
            break # Sai do loop se não houver mais dados
            
        all_data.extend(data)
        
        # Atualiza o startTime para o fechamento do último registro lido + 1 milissegundo
        # O índice [6] no retorno da Binance representa o "Close time"
        start_time = data[-1][6] + 1
        
        # Pausa rápida para respeitar o Rate Limit da API
        time.sleep(0.5)
        
    return all_data

# Executa a função buscando os últimos 90 dias de dados
raw_data = get_binance_data(SYMBOL, INTERVAL, LIMIT, days_back=90)

# 3. Modelagem do DataFrame
# Nomes das colunas documentadas oficialmente pela Binance
columns = [
    "open_time", "open", "high", "low", "close", "volume", 
    "close_time", "quote_asset_volume", "number_of_trades", 
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
]

df = pd.DataFrame(raw_data, columns=columns)

# Converte tudo para string para garantir ingestão à prova de falhas na camada Bronze
df = df.astype(str)

# Adiciona metadados de observabilidade
df["ingestion_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df["symbol"] = SYMBOL

print(f"Extração concluída. {len(df)} registros obtidos.")

# 4. Gravação na AWS (Apache Iceberg)
print("Gravando camada Bronze no S3 e registrando no Athena...")
wr.athena.to_iceberg(
    df=df,
    database=OUTPUT_DATABASE,
    table=OUTPUT_TABLE_NAME,
    table_location=OUTPUT_S3_PATH,
    temp_path=TEMP_PATH,
    mode="overwrite" # Durante o desenvolvimento do portfólio, overwrite facilita os testes
)

print("Pipeline Bronze finalizada com sucesso!")