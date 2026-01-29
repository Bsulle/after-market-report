"""
Massive.com S3-based data gatherer for stock and options data.
Uses boto3 to access flat files from Massive.com's S3 storage.
"""

import boto3
from botocore.config import Config
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import json

# Massive.com S3 Configuration
MASSIVE_S3_ENDPOINT = "https://files.massive.com"
MASSIVE_ACCESS_KEY = "03ca9a2a-b150-4ad7-bc6c-491054d89e1d"
MASSIVE_SECRET_KEY = "wm2_rIkTQVxi_xAYrv307R24TvF2Fz7R"
MASSIVE_BUCKET = "flatfiles"


def get_s3_client():
    """Create and return an S3 client configured for Massive.com."""
    return boto3.client(
        's3',
        endpoint_url=MASSIVE_S3_ENDPOINT,
        aws_access_key_id=MASSIVE_ACCESS_KEY,
        aws_secret_access_key=MASSIVE_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )


def list_bucket_contents(prefix='', max_keys=100):
    """
    List contents of the Massive.com S3 bucket.
    Useful for discovering available data files.
    """
    s3 = get_s3_client()

    try:
        response = s3.list_objects_v2(
            Bucket=MASSIVE_BUCKET,
            Prefix=prefix,
            MaxKeys=max_keys
        )

        if 'Contents' in response:
            files = []
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat()
                })
            return files
        else:
            print(f"No files found with prefix: {prefix}")
            return []

    except Exception as e:
        print(f"Error listing bucket: {str(e)}")
        return []


def discover_data_structure():
    """
    Discover the structure of available data in Massive.com S3.
    Run this to understand how data is organized.
    """
    print("Discovering Massive.com S3 data structure...")
    print("=" * 60)

    s3 = get_s3_client()

    # Try common prefixes
    prefixes = ['', 'stocks/', 'options/', 'equity/', 'market/', 'daily/', 'eod/', 'data/']

    for prefix in prefixes:
        print(f"\nTrying prefix: '{prefix}'")
        files = list_bucket_contents(prefix, max_keys=20)

        if files:
            print(f"  Found {len(files)} files:")
            for f in files[:10]:
                print(f"    - {f['key']} ({f['size']} bytes)")

    return files


def read_csv_from_s3(key):
    """Read a CSV file from Massive.com S3."""
    s3 = get_s3_client()

    try:
        response = s3.get_object(Bucket=MASSIVE_BUCKET, Key=key)
        content = response['Body'].read().decode('utf-8')
        return pd.read_csv(StringIO(content))
    except Exception as e:
        print(f"Error reading {key}: {str(e)}")
        return None


def read_parquet_from_s3(key):
    """Read a Parquet file from Massive.com S3."""
    s3 = get_s3_client()

    try:
        response = s3.get_object(Bucket=MASSIVE_BUCKET, Key=key)
        content = response['Body'].read()
        return pd.read_parquet(BytesIO(content))
    except Exception as e:
        print(f"Error reading {key}: {str(e)}")
        return None


