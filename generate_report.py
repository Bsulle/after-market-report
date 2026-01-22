#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import sys

from config import watchlist
from data_gatherer import fetch_ticker_data, fetch_macro_data, fetch_breadth_data
from calculator import Calculator
from report_builder import ReportBuilder

def gather_data(date):
    """Gather all market data for the specified date."""
    print(f"\n{'='*60}")
    print(f"Fetching market data for {date}")
    print(f"{'='*60}\n")

    print("Fetching ticker data...")
    ticker_data = fetch_ticker_data(watchlist, date)

    print("\nFetching macro data...")
    macro_data = fetch_macro_data(date)

    print("\nFetching breadth data...")
    breadth_data = fetch_breadth_data()

    return {
        'ticker_data': ticker_data,
        'macro_data': macro_data,
        'breadth_data': breadth_data
    }

def calculate_metrics(data):
    """Calculate all necessary metrics."""
    print(f"\n{'='*60}")
    print("Calculating metrics...")
    print(f"{'='*60}\n")

    calc = Calculator()
    ticker_data = data['ticker_data']
    macro_data = data['macro_data']

    # Calculate regime score
    regime_score = calc.calculate_regime_score(macro_data)
    regime_label = calc.get_regime_label(regime_score)

    print(f"Market Regime: {regime_label} (Score: {regime_score:.1f}/5.0)")

    # Calculate metrics for each ticker
    metrics = {}
    for ticker, ticker_info in ticker_data.items():
        metrics[ticker] = calc.calculate_ticker_metrics(ticker, ticker_info, regime_score)

    # Calculate correlation matrix
    correlation_matrix = calc.correlation_clusters(ticker_data)

    return {
        'regime_score': regime_score,
        'regime_label': regime_label,
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
        correlation_matrix=calculated_metrics['correlation_matrix']
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
        with open(filename, 'w') as f:
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
