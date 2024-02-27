from datetime import datetime, timedelta
import pandas as pd
from airflow import DAG
import requests
import psycopg2
from psycopg2 import pool
from config import DB_CONFIG  # Import the configuration from the config.py file
import logging
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.exceptions import AirflowException

# Define default arguments for the DAG
default_args = {
    'owner': 'mikomaxi',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 28),  # Adjust start_date as per your requirements
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# Instantiate a DAG
dag = DAG(
    'binance_data_dag',
    default_args=default_args,
    description='A DAG to fetch data from Binance API and store it in PostgreSQL',
    schedule_interval='@daily',  # Run the DAG daily
)

def check_database_connection(postgres_conn_id='Crypto_connection'):
    """
    Task: Check the connection to a PostgreSQL database using a PostgresHook.

    Parameters:
    - postgres_conn_id (str): The Airflow connection ID for PostgreSQL.

    Returns:
    - bool: True if the connection is successful, False otherwise.
    """
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        connection = hook.get_conn()
        logging.info("Successfully connected to the database.")
        return True
    except AirflowException as e:
        logging.error(f"Error checking database connection: {e}")
        return False

# Task to check database connection
check_database_task = PythonOperator(
    task_id='check_database_connection',
    python_callable=check_database_connection,
    dag=dag,
)

