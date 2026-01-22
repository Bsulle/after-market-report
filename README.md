# After-Market Stock Report Generator

## Overview
Automated after-market stock report generator for swing/long-term traders. Generates comprehensive daily reports analyzing 17 stocks with technical analysis, market regime assessment, and conviction scoring in under 60 seconds.

## Features
- **Executive Dashboard**: 30-second market regime scan with risk scores
- **Market Regime Analysis**: Risk-On/Risk-Off/Transitional classification
- **Macro Panel**: Cross-asset context (SPY, QQQ, VIX, yields, oil, gold)
- **Conviction Dashboard**: All 17 tickers ranked by conviction score
- **Pivot Levels**: Calculated for each ticker (P, R1, R2, S1, S2)
- **Technical Patterns**: Chart structure, volume analysis, trend assessment
- **Correlation Clusters**: Identify correlated tickers and divergence plays
- **Position Sizing**: Recommendations based on conviction scores
- **Theme Rotation**: Track which trading themes are gaining/losing momentum
- **Leadership Map**: Leaders, quality anchors, lagging participation
- **Earnings Calendar**: Upcoming catalysts (10-day window)
- **Options Intelligence**: Flow grades and unusual activity
- **Tomorrow's Game Plan**: Scenario analysis (green/red/flat opens)
- **High-Conviction Watch List**: Top 5 setups for next trading day

## Watchlist (17 Tickers)
ASTS, GRAB, MP, ZETA, JD, SLDP, ACHR, NVO, CRML, MCRP, DLO, IREN, OSCR, TEM, AUR, HIMS, JOBY

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
1. Clone the repository:
   git clone https://github.com/Bsulle/after-market-report.git
   cd after-market-report

2. Install dependencies:
   pip install -r requirements.txt

3. Verify installation:
   python generate_report.py --date 2026-01-22

## Usage

### Generate Report for Today
python generate_report.py

### Generate Report for Specific Date
python generate_report.py --date 2026-01-21

### Output
Reports are saved as: After_Market_Report_YYYY-MM-DD.md

## Report Sections

### 1. Executive Dashboard
- Market Regime (Risk-On/Risk-Off/Transitional)
- Regime Score (1-5)
- Trip Wires (VIX, yields, custom metrics)
- Top 3 Actionable Insights

### 2. Market Regime Coach Call
- Volatility assessment
- Rates analysis
- Energy/Geopolitics drivers
- Global risk framing
- Coach interpretation (2-3 sentences)

### 3. Macro Panel
- SPY, QQQ, VIX, 10Y Yield, DXY, WTI Oil, Gold
- Cross-asset context table

### 4. Market Tape (Your Universe)
- Breadth analysis (green vs red stocks)
- Laggard identification
- Risk appetite indicators
- NYSE A/D ratio, 52-week highs/lows, % above 50-day MA

### 5. Conviction Dashboard
- All 17 tickers sorted by conviction score
- Price, % change, flow grade, quick read
- Conviction scale: 🔥 4.5-5.0 | ✅ 3.5-4.4 | ⚠️ 2.5-3.4 | 🚫 <2.5

### 6. Correlation Clusters
- Identify cohorts (eVTOL, High-Beta Tech, China/EM Risk)
- Divergence plays (decouplers from SPY)
- Real vs fake diversification

### 7. Position Sizing Matrix
- Recommended allocation by conviction level
- Cash reserve guidance based on regime score

### 8. Theme Rotation Scorecard
- Themes gaining momentum (↗️)
- Themes losing momentum (↘️)
- Themes consolidating (→)

### 9. Leadership Map
- Leaders (momentum + participation)
- Quality anchors (stable, defensive)
- Lagging participation

### 10. Liquidity Flags
- RED (high slippage risk)
- YELLOW (moderate)
- GREEN (institutional quality)

### 11. Full Ticker Cards (All 17)
For each ticker:
- Conviction score + options flow + regime fit
- One-line thesis
- Technical pattern & pivots
- Swing setup (entry, stops, targets)
- Conviction breakdown
- Options intelligence
- Catalysts
- Correlation buddies
- Coach summary

### 12. Tomorrow's Game Plan
- Scenario analysis (GREEN/RED/FLAT opens)
- Buy signals, fade candidates, defensive anchors

### 13. Falsification Checklist
- What would break today's bullish/bearish read

### 14. RISI Wrap
- Risk assessment (improving/deteriorating)
- Industry drivers
- Sentiment analysis
- One actionable pattern
- Delta vs prior session

### 15. High-Conviction Watch List
- Top 5 setups for tomorrow
- Entry, stop, target levels

### 16. Performance Tracker
- Hit rate statistics
- Last 10 calls with outcomes

### 17. One-Sentence Coach Directive
- Daily action summary

## Calculation Methodology

### Pivot Levels
P (Pivot) = (High + Low + Close) / 3
R1 = (2 × P) - Low
R2 = P + (High - Low)
S1 = (2 × P) - High
S2 = P - (High - Low)

### Conviction Score (1-5)
Average of:
- Setup Quality (trend, structure, volume)
- Options Flow (A=5, B=4, C=2, D=1)
- Macro Fit (does it benefit from regime?)
- Risk/Reward (asymmetry scoring)

### Correlation Clusters
- Daily returns correlation matrix
- Flag pairs with |correlation| > 0.7
- Identify negative correlations (< -0.5)

## Data Sources

### Market Data
- yfinance (Yahoo Finance) - OHLC, volume, earnings dates
- Free tier with unlimited requests

### Options Intelligence
- Barchart UOA (when available)
- Falls back to "No unusual activity found"

### News & Catalysts
- RSS feeds / Financial news sources
- SEC EDGAR for insider trading

### Breadth Data
- finviz market statistics
- NYSE advance/decline ratios

## Regime Thresholds (Configurable)

Default settings in config.py:
- VIX threshold: 20 (> = Risk-Off)
- 10Y Yield threshold: 4.5% (> = Duration pressure)
- Modify as needed based on your trading style

## Performance Tracking

Reports include a performance tracker section to:
- Monitor hit rate statistics
- Track conviction accuracy
- Review last 10 calls with outcomes
- Identify what's working

## Troubleshooting

### Data Not Fetching
- Check internet connection
- Verify ticker symbols are correct
- yfinance requires active internet

### Missing Options Data
- Not all free sources have UOA data
- Report will mark as "No unusual activity found"
- Consider paid services for detailed flow

### Slow Generation
- First run downloads 1-year historical data
- Subsequent runs are cached and faster
- Normal generation time: 30-60 seconds

## File Structure
after-market-report/
├── generate_report.py       # Main script (CLI entry point)
├── config.py                # Watchlist & thresholds
├── data_gatherer.py         # Fetch market data
├── calculator.py            # Pivot levels, conviction scores, correlations
├── report_builder.py        # Markdown report generation
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── After_Market_Report_*.md # Generated reports

## Requirements
- Python 3.8+
- yfinance
- pandas
- numpy
- requests
- beautifulsoup4
- lxml
- python-dateutil
- pytz

## Contributing
Feel free to contribute by:
- Adding new data sources
- Improving calculations
- Enhancing report formatting
- Adding new analysis sections

## License
Open source - use for personal trading analysis

## Disclaimer
This tool is for educational and analysis purposes only. Not financial advice. Always do your own research and consult a financial advisor before trading.