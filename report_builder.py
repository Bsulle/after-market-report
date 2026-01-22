# report_builder.py

from datetime import datetime

class ReportBuilder:
    def __init__(self, date_str):
        self.date_str = date_str
        self.sections = []

    def build_report(self, ticker_data, macro_data, metrics, regime_score, regime_label, correlation_matrix):
        """Build the complete markdown report."""

        self.add_header()
        self.add_executive_dashboard(regime_label, regime_score, macro_data)
        self.add_market_regime_coach_call(regime_label, regime_score, macro_data)
        self.add_macro_panel(macro_data)
        self.add_market_tape(ticker_data)
        self.add_conviction_dashboard(ticker_data, metrics)
        self.add_correlation_clusters(correlation_matrix)
        self.add_position_sizing(regime_score)
        self.add_theme_rotation(ticker_data, metrics)
        self.add_leadership_map(ticker_data, metrics)
        self.add_liquidity_flags(ticker_data)
        self.add_ticker_cards(ticker_data, metrics)
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

    def add_market_regime_coach_call(self, regime_label, regime_score, macro_data):
        """Add market regime analysis."""
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
        """Add conviction dashboard."""
        section = """## 5. Conviction Dashboard

**Conviction Scale:** 🔥 4.5-5.0 | ✅ 3.5-4.4 | ⚠️ 2.5-3.4 | 🚫 <2.5

| Ticker | Price | Change | Conviction | Flow | Quick Read |
|--------|-------|--------|------------|------|------------|"""

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

            # Icon based on conviction
            if conviction >= 4.5:
                icon = "🔥"
            elif conviction >= 3.5:
                icon = "✅"
            elif conviction >= 2.5:
                icon = "⚠️"
            else:
                icon = "🚫"

            flow = "C"  # Placeholder
            quick_read = "Above MA50" if data.get('above_ma_50', False) else "Below MA50"

            section += f"\n| {ticker} | ${price:.2f} | {'+' if pct_change > 0 else ''}{pct_change:.2f}% | {icon} {conviction:.1f} | {flow} | {quick_read} |"

        self.sections.append(section)

    def add_correlation_clusters(self, correlation_matrix):
        """Add correlation clusters analysis."""
        section = """## 6. Correlation Clusters

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
        """Add detailed ticker analysis cards."""
        section = "## 11. Full Ticker Cards"

        for ticker, data in sorted(ticker_data.items()):
            metric = metrics.get(ticker, {})
            conviction = metric.get('conviction', 0)
            pivot_levels = metric.get('pivot_levels', {})

            card = f"""
### {ticker} - Conviction: {conviction:.1f}/5.0

**Current Price:** ${data.get('close', 0):.2f} ({'+' if data.get('pct_change', 0) > 0 else ''}{data.get('pct_change', 0):.2f}%)
**Options Flow:** C (Neutral)
**Regime Fit:** {'Strong' if conviction >= 4 else 'Moderate' if conviction >= 3 else 'Weak'}

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

        section = f"""## 12. Tomorrow's Game Plan

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

        section = f"""## 13. Falsification Checklist

**What would invalidate today's {regime_label.lower()} thesis:**
{checklist}"""
        self.sections.append(section)

    def add_risi_wrap(self, regime_label, macro_data):
        """Add RISI (Risk, Industry, Sentiment, Inflection) wrap."""
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)

        section = f"""## 14. RISI Wrap

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

        section = """## 15. High-Conviction Watch List

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
        section = """## 16. Performance Tracker

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

        section = f"""## 17. One-Sentence Coach Directive

**{directive}**

---

*End of Report - Trade Smart, Manage Risk*"""
        self.sections.append(section)
