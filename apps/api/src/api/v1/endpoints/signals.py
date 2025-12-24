"""Trading signals and pattern recognition endpoint."""

import random
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class Signal(BaseModel):
    """A trading signal."""
    symbol: str
    direction: str  # "buy", "sell", "neutral"
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reason: str
    indicators: dict[str, Any]
    generated_at: str


class Pattern(BaseModel):
    """A detected chart pattern."""
    symbol: str
    pattern_name: str
    pattern_type: str  # "bullish", "bearish", "neutral"
    reliability: float  # Historical accuracy
    description: str
    detected_at: str


class RiskAssessment(BaseModel):
    """Risk assessment for a symbol."""
    symbol: str
    volatility: str  # "low", "medium", "high"
    volatility_percentile: float
    atr_pips: float
    recommended_sl_pips: float
    recommended_position_size: float
    risk_score: float  # 0-100
    warnings: list[str]


class SentimentData(BaseModel):
    """Market sentiment analysis."""
    symbol: str
    overall_sentiment: str  # "bullish", "bearish", "neutral"
    sentiment_score: float  # -1.0 to 1.0
    retail_sentiment: float
    institutional_bias: str
    news_sentiment: float
    sources: list[str]


# ============================================================================
# Simulated Data Generators
# ============================================================================

# Base prices for simulation
BASE_PRICES = {
    "EURUSD": 1.0850,
    "GBPUSD": 1.2650,
    "USDJPY": 149.50,
    "AUDUSD": 0.6550,
    "USDCAD": 1.3600,
    "USDCHF": 0.8750,
    "NZDUSD": 0.6100,
}


def generate_signal(symbol: str) -> Signal:
    """Generate a simulated trading signal."""
    # Simulate indicator values
    rsi = random.uniform(20, 80)
    macd_histogram = random.uniform(-0.002, 0.002)
    sma_20 = BASE_PRICES.get(symbol, 1.0) * (1 + random.uniform(-0.01, 0.01))
    sma_50 = BASE_PRICES.get(symbol, 1.0) * (1 + random.uniform(-0.02, 0.02))
    current_price = BASE_PRICES.get(symbol, 1.0) * (1 + random.uniform(-0.005, 0.005))

    # Determine signal based on indicators
    signals = []
    reasons = []

    # RSI signal
    if rsi < 30:
        signals.append(1)  # Oversold - buy
        reasons.append(f"RSI oversold ({rsi:.1f})")
    elif rsi > 70:
        signals.append(-1)  # Overbought - sell
        reasons.append(f"RSI overbought ({rsi:.1f})")
    else:
        signals.append(0)

    # MACD signal
    if macd_histogram > 0.0005:
        signals.append(1)
        reasons.append("MACD bullish momentum")
    elif macd_histogram < -0.0005:
        signals.append(-1)
        reasons.append("MACD bearish momentum")
    else:
        signals.append(0)

    # SMA crossover
    if sma_20 > sma_50 and current_price > sma_20:
        signals.append(1)
        reasons.append("Price above rising SMAs")
    elif sma_20 < sma_50 and current_price < sma_20:
        signals.append(-1)
        reasons.append("Price below falling SMAs")
    else:
        signals.append(0)

    # Aggregate signal
    avg_signal = sum(signals) / len(signals)

    if avg_signal > 0.3:
        direction = "buy"
        strength = min(avg_signal, 1.0)
    elif avg_signal < -0.3:
        direction = "sell"
        strength = min(abs(avg_signal), 1.0)
    else:
        direction = "neutral"
        strength = 0.0

    # Confidence based on agreement
    agreement = sum(1 for s in signals if s == round(avg_signal)) / len(signals)
    confidence = agreement * 0.7 + random.uniform(0.1, 0.3)

    return Signal(
        symbol=symbol,
        direction=direction,
        strength=round(strength, 2),
        confidence=round(min(confidence, 0.95), 2),
        reason=" | ".join(reasons) if reasons else "No clear signal",
        indicators={
            "rsi": round(rsi, 1),
            "macd_histogram": round(macd_histogram, 5),
            "sma_20": round(sma_20, 5),
            "sma_50": round(sma_50, 5),
            "current_price": round(current_price, 5),
        },
        generated_at=datetime.utcnow().isoformat(),
    )


