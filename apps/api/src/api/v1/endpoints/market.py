from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter()


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


# Supported currency pairs
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
]


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
    return {"error": f"Currency pair {symbol} not found"}


@router.get("/candles/{symbol}", response_model=CandlesResponse)
async def get_candles(
    symbol: str,
    timeframe: str = Query("1H", regex="^(1M|5M|15M|30M|1H|4H|1D|1W)$"),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(500, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
):
    """
    Get OHLCV candle data for a currency pair.

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
    # TODO: Fetch from database
    return CandlesResponse(
        symbol=symbol.upper(),
        timeframe=timeframe,
        candles=[],
        count=0,
    )