def test_binance_connectivity():
    """
    Task: Test the connectivity to the Binance API.

    Prints the result of the connectivity test.
    """
    try:
        base_url = 'https://api.binance.com'
        endpoint = '/api/v3/ping'
        url = f'{base_url}{endpoint}'
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Connectivity test successful. Binance API is reachable.")
        else:
            logging.warning(f"Connectivity test failed. Status code: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"An error occurred during the connectivity test: {e}")

# Task to test Binance API connectivity
test_connectivity_task = PythonOperator(
    task_id='test_binance_connectivity',
    python_callable=test_binance_connectivity,
    dag=dag,
)

def check_if_database_empty(**kwargs):
    """
    Task: Check if the PostgreSQL database is empty.

    Parameters:
    - **kwargs: Context passed by Airflow.

    Returns:
    - str: Task ID of the next task to execute based on the database status.
    """
    try:
        hook = PostgresHook(postgres_conn_id='Crypto_connection')
        connection = hook.get_conn()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM combined_table;")
            row_count = cursor.fetchone()[0]
            if row_count > 0:
                return "extract_latest_timestamp"
            else:
                return "populate_database_task"
    except Exception as e:
        logging.error(f"Error checking if the database is empty: {e}")
        return "populate_database_task"  # In case of an error, proceed to populate_database_task
    finally:
        if connection:
            connection.close()

# Task to check if the database is empty
check_database_empty_task = BranchPythonOperator(
    task_id='check_if_database_empty',
    python_callable=check_if_database_empty,
    provide_context=True,
    dag=dag,
)

def fetch_latest_open_time(**kwargs):
    """
    Task: Fetch the latest open_time registered in the postgres database and share it on xComs.

    Parameters:
    - **kwargs: Context passed by Airflow.

    Returns:
    - None
    """
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(open_time) FROM combined_table;")
            latest_open_time = cursor.fetchone()[0]
            if latest_open_time:
                kwargs['ti'].xcom_push(key='latest_open_time', value=latest_open_time)
                logging.info("Successfully fetched the latest open time.")
            else:
                logging.warning("No data in the combined_table.")
    except Exception as e:
        logging.error(f"Error fetching latest open time: {e}")
    finally:
        if connection:
            connection.close()

# Task to fetch the latest open_time
extract_timestamp_task = PythonOperator(
    task_id='extract_latest_timestamp',
    python_callable=fetch_latest_open_time,
    provide_context=True,
    dag=dag,
)

def populate_database(**kwargs):
    """
    Task: Populate the PostgreSQL database with initial data.

    Parameters:
    - **kwargs: Context passed by Airflow.

    Returns:
    - None
    """
    try:
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
            for symbol in top_coins_usd + top_coins_eur:
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
                        logging.warning(f"Missing data for {year} - {symbol}. Expected {expected_rows} rows, got {len(df)} rows.")

                    # Check for Missing Dates
                    expected_dates = pd.date_range(start=datetime.utcfromtimestamp(start_time / 1000.0), end=datetime.utcfromtimestamp(end_time / 1000.0), freq=interval)
                    missing_dates = expected_dates[~expected_dates.isin(pd.to_datetime(df['Open Time']))]
                    if not missing_dates.empty:
                        logging.warning(f"Missing data for {year} - {symbol} on dates: {missing_dates}")

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
                        logging.error(f"Error connecting to the database or inserting data: {e}")
                    finally:
                        # Release the connection back to the pool
                        connection_pool.putconn(connection)
                else:
                    logging.error(f'Error: {response.status_code} - {response.text}')

        # Close all connections in the pool
        connection_pool.closeall()

        # Concatenate DataFrames and display the result
        result_df = pd.concat(dfs, ignore_index=True)
        logging.info("Database population task completed successfully.")
    except Exception as e:
        logging.error(f"Error in populate_database task: {e}")

# Task to populate the database
populate_database_task = PythonOperator(
    task_id='populate_database_task',
    python_callable=populate_database,
    provide_context=True,  # Provide the context to the function
    dag=dag,
)

def add_the_latest_data(**kwargs):
    """
    Task: Add the latest data to the PostgreSQL database.

    Parameters:
    - **kwargs: Context passed by Airflow.

    Returns:
    - None
    """
    try:
        # Use the xCom value as the start time for API call
        latest_open_time = kwargs['ti'].xcom_pull(task_ids='extract_latest_timestamp', key='latest_open_time')

        # Convert Unix timestamp to milliseconds
        start_time = int(latest_open_time.timestamp()) * 1000

        # Set the base API endpoint
        base_url = 'https://api.binance.com'
        endpoint = '/api/v3/klines'

        # Define top coins in USD and EUR
        top_coins_usd = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'UNIUSDT', 'LTCUSDT', 'LINKUSDT', 'BCHUSDT']
        top_coins_eur = ['BTCEUR', 'ETHEUR', 'BNBEUR', 'XRPEUR', 'ADAEUR', 'DOTEUR', 'UNIEUR', 'LTCEUR', 'LINKEUR', 'BCHEUR']

        # Define time interval and limit for API requests
        interval = '1d'
        limit = 1500

        # Set up a connection pool
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

        # Loop through symbols (coins)
        for symbol in top_coins_usd + top_coins_eur:
            currency = 'USD' if symbol in top_coins_usd else 'EUR'
            url = f'{base_url}{endpoint}?symbol={symbol}&interval={interval}&limit={limit}&startTime={start_time}'
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

                # Attempt to connect to the database using a connection from the pool
                try:
                    connection = connection_pool.getconn()
                    with connection.cursor() as cur:
                        # Insert data into the combined_table, ignoring conflicts
                        for _, row in df.iterrows():
                            cur.execute("""
                                INSERT INTO combined_table (symbol, currency, open_time, open_price, high_price, low_price, close_price, volume, close_time, trade_count)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (symbol, open_time, currency) DO NOTHING;
                            """, tuple(row))
                except Exception as e:
                    logging.error(f"Error connecting to the database or inserting data: {e}")
                finally:
                    # Release the connection back to the pool
                    connection_pool.putconn(connection)
            else:
                logging.error(f'Error: {response.status_code} - {response.text}')

        # Close all connections in the pool
        connection_pool.closeall()
        logging.info("Latest data addition task completed successfully.")

    except Exception as e:
        logging.error(f"Error in add_the_latest_data task: {e}")

# Task to add the latest data to the database
add_the_latest_data_task = PythonOperator(
    task_id='add_the_latest_data_task',
    python_callable=add_the_latest_data,
    provide_context=True,  # Provide the context to the function
    dag=dag,
)

# Define the DAG structure
check_database_task >> test_connectivity_task >> check_database_empty_task
check_database_empty_task >> [
    extract_timestamp_task,
    populate_database_task,
]
extract_timestamp_task >> add_the_latest_data_task
