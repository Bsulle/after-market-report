# calculator.py

import pandas as pd
import numpy as np

class Calculator:
    def __init__(self):
        pass

    def calculate_pivot_levels(self, high, low, close):
        """Calculate Pivot Point (P) and support/resistance levels."""
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        return {
            'P': pivot,
            'R1': r1,
            'R2': r2,
            'S1': s1,
            'S2': s2
        }

    def conviction_score(self, setup_quality, options_flow, macro_fit, risk_reward):
        """Calculate a Conviction Score based on multiple factors (1-5 scale)."""
        score = (setup_quality + options_flow + macro_fit + risk_reward) / 4
        return min(max(score, 1.0), 5.0)  # Clamp between 1 and 5

    def assess_setup_quality(self, ticker_data):
        """Assess technical setup quality (1-5)."""
        score = 3.0  # Base score

        # Trend assessment
        if ticker_data.get('above_ma_50'):
            score += 0.5

        # Volume assessment
        avg_volume = ticker_data['hist']['Volume'].mean()
        if ticker_data['volume'] > avg_volume * 1.2:
            score += 0.3

        # Momentum
        if ticker_data['pct_change'] > 2:
            score += 0.4
        elif ticker_data['pct_change'] < -2:
            score -= 0.4

        return min(max(score, 1.0), 5.0)

    def assess_options_flow(self, ticker):
        """Assess options flow (A=5, B=4, C=3, D=2, F=1)."""
        # Placeholder - would integrate with options data provider
        flow_grades = {'A': 5.0, 'B': 4.0, 'C': 3.0, 'D': 2.0, 'F': 1.0}
        return flow_grades.get('C', 3.0)  # Default to C

    def assess_macro_fit(self, regime_score):
        """Assess how well the ticker fits the current regime (1-5)."""
        # Risk-on (high score) vs Risk-off (low score)
        if regime_score >= 4:
            return 4.5  # Strong risk-on
        elif regime_score >= 3:
            return 3.5  # Moderate risk-on
        else:
            return 2.5  # Risk-off

    def assess_risk_reward(self, ticker_data, pivot_levels):
        """Assess risk/reward asymmetry (1-5)."""
        current = ticker_data['close']
        upside = pivot_levels['R2'] - current
        downside = current - pivot_levels['S2']

        if downside == 0:
            return 3.0

        rr_ratio = upside / downside

        if rr_ratio >= 3:
            return 5.0
        elif rr_ratio >= 2:
            return 4.0
        elif rr_ratio >= 1.5:
            return 3.5
        elif rr_ratio >= 1:
            return 3.0
        else:
            return 2.0

    def calculate_regime_score(self, macro_data):
        """Determine market regime score (1-5). 5=Risk-On, 1=Risk-Off."""
        score = 3.0  # Base neutral

        # VIX assessment
        vix = macro_data.get('VIX', {}).get('price', 20)
        if vix < 15:
            score += 1.0
        elif vix < 20:
            score += 0.5
        elif vix > 25:
            score -= 1.0
        elif vix > 20:
            score -= 0.5

        # SPY assessment
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)
        if spy_change > 1:
            score += 0.5
        elif spy_change < -1:
            score -= 0.5

        # QQQ assessment
        qqq_change = macro_data.get('Nasdaq', {}).get('pct_change', 0)
        if qqq_change > 1:
            score += 0.3
        elif qqq_change < -1:
            score -= 0.3

        return min(max(score, 1.0), 5.0)

    def get_regime_label(self, regime_score):
        """Get regime label from score."""
        if regime_score >= 4:
            return "RISK-ON"
        elif regime_score >= 3:
            return "TRANSITIONAL"
        else:
            return "RISK-OFF"

    def correlation_clusters(self, ticker_data_dict):
        """Calculate correlation matrix and identify clusters."""
        # Build returns dataframe
        returns_dict = {}
        for ticker, data in ticker_data_dict.items():
            if 'hist' in data and len(data['hist']) > 1:
                returns = data['hist']['Close'].pct_change().dropna()
                returns_dict[ticker] = returns

        if not returns_dict:
            return pd.DataFrame()

        # Create aligned dataframe
        returns_df = pd.DataFrame(returns_dict)
        correlation_matrix = returns_df.corr()

        return correlation_matrix

    def calculate_ticker_metrics(self, ticker, ticker_data, regime_score):
        """Calculate all metrics for a ticker."""
        # Pivot levels
        pivot_levels = self.calculate_pivot_levels(
            ticker_data['high'],
            ticker_data['low'],
            ticker_data['close']
        )

        # Setup quality
        setup_quality = self.assess_setup_quality(ticker_data)

        # Options flow
        options_flow = self.assess_options_flow(ticker)

        # Macro fit
        macro_fit = self.assess_macro_fit(regime_score)

        # Risk/Reward
        risk_reward = self.assess_risk_reward(ticker_data, pivot_levels)

        # Conviction score
        conviction = self.conviction_score(setup_quality, options_flow, macro_fit, risk_reward)

        return {
            'pivot_levels': pivot_levels,
            'setup_quality': setup_quality,
            'options_flow': options_flow,
            'macro_fit': macro_fit,
            'risk_reward': risk_reward,
            'conviction': conviction
        }
