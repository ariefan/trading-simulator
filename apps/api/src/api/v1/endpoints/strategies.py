"""Strategy CRUD API endpoints."""
from datetime import datetime
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter()

# In-memory storage for demo (replace with database in production)
_strategies_store: dict[str, dict] = {}


class StrategyParameter(BaseModel):
    """Strategy parameter definition."""

    name: str
    type: str  # int, float, bool, str
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    description: str = ""


class StrategyCreate(BaseModel):
    """Request body for creating a strategy."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    code: str = Field(..., min_length=10)
    parameters: list[StrategyParameter] = []


class StrategyUpdate(BaseModel):
    """Request body for updating a strategy."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    code: Optional[str] = Field(None, min_length=10)
    parameters: Optional[list[StrategyParameter]] = None


class StrategyResponse(BaseModel):
    """Strategy response model."""

    id: str
    name: str
    description: str
    code: str
    parameters: list[StrategyParameter]
    created_at: str
    updated_at: str


class StrategyList(BaseModel):
    """List of strategies response."""

    strategies: list[StrategyResponse]
    total: int


# Strategy templates
STRATEGY_TEMPLATES = [
    {
        "name": "SMA Crossover",
        "description": "Buy when fast SMA crosses above slow SMA, sell when it crosses below",
        "code": '''class SMACrossover(Strategy):
    """Simple Moving Average Crossover Strategy."""

    # Strategy parameters
    fast_period = 10
    slow_period = 20

    def init(self):
        """Initialize indicators."""
        close = self.data['close']
        self.sma_fast = self.I(SMA, close, self.fast_period)
        self.sma_slow = self.I(SMA, close, self.slow_period)

    def next(self):
        """Execute on each bar."""
        # Buy signal: fast SMA crosses above slow SMA
        if crossover(self.sma_fast, self.sma_slow):
            if not self.position:
                self.buy()

        # Sell signal: fast SMA crosses below slow SMA
        elif crossover(self.sma_slow, self.sma_fast):
            if self.position:
                self.sell()
''',
        "parameters": [
            {"name": "fast_period", "type": "int", "default": 10, "min": 2, "max": 50, "description": "Fast SMA period"},
            {"name": "slow_period", "type": "int", "default": 20, "min": 10, "max": 200, "description": "Slow SMA period"},
        ],
    },
    {
        "name": "RSI Overbought/Oversold",
        "description": "Buy when RSI is oversold (<30), sell when overbought (>70)",
        "code": '''class RSIStrategy(Strategy):
    """RSI Overbought/Oversold Strategy."""

    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        """Initialize indicators."""
        self.rsi = self.I(RSI, self.data['close'], self.rsi_period)

    def next(self):
        """Execute on each bar."""
        if self.rsi[-1] < self.oversold:
            if not self.position:
                self.buy()
        elif self.rsi[-1] > self.overbought:
            if self.position:
                self.sell()
''',
        "parameters": [
            {"name": "rsi_period", "type": "int", "default": 14, "min": 5, "max": 50, "description": "RSI period"},
            {"name": "oversold", "type": "int", "default": 30, "min": 10, "max": 40, "description": "Oversold level"},
            {"name": "overbought", "type": "int", "default": 70, "min": 60, "max": 90, "description": "Overbought level"},
        ],
    },
    {
        "name": "MACD Signal Line",
        "description": "Buy when MACD crosses above signal line, sell when it crosses below",
        "code": '''class MACDStrategy(Strategy):
    """MACD Signal Line Crossover Strategy."""

    fast_period = 12
    slow_period = 26
    signal_period = 9

    def init(self):
        """Initialize indicators."""
        macd_result = self.I(MACD, self.data['close'], self.fast_period, self.slow_period, self.signal_period)
        self.macd_line = macd_result['macd']
        self.signal_line = macd_result['signal']

    def next(self):
        """Execute on each bar."""
        if crossover(self.macd_line, self.signal_line):
            if not self.position:
                self.buy()
        elif crossover(self.signal_line, self.macd_line):
            if self.position:
                self.sell()
''',
        "parameters": [
            {"name": "fast_period", "type": "int", "default": 12, "min": 5, "max": 20, "description": "Fast EMA period"},
            {"name": "slow_period", "type": "int", "default": 26, "min": 15, "max": 50, "description": "Slow EMA period"},
            {"name": "signal_period", "type": "int", "default": 9, "min": 5, "max": 15, "description": "Signal line period"},
        ],
    },
    {
        "name": "Bollinger Bands Breakout",
        "description": "Buy when price breaks above upper band, sell when it breaks below lower band",
        "code": '''class BollingerBreakout(Strategy):
    """Bollinger Bands Breakout Strategy."""

    period = 20
    std_dev = 2.0

    def init(self):
        """Initialize indicators."""
        bb = self.I(BOLLINGER_BANDS, self.data['close'], self.period, self.std_dev)
        self.upper = bb['upper']
        self.lower = bb['lower']
        self.middle = bb['middle']

    def next(self):
        """Execute on each bar."""
        close = self.data['close'].iloc[-1]

        # Buy when price breaks above upper band
        if close > self.upper[-1]:
            if not self.position:
                self.buy()
        # Sell when price breaks below lower band
        elif close < self.lower[-1]:
            if self.position:
                self.sell()
''',
        "parameters": [
            {"name": "period", "type": "int", "default": 20, "min": 10, "max": 50, "description": "Bollinger period"},
            {"name": "std_dev", "type": "float", "default": 2.0, "min": 1.0, "max": 3.0, "description": "Standard deviations"},
        ],
    },
]


