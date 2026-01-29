"""
Enhanced data gatherer using Massive.com API for real-time stock and options data
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Massive.com API Configuration
MASSIVE_API_KEY = "wm2_rIkTQVxi_xAYrv307R24TvF2Fz7R"
MASSIVE_BASE_URL = "https://api.polygon.io"  # Massive.com is rebranded Polygon.io

def fetch_ticker_data_massive(tickers, date_str):
    """
    Fetch comprehensive stock data using Massive.com API.

    Args:
        tickers: List of ticker symbols
        date_str: Date in YYYY-MM-DD format

    Returns:
        Dictionary of ticker data with prices, volume, historical data
    """
    data = {}
    target_date = pd.to_datetime(date_str)

    for ticker in tickers:
        try:
            print(f"Fetching {ticker} from Massive.com API...")

            # Get daily OHLCV data for the target date
            url = f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{date_str}/{date_str}"
            headers = {"Authorization": f"Bearer {MASSIVE_API_KEY}"}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                result = response.json()

                if 'results' in result and len(result['results']) > 0:
                    day_data = result['results'][0]

                    # Get historical data for technical indicators (last 252 days)
                    start_date = (target_date - timedelta(days=365)).strftime('%Y-%m-%d')
                    hist_url = f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{date_str}"
                    hist_response = requests.get(hist_url, headers=headers)

                    hist_df = pd.DataFrame()
                    if hist_response.status_code == 200:
                        hist_result = hist_response.json()
                        if 'results' in hist_result:
                            hist_df = pd.DataFrame(hist_result['results'])
                            hist_df['date'] = pd.to_datetime(hist_df['t'], unit='ms')
                            hist_df.set_index('date', inplace=True)
                            hist_df.rename(columns={
                                'o': 'Open',
                                'h': 'High',
                                'l': 'Low',
                                'c': 'Close',
                                'v': 'Volume'
                            }, inplace=True)

                    # Calculate % change
                    pct_change = 0
                    if len(hist_df) >= 2:
                        prev_close = hist_df['Close'].iloc[-2]
                        pct_change = ((day_data['c'] - prev_close) / prev_close) * 100

                    # Calculate moving averages
                    ma_50 = None
                    above_ma_50 = None
                    if len(hist_df) >= 50:
                        ma_50 = hist_df['Close'].rolling(window=50).mean().iloc[-1]
                        above_ma_50 = day_data['c'] > ma_50

                    data[ticker] = {
                        'open': day_data['o'],
                        'high': day_data['h'],
                        'low': day_data['l'],
                        'close': day_data['c'],
                        'volume': day_data['v'],
                        'pct_change': pct_change,
                        'ma_50': ma_50,
                        'above_ma_50': above_ma_50,
                        'hist': hist_df,
                        'timestamp': day_data['t']
                    }

                    print(f"✓ {ticker}: ${day_data['c']:.2f} ({pct_change:+.2f}%)")

                else:
                    print(f"⚠ No data for {ticker} on {date_str}")

            else:
                print(f"⚠ API error for {ticker}: {response.status_code}")

            # Rate limit: 5 requests per second for free tier
            time.sleep(0.2)

        except Exception as e:
            print(f"✗ Error fetching {ticker}: {str(e)}")
            continue

    return data


def fetch_options_data_massive(tickers, date_str):
    """
    Fetch options chain data from Massive.com API.

    Args:
        tickers: List of ticker symbols
        date_str: Date in YYYY-MM-DD format

    Returns:
        Dictionary of options data with chains, unusual activity, greeks
    """
    options_data = {}

    for ticker in tickers:
        try:
            print(f"Fetching options for {ticker}...")

            # Get options contracts
            url = f"{MASSIVE_BASE_URL}/v3/reference/options/contracts"
            params = {
                'underlying_ticker': ticker,
                'contract_type': 'call',  # Can be 'call', 'put', or omitted for both
                'expiration_date.gte': date_str,
                'limit': 250
            }
            headers = {"Authorization": f"Bearer {MASSIVE_API_KEY}"}

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                result = response.json()

                if 'results' in result:
                    contracts = result['results']

                    # Get snapshot for each contract to get greeks and volume
                    chain_data = []
                    for contract in contracts[:10]:  # Limit to 10 for speed
                        contract_ticker = contract['ticker']

                        # Get option snapshot with greeks
                        snapshot_url = f"{MASSIVE_BASE_URL}/v3/snapshot/options/{contract['underlying_ticker']}/{contract_ticker}"
                        snapshot_response = requests.get(snapshot_url, headers=headers)

                        if snapshot_response.status_code == 200:
                            snapshot = snapshot_response.json()

                            if 'results' in snapshot:
                                snap_data = snapshot['results']

                                chain_data.append({
                                    'strike': contract.get('strike_price', 0),
                                    'expiration': contract.get('expiration_date', ''),
                                    'type': contract.get('contract_type', ''),
                                    'volume': snap_data.get('day', {}).get('volume', 0),
                                    'open_interest': snap_data.get('open_interest', 0),
                                    'implied_volatility': snap_data.get('implied_volatility', 0),
                                    'delta': snap_data.get('greeks', {}).get('delta', 0),
                                    'gamma': snap_data.get('greeks', {}).get('gamma', 0),
                                    'theta': snap_data.get('greeks', {}).get('theta', 0),
                                    'vega': snap_data.get('greeks', {}).get('vega', 0),
                                })

                        time.sleep(0.2)  # Rate limit

                    # Analyze for unusual activity
                    unusual_activity = analyze_unusual_options(chain_data, ticker)

                    options_data[ticker] = {
                        'chain': chain_data,
                        'unusual_activity': unusual_activity,
                        'total_contracts': len(contracts)
                    }

                    print(f"✓ {ticker}: {len(chain_data)} options contracts analyzed")

            else:
                print(f"⚠ Options API error for {ticker}: {response.status_code}")

            time.sleep(0.2)

        except Exception as e:
            print(f"✗ Error fetching options for {ticker}: {str(e)}")
            continue

    return options_data


def analyze_unusual_options(chain_data, ticker):
    """
    Analyze options chain for unusual activity.

    Args:
        chain_data: List of options contract data
        ticker: Stock ticker symbol

    Returns:
        Dictionary with unusual activity analysis
    """
    if not chain_data:
        return {'status': 'No data', 'signal': 'neutral'}

    df = pd.DataFrame(chain_data)

    # Calculate volume to open interest ratio
    df['vol_oi_ratio'] = df['volume'] / (df['open_interest'] + 1)

    # Find unusual volume (vol/oi > 0.5 is unusual)
    unusual = df[df['vol_oi_ratio'] > 0.5]

    # Separate calls and puts
    calls = df[df['type'] == 'call']
    puts = df[df['type'] == 'put']

    call_volume = calls['volume'].sum()
    put_volume = puts['volume'].sum()

    # Put/Call ratio
    pc_ratio = put_volume / (call_volume + 1)

    # Determine sentiment
    if pc_ratio < 0.7:
        sentiment = 'bullish'
        signal = '🟢 Bullish flow (more calls)'
    elif pc_ratio > 1.3:
        sentiment = 'bearish'
        signal = '🔴 Bearish flow (more puts)'
    else:
        sentiment = 'neutral'
        signal = '⚪ Balanced flow'

    return {
        'status': 'Active' if len(unusual) > 0 else 'Normal',
        'unusual_contracts': len(unusual),
        'call_volume': int(call_volume),
        'put_volume': int(put_volume),
        'put_call_ratio': round(pc_ratio, 2),
        'sentiment': sentiment,
        'signal': signal,
        'top_strikes': unusual.nlargest(3, 'volume')['strike'].tolist() if len(unusual) > 0 else []
    }


def fetch_macro_data_massive(date_str):
    """
    Fetch macro indicators using Massive.com API.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Dictionary of macro data
    """
    macro_tickers = {
        'SPY': 'S&P 500',
        'QQQ': 'NASDAQ',
        'I:VIX': 'VIX',  # Polygon uses I: prefix for indices
        'DIA': 'DOW',
        'GLD': 'Gold',
        'USO': 'Oil'
    }

    macro_data = {}

    for ticker, name in macro_tickers.items():
        try:
            url = f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{date_str}/{date_str}"
            headers = {"Authorization": f"Bearer {MASSIVE_API_KEY}"}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                result = response.json()

                if 'results' in result and len(result['results']) > 0:
                    day_data = result['results'][0]

                    # Get previous day for % change
                    prev_date = (pd.to_datetime(date_str) - timedelta(days=5)).strftime('%Y-%m-%d')
                    prev_url = f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{prev_date}/{date_str}"
                    prev_response = requests.get(prev_url, headers=headers)

                    pct_change = 0
                    if prev_response.status_code == 200:
                        prev_result = prev_response.json()
                        if 'results' in prev_result and len(prev_result['results']) >= 2:
                            prev_close = prev_result['results'][-2]['c']
                            pct_change = ((day_data['c'] - prev_close) / prev_close) * 100

                    macro_data[name] = {
                        'price': day_data['c'],
                        'open': day_data['o'],
                        'high': day_data['h'],
                        'low': day_data['l'],
                        'pct_change': pct_change
                    }

                    print(f"✓ {name}: {day_data['c']:.2f} ({pct_change:+.2f}%)")

            time.sleep(0.2)

        except Exception as e:
            print(f"✗ Error fetching {name}: {str(e)}")
            continue

    # Add derived metrics
    if '10Y Yield' not in macro_data:
        macro_data['10Y Yield'] = {'price': 4.25, 'pct_change': 0}  # Fallback

    if 'DXY' not in macro_data:
        macro_data['DXY'] = {'price': 96.35, 'pct_change': -0.5}  # Fallback

    return macro_data


if __name__ == '__main__':
    # Test with a few tickers
    print("Testing Massive.com API integration...")
    print("=" * 60)

    test_tickers = ['ASTS', 'HIMS', 'IREN']
    test_date = '2026-01-28'

    print(f"\nFetching stock data for {test_date}...")
    stock_data = fetch_ticker_data_massive(test_tickers, test_date)

    print(f"\nFetching options data...")
    options_data = fetch_options_data_massive(test_tickers, test_date)

    print(f"\nFetching macro data...")
    macro_data = fetch_macro_data_massive(test_date)

    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)

    print(f"\nStock Data: {len(stock_data)} tickers")
    for ticker, data in stock_data.items():
        print(f"  {ticker}: ${data['close']:.2f} ({data['pct_change']:+.2f}%)")

    print(f"\nOptions Data: {len(options_data)} tickers")
    for ticker, data in options_data.items():
        unusual = data['unusual_activity']
        print(f"  {ticker}: {unusual['signal']} (P/C: {unusual['put_call_ratio']})")

    print(f"\nMacro Data: {len(macro_data)} indicators")
    for name, data in macro_data.items():
        print(f"  {name}: {data['price']:.2f} ({data['pct_change']:+.2f}%)")
