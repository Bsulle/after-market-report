// API configuration for connecting to Python backend
export const API_CONFIG = {
  // Base URL for the Python analysis backend
  baseUrl: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',

  endpoints: {
    // Analysis endpoints
    generateReport: '/api/report/generate',
    getCoachSummary: '/api/coach/summary',
    getTickerAnalysis: '/api/ticker/:ticker',

    // Watchlist endpoints
    syncWatchlist: '/api/watchlist/sync',

    // Market data
    getMarketRegime: '/api/market/regime',
    getMacroData: '/api/market/macro',
  },

  // Request timeout in milliseconds
  timeout: 30000,
};

// Conviction score thresholds (matches Python backend)
export const CONVICTION_THRESHOLDS = {
  HIGH: 4.5,      // 🔥 High conviction
  GOOD: 3.5,      // ✅ Good setup
  CAUTION: 2.5,   // ⚠️ Proceed with caution
  // Below 2.5 = 🚫 Avoid
};

// Market regime types
export const MARKET_REGIMES = {
  RISK_ON: 'Risk-On',
  RISK_OFF: 'Risk-Off',
  TRANSITIONAL: 'Transitional',
} as const;

export type MarketRegime = typeof MARKET_REGIMES[keyof typeof MARKET_REGIMES];
