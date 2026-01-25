"""Strategy CRUD API endpoints."""
from datetime import datetime
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.strategy_service import strategy_service

router = APIRouter()


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

# Built-in strategy templates
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
            {"name": "fast_period", "type": "int", "default": 10, "description": "Fast SMA period"},
            {"name": "slow_period", "type": "int", "default": 20, "description": "Slow SMA period"},
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
            {"name": "rsi_period", "type": "int", "default": 14, "description": "RSI period"},
            {"name": "oversold", "type": "int", "default": 30, "description": "Oversold level"},
            {"name": "overbought", "type": "int", "default": 70, "description": "Overbought level"},
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
            {"name": "fast_period", "type": "int", "default": 12, "description": "Fast EMA period"},
            {"name": "slow_period", "type": "int", "default": 26, "description": "Slow EMA period"},
            {"name": "signal_period", "type": "int", "default": 9, "description": "Signal line period"},
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
    """List all user-created strategies."""
    strategies, total = strategy_service.list_strategies(skip, limit)
    return StrategyList(
        strategies=[StrategyResponse(**s) for s in strategies],
        total=total,
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

    # Create strategy via service
    strategy_data = strategy_service.create_strategy(
        name=strategy.name,
        description=strategy.description,
        code=strategy.code,
        parameters=[p.model_dump() for p in strategy.parameters]
    )

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
    strategy_data = strategy_service.get_strategy(strategy_id)
    if not strategy_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )

    return StrategyResponse(**strategy_data)


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy_endpoint(
    strategy_id: str,
    strategy: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a strategy."""
    # Validate code if provided
    if strategy.code is not None:
        is_valid, error = validate_strategy_code(strategy.code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid strategy code: {error}",
            )

    updates = {}
    if strategy.name is not None:
        updates["name"] = strategy.name
    if strategy.description is not None:
        updates["description"] = strategy.description
    if strategy.code is not None:
        updates["code"] = strategy.code
    if strategy.parameters is not None:
        updates["parameters"] = [p.model_dump() for p in strategy.parameters]

    updated = strategy_service.update_strategy(strategy_id, updates)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )

    return StrategyResponse(**updated)


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy_endpoint(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a strategy."""
    if not strategy_service.delete_strategy(strategy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )
