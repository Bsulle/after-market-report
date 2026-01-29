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

            # Get data up to target date (handle timezone-aware index)
            hist_index_naive = hist.index.tz_localize(None) if hist.index.tz is not None else hist.index
            hist = hist[hist_index_naive <= target_date]

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

            # Handle timezone-aware index
            hist_index_naive = hist.index.tz_localize(None) if hist.index.tz is not None else hist.index
            hist = hist[hist_index_naive <= target_date]

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


def fetch_options_data(tickers):
    """Fetch options flow data using yfinance (free)."""
    options_data = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            # Get available expiration dates
            expirations = stock.options
            if not expirations:
                continue

            # Get nearest expiration (most active)
            nearest_exp = expirations[0]

            # Get options chain
            opt_chain = stock.option_chain(nearest_exp)
            calls = opt_chain.calls
            puts = opt_chain.puts

            if calls.empty and puts.empty:
                continue

            # Calculate metrics
            total_call_volume = calls['volume'].sum() if 'volume' in calls.columns else 0
            total_put_volume = puts['volume'].sum() if 'volume' in puts.columns else 0
            total_call_oi = calls['openInterest'].sum() if 'openInterest' in calls.columns else 0
            total_put_oi = puts['openInterest'].sum() if 'openInterest' in puts.columns else 0

            # Put/Call ratio
            pc_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 0
            pc_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0

            # Find highest volume strikes
            top_call_strikes = calls.nlargest(3, 'volume')[['strike', 'volume', 'openInterest', 'impliedVolatility']] if not calls.empty else pd.DataFrame()
            top_put_strikes = puts.nlargest(3, 'volume')[['strike', 'volume', 'openInterest', 'impliedVolatility']] if not puts.empty else pd.DataFrame()

            # Average IV
            avg_call_iv = calls['impliedVolatility'].mean() * 100 if 'impliedVolatility' in calls.columns else 0
            avg_put_iv = puts['impliedVolatility'].mean() * 100 if 'impliedVolatility' in puts.columns else 0

            options_data[ticker] = {
                'nearest_expiry': nearest_exp,
                'total_call_volume': int(total_call_volume) if not pd.isna(total_call_volume) else 0,
                'total_put_volume': int(total_put_volume) if not pd.isna(total_put_volume) else 0,
                'total_call_oi': int(total_call_oi) if not pd.isna(total_call_oi) else 0,
                'total_put_oi': int(total_put_oi) if not pd.isna(total_put_oi) else 0,
                'put_call_ratio': round(pc_ratio, 2) if not pd.isna(pc_ratio) else 0,
                'put_call_oi_ratio': round(pc_oi_ratio, 2) if not pd.isna(pc_oi_ratio) else 0,
                'avg_call_iv': round(avg_call_iv, 1) if not pd.isna(avg_call_iv) else 0,
                'avg_put_iv': round(avg_put_iv, 1) if not pd.isna(avg_put_iv) else 0,
                'top_call_strikes': top_call_strikes.to_dict('records') if not top_call_strikes.empty else [],
                'top_put_strikes': top_put_strikes.to_dict('records') if not top_put_strikes.empty else [],
                'sentiment': 'BULLISH' if pc_ratio < 0.7 else ('BEARISH' if pc_ratio > 1.3 else 'NEUTRAL')
            }

            print(f"Fetched options for {ticker}: P/C={pc_ratio:.2f} ({options_data[ticker]['sentiment']})")

        except Exception as e:
            print(f"Options error for {ticker}: {str(e)[:50]}")
            continue

    return options_data


def fetch_earnings_calendar(tickers):
    """Fetch upcoming earnings dates for watchlist tickers."""
    earnings_data = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get earnings date if available
            earnings_date = info.get('earningsDate')

            if earnings_date:
                # Handle list format from yfinance
                if isinstance(earnings_date, list) and len(earnings_date) > 0:
                    earnings_date = earnings_date[0]

                earnings_data[ticker] = {
                    'earnings_date': str(earnings_date)[:10] if earnings_date else 'N/A',
                    'earnings_estimate': info.get('earningsQuarterlyGrowth'),
                    'revenue_estimate': info.get('revenueQuarterlyGrowth')
                }
        except Exception as e:
            continue

    return earnings_data


def fetch_52week_data(ticker_data):
    """Calculate 52-week high/low positions for each ticker."""
    for ticker, data in ticker_data.items():
        try:
            hist = data.get('hist')
            if hist is None or len(hist) < 20:
                continue

            # Get 52-week high/low from available data
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            current = data['current_price']

            # Calculate position in range (0-100%)
            range_52w = high_52w - low_52w
            position = ((current - low_52w) / range_52w * 100) if range_52w > 0 else 50

            # Distance from high/low
            pct_from_high = ((current - high_52w) / high_52w * 100)
            pct_from_low = ((current - low_52w) / low_52w * 100)

            data['high_52w'] = high_52w
            data['low_52w'] = low_52w
            data['position_52w'] = round(position, 1)
            data['pct_from_high'] = round(pct_from_high, 1)
            data['pct_from_low'] = round(pct_from_low, 1)

            # Flag if near high or low
            data['near_52w_high'] = position > 90
            data['near_52w_low'] = position < 10

        except Exception as e:
            continue

    return ticker_data

if __name__ == '__main__':
    tickers = ['AAPL', 'MSFT', 'AMZN']
    ticker_data = fetch_ticker_data(tickers, '2026-01-21')
    macro_data = fetch_macro_data('2026-01-21')
    print(ticker_data)
    print(macro_data)