def validate_strategy_code(code: str) -> tuple[bool, str]:
    """
    Basic validation of strategy code.
    Returns (is_valid, error_message).
    """
    # Check for dangerous patterns
    dangerous_patterns = [
        "import os",
        "import sys",
        "import subprocess",
        "eval(",
        "exec(",
        "__import__",
        "open(",
        "file(",
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            return False, f"Forbidden pattern detected: {pattern}"

    # Check for required class structure
    if "class " not in code:
        return False, "Strategy must define a class"

    if "def next(" not in code:
        return False, "Strategy must implement next() method"

    return True, ""


@router.get("/", response_model=StrategyList)
async def list_strategies(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List all strategies."""
    strategies = list(_strategies_store.values())
    strategies.sort(key=lambda x: x["created_at"], reverse=True)

    return StrategyList(
        strategies=[StrategyResponse(**s) for s in strategies[skip:skip + limit]],
        total=len(strategies),
    )


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy: StrategyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new strategy."""
    # Validate code
    is_valid, error = validate_strategy_code(strategy.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid strategy code: {error}",
        )

    # Create strategy
    now = datetime.now().isoformat()
    strategy_id = str(uuid.uuid4())

    strategy_data = {
        "id": strategy_id,
        "name": strategy.name,
        "description": strategy.description,
        "code": strategy.code,
        "parameters": [p.model_dump() for p in strategy.parameters],
        "created_at": now,
        "updated_at": now,
    }

    _strategies_store[strategy_id] = strategy_data

    return StrategyResponse(**strategy_data)


@router.get("/templates")
async def get_strategy_templates():
    """Get built-in strategy templates."""
    return {"templates": STRATEGY_TEMPLATES}


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific strategy by ID."""
    if strategy_id not in _strategies_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )

    return StrategyResponse(**_strategies_store[strategy_id])


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    strategy: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a strategy."""
    if strategy_id not in _strategies_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )

    existing = _strategies_store[strategy_id]

    # Validate code if provided
    if strategy.code is not None:
        is_valid, error = validate_strategy_code(strategy.code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid strategy code: {error}",
            )
        existing["code"] = strategy.code

    if strategy.name is not None:
        existing["name"] = strategy.name
    if strategy.description is not None:
        existing["description"] = strategy.description
    if strategy.parameters is not None:
        existing["parameters"] = [p.model_dump() for p in strategy.parameters]

    existing["updated_at"] = datetime.now().isoformat()

    return StrategyResponse(**existing)


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a strategy."""
    if strategy_id not in _strategies_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )

    del _strategies_store[strategy_id]