def detect_pattern(symbol: str) -> Pattern | None:
    """Detect chart patterns (simulated)."""
    patterns = [
        ("Double Bottom", "bullish", 0.65, "Price formed two lows at similar levels, suggesting potential reversal upward"),
        ("Double Top", "bearish", 0.63, "Price formed two highs at similar levels, suggesting potential reversal downward"),
        ("Head and Shoulders", "bearish", 0.70, "Classic reversal pattern with three peaks, middle being highest"),
        ("Inverse Head and Shoulders", "bullish", 0.68, "Bullish reversal pattern with three troughs"),
        ("Ascending Triangle", "bullish", 0.72, "Higher lows with flat resistance, typically bullish"),
        ("Descending Triangle", "bearish", 0.71, "Lower highs with flat support, typically bearish"),
        ("Bull Flag", "bullish", 0.67, "Consolidation after uptrend, continuation pattern"),
        ("Bear Flag", "bearish", 0.66, "Consolidation after downtrend, continuation pattern"),
        ("Doji", "neutral", 0.45, "Indecision candle, potential reversal or continuation"),
        ("Engulfing Bullish", "bullish", 0.60, "Strong bullish candle engulfing previous bearish candle"),
        ("Engulfing Bearish", "bearish", 0.59, "Strong bearish candle engulfing previous bullish candle"),
    ]

    # 70% chance of detecting a pattern
    if random.random() > 0.7:
        return None

    pattern = random.choice(patterns)
    return Pattern(
        symbol=symbol,
        pattern_name=pattern[0],
        pattern_type=pattern[1],
        reliability=pattern[2],
        description=pattern[3],
        detected_at=datetime.utcnow().isoformat(),
    )


def assess_risk(symbol: str, account_balance: float = 10000) -> RiskAssessment:
    """Assess trading risk for a symbol."""
    # Simulate ATR (Average True Range)
    is_jpy = "JPY" in symbol
    base_atr = random.uniform(0.0005, 0.0015) if not is_jpy else random.uniform(0.5, 1.5)
    atr_pips = base_atr * (10000 if not is_jpy else 100)

    # Volatility assessment
    volatility_percentile = random.uniform(20, 80)
    if volatility_percentile < 30:
        volatility = "low"
    elif volatility_percentile < 70:
        volatility = "medium"
    else:
        volatility = "high"

    # Risk-based recommendations
    recommended_sl_pips = atr_pips * 1.5
    pip_value = 10 if not is_jpy else 1000 / 150  # Approximate for JPY pairs
    risk_amount = account_balance * 0.01  # 1% risk
    recommended_position_size = risk_amount / (recommended_sl_pips * pip_value)

    # Risk score (higher = more risky)
    risk_score = volatility_percentile * 0.5 + (100 - atr_pips * 2) * 0.3 + random.uniform(0, 20)
    risk_score = max(0, min(100, risk_score))

    # Warnings
    warnings = []
    if volatility == "high":
        warnings.append("High volatility - consider reducing position size")
    if atr_pips > 20:
        warnings.append("Wide price swings - use wider stops")
    if datetime.utcnow().weekday() == 4:  # Friday
        warnings.append("End of week - be cautious of weekend gaps")
    if random.random() > 0.7:
        warnings.append("Major economic event upcoming - expect volatility")

    return RiskAssessment(
        symbol=symbol,
        volatility=volatility,
        volatility_percentile=round(volatility_percentile, 1),
        atr_pips=round(atr_pips, 1),
        recommended_sl_pips=round(recommended_sl_pips, 1),
        recommended_position_size=round(recommended_position_size, 2),
        risk_score=round(risk_score, 1),
        warnings=warnings,
    )


def get_sentiment(symbol: str) -> SentimentData:
    """Get market sentiment analysis (simulated)."""
    # Simulate sentiment scores
    retail_sentiment = random.uniform(-0.8, 0.8)
    news_sentiment = random.uniform(-0.5, 0.5)

    # Institutional bias often contrarian to retail
    if retail_sentiment > 0.3:
        institutional_bias = "bearish" if random.random() > 0.4 else "neutral"
    elif retail_sentiment < -0.3:
        institutional_bias = "bullish" if random.random() > 0.4 else "neutral"
    else:
        institutional_bias = random.choice(["bullish", "bearish", "neutral"])

    # Overall sentiment
    combined = retail_sentiment * 0.3 + news_sentiment * 0.4 + (
        0.3 if institutional_bias == "bullish" else -0.3 if institutional_bias == "bearish" else 0
    ) * 0.3

    if combined > 0.2:
        overall = "bullish"
    elif combined < -0.2:
        overall = "bearish"
    else:
        overall = "neutral"

    return SentimentData(
        symbol=symbol,
        overall_sentiment=overall,
        sentiment_score=round(combined, 2),
        retail_sentiment=round(retail_sentiment, 2),
        institutional_bias=institutional_bias,
        news_sentiment=round(news_sentiment, 2),
        sources=["Retail positioning data", "News sentiment analysis", "COT report estimates"],
    )


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/", response_model=list[Signal])
async def get_all_signals() -> list[Signal]:
    """Get trading signals for all symbols."""
    return [generate_signal(symbol) for symbol in BASE_PRICES.keys()]


