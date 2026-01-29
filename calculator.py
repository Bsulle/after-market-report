# calculator.py

import pandas as pd
import numpy as np

class Calculator:
    def __init__(self):
        pass

    # ==================== TECHNICAL INDICATORS ====================

    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None

        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator."""
        if len(prices) < slow:
            return None, None, None

        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return (
            macd_line.iloc[-1] if not macd_line.empty else None,
            signal_line.iloc[-1] if not signal_line.empty else None,
            histogram.iloc[-1] if not histogram.empty else None
        )

    def calculate_momentum(self, prices, period=20):
        """Calculate momentum (rate of change)."""
        if len(prices) < period + 1:
            return None
        return ((prices.iloc[-1] / prices.iloc[-period - 1]) - 1) * 100

    def calculate_volatility(self, returns, period=30):
        """Calculate annualized volatility."""
        if len(returns) < period:
            return None
        return returns.tail(period).std() * np.sqrt(252) * 100

    def calculate_beta(self, ticker_returns, market_returns):
        """Calculate beta vs market (SPY)."""
        if len(ticker_returns) < 30 or len(market_returns) < 30:
            return None

        # Align the series
        combined = pd.DataFrame({
            'ticker': ticker_returns,
            'market': market_returns
        }).dropna()

        if len(combined) < 20:
            return None

        covariance = combined['ticker'].cov(combined['market'])
        market_variance = combined['market'].var()

        if market_variance == 0:
            return None

        return covariance / market_variance

    def calculate_relative_volume(self, current_volume, avg_volume):
        """Calculate relative volume."""
        if avg_volume == 0:
            return 0
        return current_volume / avg_volume

    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range for volatility-based stops."""
        if len(high) < period + 1:
            return None

        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr.iloc[-1] if not atr.empty and not pd.isna(atr.iloc[-1]) else None

    def calculate_relative_strength(self, ticker_returns, market_returns, period=20):
        """Calculate relative strength vs market (SPY) over period."""
        if len(ticker_returns) < period or len(market_returns) < period:
            return None

        # Sum of returns over period
        ticker_perf = (1 + ticker_returns.tail(period)).prod() - 1
        market_perf = (1 + market_returns.tail(period)).prod() - 1

        # Relative strength = ticker performance - market performance
        return (ticker_perf - market_perf) * 100

    def detect_gap(self, current_open, prev_close):
        """Detect gap up/down from previous close."""
        if prev_close == 0:
            return None, 0

        gap_pct = ((current_open - prev_close) / prev_close) * 100

        if gap_pct > 2:
            return 'GAP_UP', gap_pct
        elif gap_pct < -2:
            return 'GAP_DOWN', gap_pct
        else:
            return None, gap_pct

    # ==================== PIVOT LEVELS ====================

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

    # ==================== CONVICTION SCORING (TRANSPARENT) ====================

    def conviction_score_breakdown(self, setup_quality, macro_fit, risk_reward, momentum_score):
        """Calculate conviction score with transparent breakdown.

        Weights:
        - Setup Quality: 30%
        - Macro Fit: 30%
        - Risk/Reward: 25%
        - Momentum: 15%
        """
        weights = {
            'setup_quality': 0.30,
            'macro_fit': 0.30,
            'risk_reward': 0.25,
            'momentum': 0.15
        }

        components = {
            'Setup Quality': {
                'score': setup_quality,
                'weight': weights['setup_quality'],
                'contribution': setup_quality * weights['setup_quality']
            },
            'Macro Fit': {
                'score': macro_fit,
                'weight': weights['macro_fit'],
                'contribution': macro_fit * weights['macro_fit']
            },
            'Risk/Reward': {
                'score': risk_reward,
                'weight': weights['risk_reward'],
                'contribution': risk_reward * weights['risk_reward']
            },
            'Momentum': {
                'score': momentum_score,
                'weight': weights['momentum'],
                'contribution': momentum_score * weights['momentum']
            }
        }

        total_score = sum(c['contribution'] for c in components.values())
        total_score = min(max(total_score, 1.0), 5.0)  # Clamp between 1 and 5

        return total_score, components

    def assess_setup_quality(self, ticker_data, tech_indicators):
        """Assess technical setup quality (1-5) with multiple factors."""
        score = 3.0  # Base score

        # Trend assessment (MA-based)
        if ticker_data.get('above_ma_50'):
            score += 0.5

        # RSI assessment
        rsi = tech_indicators.get('rsi')
        if rsi is not None:
            if 40 <= rsi <= 60:
                score += 0.3  # Neutral/balanced
            elif 30 <= rsi < 40:
                score += 0.5  # Oversold (buying opportunity)
            elif rsi > 70:
                score -= 0.3  # Overbought (risk)

        # MACD signal
        macd_hist = tech_indicators.get('macd_histogram')
        if macd_hist is not None:
            if macd_hist > 0:
                score += 0.2  # Bullish
            else:
                score -= 0.2  # Bearish

        # Volume confirmation
        rel_volume = ticker_data.get('relative_volume', 1.0)
        if rel_volume > 1.5:
            score += 0.3  # Strong volume
        elif rel_volume < 0.5:
            score -= 0.4  # Weak volume (red flag)

        # Recent momentum
        if ticker_data.get('pct_change', 0) > 2:
            score += 0.3
        elif ticker_data.get('pct_change', 0) < -3:
            score -= 0.4

        return min(max(score, 1.0), 5.0)

    def assess_momentum_score(self, tech_indicators):
        """Assess momentum strength (1-5)."""
        score = 3.0

        # 5-day momentum
        mom_5d = tech_indicators.get('momentum_5d', 0)
        if mom_5d > 5:
            score += 0.8
        elif mom_5d > 2:
            score += 0.4
        elif mom_5d < -5:
            score -= 0.8
        elif mom_5d < -2:
            score -= 0.4

        # 20-day momentum
        mom_20d = tech_indicators.get('momentum_20d', 0)
        if mom_20d > 10:
            score += 0.6
        elif mom_20d > 5:
            score += 0.3
        elif mom_20d < -10:
            score -= 0.6

        # RSI momentum
        rsi = tech_indicators.get('rsi')
        if rsi is not None:
            if rsi > 60:
                score += 0.3
            elif rsi < 40:
                score -= 0.3

        return min(max(score, 1.0), 5.0)

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
        """Assess risk/reward asymmetry (1-5) with actual ratio."""
        current = ticker_data['close']
        upside = pivot_levels['R2'] - current
        downside = current - pivot_levels['S2']

        if downside <= 0:
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

    # ==================== REGIME SCORING ====================

    def calculate_regime_score_detailed(self, macro_data):
        """Calculate regime score with detailed breakdown."""
        components = {}
        score = 0.0

        # VIX assessment
        vix = macro_data.get('VIX', {}).get('price', 20)
        if vix < 15:
            vix_score = 1.0
        elif vix < 20:
            vix_score = 0.5
        elif vix > 25:
            vix_score = -1.0
        elif vix > 20:
            vix_score = -0.5
        else:
            vix_score = 0.0
        components['VIX'] = {'value': vix, 'score': vix_score}
        score += vix_score

        # SPY assessment
        spy_change = macro_data.get('S&P 500', {}).get('pct_change', 0)
        if spy_change > 1:
            spy_score = 0.5
        elif spy_change < -1:
            spy_score = -0.5
        else:
            spy_score = 0.0
        components['SPY'] = {'value': spy_change, 'score': spy_score}
        score += spy_score

        # QQQ assessment
        qqq_change = macro_data.get('Nasdaq', {}).get('pct_change', 0)
        if qqq_change > 1:
            qqq_score = 0.3
        elif qqq_change < -1:
            qqq_score = -0.3
        else:
            qqq_score = 0.0
        components['QQQ'] = {'value': qqq_change, 'score': qqq_score}
        score += qqq_score

        # DXY (dollar strength)
        dxy_change = macro_data.get('DXY', {}).get('pct_change', 0)
        if dxy_change < -0.2:
            dxy_score = 0.5  # Weaker dollar = risk on
        elif dxy_change > 0.2:
            dxy_score = -0.5  # Stronger dollar = risk off
        else:
            dxy_score = 0.0
        components['DXY'] = {'value': dxy_change, 'score': dxy_score}
        score += dxy_score

        # Gold (safe haven bid)
        gold_change = macro_data.get('Gold', {}).get('pct_change', 0)
        if gold_change > 2:
            gold_score = -0.5  # Strong gold = flight to safety
        elif gold_change < -1:
            gold_score = 0.3  # Weak gold = risk appetite
        else:
            gold_score = 0.0
        components['Gold'] = {'value': gold_change, 'score': gold_score}
        score += gold_score

        # Base score of 3.0
        final_score = 3.0 + score
        final_score = min(max(final_score, 1.0), 5.0)

        return final_score, components

    def calculate_regime_score(self, macro_data):
        """Determine market regime score (1-5). 5=Risk-On, 1=Risk-Off."""
        score, _ = self.calculate_regime_score_detailed(macro_data)
        return score

    def get_regime_label(self, regime_score):
        """Get regime label from score."""
        if regime_score >= 4:
            return "RISK-ON"
        elif regime_score >= 3:
            return "TRANSITIONAL"
        else:
            return "RISK-OFF"

    # ==================== CORRELATION & RISK ====================

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

    def get_top_correlations(self, correlation_matrix, n=10):
        """Get top N correlated pairs."""
        if correlation_matrix.empty:
            return []

        # Get upper triangle to avoid duplicates
        correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                ticker1 = correlation_matrix.columns[i]
                ticker2 = correlation_matrix.columns[j]
                corr = correlation_matrix.iloc[i, j]
                correlations.append({
                    'ticker1': ticker1,
                    'ticker2': ticker2,
                    'correlation': corr
                })

        # Sort by absolute correlation
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        return correlations[:n]

    def calculate_portfolio_metrics(self, ticker_data_dict, metrics_dict):
        """Calculate portfolio-level risk metrics."""
        if not ticker_data_dict:
            return {}

        # Calculate average performance
        returns = [data.get('pct_change', 0) for data in ticker_data_dict.values()]
        avg_return = np.mean(returns)

        # Calculate beta-weighted exposure (if we have betas)
        betas = []
        for ticker, data in ticker_data_dict.items():
            tech = metrics_dict.get(ticker, {}).get('technical_indicators', {})
            beta = tech.get('beta')
            if beta is not None:
                betas.append(beta)

        avg_beta = np.mean(betas) if betas else None

        # Count positions by conviction
        high_conviction = sum(1 for m in metrics_dict.values() if m.get('conviction', 0) >= 4.5)
        med_conviction = sum(1 for m in metrics_dict.values() if 3.5 <= m.get('conviction', 0) < 4.5)
        low_conviction = sum(1 for m in metrics_dict.values() if m.get('conviction', 0) < 3.5)

        return {
            'avg_return': avg_return,
            'avg_beta': avg_beta,
            'high_conviction_count': high_conviction,
            'med_conviction_count': med_conviction,
            'low_conviction_count': low_conviction,
            'total_positions': len(ticker_data_dict)
        }

    # ==================== MAIN CALCULATION ====================

    def calculate_ticker_metrics(self, ticker, ticker_data, regime_score, market_data=None):
        """Calculate all metrics for a ticker with full breakdown."""

        # Calculate technical indicators
        hist = ticker_data.get('hist')
        tech_indicators = {}

        if hist is not None and len(hist) > 0:
            prices = hist['Close']
            returns = prices.pct_change().dropna()

            tech_indicators['rsi'] = self.calculate_rsi(prices)
            macd, signal, hist_val = self.calculate_macd(prices)
            tech_indicators['macd'] = macd
            tech_indicators['macd_signal'] = signal
            tech_indicators['macd_histogram'] = hist_val

            tech_indicators['momentum_5d'] = self.calculate_momentum(prices, 5)
            tech_indicators['momentum_20d'] = self.calculate_momentum(prices, 20)
            tech_indicators['volatility_30d'] = self.calculate_volatility(returns, 30)

            # Calculate ATR for volatility-based stops
            tech_indicators['atr'] = self.calculate_atr(
                hist['High'], hist['Low'], hist['Close']
            )

            # Calculate beta and relative strength if market data available
            if market_data is not None and 'hist' in market_data:
                market_returns = market_data['hist']['Close'].pct_change().dropna()
                tech_indicators['beta'] = self.calculate_beta(returns, market_returns)
                tech_indicators['relative_strength'] = self.calculate_relative_strength(
                    returns, market_returns, period=20
                )

        # Gap detection
        gap_type, gap_pct = self.detect_gap(
            ticker_data.get('open', 0),
            ticker_data.get('prev_close', ticker_data.get('close', 0))
        )
        tech_indicators['gap_type'] = gap_type
        tech_indicators['gap_pct'] = gap_pct

        # Calculate relative volume
        avg_volume = ticker_data['hist']['Volume'].mean() if hist is not None else ticker_data.get('volume', 1)
        current_volume = ticker_data.get('volume', avg_volume)
        rel_volume = self.calculate_relative_volume(current_volume, avg_volume)
        ticker_data['relative_volume'] = rel_volume
        ticker_data['avg_volume'] = avg_volume

        # Pivot levels
        pivot_levels = self.calculate_pivot_levels(
            ticker_data['high'],
            ticker_data['low'],
            ticker_data['close']
        )

        # ATR-based stop levels
        atr = tech_indicators.get('atr')
        if atr is not None:
            pivot_levels['ATR_Stop'] = ticker_data['close'] - (2 * atr)
            pivot_levels['ATR_Target'] = ticker_data['close'] + (3 * atr)

        # Setup quality
        setup_quality = self.assess_setup_quality(ticker_data, tech_indicators)

        # Momentum score
        momentum_score = self.assess_momentum_score(tech_indicators)

        # Macro fit
        macro_fit = self.assess_macro_fit(regime_score)

        # Risk/Reward
        risk_reward = self.assess_risk_reward(ticker_data, pivot_levels)

        # Conviction score with breakdown
        conviction, conviction_breakdown = self.conviction_score_breakdown(
            setup_quality, macro_fit, risk_reward, momentum_score
        )

        return {
            'pivot_levels': pivot_levels,
            'technical_indicators': tech_indicators,
            'setup_quality': setup_quality,
            'momentum_score': momentum_score,
            'macro_fit': macro_fit,
            'risk_reward': risk_reward,
            'conviction': conviction,
            'conviction_breakdown': conviction_breakdown,
            'relative_volume': rel_volume,
            'avg_volume': avg_volume,
            'rsi': tech_indicators.get('rsi'),
            'macd': {
                'line': tech_indicators.get('macd'),
                'signal': tech_indicators.get('macd_signal'),
                'histogram': tech_indicators.get('macd_histogram')
            },
            'atr': tech_indicators.get('atr'),
            'relative_strength': tech_indicators.get('relative_strength'),
            'gap_type': tech_indicators.get('gap_type'),
            'gap_pct': tech_indicators.get('gap_pct'),
            'beta': tech_indicators.get('beta'),
            'volatility': tech_indicators.get('volatility_30d'),
            'momentum_5d': tech_indicators.get('momentum_5d'),
            'momentum_20d': tech_indicators.get('momentum_20d')
        }
