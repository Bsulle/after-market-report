#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import sys

from config import watchlist
from data_gatherer import (
    fetch_ticker_data, fetch_macro_data, fetch_breadth_data,
    fetch_options_data, fetch_earnings_calendar, fetch_52week_data
)
from calculator import Calculator
from report_builder import ReportBuilder

# Try to import Massive.com S3 integration (flat files)
try:
    from data_gatherer_massive_s3 import (
        fetch_ticker_data_s3,
        fetch_options_data_s3,
        discover_data_structure
    )
    MASSIVE_S3_AVAILABLE = True
except ImportError:
    MASSIVE_S3_AVAILABLE = False

# Try to import Massive.com REST API integration (legacy)
try:
    from data_gatherer_massive import (
        fetch_ticker_data_massive,
        fetch_options_data_massive,
        fetch_macro_data_massive
    )
    MASSIVE_API_AVAILABLE = True
except ImportError:
    MASSIVE_API_AVAILABLE = False

def gather_data(date):
    """Gather all market data for the specified date."""
    print(f"\n{'='*60}")
    print(f"Fetching market data for {date}")
    print(f"{'='*60}\n")

    ticker_data = {}
    macro_data = {}
    options_data = {}

    # Try Massive.com S3 first (flat files - most reliable)
    if MASSIVE_S3_AVAILABLE and not ticker_data:
        try:
            print("Attempting to fetch data from Massive.com S3...")
            ticker_data = fetch_ticker_data_s3(watchlist, date)

            if ticker_data:
                print("\nFetching options data from S3...")
                options_data = fetch_options_data_s3(watchlist, date)

                print(f"\n✓ Successfully fetched data via Massive.com S3")
                print(f"  - Tickers: {len(ticker_data)}")
                print(f"  - Options: {len(options_data)}")
        except Exception as e:
            print(f"\n⚠ Massive.com S3 failed: {str(e)}")
            ticker_data = {}
            options_data = {}

    # Try Massive.com REST API (legacy Polygon-style)
    if MASSIVE_API_AVAILABLE and not ticker_data:
        try:
            print("Attempting to fetch data using Massive.com REST API...")

            print("Fetching ticker data...")
            ticker_data = fetch_ticker_data_massive(watchlist, date)

            if ticker_data:
                print("\nFetching options data...")
                options_data = fetch_options_data_massive(watchlist, date)

                print("\nFetching macro data...")
                macro_data = fetch_macro_data_massive(date)

                print(f"\n✓ Successfully fetched data via Massive.com API")
                print(f"  - Tickers: {len(ticker_data)}")
                print(f"  - Options: {len(options_data)}")
                print(f"  - Macro indicators: {len(macro_data)}")
        except Exception as e:
            print(f"\n⚠ Massive.com API failed: {str(e)}")
            print("Falling back to yfinance...")
            ticker_data = {}
            options_data = {}

    # Fallback to yfinance if Massive.com unavailable or failed
    if not ticker_data:
        print("Fetching ticker data via yfinance...")
        ticker_data = fetch_ticker_data(watchlist, date)

        print("\nFetching macro data via yfinance...")
        macro_data = fetch_macro_data(date)

        # Fetch options data via yfinance (free!)
        if not options_data:
            print("\nFetching options data via yfinance...")
            options_data = fetch_options_data(watchlist)

    # Add 52-week data to ticker data
    print("\nCalculating 52-week positions...")
    ticker_data = fetch_52week_data(ticker_data)

    # Fetch earnings calendar
    print("Fetching earnings calendar...")
    earnings_data = fetch_earnings_calendar(watchlist)

    print("\nFetching breadth data...")
    breadth_data = fetch_breadth_data()

    return {
        'ticker_data': ticker_data,
        'macro_data': macro_data,
        'breadth_data': breadth_data,
        'options_data': options_data,
        'earnings_data': earnings_data
    }

def calculate_metrics(data):
    """Calculate all necessary metrics."""
    print(f"\n{'='*60}")
    print("Calculating metrics...")
    print(f"{'='*60}\n")

    calc = Calculator()
    ticker_data = data['ticker_data']
    macro_data = data['macro_data']

    # Calculate regime score with detailed breakdown
    regime_score, regime_components = calc.calculate_regime_score_detailed(macro_data)
    regime_label = calc.get_regime_label(regime_score)

    print(f"Market Regime: {regime_label} (Score: {regime_score:.1f}/5.0)")

    # Calculate metrics for each ticker, passing market data for beta calculation
    market_data = macro_data.get('S&P 500', {})
    metrics = {}
    for ticker, ticker_info in ticker_data.items():
        metrics[ticker] = calc.calculate_ticker_metrics(ticker, ticker_info, regime_score, market_data)

    # Calculate correlation matrix
    correlation_matrix = calc.correlation_clusters(ticker_data)

    return {
        'regime_score': regime_score,
        'regime_label': regime_label,
        'regime_components': regime_components,
        'metrics': metrics,
        'correlation_matrix': correlation_matrix
    }

def determine_regime(metrics):
    """Determine the trading regime (included for compatibility)."""
    return {
        'label': metrics['regime_label'],
        'score': metrics['regime_score']
    }

def build_markdown_report(data, calculated_metrics):
    """Build the markdown report."""
    print(f"\n{'='*60}")
    print("Building report...")
    print(f"{'='*60}\n")

    builder = ReportBuilder(args.date)

    report = builder.build_report(
        ticker_data=data['ticker_data'],
        macro_data=data['macro_data'],
        metrics=calculated_metrics['metrics'],
        regime_score=calculated_metrics['regime_score'],
        regime_label=calculated_metrics['regime_label'],
        correlation_matrix=calculated_metrics['correlation_matrix'],
        regime_components=calculated_metrics.get('regime_components'),
        options_data=data.get('options_data', {}),
        earnings_data=data.get('earnings_data', {}),
        prev_data=None  # Could be enhanced to load previous day's data
    )

    return report

if __name__ == '__main__':
    # Argument parser for date input
    parser = argparse.ArgumentParser(description='Generate After-Market Stock Report')
    parser.add_argument(
        '--date',
        type=str,
        help='Date for the report in YYYY-MM-DD format (defaults to yesterday)'
    )
    args = parser.parse_args()

    # Default to yesterday if no date provided
    if not args.date:
        yesterday = datetime.now() - timedelta(days=1)
        args.date = yesterday.strftime('%Y-%m-%d')

    print(f"\n{'#'*60}")
    print(f"# After-Market Report Generator")
    print(f"# Date: {args.date}")
    print(f"# Watchlist: {len(watchlist)} tickers")
    print(f"{'#'*60}")

    try:
        # Gather data
        data = gather_data(args.date)

        if not data['ticker_data']:
            print("\nERROR: No ticker data was fetched. Cannot generate report.")
            sys.exit(1)

        # Calculate metrics
        calculated_metrics = calculate_metrics(data)

        # Determine regime (compatibility)
        regime = determine_regime(calculated_metrics)

        # Build report
        report = build_markdown_report(data, calculated_metrics)

        # Save to file
        filename = f"After_Market_Report_{args.date}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n{'='*60}")
        print(f"Report generated successfully!")
        print(f"Saved to: {filename}")
        print(f"{'='*60}\n")

        # Also print to stdout
        print(report)

    except Exception as e:
        print(f"\n{'!'*60}")
        print(f"ERROR: {str(e)}")
        print(f"{'!'*60}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