@router.get("/{symbol}", response_model=Signal)
async def get_signal(symbol: str) -> Signal:
    """Get trading signal for a specific symbol."""
    symbol = symbol.upper()
    if symbol not in BASE_PRICES:
        return Signal(
            symbol=symbol,
            direction="neutral",
            strength=0.0,
            confidence=0.0,
            reason="Unknown symbol",
            indicators={},
            generated_at=datetime.utcnow().isoformat(),
        )
    return generate_signal(symbol)


@router.get("/{symbol}/patterns", response_model=list[Pattern])
async def get_patterns(symbol: str) -> list[Pattern]:
    """Detect chart patterns for a symbol."""
    symbol = symbol.upper()
    patterns = []

    # Generate 0-3 patterns
    for _ in range(random.randint(0, 3)):
        pattern = detect_pattern(symbol)
        if pattern:
            patterns.append(pattern)

    return patterns


@router.get("/{symbol}/risk", response_model=RiskAssessment)
async def get_risk_assessment(symbol: str, balance: float = 10000) -> RiskAssessment:
    """Get risk assessment for a symbol."""
    symbol = symbol.upper()
    return assess_risk(symbol, balance)


@router.get("/{symbol}/sentiment", response_model=SentimentData)
async def get_sentiment_analysis(symbol: str) -> SentimentData:
    """Get sentiment analysis for a symbol."""
    symbol = symbol.upper()
    return get_sentiment(symbol)


@router.get("/{symbol}/analysis")
async def get_full_analysis(symbol: str, balance: float = 10000) -> dict[str, Any]:
    """Get comprehensive analysis for a symbol.

    Includes signals, patterns, risk assessment, and sentiment.
    """
    symbol = symbol.upper()

    signal = generate_signal(symbol)
    patterns = [p for p in [detect_pattern(symbol) for _ in range(3)] if p]
    risk = assess_risk(symbol, balance)
    sentiment = get_sentiment(symbol)

    # Generate summary
    factors = []
    if signal.direction == "buy":
        factors.append(f"Technical indicators suggest BUY ({signal.confidence:.0%} confidence)")
    elif signal.direction == "sell":
        factors.append(f"Technical indicators suggest SELL ({signal.confidence:.0%} confidence)")
    else:
        factors.append("Technical indicators are neutral")

    if patterns:
        bullish = sum(1 for p in patterns if p.pattern_type == "bullish")
        bearish = sum(1 for p in patterns if p.pattern_type == "bearish")
        if bullish > bearish:
            factors.append(f"{bullish} bullish pattern(s) detected")
        elif bearish > bullish:
            factors.append(f"{bearish} bearish pattern(s) detected")

    if sentiment.overall_sentiment != "neutral":
        factors.append(f"Market sentiment is {sentiment.overall_sentiment}")

    if risk.volatility == "high":
        factors.append("High volatility - trade with caution")

    # Overall bias
    buy_score = (
        (1 if signal.direction == "buy" else 0) * signal.confidence +
        (0.3 if sentiment.overall_sentiment == "bullish" else 0) +
        sum(0.2 for p in patterns if p.pattern_type == "bullish")
    )
    sell_score = (
        (1 if signal.direction == "sell" else 0) * signal.confidence +
        (0.3 if sentiment.overall_sentiment == "bearish" else 0) +
        sum(0.2 for p in patterns if p.pattern_type == "bearish")
    )

    if buy_score > sell_score + 0.3:
        overall_bias = "bullish"
    elif sell_score > buy_score + 0.3:
        overall_bias = "bearish"
    else:
        overall_bias = "neutral"

    return {
        "symbol": symbol,
        "overall_bias": overall_bias,
        "summary": factors,
        "signal": signal.model_dump(),
        "patterns": [p.model_dump() for p in patterns],
        "risk": risk.model_dump(),
        "sentiment": sentiment.model_dump(),
        "disclaimer": "This analysis is for educational purposes only. Past performance does not guarantee future results.",
        "generated_at": datetime.utcnow().isoformat(),
    }
