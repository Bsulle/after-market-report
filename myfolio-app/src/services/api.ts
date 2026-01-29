import { API_CONFIG, CONVICTION_THRESHOLDS, MarketRegime } from '../config/api';

// Types matching Python backend output
export interface CoachSummary {
  marketRegime: MarketRegime;
  regimeScore: number;
  headline: string;
  keyInsights: string[];
  topPicks: TickerSummary[];
  avoidList: string[];
  actionItems: string[];
  generatedAt: string;
}

export interface TickerSummary {
  symbol: string;
  convictionScore: number;
  convictionEmoji: string;
  thesis: string;
  pivotLevels?: PivotLevels;
  catalyst?: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface PivotLevels {
  pivot: number;
  r1: number;
  r2: number;
  s1: number;
  s2: number;
}

export interface MacroData {
  spy: { price: number; change: number };
  qqq: { price: number; change: number };
  vix: { value: number; status: 'LOW' | 'ELEVATED' | 'HIGH' };
  dxy: { value: number; trend: string };
  oil: { price: number; change: number };
  gold: { price: number; change: number };
  yield10y: { value: number; threshold: number };
}

// Get conviction emoji based on score
export function getConvictionEmoji(score: number): string {
  if (score >= CONVICTION_THRESHOLDS.HIGH) return '🔥';
  if (score >= CONVICTION_THRESHOLDS.GOOD) return '✅';
  if (score >= CONVICTION_THRESHOLDS.CAUTION) return '⚠️';
  return '🚫';
}

// API client class
class ApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = API_CONFIG.baseUrl;
    this.timeout = API_CONFIG.timeout;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timed out');
      }
      throw error;
    }
  }

  // Get coach summary for watchlist
  async getCoachSummary(watchlist: string[]): Promise<CoachSummary> {
    return this.request<CoachSummary>(API_CONFIG.endpoints.getCoachSummary, {
      method: 'POST',
      body: JSON.stringify({ tickers: watchlist }),
    });
  }

  // Get detailed analysis for a single ticker
  async getTickerAnalysis(ticker: string): Promise<TickerSummary> {
    const endpoint = API_CONFIG.endpoints.getTickerAnalysis.replace(':ticker', ticker);
    return this.request<TickerSummary>(endpoint);
  }

  // Get current market regime
  async getMarketRegime(): Promise<{ regime: MarketRegime; details: string }> {
    return this.request(API_CONFIG.endpoints.getMarketRegime);
  }

  // Get macro data
  async getMacroData(): Promise<MacroData> {
    return this.request(API_CONFIG.endpoints.getMacroData);
  }

  // Generate full report (Pro feature)
  async generateReport(watchlist: string[], date?: string): Promise<{ reportUrl: string }> {
    return this.request(API_CONFIG.endpoints.generateReport, {
      method: 'POST',
      body: JSON.stringify({
        tickers: watchlist,
        date: date || new Date().toISOString().split('T')[0],
      }),
    });
  }
}

export const apiClient = new ApiClient();

// Mock data for development/demo
export const mockCoachSummary: CoachSummary = {
  marketRegime: 'Risk-On',
  regimeScore: 7.5,
  headline: 'Constructive tape with sector rotation favoring growth',
  keyInsights: [
    'VIX below 20 signals low fear environment',
    'Tech leadership intact, QQQ holding above 50-day MA',
    'Small caps showing relative strength vs large caps',
    'Dollar weakness supportive for commodities and EM',
  ],
  topPicks: [
    {
      symbol: 'HIMS',
      convictionScore: 4.7,
      convictionEmoji: '🔥',
      thesis: 'Telehealth momentum continues with strong subscriber growth',
      riskLevel: 'MEDIUM',
      catalyst: 'Q4 earnings Feb 15',
    },
    {
      symbol: 'GRAB',
      convictionScore: 4.2,
      convictionEmoji: '✅',
      thesis: 'Southeast Asia super-app with improving unit economics',
      riskLevel: 'MEDIUM',
      catalyst: 'Path to profitability update',
    },
    {
      symbol: 'ASTS',
      convictionScore: 3.8,
      convictionEmoji: '✅',
      thesis: 'Space-based cellular broadband with first commercial launch approaching',
      riskLevel: 'HIGH',
      catalyst: 'BlueBird satellite deployment',
    },
  ],
  avoidList: ['SLDP', 'MCRP'],
  actionItems: [
    'Consider adding to HIMS on any pullback to $18 support',
    'Watch GRAB for breakout above $4.50 resistance',
    'Reduce position size in high-beta names if VIX spikes above 20',
  ],
  generatedAt: new Date().toISOString(),
};
