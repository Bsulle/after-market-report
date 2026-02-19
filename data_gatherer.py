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
        '^GSPC': 'S&P 500',  # Actual index, not SPY ETF
        '^IXIC': 'Nasdaq',   # Actual index, not QQQ ETF
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
    """
    Fetch market breadth using SPY component ETFs and broad market data.
    Uses sector ETFs to approximate advance/decline breadth.
    """
    breadth_tickers = ['SPY', 'QQQ', 'IWM', 'DIA',
                       'XLF', 'XLK', 'XLV', 'XLE', 'XLY',
                       'XLP', 'XLC', 'XLI', 'XLB', 'XLU', 'XLRE']

    advancers = 0
    decliners = 0
    unchanged = 0

    for ticker in breadth_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            if len(hist) >= 2:
                pct = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                if pct > 0.05:
                    advancers += 1
                elif pct < -0.05:
                    decliners += 1
                else:
                    unchanged += 1
        except:
            continue

    total = advancers + decliners + unchanged
    ad_ratio = advancers / decliners if decliners > 0 else advancers

    breadth_data = {
        'advancers': advancers,
        'decliners': decliners,
        'unchanged': unchanged,
        'total_measured': total,
        'ad_ratio': round(ad_ratio, 2),
        'pct_advancing': round(advancers / total * 100, 1) if total > 0 else 50.0,
    }

    print(f"Breadth: {advancers} advancing, {decliners} declining (A/D={ad_ratio:.2f})")
    return breadth_data


def fetch_options_data(tickers):
    """
    Fetch options flow data using yfinance with manual chain reconstruction.
    Scans first 4 expirations (~60 days) and sums volume/OI across all strikes
    to get accurate P/C ratios. Fixes undercounting bugs (NVO, AUR).
    """
    options_data = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            expirations = stock.options
            if not expirations:
                continue

            # Get current price for ATM IV filtering
            hist = stock.history(period='5d')
            price = hist['Close'].iloc[-1] if not hist.empty else 0

            # --- MANUAL CHAIN RECONSTRUCTION ---
            # Sum across first 4 expirations instead of just the nearest
            total_call_volume = 0
            total_put_volume = 0
            total_call_oi = 0
            total_put_oi = 0
            call_iv_data = []
            put_iv_data = []
            all_top_calls = []
            all_top_puts = []

            for exp in expirations[:4]:
                try:
                    opt_chain = stock.option_chain(exp)
                    calls = opt_chain.calls
                    puts = opt_chain.puts

                    if calls.empty and puts.empty:
                        continue

                    # Sum ALL volume and OI (fillna to avoid NaN issues)
                    total_call_volume += calls['volume'].fillna(0).sum()
                    total_put_volume += puts['volume'].fillna(0).sum()
                    total_call_oi += calls['openInterest'].fillna(0).sum()
                    total_put_oi += puts['openInterest'].fillna(0).sum()

                    # Collect ATM IV separately for calls and puts (within 5% of current price)
                    if price > 0:
                        atm_calls = calls[(calls['strike'] > price * 0.95) & (calls['strike'] < price * 1.05)]
                        atm_puts = puts[(puts['strike'] > price * 0.95) & (puts['strike'] < price * 1.05)]
                        call_iv_data.extend(atm_calls['impliedVolatility'].dropna().tolist())
                        put_iv_data.extend(atm_puts['impliedVolatility'].dropna().tolist())

                    # Collect top strikes by volume for this expiration
                    if not calls.empty:
                        top_c = calls.nlargest(3, 'volume')[['strike', 'volume', 'openInterest', 'impliedVolatility']]
                        all_top_calls.append(top_c)
                    if not puts.empty:
                        top_p = puts.nlargest(3, 'volume')[['strike', 'volume', 'openInterest', 'impliedVolatility']]
                        all_top_puts.append(top_p)

                except Exception:
                    continue

            if total_call_volume == 0 and total_put_volume == 0:
                continue

            # Calculate ratios from aggregated data
            pc_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 0
            pc_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0

            # Use median ATM IV separately for calls and puts (put skew is real)
            avg_call_iv = np.median(call_iv_data) * 100 if call_iv_data else 0
            avg_put_iv = np.median(put_iv_data) * 100 if put_iv_data else avg_call_iv

            # Merge and sort top strikes across all expirations
            top_call_strikes = pd.concat(all_top_calls).nlargest(3, 'volume') if all_top_calls else pd.DataFrame()
            top_put_strikes = pd.concat(all_top_puts).nlargest(3, 'volume') if all_top_puts else pd.DataFrame()

            # Confidence flag
            confidence = "HIGH" if total_call_volume > 100 else "LOW"

            options_data[ticker] = {
                'nearest_expiry': expirations[0],
                'expirations_scanned': min(len(expirations), 4),
                'total_call_volume': int(total_call_volume),
                'total_put_volume': int(total_put_volume),
                'total_call_oi': int(total_call_oi),
                'total_put_oi': int(total_put_oi),
                'put_call_ratio': round(pc_ratio, 2) if not pd.isna(pc_ratio) else 0,
                'put_call_oi_ratio': round(pc_oi_ratio, 2) if not pd.isna(pc_oi_ratio) else 0,
                'avg_call_iv': round(avg_call_iv, 1) if not pd.isna(avg_call_iv) else 0,
                'avg_put_iv': round(avg_put_iv, 1) if not pd.isna(avg_put_iv) else 0,
                'top_call_strikes': top_call_strikes.to_dict('records') if not top_call_strikes.empty else [],
                'top_put_strikes': top_put_strikes.to_dict('records') if not top_put_strikes.empty else [],
                'sentiment': 'BULLISH' if pc_ratio < 0.7 else ('BEARISH' if pc_ratio > 1.3 else 'NEUTRAL'),
                'confidence': confidence
            }

            print(f"Fetched options for {ticker}: P/C={pc_ratio:.2f} ({options_data[ticker]['sentiment']}) [4-exp scan, {confidence}]")

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


