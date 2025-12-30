"""Market data endpoints with synthetic data generation."""

from datetime import datetime, timedelta
from typing import Optional
import random

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class CurrencyPair(BaseModel):
    """Currency pair information."""
    symbol: str
    base_currency: str
    quote_currency: str
    pip_value: float
    min_lot_size: float
    max_lot_size: float
    max_leverage: int
    is_active: bool


class Candle(BaseModel):
    """OHLCV candle data."""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandlesResponse(BaseModel):
    """Response containing candle data."""
    symbol: str
    timeframe: str
    candles: list[Candle]
    count: int


# ============================================================================
# Currency Pairs Data
# ============================================================================

CURRENCY_PAIRS = [
    CurrencyPair(
        symbol="EURUSD",
        base_currency="EUR",
        quote_currency="USD",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="GBPUSD",
        base_currency="GBP",
        quote_currency="USD",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="USDJPY",
        base_currency="USD",
        quote_currency="JPY",
        pip_value=0.01,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="USDCHF",
        base_currency="USD",
        quote_currency="CHF",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="AUDUSD",
        base_currency="AUD",
        quote_currency="USD",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="USDCAD",
        base_currency="USD",
        quote_currency="CAD",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="NZDUSD",
        base_currency="NZD",
        quote_currency="USD",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="EURGBP",
        base_currency="EUR",
        quote_currency="GBP",
        pip_value=0.0001,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="EURJPY",
        base_currency="EUR",
        quote_currency="JPY",
        pip_value=0.01,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
    CurrencyPair(
        symbol="GBPJPY",
        base_currency="GBP",
        quote_currency="JPY",
        pip_value=0.01,
        min_lot_size=0.01,
        max_lot_size=100.0,
        max_leverage=100,
        is_active=True,
    ),
]

# Base prices for synthetic data generation
BASE_PRICES = {
    "EURUSD": 1.0850,
    "GBPUSD": 1.2650,
    "USDJPY": 149.50,
    "USDCHF": 0.8750,
    "AUDUSD": 0.6550,
    "USDCAD": 1.3600,
    "NZDUSD": 0.6100,
    "EURGBP": 0.8580,
    "EURJPY": 162.20,
    "GBPJPY": 189.10,
}

# Timeframe in minutes
TIMEFRAME_MINUTES = {
    "1M": 1,
    "5M": 5,
    "15M": 15,
    "30M": 30,
    "1H": 60,
    "4H": 240,
    "1D": 1440,
    "1W": 10080,
}


# ============================================================================
# Synthetic Data Generation
# ============================================================================

def generate_candles(
    symbol: str,
    timeframe: str,
    count: int,
    end_time: Optional[datetime] = None,
) -> list[Candle]:
    """Generate synthetic OHLCV candle data.

    Uses a random walk with mean reversion to create realistic-looking price data.
    """
    if symbol not in BASE_PRICES:
        return []

    base_price = BASE_PRICES[symbol]
    is_jpy = "JPY" in symbol

    # Volatility based on pair type
    volatility = 0.0002 if not is_jpy else 0.02

    # Minutes per candle
    minutes = TIMEFRAME_MINUTES.get(timeframe, 60)

    # Generate from end time backwards
    if end_time is None:
        end_time = datetime.utcnow()

    candles = []
    current_price = base_price
    current_time = end_time

    # Use a seed based on symbol for reproducibility
    random.seed(hash(symbol + timeframe) % 2**32)

    for _ in range(count):
        # Random price movement with slight mean reversion
        drift = (base_price - current_price) * 0.001  # Mean reversion
        change = random.gauss(drift, volatility * base_price)

        open_price = current_price
        close_price = current_price + change

        # Generate high/low
        high_extension = abs(random.gauss(0, volatility * base_price * 0.5))
        low_extension = abs(random.gauss(0, volatility * base_price * 0.5))

        high_price = max(open_price, close_price) + high_extension
        low_price = min(open_price, close_price) - low_extension

        # Generate volume
        base_volume = 1000 * (minutes / 60)  # Scale with timeframe
        volume = max(100, random.gauss(base_volume, base_volume * 0.3))

        candles.append(Candle(
            time=current_time,
            open=round(open_price, 3 if is_jpy else 5),
            high=round(high_price, 3 if is_jpy else 5),
            low=round(low_price, 3 if is_jpy else 5),
            close=round(close_price, 3 if is_jpy else 5),
            volume=round(volume, 0),
        ))

        current_price = close_price
        current_time = current_time - timedelta(minutes=minutes)

    # Reverse to get chronological order
    candles.reverse()

    # Reset random seed
    random.seed()

    return candles


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/pairs", response_model=list[CurrencyPair])
async def get_currency_pairs():
    """Get list of available currency pairs."""
    return CURRENCY_PAIRS


@router.get("/pairs/{symbol}", response_model=CurrencyPair)
async def get_currency_pair(symbol: str):
    """Get details for a specific currency pair."""
    symbol = symbol.upper()
    for pair in CURRENCY_PAIRS:
        if pair.symbol == symbol:
            return pair
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Currency pair {symbol} not found",
    )


@router.get("/candles/{symbol}", response_model=CandlesResponse)
async def get_candles(
    symbol: str,
    timeframe: str = Query("1H", pattern="^(1M|5M|15M|30M|1H|4H|1D|1W)$"),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(500, ge=1, le=5000),
):
    """
    Get OHLCV candle data for a currency pair.

    Generates synthetic data for demonstration purposes.
    In production, this would fetch from a real data source.

    Timeframes:
    - 1M: 1 minute
    - 5M: 5 minutes
    - 15M: 15 minutes
    - 30M: 30 minutes
    - 1H: 1 hour
    - 4H: 4 hours
    - 1D: 1 day
    - 1W: 1 week
    """
    symbol = symbol.upper()

    if symbol not in BASE_PRICES:
        return CandlesResponse(
            symbol=symbol,
            timeframe=timeframe,
            candles=[],
            count=0,
        )

    candles = generate_candles(symbol, timeframe, limit, end)

    # Filter by start time if provided
    if start:
        candles = [c for c in candles if c.time >= start]

    return CandlesResponse(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        count=len(candles),
    )


@router.get("/quotes")
async def get_quotes():
    """Get current quotes for all pairs."""
    quotes = {}
    for symbol, base_price in BASE_PRICES.items():
        # Add some random variation
        variation = random.uniform(-0.001, 0.001)
        price = base_price * (1 + variation)
        spread = price * 0.0001

        is_jpy = "JPY" in symbol
        decimals = 3 if is_jpy else 5

        quotes[symbol] = {
            "bid": round(price - spread / 2, decimals),
            "ask": round(price + spread / 2, decimals),
            "mid": round(price, decimals),
            "spread_pips": round(spread * (10000 if not is_jpy else 100), 1),
        }

    return quotes