def fetch_ticker_data_s3(tickers, date_str):
    """
    Fetch stock data from Massive.com S3 flat files.

    Note: The exact file path structure depends on how Massive.com
    organizes their data. This function will attempt common patterns.
    """
    data = {}
    target_date = pd.to_datetime(date_str)
    date_formatted = target_date.strftime('%Y-%m-%d')
    date_compact = target_date.strftime('%Y%m%d')

    s3 = get_s3_client()

    # Common file path patterns to try
    path_patterns = [
        f"stocks/{date_formatted}/",
        f"equity/daily/{date_formatted}/",
        f"eod/{date_compact}/",
        f"market/stocks/{date_formatted}/",
        f"daily/{date_formatted}/stocks/",
        f"data/stocks/{date_formatted}/",
    ]

    print(f"Fetching data for {len(tickers)} tickers from Massive.com S3...")

    # First, try to find the data directory
    found_path = None
    for pattern in path_patterns:
        files = list_bucket_contents(pattern, max_keys=5)
        if files:
            found_path = pattern
            print(f"Found data at: {pattern}")
            break

    if not found_path:
        print("Could not locate stock data in S3. Trying alternative approaches...")

        # Try to find any recent files
        all_files = list_bucket_contents('', max_keys=50)
        if all_files:
            print("Available files in bucket:")
            for f in all_files[:10]:
                print(f"  {f['key']}")

        return data

    # Fetch data for each ticker
    for ticker in tickers:
        try:
            # Try different file naming conventions
            possible_files = [
                f"{found_path}{ticker}.csv",
                f"{found_path}{ticker.lower()}.csv",
                f"{found_path}{ticker}.parquet",
                f"{found_path}{ticker.lower()}.parquet",
            ]

            for file_path in possible_files:
                try:
                    if file_path.endswith('.csv'):
                        df = read_csv_from_s3(file_path)
                    else:
                        df = read_parquet_from_s3(file_path)

                    if df is not None and not df.empty:
                        # Parse the data (adjust column names based on actual structure)
                        latest = df.iloc[-1] if len(df) > 0 else df.iloc[0]

                        # Common column name mappings
                        col_map = {
                            'open': ['open', 'Open', 'o', 'OPEN'],
                            'high': ['high', 'High', 'h', 'HIGH'],
                            'low': ['low', 'Low', 'l', 'LOW'],
                            'close': ['close', 'Close', 'c', 'CLOSE', 'adj_close'],
                            'volume': ['volume', 'Volume', 'v', 'VOLUME', 'vol']
                        }

                        def get_col(df, options):
                            for opt in options:
                                if opt in df.columns:
                                    return df[opt]
                            return None

                        close_val = get_col(pd.DataFrame([latest]), col_map['close'])
                        if close_val is not None:
                            close_price = float(close_val.iloc[0])
                        else:
                            continue

                        data[ticker] = {
                            'current_price': close_price,
                            'open': float(get_col(pd.DataFrame([latest]), col_map['open']).iloc[0]) if get_col(pd.DataFrame([latest]), col_map['open']) is not None else close_price,
                            'high': float(get_col(pd.DataFrame([latest]), col_map['high']).iloc[0]) if get_col(pd.DataFrame([latest]), col_map['high']) is not None else close_price,
                            'low': float(get_col(pd.DataFrame([latest]), col_map['low']).iloc[0]) if get_col(pd.DataFrame([latest]), col_map['low']) is not None else close_price,
                            'close': close_price,
                            'volume': int(get_col(pd.DataFrame([latest]), col_map['volume']).iloc[0]) if get_col(pd.DataFrame([latest]), col_map['volume']) is not None else 0,
                            'hist': df,
                            'pct_change': 0,  # Calculate if historical data available
                            'ma_50': None,
                            'above_ma_50': None
                        }

                        print(f"  Fetched {ticker}: ${close_price:.2f}")
                        break

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  Error fetching {ticker}: {str(e)[:50]}")
            continue

    return data


def fetch_options_data_s3(tickers, date_str):
    """
    Fetch options data from Massive.com S3 flat files.
    """
    options_data = {}
    target_date = pd.to_datetime(date_str)
    date_formatted = target_date.strftime('%Y-%m-%d')

    # Common path patterns for options data
    path_patterns = [
        f"options/{date_formatted}/",
        f"options/chains/{date_formatted}/",
        f"market/options/{date_formatted}/",
        f"data/options/{date_formatted}/",
    ]

    print(f"Fetching options data from Massive.com S3...")

    # Try to find options data directory
    found_path = None
    for pattern in path_patterns:
        files = list_bucket_contents(pattern, max_keys=5)
        if files:
            found_path = pattern
            print(f"Found options data at: {pattern}")
            break

    if not found_path:
        print("Options data not found in S3. Using yfinance fallback.")
        return options_data

    # Fetch options for each ticker
    for ticker in tickers:
        try:
            file_path = f"{found_path}{ticker}.csv"
            df = read_csv_from_s3(file_path)

            if df is not None and not df.empty:
                # Process options chain
                calls = df[df['type'].str.lower() == 'call'] if 'type' in df.columns else pd.DataFrame()
                puts = df[df['type'].str.lower() == 'put'] if 'type' in df.columns else pd.DataFrame()

                call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
                put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0

                pc_ratio = put_volume / call_volume if call_volume > 0 else 0

                options_data[ticker] = {
                    'total_call_volume': int(call_volume),
                    'total_put_volume': int(put_volume),
                    'put_call_ratio': round(pc_ratio, 2),
                    'sentiment': 'BULLISH' if pc_ratio < 0.7 else ('BEARISH' if pc_ratio > 1.3 else 'NEUTRAL'),
                    'chain': df.to_dict('records')[:50]  # Limit to 50 contracts
                }

                print(f"  Fetched options for {ticker}: P/C={pc_ratio:.2f}")

        except Exception as e:
            continue

    return options_data


if __name__ == '__main__':
    print("=" * 60)
    print("Massive.com S3 Data Gatherer")
    print("=" * 60)

    # First, discover the data structure
    print("\n1. Discovering bucket structure...")
    discover_data_structure()

    # Test fetching data
    print("\n2. Testing stock data fetch...")
    test_tickers = ['ASTS', 'IREN', 'HIMS']
    test_date = '2026-01-29'

    stock_data = fetch_ticker_data_s3(test_tickers, test_date)
    print(f"\nFetched {len(stock_data)} tickers")

    for ticker, data in stock_data.items():
        print(f"  {ticker}: ${data['close']:.2f}")

    print("\n3. Testing options data fetch...")
    options_data = fetch_options_data_s3(test_tickers, test_date)
    print(f"\nFetched options for {len(options_data)} tickers")
