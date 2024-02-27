from datetime import datetime
import pandas as pd
from tqdm import tqdm
import psycopg2
from psycopg2 import pool
from config import DB_CONFIG  # Import the configuration from the config.py file
import requests

# Set the base API endpoint
base_url = 'https://api.binance.com'
endpoint = '/api/v3/klines'

# Define top coins in USD and EUR
top_coins_usd = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'UNIUSDT', 'LTCUSDT', 'LINKUSDT', 'BCHUSDT']
top_coins_eur = ['BTCEUR', 'ETHEUR', 'BNBEUR', 'XRPEUR', 'ADAEUR', 'DOTEUR', 'UNIEUR', 'LTCEUR', 'LINKEUR', 'BCHEUR']

# Define time interval and limit for API requests
interval = '1d'
limit = 1500
dfs = []

# Set up a connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

# Loop through years
for year in range(2017, datetime.now().year + 1):
    start_time = int(datetime(year, 1, 1).timestamp()) * 1000
    end_time = int(datetime(year, 12, 31).timestamp()) * 1000

    # Loop through symbols (coins) for each year
    for symbol in tqdm(top_coins_usd + top_coins_eur, desc=f"Processing coins for {year}"):
        currency = 'USD' if symbol in top_coins_usd else 'EUR'
        url = f'{base_url}{endpoint}?symbol={symbol}&interval={interval}&limit={limit}&startTime={start_time}&endTime={end_time}'
        response = requests.get(url)

        # Check if API request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            columns = ["Symbol", "Currency", "Open Time", "Open Price", "High Price", "Low Price", "Close Price", "Volume", "Close Time", "Trade Count"]
            df = pd.DataFrame(columns=columns)
            rows = []

            # Process kline data and populate rows
            for kline in data:
                open_time = datetime.utcfromtimestamp(kline[0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                close_time = datetime.utcfromtimestamp(kline[6] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
                row = [symbol, currency, open_time, kline[1], kline[2], kline[3], kline[4], kline[5], close_time, kline[8]]
                rows.append(row)

            # Create a DataFrame from processed data
            df = pd.concat([df, pd.DataFrame(rows, columns=columns)], ignore_index=True)

            # Check for Missing Rows
            expected_rows = (int((end_time - start_time) / 1000) // int(interval[:-1])) + 1
            if len(df) != expected_rows:
                print(f"Missing data for {year} - {symbol}. Expected {expected_rows} rows, got {len(df)} rows.")

            # Check for Missing Dates
            expected_dates = pd.date_range(start=datetime.utcfromtimestamp(start_time / 1000.0), end=datetime.utcfromtimestamp(end_time / 1000.0), freq=interval)
            missing_dates = expected_dates[~expected_dates.isin(pd.to_datetime(df['Open Time']))]
            if not missing_dates.empty:
                print(f"Missing data for {year} - {symbol} on dates: {missing_dates}")

            # Attempt to connect to the database using a connection from the pool
            try:
                connection = connection_pool.getconn()
                with connection.cursor() as cur:
                    # Create the combined_table if it doesn't exist
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS combined_table (
                            id SERIAL PRIMARY KEY,
                            symbol VARCHAR(20) NOT NULL,
                            currency VARCHAR(3) NOT NULL,
                            open_time TIMESTAMP NOT NULL,
                            open_price NUMERIC NOT NULL,
                            high_price NUMERIC NOT NULL,
                            low_price NUMERIC NOT NULL,
                            close_price NUMERIC NOT NULL,
                            volume NUMERIC NOT NULL,
                            close_time TIMESTAMP NOT NULL,
                            trade_count INTEGER NOT NULL,
                            CONSTRAINT symbol_open_time_currency_unique_constraint UNIQUE (symbol, open_time, currency)
                        );
                    """)
                    # Create an index if it doesn't exist
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_symbol_open_time_currency ON combined_table (symbol, open_time, currency);")

                    # Insert data into the combined_table, ignoring conflicts
                    for _, row in df.iterrows():
                        cur.execute("""
                            INSERT INTO combined_table (symbol, currency, open_time, open_price, high_price, low_price, close_price, volume, close_time, trade_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, open_time, currency) DO NOTHING;
                        """, tuple(row))
            except Exception as e:
                print(f"Error connecting to the database or inserting data: {e}")
            finally:
                # Release the connection back to the pool
                connection_pool.putconn(connection)
        else:
            print(f'Error: {response.status_code} - {response.text}')

# Close all connections in the pool
connection_pool.closeall()

# Concatenate DataFrames and display the result
result_df = pd.concat(dfs, ignore_index=True)
result_df
