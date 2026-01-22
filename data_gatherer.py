import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def fetch_ticker_data(tickers, date_str):
    """Fetch comprehensive data for all tickers for a specific date."""
    data = {}
    target_date = pd.to_datetime(date_str)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # Fetch historical data (last 252 trading days ~1 year)
            hist = stock.history(period='1y')

            if hist.empty:
                print(f"Warning: No data for {ticker}")
                continue

            # Get data up to target date
            hist = hist[hist.index <= target_date]

            if hist.empty:
                print(f"Warning: No data for {ticker} up to {date_str}")
                continue

            # Get the most recent day's data
            latest = hist.iloc[-1]

            data[ticker] = {
                'current_price': latest['Close'],
                'open': latest['Open'],
                'high': latest['High'],
                'low': latest['Low'],
                'close': latest['Close'],
                'volume': latest['Volume'],
                'hist': hist,
                'info': stock.info if hasattr(stock, 'info') else {}
            }

            # Calculate % change
            if len(hist) >= 2:
                prev_close = hist.iloc[-2]['Close']
                data[ticker]['pct_change'] = ((latest['Close'] - prev_close) / prev_close) * 100
                data[ticker]['prev_close'] = prev_close
            else:
                data[ticker]['pct_change'] = 0
                data[ticker]['prev_close'] = latest['Close']

            # Calculate moving averages
            if len(hist) >= 50:
                data[ticker]['ma_50'] = hist['Close'].rolling(window=50).mean().iloc[-1]
                data[ticker]['above_ma_50'] = latest['Close'] > data[ticker]['ma_50']
            else:
                data[ticker]['ma_50'] = None
                data[ticker]['above_ma_50'] = None

            if len(hist) >= 200:
                data[ticker]['ma_200'] = hist['Close'].rolling(window=200).mean().iloc[-1]
            else:
                data[ticker]['ma_200'] = None

            print(f"Fetched data for {ticker}: ${latest['Close']:.2f}")

        except Exception as e:
            print(f"Error fetching {ticker}: {str(e)}")
            continue

    return data

def fetch_macro_data(date_str):
    """Fetch macro market indicators."""
    macro_tickers = {
        'SPY': 'S&P 500',
        'QQQ': 'Nasdaq',
        '^VIX': 'VIX',
        '^TNX': '10Y Yield',
        'DX-Y.NYB': 'DXY',
        'CL=F': 'WTI Oil',
        'GC=F': 'Gold'
    }

    macro_data = {}
    target_date = pd.to_datetime(date_str)

    for ticker, name in macro_tickers.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')

            if hist.empty:
                print(f"Warning: No data for {name} ({ticker})")
                continue

            hist = hist[hist.index <= target_date]

            if hist.empty:
                print(f"Warning: No data for {name} ({ticker}) up to {date_str}")
                continue

            latest = hist.iloc[-1]

            macro_data[name] = {
                'ticker': ticker,
                'price': latest['Close'],
                'open': latest['Open'],
                'high': latest['High'],
                'low': latest['Low'],
                'close': latest['Close']
            }

            # Calculate % change
            if len(hist) >= 2:
                prev_close = hist.iloc[-2]['Close']
                macro_data[name]['pct_change'] = ((latest['Close'] - prev_close) / prev_close) * 100
            else:
                macro_data[name]['pct_change'] = 0

            print(f"Fetched {name}: {latest['Close']:.2f}")

        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")
            continue

    return macro_data

def fetch_breadth_data():
    """Fetch market breadth indicators."""
    breadth_data = {
        'advancers': 0,
        'decliners': 0,
        'new_highs_52w': 0,
        'new_lows_52w': 0,
        'ad_ratio': 1.0
    }

    # Note: Real breadth data would come from market data providers
    # This is a placeholder

    return breadth_data

if __name__ == '__main__':
    tickers = ['AAPL', 'MSFT', 'AMZN']
    ticker_data = fetch_ticker_data(tickers, '2026-01-21')
    macro_data = fetch_macro_data('2026-01-21')
    print(ticker_data)
    print(macro_data)
