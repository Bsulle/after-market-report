# Watchlist configuration (after-market report + thesis tickers)
watchlist = [
    'ASTS', 'GRAB', 'MP', 'ZETA',
    'JD', 'SLDP', 'NVO',
    'CRML', 'MCRP', 'DLO', 'IREN',
    'OSCR', 'TEM', 'AUR', 'BZ',
    'NBIS', 'PATH', 'OKLO',
    'TCOM'
]

# Regime thresholds
thresholds = {
    'VIX': 20,
    '10Y Yield': 4.5,
    'Sector ETFs': {
        'XLF': 'Financials',
        'XLY': 'Consumer Discretionary',
        'XLP': 'Consumer Staples',
        'XLC': 'Communication Services',
        'XLI': 'Industrials',
        'XLB': 'Materials',
        'XLK': 'Technology',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLRE': 'Real Estate',
        'XLU': 'Utilities'
    }
}