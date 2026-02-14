# report_builder.py

from datetime import datetime
import pandas as pd

class ReportBuilder:
    def __init__(self, date_str):
        self.date_str = date_str
        self.sections = []

    def _create_range_bar(self, position_pct):
        """Create a visual range bar showing position in 52-week range."""
        bar_length = 10
        filled = int(position_pct / 100 * bar_length)
        filled = max(0, min(bar_length, filled))  # Clamp to valid range
        bar = '[' + '=' * filled + '|' + '-' * (bar_length - filled) + ']'
        return bar

    def build_report(self, ticker_data, macro_data, metrics, regime_score, regime_label, correlation_matrix, regime_components=None, options_data=None, earnings_data=None, news_data=None, prev_data=None):
        """Build the complete markdown report."""
        # Store data for use in ticker cards
        self.options_data = options_data or {}
        self.news_data = news_data or {}
        self.regime_label = regime_label
        self.regime_score = regime_score

        self.add_header()
        self.add_summary_stats(ticker_data, macro_data, regime_label, regime_score)
        self.add_what_changed_today(ticker_data, macro_data, prev_data)  # NEW: Delta analysis
        self.add_executive_dashboard(regime_label, regime_score, macro_data)
        self.add_market_regime_coach_call(regime_label, regime_score, macro_data, regime_components)
        self.add_macro_panel(macro_data)
        self.add_market_tape(ticker_data)
        self.add_conviction_dashboard(ticker_data, metrics)
        self.add_technical_signals(ticker_data, metrics)  # NEW: Technical signals
        self.add_correlation_clusters(correlation_matrix)
        self.add_position_sizing(regime_score)
        self.add_theme_rotation(ticker_data, metrics)
        self.add_leadership_map(ticker_data, metrics)
        self.add_liquidity_flags(ticker_data)
        self.add_options_flow(ticker_data, options_data)  # NEW: Options flow
        self.add_earnings_calendar(earnings_data)  # NEW: Earnings calendar
        self.add_ticker_cards(ticker_data, metrics)
        self.add_portfolio_risk_metrics(ticker_data, metrics)
        self.add_game_plan(regime_label)
        self.add_falsification_checklist(regime_label)
        self.add_risi_wrap(regime_label, macro_data)
        self.add_high_conviction_watch_list(ticker_data, metrics)
        self.add_performance_tracker()
        self.add_coach_directive(regime_label)

        return '\n\n'.join(self.sections)

    def add_header(self):
        """Add report header."""
        header = f"""# After-Market Report - {self.date_str}
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---"""
        self.sections.append(header)

    def add_summary_stats(self, ticker_data, macro_data, regime_label, regime_score):
        """Add quick summary stats box at the top."""
        # Calculate watchlist performance
        pct_changes = [data.get('pct_change', 0) for data in ticker_data.values()]
        avg_return = sum(pct_changes) / len(pct_changes) if pct_changes else 0
        green_count = sum(1 for pc in pct_changes if pc > 0)
        green_pct = (green_count / len(pct_changes) * 100) if pct_changes else 0

        # Get market performance
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)
        alpha = avg_return - spy_change

        # Best and worst performers
        sorted_by_perf = sorted(ticker_data.items(), key=lambda x: x[1].get('pct_change', 0), reverse=True)
        best = sorted_by_perf[0] if sorted_by_perf else ('N/A', {})
        worst = sorted_by_perf[-1] if sorted_by_perf else ('N/A', {})

        section = f"""## Summary Stats

```
┌─────────────────────────────────────────────────────────┐
│ WATCHLIST PERFORMANCE                                    │
├─────────────────────────────────────────────────────────┤
│ Avg Return:  {avg_return:+.2f}%  │  Market (SPY): {spy_change:+.2f}%   │
│ Alpha:       {alpha:+.2f}%  │  Regime: {regime_label} ({regime_score:.1f}/5.0) │
│ Green/Red:   {green_count}/{len(pct_changes)} ({green_pct:.0f}%/{100-green_pct:.0f}%)                          │
├─────────────────────────────────────────────────────────┤
│ Best:  {best[0]:6} {best[1].get('pct_change', 0):+.2f}%                             │
│ Worst: {worst[0]:6} {worst[1].get('pct_change', 0):+.2f}%                             │
└─────────────────────────────────────────────────────────┘
```"""
        self.sections.append(section)

    def add_what_changed_today(self, ticker_data, macro_data, prev_data=None):
        """Add delta analysis - what changed vs yesterday."""
        section = """## What Changed Today

**Market Delta (vs Previous Session):**"""

        # Macro changes
        vix_change = macro_data.get('VIX', {}).get('pct_change', 0)
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)
        dxy_change = macro_data.get('DXY', {}).get('pct_change', 0)
        gold_change = macro_data.get('Gold', {}).get('pct_change', 0)

        section += f"""
- **VIX:** {macro_data.get('VIX', {}).get('price', 'N/A')} ({vix_change:+.2f}%) - {'Fear subsiding' if vix_change < 0 else 'Fear rising'}
- **Gold:** ${macro_data.get('Gold', {}).get('price', 0):.2f} ({gold_change:+.2f}%) - {'Safe haven bid' if gold_change > 0 else 'Risk-on rotation'}
- **DXY:** {macro_data.get('DXY', {}).get('price', 0):.2f} ({dxy_change:+.2f}%) - {'Dollar strength' if dxy_change > 0 else 'Dollar weakness'}

**Your Watchlist Major Shifts:**"""

        # Find biggest movers and reversals
        sorted_by_change = sorted(ticker_data.items(), key=lambda x: abs(x[1].get('pct_change', 0)), reverse=True)

        section += "\n- **Biggest Mover:** "
        if sorted_by_change:
            top_mover = sorted_by_change[0]
            section += f"{top_mover[0]} ({top_mover[1].get('pct_change', 0):+.2f}%)"
            if abs(top_mover[1].get('pct_change', 0)) > 5:
                section += " - Significant momentum"

        section += "\n- **Market Breadth:** "
        green_pct = sum(1 for t in ticker_data.values() if t.get('pct_change', 0) > 0) / len(ticker_data) * 100
        section += f"{green_pct:.0f}% green ({'Improving' if green_pct > 50 else 'Deteriorating'})"

        # Show conviction/price changes if previous data is available
        if prev_data:
            section += "\n\n**Changes Since Last Report:**"
            upgrades = []
            downgrades = []
            for ticker, tdata in ticker_data.items():
                if ticker in prev_data:
                    prev_price = prev_data[ticker].get('price', 0)
                    curr_price = tdata.get('current_price', 0)
                    if prev_price > 0 and curr_price > 0:
                        delta = ((curr_price - prev_price) / prev_price) * 100
                        prev_signal = prev_data[ticker].get('signal', '')
                        if delta > 2:
                            upgrades.append((ticker, delta, prev_signal))
                        elif delta < -2:
                            downgrades.append((ticker, delta, prev_signal))

            if upgrades:
                upgrades.sort(key=lambda x: x[1], reverse=True)
                for t, d, s in upgrades[:3]:
                    section += f"\n- **{t}:** {d:+.1f}% since last report (was {s})"
            if downgrades:
                downgrades.sort(key=lambda x: x[1])
                for t, d, s in downgrades[:3]:
                    section += f"\n- **{t}:** {d:+.1f}% since last report (was {s})"
            if not upgrades and not downgrades:
                section += "\n- No major moves (>2%) since last report"

        section += "\n\n**Key Takeaway:** "
        if vix_change < -2 and spy_change > 0.5:
            section += "Risk-on environment strengthening - low vol + market strength"
        elif vix_change > 2 and spy_change < -0.5:
            section += "Risk-off pressures building - rising fear + market weakness"
        elif abs(gold_change) > 1:
            section += f"Gold making moves ({gold_change:+.2f}%) - watch for macro shifts"
        else:
            section += "Mixed signals - maintain selective positioning"

        self.sections.append(section)

    def add_executive_dashboard(self, regime_label, regime_score, macro_data):
        """Add executive dashboard section."""
        vix = macro_data.get('VIX', {}).get('price', 'N/A')
        yield_10y = macro_data.get('10Y Yield', {}).get('price', 'N/A')

        section = f"""## 1. Executive Dashboard

**Market Regime:** {regime_label}
**Regime Score:** {regime_score:.1f}/5.0

**Trip Wires:**
- VIX: {vix if vix == 'N/A' else f'{vix:.2f}'}
- 10Y Yield: {yield_10y if yield_10y == 'N/A' else f'{yield_10y:.2f}%'}

**Top 3 Actionable Insights:**
1. Market regime is {regime_label.lower()} - adjust position sizing accordingly
2. Monitor VIX levels for volatility regime shifts
3. Focus on high-conviction setups in current environment"""
        self.sections.append(section)

    def add_market_regime_coach_call(self, regime_label, regime_score, macro_data, regime_components=None):
        """Add market regime analysis with detailed breakdown."""
        vix = macro_data.get('VIX', {}).get('price', 20)
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)

        if regime_label == "RISK-ON":
            assessment = "Market showing strong risk appetite with low volatility and positive breadth."
        elif regime_label == "TRANSITIONAL":
            assessment = "Market in transition - mixed signals require selective positioning."
        else:
            assessment = "Risk-off environment - defensive positioning recommended."

        section = f"""## 2. Market Regime Coach Call

**Volatility Assessment:** VIX at {vix:.2f} - {'Low' if vix < 15 else 'Moderate' if vix < 20 else 'Elevated'}
**Market Breadth:** SPY {'+' if spy_change > 0 else ''}{spy_change:.2f}%

**Coach Interpretation:** {assessment} Current regime score of {regime_score:.1f}/5.0 suggests {'aggressive' if regime_score >= 4 else 'moderate' if regime_score >= 3 else 'defensive'} positioning."""

        # Add regime score breakdown if available
        if regime_components:
            section += "\n\n**Regime Score Breakdown:**\n\n| Component | Value | Score Contribution |\n|-----------|-------|-------------------|\n"
            for comp_name, comp_data in regime_components.items():
                value = comp_data.get('value', 'N/A')
                score = comp_data.get('score', 0)
                if isinstance(value, float):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)
                section += f"| {comp_name} | {value_str} | {score:+.2f} |\n"
            section += f"\n**Base Score:** 3.0 (Neutral)\n**Final Score:** {regime_score:.2f}/5.0"

        self.sections.append(section)

    def add_macro_panel(self, macro_data):
        """Add macro indicators panel."""
        section = """## 3. Macro Panel

| Asset | Price | Change |
|-------|-------|--------|"""

        for name, data in macro_data.items():
            price = data.get('price', 'N/A')
            pct_change = data.get('pct_change', 0)
            price_str = f"${price:.2f}" if isinstance(price, (int, float)) else price
            change_str = f"{'+' if pct_change > 0 else ''}{pct_change:.2f}%"
            section += f"\n| {name} | {price_str} | {change_str} |"

        self.sections.append(section)

    def add_market_tape(self, ticker_data):
        """Add market tape analysis."""
        green_count = sum(1 for t in ticker_data.values() if t.get('pct_change', 0) > 0)
        red_count = len(ticker_data) - green_count
        above_ma_50 = sum(1 for t in ticker_data.values() if t.get('above_ma_50', False))

        section = f"""## 4. Market Tape (Your Universe)

**Breadth Analysis:**
- Green: {green_count} tickers ({green_count/len(ticker_data)*100:.0f}%)
- Red: {red_count} tickers ({red_count/len(ticker_data)*100:.0f}%)
- Above 50-day MA: {above_ma_50}/{len(ticker_data)}

**Risk Appetite:** {'Strong' if green_count > len(ticker_data)*0.6 else 'Moderate' if green_count > len(ticker_data)*0.4 else 'Weak'}"""
        self.sections.append(section)

    def add_conviction_dashboard(self, ticker_data, metrics):
        """Add conviction dashboard with detailed breakdown for top tickers."""
        section = """## 5. Conviction Dashboard

**Conviction Scale:** 🔥 4.5-5.0 | ✅ 3.5-4.4 | ⚠️ 2.5-3.4 | 🚫 <2.5
**RSI:** 🔴 >70 Overbought | 🟢 <30 Oversold | ⚪ 30-70 Neutral

| Ticker | Price | Change | RSI | MACD | Rel Vol | Conv | Signal |
|--------|-------|--------|-----|------|---------|------|--------|"""

        # Sort by conviction
        sorted_tickers = sorted(
            ticker_data.items(),
            key=lambda x: metrics.get(x[0], {}).get('conviction', 0),
            reverse=True
        )

        for ticker, data in sorted_tickers:
            price = data.get('close', 0)
            pct_change = data.get('pct_change', 0)
            conviction = metrics.get(ticker, {}).get('conviction', 0)
            rel_vol = metrics.get(ticker, {}).get('relative_volume', 1.0)
            rsi = metrics.get(ticker, {}).get('rsi')
            macd = metrics.get(ticker, {}).get('macd', {})
            macd_hist = macd.get('histogram', 0) if macd else 0

            # Conviction icon
            if conviction >= 4.5:
                conv_icon = "🔥"
            elif conviction >= 3.5:
                conv_icon = "✅"
            elif conviction >= 2.5:
                conv_icon = "⚠️"
            else:
                conv_icon = "🚫"

            # RSI signal with color
            if rsi is not None:
                if rsi > 70:
                    rsi_str = f"🔴{rsi:.0f}"
                elif rsi < 30:
                    rsi_str = f"🟢{rsi:.0f}"
                else:
                    rsi_str = f"{rsi:.0f}"
            else:
                rsi_str = "-"

            # MACD signal with trend
            if macd_hist != 0:
                macd_str = f"{'📈' if macd_hist > 0 else '📉'}"
            else:
                macd_str = "-"

            # Quick signal based on technicals
            above_ma = data.get('above_ma_50', False)
            if above_ma and (rsi is None or rsi < 70) and macd_hist > 0:
                signal = "🟢 BUY"
            elif not above_ma and (rsi is None or rsi > 30) and macd_hist < 0:
                signal = "🔴 SELL"
            else:
                signal = "⚪ HOLD"

            section += f"\n| {ticker} | ${price:.2f} | {'+' if pct_change > 0 else ''}{pct_change:.2f}% | {rsi_str} | {macd_str} | {rel_vol:.2f}x | {conv_icon}{conviction:.1f} | {signal} |"

        # Add conviction breakdown for top 3 tickers
        section += "\n\n**Top 3 Conviction Score Breakdowns:**\n"
        for i, (ticker, data) in enumerate(sorted_tickers[:3], 1):
            metric = metrics.get(ticker, {})
            conviction_breakdown = metric.get('conviction_breakdown', {})

            if conviction_breakdown:
                section += f"\n**{i}. {ticker}** (Total: {metric.get('conviction', 0):.2f}/5.0)\n\n"
                section += "| Factor | Score | Weight | Contribution |\n"
                section += "|--------|-------|--------|-------------|\n"
                for factor_name, factor_data in conviction_breakdown.items():
                    score = factor_data.get('score', 0)
                    weight = factor_data.get('weight', 0)
                    contrib = factor_data.get('contribution', 0)
                    section += f"| {factor_name} | {score:.2f} | {weight*100:.0f}% | {contrib:.2f} |\n"

        self.sections.append(section)

    def add_technical_signals(self, ticker_data, metrics):
        """Add technical signal summary dashboard."""
        section = """## 6. Technical Signals Dashboard

**BUY Signals:**"""

        buy_signals = []
        sell_signals = []
        hold_signals = []

        for ticker, data in ticker_data.items():
            metric = metrics.get(ticker, {})
            rsi = metric.get('rsi')
            macd = metric.get('macd', {})
            pct_change = data.get('pct_change', 0)
            above_ma_50 = data.get('above_ma_50', False)
            momentum_5d = metric.get('momentum_5d', 0)

            signals = []

            # RSI signals
            if rsi is not None:
                if rsi < 30:
                    signals.append("RSI oversold")
                elif rsi > 70:
                    signals.append("RSI overbought")

            # MACD signals
            if macd.get('histogram') is not None:
                if macd['histogram'] > 0 and momentum_5d > 2:
                    signals.append("MACD bullish + momentum")
                elif macd['histogram'] < 0 and momentum_5d < -2:
                    signals.append("MACD bearish + breakdown")

            # MA breakout
            if above_ma_50 and pct_change > 3:
                signals.append("Above MA50 with volume")

            # Classify
            if any('oversold' in s or 'bullish' in s.lower() or 'volume' in s for s in signals):
                buy_signals.append(f"{ticker}: {', '.join(signals)}")
            elif any('overbought' in s or 'bearish' in s.lower() or 'breakdown' in s for s in signals):
                sell_signals.append(f"{ticker}: {', '.join(signals)}")
            elif signals:
                hold_signals.append(f"{ticker}: {', '.join(signals)}")

        # Display buy signals
        if buy_signals:
            for signal in buy_signals[:5]:  # Top 5
                section += f"\n- 🟢 {signal}"
        else:
            section += "\n- No strong buy signals detected"

        section += "\n\n**SELL/TRIM Signals:**"
        if sell_signals:
            for signal in sell_signals[:5]:  # Top 5
                section += f"\n- 🔴 {signal}"
        else:
            section += "\n- No strong sell signals detected"

        section += "\n\n**HOLD/WATCH:**"
        if hold_signals:
            for signal in hold_signals[:3]:  # Top 3
                section += f"\n- ⚪ {signal}"
        else:
            section += "\n- Most positions in neutral territory"

        self.sections.append(section)

    def add_correlation_clusters(self, correlation_matrix):
        """Add correlation clusters analysis with actual correlation matrix."""
        section = """## 7. Correlation Clusters

**30-Day Rolling Correlation Matrix** (Top correlations shown):\n"""

        if correlation_matrix is not None and not correlation_matrix.empty:
            # Get top correlated pairs
            correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    ticker1 = correlation_matrix.columns[i]
                    ticker2 = correlation_matrix.columns[j]
                    corr = correlation_matrix.iloc[i, j]
                    if not pd.isna(corr):
                        correlations.append({
                            'ticker1': ticker1,
                            'ticker2': ticker2,
                            'correlation': corr
                        })

            correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)

            # Show top 15 correlations
            section += "\n| Ticker 1 | Ticker 2 | Correlation | Strength |\n"
            section += "|----------|----------|-------------|----------|\n"
            for corr_data in correlations[:15]:
                corr = corr_data['correlation']
                if abs(corr) >= 0.7:
                    strength = "🔴 Very Strong"
                elif abs(corr) >= 0.5:
                    strength = "🟡 Strong"
                elif abs(corr) >= 0.3:
                    strength = "🟢 Moderate"
                else:
                    strength = "⚪ Weak"

                section += f"| {corr_data['ticker1']} | {corr_data['ticker2']} | {corr:+.3f} | {strength} |\n"
        else:
            section += "\n*Correlation matrix not available - insufficient data*\n"

        section += """
**Identified Cohorts:**
- eVTOL Cluster: ACHR, JOBY (aviation/mobility theme)
- High-Beta Tech: ASTS, ZETA, GRAB (growth/tech exposure)
- China/EM Risk: JD, GRAB (emerging markets exposure)
- Materials: MP, DLO (commodity-linked)
- Healthcare/Biotech: NVO, HIMS, CRML, MCRP (defensive growth)

**Divergence Plays:** Look for tickers decoupling from SPY correlation for independent alpha opportunities."""

        self.sections.append(section)

    def add_position_sizing(self, regime_score):
        """Add position sizing matrix."""
        if regime_score >= 4:
            high_conv = "3-5%"
            med_conv = "2-3%"
            low_conv = "1-2%"
            cash = "10-20%"
        elif regime_score >= 3:
            high_conv = "2-3%"
            med_conv = "1-2%"
            low_conv = "0.5-1%"
            cash = "20-30%"
        else:
            high_conv = "1-2%"
            med_conv = "0.5-1%"
            low_conv = "0.25-0.5%"
            cash = "30-40%"

        section = f"""## 8. Position Sizing Matrix

**Recommended Allocation by Conviction Level:**
- High Conviction (🔥 4.5-5.0): {high_conv} per position
- Medium Conviction (✅ 3.5-4.4): {med_conv} per position
- Low Conviction (⚠️ 2.5-3.4): {low_conv} per position

**Cash Reserve:** {cash} (based on regime score {regime_score:.1f}/5.0)"""
        self.sections.append(section)

    def add_theme_rotation(self, ticker_data, metrics):
        """Add theme rotation scorecard."""
        section = """## 9. Theme Rotation Scorecard

**Themes Gaining Momentum:** ↗️
- Space/Satellite: ASTS showing strength
- Healthcare Innovation: NVO, HIMS maintaining leadership

**Themes Consolidating:** →
- eVTOL: ACHR, JOBY in base-building mode
- China Tech: JD awaiting catalyst

**Themes Losing Momentum:** ↘️
- Monitor high-beta names for risk rotation"""
        self.sections.append(section)

    def add_leadership_map(self, ticker_data, metrics):
        """Add leadership map."""
        sorted_tickers = sorted(
            ticker_data.items(),
            key=lambda x: metrics.get(x[0], {}).get('conviction', 0),
            reverse=True
        )

        leaders = [t[0] for t in sorted_tickers[:5]]
        laggards = [t[0] for t in sorted_tickers[-5:]]

        section = f"""## 10. Leadership Map

**Leaders** (Momentum + Participation):
{', '.join(leaders)}

**Quality Anchors** (Stable, Defensive):
NVO, HIMS (healthcare stability)

**Lagging Participation:**
{', '.join(laggards)}"""
        self.sections.append(section)

    def add_liquidity_flags(self, ticker_data):
        """Add liquidity assessment."""
        section = """## 11. Liquidity Flags

**Assessment by Ticker:**"""

        for ticker, data in sorted(ticker_data.items()):
            volume = data.get('volume', 0)
            # Simple heuristic based on volume
            if volume > 5_000_000:
                flag = "🟢 GREEN (Institutional quality)"
            elif volume > 1_000_000:
                flag = "🟡 YELLOW (Moderate liquidity)"
            else:
                flag = "🔴 RED (High slippage risk)"

            section += f"\n- {ticker}: {flag} ({volume:,.0f} shares)"

        self.sections.append(section)

    def add_options_flow(self, ticker_data, options_data=None):
        """Add options flow analysis section."""
        section = """## 12. Options Flow Analysis

**Unusual Activity Detected:**"""

        if options_data and len(options_data) > 0:
            # Real options data available (yfinance or Massive.com format)
            section += "\n\n| Ticker | P/C Ratio | Call Vol | Put Vol | Avg Call IV | Avg Put IV | Sentiment |\n"
            section += "|--------|-----------|----------|---------|-------------|------------|-----------|"

            # Sort by put/call ratio (extreme values first)
            sorted_options = sorted(options_data.items(),
                                   key=lambda x: abs(x[1].get('put_call_ratio', 1) - 1),
                                   reverse=True)

            for ticker, opt_data in sorted_options:
                # Handle both yfinance and Massive.com data formats
                pc_ratio = opt_data.get('put_call_ratio', opt_data.get('unusual_activity', {}).get('put_call_ratio', 0))
                call_vol = opt_data.get('total_call_volume', opt_data.get('unusual_activity', {}).get('call_volume', 0))
                put_vol = opt_data.get('total_put_volume', opt_data.get('unusual_activity', {}).get('put_volume', 0))
                avg_call_iv = opt_data.get('avg_call_iv', 0)
                avg_put_iv = opt_data.get('avg_put_iv', 0)
                sentiment = opt_data.get('sentiment', 'NEUTRAL')

                # Sentiment emoji
                sent_emoji = '🟢' if sentiment == 'BULLISH' else ('🔴' if sentiment == 'BEARISH' else '⚪')

                section += f"\n| {ticker} | {pc_ratio:.2f} | {call_vol:,} | {put_vol:,} | {avg_call_iv:.1f}% | {avg_put_iv:.1f}% | {sent_emoji} {sentiment} |"

            section += "\n\n**Key Takeaways:**"

            # Analyze overall flow
            bullish_count = sum(1 for opt in options_data.values()
                              if opt.get('sentiment') == 'BULLISH')
            bearish_count = sum(1 for opt in options_data.values()
                              if opt.get('sentiment') == 'BEARISH')
            neutral_count = len(options_data) - bullish_count - bearish_count

            section += f"\n- **Bullish Flow:** {bullish_count} tickers (P/C < 0.7)"
            section += f"\n- **Bearish Flow:** {bearish_count} tickers (P/C > 1.3)"
            section += f"\n- **Neutral Flow:** {neutral_count} tickers"

            # Find most bullish/bearish
            most_bullish = min(options_data.items(), key=lambda x: x[1].get('put_call_ratio', 1), default=None)
            most_bearish = max(options_data.items(), key=lambda x: x[1].get('put_call_ratio', 1), default=None)

            if most_bullish and most_bullish[1].get('put_call_ratio', 1) < 0.7:
                section += f"\n- **Most Bullish:** {most_bullish[0]} (P/C: {most_bullish[1].get('put_call_ratio', 0):.2f})"
            if most_bearish and most_bearish[1].get('put_call_ratio', 1) > 1.3:
                section += f"\n- **Most Bearish:** {most_bearish[0]} (P/C: {most_bearish[1].get('put_call_ratio', 0):.2f})"

            # Show top strikes for highest volume tickers
            section += "\n\n**Top Strike Prices (Highest Volume):**"
            for ticker, opt_data in sorted(options_data.items(),
                                          key=lambda x: x[1].get('total_call_volume', 0) + x[1].get('total_put_volume', 0),
                                          reverse=True)[:3]:
                top_calls = opt_data.get('top_call_strikes', [])
                top_puts = opt_data.get('top_put_strikes', [])
                if top_calls or top_puts:
                    call_strikes = ', '.join([f"${s.get('strike', 0):.0f}" for s in top_calls[:2]]) if top_calls else 'N/A'
                    put_strikes = ', '.join([f"${s.get('strike', 0):.0f}" for s in top_puts[:2]]) if top_puts else 'N/A'
                    section += f"\n- **{ticker}:** Calls at {call_strikes} | Puts at {put_strikes}"

        else:
            # No options data - show placeholder
            section += "\n\n*Note: Options data not available. Check API connectivity.*"

            section += "\n\n**When Available, You'll See:**"
            section += "\n- Real-time unusual options activity"
            section += "\n- Put/Call ratios and sentiment"
            section += "\n- Top strike prices with heavy volume"
            section += "\n- Institutional vs retail flow patterns"
            section += "\n- Implied volatility changes"

        self.sections.append(section)

    def add_earnings_calendar(self, earnings_data=None):
        """Add upcoming earnings calendar section."""
        section = """## 12b. Upcoming Earnings Calendar

**Watchlist Earnings Dates:**"""

        if earnings_data and len(earnings_data) > 0:
            section += "\n\n| Ticker | Earnings Date | Est. EPS Growth | Status |\n"
            section += "|--------|---------------|-----------------|--------|"

            # Sort by earnings date
            from datetime import datetime
            sorted_earnings = sorted(
                earnings_data.items(),
                key=lambda x: x[1].get('earnings_date', '9999-99-99')
            )

            for ticker, data in sorted_earnings:
                date = data.get('earnings_date', 'TBD')
                eps_growth = data.get('earnings_estimate')
                eps_str = f"{eps_growth*100:.1f}%" if eps_growth else 'N/A'

                # Determine if it's soon
                try:
                    days_until = (datetime.strptime(date[:10], '%Y-%m-%d') - datetime.now()).days
                    if days_until < 0:
                        status = 'PASSED'
                    elif days_until <= 7:
                        status = '🔴 THIS WEEK'
                    elif days_until <= 14:
                        status = '🟡 NEXT WEEK'
                    else:
                        status = '🟢 >2 WEEKS'
                except:
                    status = 'TBD'

                section += f"\n| {ticker} | {date} | {eps_str} | {status} |"

            # Count upcoming
            upcoming_week = sum(1 for d in earnings_data.values()
                               if 'THIS WEEK' in str(d.get('earnings_date', '')))

            section += f"\n\n**Earnings Risk:** {len(earnings_data)} tickers with known dates"
            section += "\n\n**Pre-Earnings Strategy:**"
            section += "\n- Consider reducing position size 3-5 days before earnings"
            section += "\n- Watch for IV crush opportunities post-earnings"
            section += "\n- Set alerts for earnings date reminders"
        else:
            section += "\n\n*Earnings calendar data not available.*"

        self.sections.append(section)

    def _generate_coach_summary(self, ticker, data, metric, options_info=None, news_items=None):
        """
        Generate an intelligent, broker-level coach summary for a ticker.
        Analyzes technicals, options flow, relative strength, and news.
        """
        from data_gatherer import get_sector_info

        summary_parts = []

        # Get sector info
        sector_info = get_sector_info(ticker)
        sector = sector_info.get('sector', 'Unknown')
        industry = sector_info.get('industry', 'Unknown')

        # Technical analysis
        rsi = metric.get('rsi')
        macd = metric.get('macd', {})
        macd_hist = macd.get('histogram', 0) if macd else 0
        above_ma_50 = data.get('above_ma_50', False)
        pct_change = data.get('pct_change', 0)
        rel_strength = metric.get('relative_strength')
        gap_type = metric.get('gap_type')
        gap_pct = metric.get('gap_pct', 0)
        conviction = metric.get('conviction', 0)
        position_52w = data.get('position_52w')
        near_52w_high = data.get('near_52w_high', False)
        near_52w_low = data.get('near_52w_low', False)
        momentum_5d = metric.get('momentum_5d', 0)

        # 1. PRICE ACTION ASSESSMENT
        if gap_type == 'GAP_UP':
            summary_parts.append(f"**Price Action:** Opened with a {gap_pct:+.1f}% gap up - watch for continuation or gap fill.")
        elif gap_type == 'GAP_DOWN':
            summary_parts.append(f"**Price Action:** Gap down of {gap_pct:.1f}% - potential capitulation or weakness signal.")
        elif abs(pct_change) > 3:
            direction = "strong bullish momentum" if pct_change > 0 else "significant selling pressure"
            summary_parts.append(f"**Price Action:** {pct_change:+.2f}% move shows {direction}.")
        else:
            summary_parts.append(f"**Price Action:** Relatively quiet session ({pct_change:+.2f}%), consolidating near current levels.")

        # 2. TECHNICAL SETUP
        tech_signals = []
        if rsi is not None:
            if rsi > 70:
                tech_signals.append("RSI overbought - potential pullback zone")
            elif rsi < 30:
                tech_signals.append("RSI oversold - potential bounce candidate")
            elif 40 <= rsi <= 60:
                tech_signals.append("RSI neutral territory")

        if macd_hist > 0 and momentum_5d > 0:
            tech_signals.append("MACD bullish with positive momentum")
        elif macd_hist < 0 and momentum_5d < 0:
            tech_signals.append("MACD bearish with negative momentum")

        if above_ma_50:
            tech_signals.append("trading above 50-day MA (bullish structure)")
        else:
            tech_signals.append("below 50-day MA (repair work needed)")

        if tech_signals:
            summary_parts.append(f"**Technical Setup:** {', '.join(tech_signals)}.")

        # 3. 52-WEEK CONTEXT
        if position_52w is not None:
            if near_52w_high:
                summary_parts.append("**52-Week Context:** Trading near 52-week highs - momentum traders in control, watch for breakout or reversal.")
            elif near_52w_low:
                summary_parts.append("**52-Week Context:** Near 52-week lows - high risk/reward setup. Watch for capitulation or base-building.")
            elif position_52w > 70:
                summary_parts.append(f"**52-Week Context:** In upper 30% of range ({position_52w:.0f}%) - strength but not extended.")
            elif position_52w < 30:
                summary_parts.append(f"**52-Week Context:** In lower 30% of range ({position_52w:.0f}%) - value territory but need catalyst.")
            else:
                summary_parts.append(f"**52-Week Context:** Mid-range at {position_52w:.0f}% - watch for directional breakout.")

        # 4. RELATIVE STRENGTH
        if rel_strength is not None:
            if rel_strength > 10:
                summary_parts.append(f"**Relative Strength:** Significantly outperforming SPY ({rel_strength:+.1f}% over 20 days) - institutional accumulation likely.")
            elif rel_strength > 5:
                summary_parts.append(f"**Relative Strength:** Outperforming market ({rel_strength:+.1f}% vs SPY) - showing leadership.")
            elif rel_strength < -10:
                summary_parts.append(f"**Relative Strength:** Underperforming SPY by {abs(rel_strength):.1f}% - potential distribution or sector rotation away.")
            elif rel_strength < -5:
                summary_parts.append(f"**Relative Strength:** Lagging market ({rel_strength:+.1f}% vs SPY) - needs catalyst to catch up.")

        # 5. OPTIONS FLOW ANALYSIS
        if options_info:
            pc_ratio = options_info.get('put_call_ratio', 1)
            sentiment = options_info.get('sentiment', 'NEUTRAL')
            call_vol = options_info.get('total_call_volume', 0)
            put_vol = options_info.get('total_put_volume', 0)
            avg_call_iv = options_info.get('avg_call_iv', 0)

            if sentiment == 'BULLISH' and pc_ratio < 0.5:
                summary_parts.append(f"**Options Flow:** Heavy call buying (P/C: {pc_ratio:.2f}) - bullish institutional positioning.")
            elif sentiment == 'BULLISH':
                summary_parts.append(f"**Options Flow:** Call-heavy flow (P/C: {pc_ratio:.2f}) suggests bullish sentiment.")
            elif sentiment == 'BEARISH' and pc_ratio > 1.5:
                summary_parts.append(f"**Options Flow:** Elevated put activity (P/C: {pc_ratio:.2f}) - hedging or bearish bets in play.")
            elif sentiment == 'BEARISH':
                summary_parts.append(f"**Options Flow:** Put-heavy flow (P/C: {pc_ratio:.2f}) indicates caution.")
            else:
                summary_parts.append(f"**Options Flow:** Balanced positioning (P/C: {pc_ratio:.2f}) - no strong directional bias.")

            if avg_call_iv > 60:
                summary_parts.append(f"  - Elevated IV ({avg_call_iv:.0f}%) - expect large moves, consider selling premium.")

        # 6. NEWS & CATALYSTS
        if news_items and len(news_items) > 0:
            summary_parts.append("**Recent News:**")
            for item in news_items[:2]:  # Show top 2 news items
                title = item.get('title', '')
                publisher = item.get('publisher', '')
                if title:
                    # Truncate long titles
                    if len(title) > 80:
                        title = title[:77] + "..."
                    summary_parts.append(f"  - \"{title}\" ({publisher})")
        else:
            summary_parts.append(f"**Sector Context:** {industry} within {sector} - monitor sector-level catalysts and rotation.")

        # 7. REGIME FIT
        regime_fit = ""
        if self.regime_label == "RISK-ON":
            if conviction >= 4 and above_ma_50:
                regime_fit = "Excellent regime fit - high-conviction setup in risk-on environment. Consider adding on dips."
            elif conviction >= 3:
                regime_fit = "Good regime fit - favorable conditions for swing trades. Set tight stops."
            else:
                regime_fit = "Below-average conviction despite risk-on regime - better opportunities elsewhere."
        elif self.regime_label == "TRANSITIONAL":
            if conviction >= 4:
                regime_fit = "Quality setup in uncertain market - size down but keep on radar."
            else:
                regime_fit = "Mixed regime calls for selectivity - wait for regime clarity before committing capital."
        else:  # RISK-OFF
            if above_ma_50 and rel_strength and rel_strength > 0:
                regime_fit = "Holding up well in risk-off - potential relative strength play but size appropriately."
            else:
                regime_fit = "Risk-off environment - prioritize capital preservation over returns."

        summary_parts.append(f"**Coach's Take:** {regime_fit}")

        # 8. ACTIONABLE RECOMMENDATION
        action = ""
        if conviction >= 4.5 and above_ma_50 and (rsi is None or rsi < 70):
            action = "🎯 **Action:** Add to position on pullback to support. Strong conviction setup."
        elif conviction >= 4 and (rsi is not None and rsi < 35):
            action = "👀 **Action:** Oversold with high conviction - consider starter position with tight stop."
        elif conviction >= 3.5 and above_ma_50:
            action = "📋 **Action:** Hold existing position. Add only on confirmed breakout above resistance."
        elif conviction < 2.5 or (rsi is not None and rsi > 75):
            action = "⚠️ **Action:** Reduce exposure or avoid. Unfavorable risk/reward at current levels."
        elif not above_ma_50 and momentum_5d < -3:
            action = "🛑 **Action:** Repair mode - wait for reclaim of 50-day MA before considering entry."
        else:
            action = "⏳ **Action:** Monitor for better entry. Current setup is neutral - patience warranted."

        summary_parts.append(action)

        return "\n".join(summary_parts)

    def add_ticker_cards(self, ticker_data, metrics):
        """Add detailed ticker analysis cards with technical indicators."""
        section = "## 13. Full Ticker Cards"

        for ticker, data in sorted(ticker_data.items()):
            metric = metrics.get(ticker, {})
            conviction = metric.get('conviction', 0)
            pivot_levels = metric.get('pivot_levels', {})

            # Get technical indicators
            rsi = metric.get('rsi', None)
            macd = metric.get('macd', {})
            beta = metric.get('beta', None)
            volatility = metric.get('volatility', None)
            momentum_5d = metric.get('momentum_5d', None)
            momentum_20d = metric.get('momentum_20d', None)
            rel_vol = metric.get('relative_volume', 1.0)
            atr = metric.get('atr', None)
            rel_strength = metric.get('relative_strength', None)
            gap_type = metric.get('gap_type', None)
            gap_pct = metric.get('gap_pct', 0)

            # 52-week data
            high_52w = data.get('high_52w')
            low_52w = data.get('low_52w')
            position_52w = data.get('position_52w')
            pct_from_high = data.get('pct_from_high')

            # Gap alert
            gap_alert = ""
            if gap_type == 'GAP_UP':
                gap_alert = f" | 🚀 GAP UP {gap_pct:+.1f}%"
            elif gap_type == 'GAP_DOWN':
                gap_alert = f" | 💥 GAP DOWN {gap_pct:+.1f}%"

            # Relative strength indicator
            rs_indicator = ""
            if rel_strength is not None:
                if rel_strength > 5:
                    rs_indicator = "🟢 Outperforming SPY"
                elif rel_strength < -5:
                    rs_indicator = "🔴 Underperforming SPY"
                else:
                    rs_indicator = "⚪ In-line with SPY"

            card = f"""
### {ticker} - Conviction: {conviction:.1f}/5.0{gap_alert}

**Current Price:** ${data.get('close', 0):.2f} ({'+' if data.get('pct_change', 0) > 0 else ''}{data.get('pct_change', 0):.2f}%)
**Volume:** {data.get('volume', 0):,.0f} (Rel Vol: {rel_vol:.2f}x)
**Regime Fit:** {'Strong' if conviction >= 4 else 'Moderate' if conviction >= 3 else 'Weak'}
**Relative Strength (20d):** {rs_indicator} ({rel_strength:+.1f}% vs SPY)""" if rel_strength is not None else f"""
### {ticker} - Conviction: {conviction:.1f}/5.0{gap_alert}

**Current Price:** ${data.get('close', 0):.2f} ({'+' if data.get('pct_change', 0) > 0 else ''}{data.get('pct_change', 0):.2f}%)
**Volume:** {data.get('volume', 0):,.0f} (Rel Vol: {rel_vol:.2f}x)
**Regime Fit:** {'Strong' if conviction >= 4 else 'Moderate' if conviction >= 3 else 'Weak'}"""

            # Add 52-week range if available
            if high_52w and low_52w and position_52w is not None:
                range_bar = self._create_range_bar(position_52w)
                card += f"""
**52-Week Range:** ${low_52w:.2f} {range_bar} ${high_52w:.2f}
**Position:** {position_52w:.0f}% of range ({pct_from_high:+.1f}% from 52w high)"""

            card += "\n\n**Technical Indicators:**"

            if rsi is not None:
                rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                card += f"\n- RSI(14): {rsi:.1f} ({rsi_signal})"

            if macd.get('line') is not None:
                macd_line = macd.get('line', 0)
                macd_signal = macd.get('signal', 0)
                macd_histogram = macd.get('histogram', 0)
                macd_trend = "Bullish" if macd_histogram > 0 else "Bearish"
                card += f"\n- MACD: Line={macd_line:.2f}, Signal={macd_signal:.2f}, Histogram={macd_histogram:.2f} ({macd_trend})"

            if beta is not None:
                beta_desc = "High Beta" if beta > 1.5 else "Market Beta" if beta > 0.5 else "Low Beta"
                card += f"\n- Beta (vs SPY): {beta:.2f} ({beta_desc})"

            if volatility is not None:
                vol_desc = "High Vol" if volatility > 50 else "Moderate Vol" if volatility > 30 else "Low Vol"
                card += f"\n- Volatility (30d): {volatility:.1f}% annualized ({vol_desc})"

            if momentum_5d is not None and momentum_20d is not None:
                card += f"\n- Momentum: 5D={momentum_5d:+.2f}%, 20D={momentum_20d:+.2f}%"

            # ATR info
            atr_stop = pivot_levels.get('ATR_Stop')
            atr_target = pivot_levels.get('ATR_Target')

            card += f"""

**Technical Pattern:**
- Pivot Point: ${pivot_levels.get('P', 0):.2f}
- Resistance: R1=${pivot_levels.get('R1', 0):.2f}, R2=${pivot_levels.get('R2', 0):.2f}
- Support: S1=${pivot_levels.get('S1', 0):.2f}, S2=${pivot_levels.get('S2', 0):.2f}
- Trend: {'Bullish' if data.get('above_ma_50', False) else 'Bearish/Neutral'}

**Swing Setup (Pivot-Based):**
- Entry Zone: ${pivot_levels.get('S1', 0):.2f} - ${pivot_levels.get('P', 0):.2f}
- Stop: ${pivot_levels.get('S2', 0):.2f}
- Target: ${pivot_levels.get('R2', 0):.2f}"""

            if atr is not None and atr_stop is not None:
                card += f"""

**Volatility-Based Setup (ATR):**
- ATR(14): ${atr:.2f}
- ATR Stop (2x): ${atr_stop:.2f}
- ATR Target (3x): ${atr_target:.2f}
- Risk/Reward: 1:1.5"""

            # Get options and news data for this ticker
            ticker_options = self.options_data.get(ticker, {})
            ticker_news = self.news_data.get(ticker, [])

            # Generate intelligent coach summary
            coach_summary = self._generate_coach_summary(
                ticker, data, metric,
                options_info=ticker_options,
                news_items=ticker_news
            )

            card += f"""

---
**COACH SUMMARY:**

{coach_summary}"""

            section += card

        self.sections.append(section)

    def add_portfolio_risk_metrics(self, ticker_data, metrics):
        """Add portfolio-level risk metrics."""
        section = """## 14. Portfolio Risk Metrics

**Risk Assessment:**"""

        # Calculate portfolio average beta
        betas = [m.get('beta', 1.0) for m in metrics.values() if m.get('beta') is not None]
        avg_beta = sum(betas) / len(betas) if betas else 1.0

        # Calculate portfolio average volatility
        vols = [m.get('volatility', 30) for m in metrics.values() if m.get('volatility') is not None]
        avg_vol = sum(vols) / len(vols) if vols else 30

        # Identify high risk positions (high vol + high beta)
        high_risk_tickers = []
        for ticker, metric in metrics.items():
            beta = metric.get('beta', 1.0)
            vol = metric.get('volatility', 30)
            if beta and vol and beta > 1.5 and vol > 40:
                high_risk_tickers.append(f"{ticker} (β={beta:.2f}, σ={vol:.1f}%)")

        # Calculate concentration risk
        sorted_by_conviction = sorted(
            ticker_data.items(),
            key=lambda x: metrics.get(x[0], {}).get('conviction', 0),
            reverse=True
        )
        top_5_tickers = [t[0] for t in sorted_by_conviction[:5]]

        section += f"""
- **Portfolio Beta:** {avg_beta:.2f} ({'Higher than market' if avg_beta > 1.2 else 'Market-like' if avg_beta > 0.8 else 'Lower than market'})
- **Average Volatility:** {avg_vol:.1f}% annualized
- **Top 5 Concentration:** {', '.join(top_5_tickers)}

**High Risk Positions:**"""

        if high_risk_tickers:
            for ticker_info in high_risk_tickers[:5]:  # Show top 5
                section += f"\n- {ticker_info}"
        else:
            section += "\n- No extreme high-risk positions identified"

        section += """

**Risk Management Notes:**
- Monitor position sizes for high-beta tickers
- Consider hedging strategies if portfolio beta exceeds comfort level
- Diversification across sectors and themes reduces idiosyncratic risk"""

        self.sections.append(section)

    def add_game_plan(self, regime_label):
        """Add tomorrow's game plan."""
        if regime_label == "RISK-ON":
            green_plan = "Add to high-conviction names on any morning dip"
            red_plan = "Defensive hedge - reduce exposure to high-beta"
            flat_plan = "Watch for breakouts in leaders"
        elif regime_label == "TRANSITIONAL":
            green_plan = "Selective adds in quality setups"
            red_plan = "Raise cash, tighten stops"
            flat_plan = "Patience - wait for regime clarity"
        else:
            green_plan = "Fade strength, maintain defensive positioning"
            red_plan = "Comfortable in cash/defensive anchors"
            flat_plan = "Scout for capitulation/reversal signals"

        section = f"""## 15. Tomorrow's Game Plan

**Scenario Analysis:**

**GREEN Open (+0.5%+ SPY):**
{green_plan}

**RED Open (-0.5%+ SPY):**
{red_plan}

**FLAT Open (-0.5% to +0.5%):**
{flat_plan}"""
        self.sections.append(section)

    def add_falsification_checklist(self, regime_label):
        """Add falsification checklist."""
        if regime_label == "RISK-ON":
            checklist = """- VIX spike above 20
- Tech leaders (QQQ) breaking key support
- Credit spreads widening
- Loss of momentum in sector leaders"""
        else:
            checklist = """- VIX collapse below 15
- Strong breadth expansion (>70% stocks green)
- Financials (XLF) showing leadership
- High-beta names reclaiming moving averages"""

        section = f"""## 16. Falsification Checklist

**What would invalidate today's {regime_label.lower()} thesis:**
{checklist}"""
        self.sections.append(section)

    def add_risi_wrap(self, regime_label, macro_data):
        """Add RISI (Risk, Industry, Sentiment, Inflection) wrap."""
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)

        section = f"""## 17. RISI Wrap

**Risk:** {regime_label} - {'Improving' if spy_change > 0 else 'Deteriorating'}
**Industry:** Sector rotation ongoing - monitor relative strength
**Sentiment:** {'Optimistic' if regime_label == 'RISK-ON' else 'Cautious' if regime_label == 'TRANSITIONAL' else 'Defensive'}
**Inflection:** Watch for regime shift signals in VIX and breadth

**One Actionable Pattern:** Focus on high-conviction setups that align with current regime

**Delta vs Prior Session:** Market regime {'strengthening' if spy_change > 0 else 'weakening'}"""
        self.sections.append(section)

    def add_high_conviction_watch_list(self, ticker_data, metrics):
        """Add high-conviction watch list."""
        sorted_tickers = sorted(
            ticker_data.items(),
            key=lambda x: metrics.get(x[0], {}).get('conviction', 0),
            reverse=True
        )[:5]

        section = """## 18. High-Conviction Watch List

**Top 5 Setups for Tomorrow:**
"""

        for i, (ticker, data) in enumerate(sorted_tickers, 1):
            metric = metrics.get(ticker, {})
            pivot_levels = metric.get('pivot_levels', {})
            conviction = metric.get('conviction', 0)

            section += f"""
{i}. **{ticker}** (Conviction: {conviction:.1f}/5.0)
   - Entry: ${pivot_levels.get('S1', 0):.2f} - ${pivot_levels.get('P', 0):.2f}
   - Stop: ${pivot_levels.get('S2', 0):.2f}
   - Target: ${pivot_levels.get('R2', 0):.2f}"""

        self.sections.append(section)

    def add_performance_tracker(self):
        """Add performance tracker."""
        section = """## 19. Performance Tracker

**Hit Rate Statistics:**
- Last 10 Calls: TBD (tracking begins)
- High-Conviction Accuracy: TBD
- Average R-Multiple: TBD

*Note: Performance tracking will populate as calls are made and resolved*"""
        self.sections.append(section)

    def add_coach_directive(self, regime_label):
        """Add one-sentence coach directive."""
        if regime_label == "RISK-ON":
            directive = "Press your high-conviction winners while market tailwinds persist."
        elif regime_label == "TRANSITIONAL":
            directive = "Stay selective and patient - let the regime declare itself."
        else:
            directive = "Protect capital first, scout second - survive to trade another day."

        section = f"""## 20. One-Sentence Coach Directive

**{directive}**

---

*End of Report - Trade Smart, Manage Risk*"""
        self.sections.append(section)
