#!/usr/bin/env python3
"""
Institutional-Grade Quant Engine for Options Flow Analysis
Fixes yfinance data bugs (NVO/AUR undercounting) via manual chain reconstruction.
Includes: Skew Analysis, Gamma Walls, Swing Trade Scoring, Earnings IV Crush Detection.
Usage:
    python quant_engine_pro.py                    # Uses config.py watchlist
    python quant_engine_pro.py --tickers AAPL TSLA NVO
"""
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import argparse
import os

# --- CREDENTIALS ---
POLYGON_API_KEY = "wm2_rIkTQVxi_xAYrv307R24TvF2Fz7R"


class InstitutionalQuantEngine:
    def __init__(self, tickers, earnings_calendar=None):
        self.tickers = tickers
        self.polygon_key = POLYGON_API_KEY
        self.earnings_calendar = earnings_calendar or {}
        self.spy_bench = self._get_spy_benchmark()

    def _get_spy_benchmark(self):
        """Standardizes performance against the S&P 500 (63-day RS)."""
        print("Benchmarking against SPY...")
        try:
            spy = yf.Ticker("SPY")
            h = spy.history(period="6mo")
            if len(h) >= 63:
                return (h['Close'].iloc[-1] / h['Close'].iloc[-63]) - 1
        except Exception as e:
            print(f"  Warning: SPY benchmark failed: {e}")
        return 0.0

    def _get_polygon_contract_count(self, ticker):
        """Cross-references with Polygon to validate yfinance data completeness."""
        url = "https://api.polygon.io/v3/reference/options/contracts"
        params = {
            "underlying_ticker": ticker,
            "expired": "false",
            "limit": 1000,
            "apiKey": self.polygon_key
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return len(r.json().get('results', []))
        except:
            pass
        return 0

    def _check_earnings_proximity(self, ticker):
        """
        Check if ticker has earnings within 7 days.
        Returns (is_near_earnings, days_until, date_str)
        """
        if ticker in self.earnings_calendar:
            earnings_date = self.earnings_calendar[ticker]
            if isinstance(earnings_date, str):
                earnings_date = datetime.strptime(earnings_date, '%Y-%m-%d')
            days_until = (earnings_date - datetime.now()).days
            if 0 <= days_until <= 7:
                return True, days_until, earnings_date.strftime('%Y-%m-%d')

        # Try to fetch from yfinance if not in calendar
        try:
            t = yf.Ticker(ticker)
            cal = t.calendar
            if cal is not None and not cal.empty:
                if 'Earnings Date' in cal.index:
                    earnings_date = cal.loc['Earnings Date'].iloc[0]
                    if pd.notna(earnings_date):
                        days_until = (earnings_date - datetime.now()).days
                        if 0 <= days_until <= 7:
                            return True, days_until, earnings_date.strftime('%Y-%m-%d')
        except:
            pass

        return False, None, None

    def _calculate_skew(self, calls, puts, price):
        """
        Skew Analysis: OTM Put IV / OTM Call IV
        > 1.4 = Heavy hedging (institutions buying puts)
        < 0.7 = Complacency (no fear)
        """
        otm_calls = calls[calls['strike'] > price * 1.05]
        otm_puts = puts[puts['strike'] < price * 0.95]

        if not otm_calls.empty and not otm_puts.empty:
            call_iv = otm_calls['impliedVolatility'].mean()
            put_iv = otm_puts['impliedVolatility'].mean()
            if call_iv > 0:
                return round(put_iv / call_iv, 2)
        return 1.0

    def _calculate_swing_score(self, metrics):
        """
        SWING TRADE SCORE (0-10) - Graduated scoring

        Factors (graduated, not binary):
        - Trend (Price vs 50SMA): 0-2 pts
        - Daily Price Action: 0-2 pts
        - RS Score (vs SPY): 0-2 pts
        - Options Flow (P/C ratio): 0-2 pts
        - Volume + IV context: 0-2 pts

        Penalties:
        - Near earnings (IV crush risk): -1 to -2
        - Heavy hedging (Skew > 1.4): -1
        """
        score = 0.0

        # --- TREND (0-2 pts) ---
        price = metrics.get('price', 0)
        sma50 = metrics.get('sma50', 0)
        if sma50 > 0 and price > 0:
            pct_from_sma = ((price - sma50) / sma50) * 100
            if pct_from_sma > 5:
                score += 2.0   # Well above 50 SMA
            elif pct_from_sma > 0:
                score += 1.5   # Above 50 SMA
            elif pct_from_sma > -5:
                score += 0.5   # Slightly below (not terrible)
            # > 5% below = 0 pts

        # --- DAILY PRICE ACTION (0-2 pts) ---
        pct_change = metrics.get('pct_change', 0)
        if pct_change > 5:
            score += 2.0   # Strong rally
        elif pct_change > 3:
            score += 1.5   # Solid green day
        elif pct_change > 1:
            score += 1.0   # Decent green
        elif pct_change > 0:
            score += 0.5   # Slightly green
        elif pct_change > -2:
            score += 0.0   # Mild red, neutral
        else:
            score -= 0.5   # Significant selling

        # --- RELATIVE STRENGTH vs SPY (0-2 pts) ---
        rs_raw = metrics.get('rs_raw', 0)
        # Also consider short-term RS (5-day) if available
        rs_5d = metrics.get('rs_5d', None)
        if rs_5d is not None:
            # Blend 63-day and 5-day RS
            if rs_5d > 0.05:
                score += 1.0  # Short-term outperformance
            elif rs_5d > 0:
                score += 0.5
        if rs_raw > 0.10:
            score += 1.0  # Strong long-term outperformance
        elif rs_raw > 0:
            score += 0.5  # Modest outperformance
        elif rs_raw > -0.10:
            score += 0.0  # Mild underperformance, neutral
        # Heavy underperformance = 0

        # --- OPTIONS FLOW (0-2 pts) ---
        pc_ratio = metrics.get('pc_ratio', 1.0)
        if pc_ratio < 0.4:
            score += 2.0   # Very bullish flow
        elif pc_ratio < 0.7:
            score += 1.5   # Bullish flow
        elif pc_ratio < 1.0:
            score += 0.5   # Slightly call-heavy
        elif pc_ratio < 1.3:
            score += 0.0   # Neutral
        else:
            score -= 0.5   # Bearish flow (penalty)

        # --- VOLUME + IV CONTEXT (0-2 pts) ---
        vol_surge = metrics.get('vol_surge', 1.0)
        avg_iv = metrics.get('avg_iv', 0.5)

        # Volume component (0-1 pt)
        if vol_surge > 2.0:
            score += 1.0   # Heavy volume
        elif vol_surge > 1.3:
            score += 0.5   # Above average
        # Low volume = 0 (not penalized)

        # IV component (0-1 pt) - adjusted for growth/small-cap reality
        if avg_iv < 0.40:
            score += 1.0   # Cheap vol
        elif avg_iv < 0.60:
            score += 0.5   # Moderate vol
        elif avg_iv < 0.80:
            score += 0.0   # Typical for growth names
        # Very high IV = 0 (not extra penalized unless near earnings)

        # --- PENALTIES ---
        if metrics.get('near_earnings', False):
            score -= 2.0   # IV crush risk

        skew = metrics.get('skew', 1.0)
        if skew > 1.6:
            score -= 1.0   # Very heavy hedging
        elif skew > 1.4:
            score -= 0.5   # Moderate hedging

        # Daily price action floor: a stock up big today should never be 0
        if pct_change > 5:
            score = max(score, 3)  # Up 5%+ = at least 3/10
        elif pct_change > 2:
            score = max(score, 2)  # Up 2%+ = at least 2/10
        elif pct_change > 0:
            score = max(score, 1)  # Green day = at least 1/10

        return max(0, min(10, round(score)))

    def analyze_ticker(self, ticker):
        """
        Full quant analysis for a single ticker.
        Uses manual chain reconstruction to fix yfinance undercounting.
        """
        try:
            print(f"  Analyzing {ticker}...")
            t = yf.Ticker(ticker)
            hist = t.history(period="1y")

            if hist.empty:
                return {"Ticker": ticker, "Error": "No price data"}

            price = hist['Close'].iloc[-1]
            sma50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else price

            # Daily % change
            pct_change = 0
            if len(hist) >= 2:
                pct_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100

            # Check earnings proximity
            near_earnings, days_to_earnings, earnings_date = self._check_earnings_proximity(ticker)

            # Get available expirations
            try:
                exps = t.options
            except:
                return {"Ticker": ticker, "Error": "No options available"}

            if not exps:
                return {"Ticker": ticker, "Error": "No options expirations"}

            # --- MANUAL CHAIN RECONSTRUCTION ---
            # This fixes the NVO/AUR bugs by summing across all strikes
            total_call_vol = 0
            total_put_vol = 0
            total_call_oi = 0
            total_put_oi = 0
            iv_data = []
            gamma_wall_strike = 0
            max_oi = 0
            contracts_found = 0
            skew = 1.0

            # Scan first 4 expirations (roughly 60 days out)
            for i, exp in enumerate(exps[:4]):
                try:
                    chain = t.option_chain(exp)
                    calls = chain.calls
                    puts = chain.puts

                    # Sum ALL volume and OI (the fix)
                    c_vol = calls['volume'].fillna(0).sum()
                    p_vol = puts['volume'].fillna(0).sum()
                    c_oi = calls['openInterest'].fillna(0).sum()
                    p_oi = puts['openInterest'].fillna(0).sum()

                    total_call_vol += c_vol
                    total_put_vol += p_vol
                    total_call_oi += c_oi
                    total_put_oi += p_oi
                    contracts_found += len(calls) + len(puts)

                    # Find Gamma Wall (strike with max call OI)
                    if not calls.empty and calls['openInterest'].max() > max_oi:
                        max_oi = calls['openInterest'].max()
                        gamma_wall_strike = calls.loc[calls['openInterest'].idxmax(), 'strike']

                    # Collect ATM IV for expected move calculation
                    atm_calls = calls[(calls['strike'] > price * 0.95) & (calls['strike'] < price * 1.05)]
                    iv_data.extend(atm_calls['impliedVolatility'].dropna().tolist())

                    # Calculate skew from nearest expiration
                    if i == 0:
                        skew = self._calculate_skew(calls, puts, price)

                except Exception as e:
                    continue

            # --- CALCULATED METRICS ---
            pc_ratio = round(total_put_vol / total_call_vol, 2) if total_call_vol > 0 else 0
            avg_iv = np.median(iv_data) if iv_data else 0
            expected_move_7d = round(price * avg_iv * np.sqrt(7/365), 2) if avg_iv > 0 else 0

            # RS vs SPY (63-day relative strength)
            rs_raw = 0
            if len(hist) >= 63:
                ticker_return = (price / hist['Close'].iloc[-63]) - 1
                rs_raw = ticker_return - self.spy_bench

            # 5-day RS vs SPY (short-term momentum)
            rs_5d = None
            if len(hist) >= 6:
                ticker_5d = (price / hist['Close'].iloc[-6]) - 1
                try:
                    spy = yf.Ticker("SPY")
                    spy_h = spy.history(period="10d")
                    if len(spy_h) >= 6:
                        spy_5d = (spy_h['Close'].iloc[-1] / spy_h['Close'].iloc[-6]) - 1
                        rs_5d = ticker_5d - spy_5d
                except:
                    rs_5d = None

            # Volume surge
            vol_surge = round(hist['Volume'].iloc[-1] / hist['Volume'].tail(20).mean(), 2) if len(hist) >= 20 else 1.0

            # Polygon validation
            poly_count = self._get_polygon_contract_count(ticker)
            if poly_count > 0:
                confidence = "HIGH" if contracts_found >= (poly_count * 0.7) else "MEDIUM"
            else:
                confidence = "HIGH" if total_call_vol > 100 else "LOW (Illiquid)"

            # Build metrics dict for scoring
            metrics = {
                'price': price,
                'sma50': sma50,
                'pct_change': pct_change,
                'pc_ratio': pc_ratio,
                'avg_iv': avg_iv,
                'rs_raw': rs_raw,
                'rs_5d': rs_5d,
                'vol_surge': vol_surge,
                'skew': skew,
                'near_earnings': near_earnings
            }

            score = self._calculate_swing_score(metrics)

            # Signal determination
            if score >= 8:
                signal = "STRONG BUY"
            elif score >= 6:
                signal = "ACCUMULATION"
            elif score >= 4:
                signal = "NEUTRAL"
            elif score >= 2:
                signal = "CAUTION"
            else:
                signal = "DISTRIBUTION"

            # Add earnings warning to signal
            if near_earnings:
                signal += f" [EARNINGS {days_to_earnings}d]"

            return {
                "Ticker": ticker,
                "Score": score,
                "Signal": signal,
                "Price": round(price, 2),
                "P/C Ratio": pc_ratio,
                "Skew": skew,
                "Exp Move 7D": expected_move_7d,
                "Gamma Wall": gamma_wall_strike,
                "RS vs SPY": f"{rs_raw:+.1%}",
                "Vol Surge": f"{vol_surge:.1f}x",
                "Call Vol": f"{int(total_call_vol):,}",
                "Put Vol": f"{int(total_put_vol):,}",
                "Avg IV": f"{avg_iv*100:.0f}%" if avg_iv > 0 else "N/A",
                "Confidence": confidence,
                "Near Earnings": "YES" if near_earnings else "No"
            }

        except Exception as e:
            return {"Ticker": ticker, "Error": str(e)}

    def analyze_all(self):
        """Analyze all tickers in parallel."""
        print(f"\nAnalyzing {len(self.tickers)} tickers...")
        print("-" * 50)

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.analyze_ticker, self.tickers))

        # Filter out errors and sort by score
        valid_results = [r for r in results if 'Score' in r]
        error_results = [r for r in results if 'Error' in r]

        if error_results:
            print(f"\nWarnings: {len(error_results)} tickers had issues")
            for e in error_results:
                print(f"  - {e['Ticker']}: {e.get('Error', 'Unknown')}")

        # Sort by score descending
        valid_results.sort(key=lambda x: x.get('Score', 0), reverse=True)

        return valid_results

    def generate_excel_report(self, filename="Quant_Options_Flow.xlsx"):
        """Generate professional Excel report with conditional formatting."""
        results = self.analyze_all()

        if not results:
            print("No valid results to report.")
            return None

        df = pd.DataFrame(results)

        # Try to use xlsxwriter for formatting
        try:
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Options Flow', index=False)

            workbook = writer.book
            worksheet = writer.sheets['Options Flow']

            # Formats
            header_fmt = workbook.add_format({
                'bold': True,
                'bg_color': '#1F4E78',
                'font_color': 'white',
                'border': 1,
                'align': 'center'
            })
            bull_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
            bear_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            warn_fmt = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700'})

            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
                worksheet.set_column(col_num, col_num, 12)

            # Conditional formatting for Score column (B)
            worksheet.conditional_format('B2:B100', {
                'type': 'cell', 'criteria': '>=', 'value': 8, 'format': bull_fmt
            })
            worksheet.conditional_format('B2:B100', {
                'type': 'cell', 'criteria': '<=', 'value': 3, 'format': bear_fmt
            })

            # Conditional formatting for Signal column (C)
            worksheet.conditional_format('C2:C100', {
                'type': 'text', 'criteria': 'containing', 'value': 'BUY', 'format': bull_fmt
            })
            worksheet.conditional_format('C2:C100', {
                'type': 'text', 'criteria': 'containing', 'value': 'DISTRIBUTION', 'format': bear_fmt
            })
            worksheet.conditional_format('C2:C100', {
                'type': 'text', 'criteria': 'containing', 'value': 'EARNINGS', 'format': warn_fmt
            })

            writer.close()
        except ImportError:
            # Fallback to basic Excel without formatting
            df.to_excel(filename, index=False)

        print(f"\nReport saved: {os.path.abspath(filename)}")
        return df

    def generate_markdown_section(self):
        """Generate markdown for inclusion in the main report."""
        results = self.analyze_all()

        if not results:
            return "## Options Flow Analysis\n\nNo options data available.\n"

        lines = [
            "## Options Flow Analysis (Quant Engine)",
            "",
            "| Ticker | Score | Signal | P/C | Skew | Exp Move | Gamma Wall | RS vs SPY |",
            "|--------|-------|--------|-----|------|----------|------------|-----------|"
        ]

        for r in results:
            lines.append(
                f"| {r['Ticker']} | {r['Score']}/10 | {r['Signal']} | "
                f"{r['P/C Ratio']} | {r['Skew']} | ${r['Exp Move 7D']} | "
                f"${r['Gamma Wall']} | {r['RS vs SPY']} |"
            )

        lines.extend([
            "",
            "**Score Interpretation:**",
            "- 8-10: Strong institutional accumulation",
            "- 6-7: Moderate bullish flow",
            "- 4-5: Neutral/mixed signals",
            "- 2-3: Distribution/selling pressure",
            "- 0-1: Strong bearish flow",
            "",
            "**Key Metrics:**",
            "- P/C < 0.7 = Bullish flow | P/C > 1.3 = Bearish flow",
            "- Skew > 1.4 = Heavy put hedging (caution)",
            "- Gamma Wall = Price magnet / resistance level",
            ""
        ])

        # Add earnings warnings
        earnings_tickers = [r for r in results if 'EARNINGS' in r.get('Signal', '')]
        if earnings_tickers:
            lines.append("**EARNINGS WARNING:** The following have earnings within 7 days (IV crush risk):")
            for r in earnings_tickers:
                lines.append(f"- {r['Ticker']}: {r['Signal']}")
            lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Institutional Quant Options Engine')
    parser.add_argument('--tickers', nargs='+', help='Tickers to analyze')
    parser.add_argument('--output', default='Quant_Options_Flow.xlsx', help='Output filename')
    parser.add_argument('--markdown', action='store_true', help='Output markdown instead of Excel')
    args = parser.parse_args()

    # Get tickers from args or config
    if args.tickers:
        tickers = args.tickers
        print(f"Using custom tickers: {len(tickers)} tickers")
    else:
        # Default to thesis watchlist (your core positions)
        from thesis_config import thesis_watchlist
        tickers = thesis_watchlist
        print(f"Using THESIS watchlist: {len(tickers)} tickers")
        print(f"Tickers: {', '.join(tickers)}")

    engine = InstitutionalQuantEngine(tickers)

    if args.markdown:
        print(engine.generate_markdown_section())
    else:
        engine.generate_excel_report(args.output)

if __name__ == "__main__":
    main()