def fetch_news_data(tickers):
    """Fetch recent news for watchlist tickers using yfinance."""
    news_data = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            news = stock.news

            if news:
                # Get top 3 recent news items
                ticker_news = []
                for item in news[:3]:
                    ticker_news.append({
                        'title': item.get('title', ''),
                        'publisher': item.get('publisher', ''),
                        'link': item.get('link', ''),
                        'timestamp': item.get('providerPublishTime', 0),
                        'type': item.get('type', 'STORY')
                    })

                if ticker_news:
                    news_data[ticker] = ticker_news
                    print(f"Fetched {len(ticker_news)} news items for {ticker}")

        except Exception as e:
            continue

    return news_data


# Sector mappings for context
SECTOR_MAP = {
    'ASTS': {'sector': 'Space/Satellite', 'industry': 'Telecommunications'},
    'GRAB': {'sector': 'Technology', 'industry': 'Ride-Hailing/Super App'},
    'MP': {'sector': 'Materials', 'industry': 'Rare Earth Mining'},
    'ZETA': {'sector': 'Technology', 'industry': 'Marketing Technology'},
    'JD': {'sector': 'Consumer Discretionary', 'industry': 'E-Commerce (China)'},
    'SLDP': {'sector': 'Materials', 'industry': 'Battery Technology'},
    'ACHR': {'sector': 'Industrials', 'industry': 'eVTOL/Urban Air Mobility'},
    'NVO': {'sector': 'Healthcare', 'industry': 'Pharmaceuticals (Obesity/Diabetes)'},
    'CRML': {'sector': 'Healthcare', 'industry': 'Biotech/Rare Disease'},
    'MCRP': {'sector': 'Healthcare', 'industry': 'Medical Devices'},
    'DLO': {'sector': 'Technology', 'industry': 'Fintech/Payments (LatAm)'},
    'IREN': {'sector': 'Technology', 'industry': 'Bitcoin Mining/Data Centers'},
    'OSCR': {'sector': 'Healthcare', 'industry': 'Health Insurance Tech'},
    'TEM': {'sector': 'Healthcare', 'industry': 'AI Healthcare/Precision Medicine'},
    'AUR': {'sector': 'Technology', 'industry': 'Autonomous Vehicles'},
    'HIMS': {'sector': 'Healthcare', 'industry': 'Telehealth/DTC Healthcare'},
    'JOBY': {'sector': 'Industrials', 'industry': 'eVTOL/Urban Air Mobility'},
    'NBIS': {'sector': 'Technology', 'industry': 'AI Infrastructure/Cloud'},
    'PATH': {'sector': 'Technology', 'industry': 'AI/Robotic Process Automation'},
    'OKLO': {'sector': 'Energy', 'industry': 'Nuclear/Advanced Fission'},
}


def get_sector_info(ticker):
    """Get sector and industry info for a ticker."""
    return SECTOR_MAP.get(ticker, {'sector': 'Unknown', 'industry': 'Unknown'})


if __name__ == '__main__':
    tickers = ['AAPL', 'MSFT', 'AMZN']
    ticker_data = fetch_ticker_data(tickers, '2026-01-21')
    macro_data = fetch_macro_data('2026-01-21')
    print(ticker_data)
    print(macro_data)
