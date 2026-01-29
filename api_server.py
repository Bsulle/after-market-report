"""
Flask API Server for MyFolio Mobile App

This provides REST endpoints for the mobile app to consume
the analysis from the Python backend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

from config import WATCHLIST, VIX_THRESHOLD, TEN_YEAR_YIELD_THRESHOLD
from data_gatherer import fetch_ticker_data, fetch_macro_data
from calculator import Calculator

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

calc = Calculator()


def get_conviction_emoji(score: float) -> str:
    """Return emoji based on conviction score."""
    if score >= 4.5:
        return "🔥"
    elif score >= 3.5:
        return "✅"
    elif score >= 2.5:
        return "⚠️"
    return "🚫"


def determine_market_regime(macro_data: dict) -> dict:
    """Determine market regime from macro data."""
    vix = macro_data.get("vix", {}).get("value", 15)
    yield_10y = macro_data.get("yield10y", {}).get("value", 4.0)

    if vix < VIX_THRESHOLD and yield_10y < TEN_YEAR_YIELD_THRESHOLD:
        regime = "Risk-On"
        score = 7.5 + (VIX_THRESHOLD - vix) / 10
    elif vix > VIX_THRESHOLD * 1.5:
        regime = "Risk-Off"
        score = 3.0 - (vix - VIX_THRESHOLD) / 20
    else:
        regime = "Transitional"
        score = 5.0

    return {
        "regime": regime,
        "score": min(10, max(1, round(score, 1))),
        "details": f"VIX at {vix:.1f}, 10Y at {yield_10y:.2f}%",
    }


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/market/regime", methods=["GET"])
def get_market_regime():
    """Get current market regime assessment."""
    try:
        macro = fetch_macro_data()
        regime_data = determine_market_regime(macro)
        return jsonify(regime_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/macro", methods=["GET"])
def get_macro_data():
    """Get macro market data."""
    try:
        macro = fetch_macro_data()
        return jsonify(macro)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ticker/<ticker>", methods=["GET"])
def get_ticker_analysis(ticker: str):
    """Get analysis for a specific ticker."""
    try:
        ticker = ticker.upper()
        data = fetch_ticker_data([ticker])

        if ticker not in data:
            return jsonify({"error": f"Ticker {ticker} not found"}), 404

        ticker_data = data[ticker]

        # Calculate pivot levels if we have OHLC data
        pivot_levels = None
        if all(k in ticker_data for k in ["high", "low", "close"]):
            pivot_levels = calc.calculate_pivot_levels(
                ticker_data["high"], ticker_data["low"], ticker_data["close"]
            )

        # Mock conviction score (in production, this would be calculated)
        conviction_score = 3.5  # Placeholder

        return jsonify(
            {
                "symbol": ticker,
                "convictionScore": conviction_score,
                "convictionEmoji": get_conviction_emoji(conviction_score),
                "pivotLevels": pivot_levels,
                "data": ticker_data,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/coach/summary", methods=["POST"])
def get_coach_summary():
    """Generate coach summary for given tickers."""
    try:
        body = request.get_json()
        tickers = body.get("tickers", WATCHLIST)

        # Fetch data
        ticker_data = fetch_ticker_data(tickers)
        macro = fetch_macro_data()
        regime = determine_market_regime(macro)

        # Generate insights based on regime
        insights = []
        if regime["regime"] == "Risk-On":
            insights = [
                "VIX below 20 signals low fear environment",
                "Growth stocks favored in current regime",
                "Consider adding to high-conviction positions",
            ]
        elif regime["regime"] == "Risk-Off":
            insights = [
                "Elevated VIX suggests increased hedging",
                "Quality over beta - favor profitable names",
                "Reduce position sizes and tighten stops",
            ]
        else:
            insights = [
                "Mixed signals - wait for confirmation",
                "Sector rotation in progress",
                "Focus on individual setups over market direction",
            ]

        # Build top picks (mock data - would be calculated from analysis)
        top_picks = []
        for ticker in tickers[:3]:
            if ticker in ticker_data:
                score = 4.0  # Placeholder
                top_picks.append(
                    {
                        "symbol": ticker,
                        "convictionScore": score,
                        "convictionEmoji": get_conviction_emoji(score),
                        "thesis": f"Technical setup forming on {ticker}",
                        "riskLevel": "MEDIUM",
                    }
                )

        return jsonify(
            {
                "marketRegime": regime["regime"],
                "regimeScore": regime["score"],
                "headline": f"{regime['regime']} environment - {regime['details']}",
                "keyInsights": insights,
                "topPicks": top_picks,
                "avoidList": [],
                "actionItems": [
                    "Review position sizing based on current regime",
                    "Update stop losses for existing positions",
                ],
                "generatedAt": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/report/generate", methods=["POST"])
def generate_report():
    """Generate full after-market report (Pro feature)."""
    try:
        body = request.get_json()
        tickers = body.get("tickers", WATCHLIST)
        date = body.get("date", datetime.now().strftime("%Y-%m-%d"))

        # This would trigger the full report generation
        # For now, return a mock response
        return jsonify(
            {
                "status": "generated",
                "reportUrl": f"/reports/After_Market_Report_{date}.md",
                "generatedAt": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
