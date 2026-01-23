# report_builder.py

from datetime import datetime
import pandas as pd

class ReportBuilder:
    def __init__(self, date_str):
        self.date_str = date_str
        self.sections = []

    def build_report(self, ticker_data, macro_data, metrics, regime_score, regime_label, correlation_matrix, regime_components=None):
        """Build the complete markdown report."""

        self.add_header()
        self.add_summary_stats(ticker_data, macro_data, regime_label, regime_score)
        self.add_executive_dashboard(regime_label, regime_score, macro_data)
        self.add_market_regime_coach_call(regime_label, regime_score, macro_data, regime_components)
        self.add_macro_panel(macro_data)
        self.add_market_tape(ticker_data)
        self.add_conviction_dashboard(ticker_data, metrics)
        self.add_correlation_clusters(correlation_matrix)
        self.add_position_sizing(regime_score)
        self.add_theme_rotation(ticker_data, metrics)
        self.add_leadership_map(ticker_data, metrics)
        self.add_liquidity_flags(ticker_data)
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

| Ticker | Price | Change | Rel Vol | Conviction | Quick Read |
|--------|-------|--------|---------|------------|------------|"""

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

            # Icon based on conviction
            if conviction >= 4.5:
                icon = "🔥"
            elif conviction >= 3.5:
                icon = "✅"
            elif conviction >= 2.5:
                icon = "⚠️"
            else:
                icon = "🚫"

            quick_read = "Above MA50" if data.get('above_ma_50', False) else "Below MA50"

            section += f"\n| {ticker} | ${price:.2f} | {'+' if pct_change > 0 else ''}{pct_change:.2f}% | {rel_vol:.2f}x | {icon} {conviction:.1f} | {quick_read} |"

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

    def add_correlation_clusters(self, correlation_matrix):
        """Add correlation clusters analysis with actual correlation matrix."""
        section = """## 6. Correlation Clusters

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

        section = f"""## 7. Position Sizing Matrix

**Recommended Allocation by Conviction Level:**
- High Conviction (🔥 4.5-5.0): {high_conv} per position
- Medium Conviction (✅ 3.5-4.4): {med_conv} per position
- Low Conviction (⚠️ 2.5-3.4): {low_conv} per position

**Cash Reserve:** {cash} (based on regime score {regime_score:.1f}/5.0)"""
        self.sections.append(section)

    def add_theme_rotation(self, ticker_data, metrics):
        """Add theme rotation scorecard."""
        section = """## 8. Theme Rotation Scorecard

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

        section = f"""## 9. Leadership Map

**Leaders** (Momentum + Participation):
{', '.join(leaders)}

**Quality Anchors** (Stable, Defensive):
NVO, HIMS (healthcare stability)

**Lagging Participation:**
{', '.join(laggards)}"""
        self.sections.append(section)

    def add_liquidity_flags(self, ticker_data):
        """Add liquidity assessment."""
        section = """## 10. Liquidity Flags

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

    def add_ticker_cards(self, ticker_data, metrics):
        """Add detailed ticker analysis cards with technical indicators."""
        section = "## 11. Full Ticker Cards"

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

            card = f"""
### {ticker} - Conviction: {conviction:.1f}/5.0

**Current Price:** ${data.get('close', 0):.2f} ({'+' if data.get('pct_change', 0) > 0 else ''}{data.get('pct_change', 0):.2f}%)
**Volume:** {data.get('volume', 0):,.0f} (Rel Vol: {rel_vol:.2f}x)
**Regime Fit:** {'Strong' if conviction >= 4 else 'Moderate' if conviction >= 3 else 'Weak'}

**Technical Indicators:**"""

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

            card += f"""

**Technical Pattern:**
- Pivot Point: ${pivot_levels.get('P', 0):.2f}
- Resistance: R1=${pivot_levels.get('R1', 0):.2f}, R2=${pivot_levels.get('R2', 0):.2f}
- Support: S1=${pivot_levels.get('S1', 0):.2f}, S2=${pivot_levels.get('S2', 0):.2f}
- Trend: {'Bullish' if data.get('above_ma_50', False) else 'Bearish/Neutral'}

**Swing Setup:**
- Entry Zone: ${pivot_levels.get('S1', 0):.2f} - ${pivot_levels.get('P', 0):.2f}
- Stop: ${pivot_levels.get('S2', 0):.2f}
- Target: ${pivot_levels.get('R2', 0):.2f}

**Coach Summary:** Monitor price action around pivot levels. Conviction score of {conviction:.1f} suggests {'high priority' if conviction >= 4 else 'moderate watch' if conviction >= 3 else 'low priority'}."""

            section += card

        self.sections.append(section)

    def add_portfolio_risk_metrics(self, ticker_data, metrics):
        """Add portfolio-level risk metrics."""
        section = """## 12. Portfolio Risk Metrics

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

        section = f"""## 13. Tomorrow's Game Plan

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

        section = f"""## 14. Falsification Checklist

**What would invalidate today's {regime_label.lower()} thesis:**
{checklist}"""
        self.sections.append(section)

    def add_risi_wrap(self, regime_label, macro_data):
        """Add RISI (Risk, Industry, Sentiment, Inflection) wrap."""
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)

        section = f"""## 15. RISI Wrap

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

        section = """## 16. High-Conviction Watch List

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
        section = """## 17. Performance Tracker

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

        section = f"""## 18. One-Sentence Coach Directive

**{directive}**

---

*End of Report - Trade Smart, Manage Risk*"""
        self.sections.append(section)
