from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

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


class Strategy(BaseModel):
    """Strategy response model."""

    id: str
    user_id: str
    name: str
    description: str
    code: str
    parameters: list[StrategyParameter]
    created_at: datetime
    updated_at: datetime


class StrategyList(BaseModel):
    """List of strategies response."""

    strategies: list[Strategy]
    total: int


# Example strategy template
EXAMPLE_STRATEGY = """
class SMAcrossover(Strategy):
    \"\"\"Simple Moving Average Crossover Strategy.\"\"\"

    # Strategy parameters
    fast_period = 10
    slow_period = 20

    def init(self):
        \"\"\"Initialize indicators.\"\"\"
        close = self.data['close']
        self.sma_fast = self.I(self.sma, close, self.fast_period)
        self.sma_slow = self.I(self.sma, close, self.slow_period)

    def next(self):
        \"\"\"Execute on each bar.\"\"\"
        # Buy signal: fast SMA crosses above slow SMA
        if self.crossover(self.sma_fast, self.sma_slow):
            if not self.position:
                self.buy()

        # Sell signal: fast SMA crosses below slow SMA
        elif self.crossover(self.sma_slow, self.sma_fast):
            if self.position:
                self.sell()

    @staticmethod
    def sma(data, period):
        \"\"\"Simple Moving Average.\"\"\"
        return data.rolling(window=period).mean()

    @staticmethod
    def crossover(series1, series2):
        \"\"\"Check if series1 crosses above series2.\"\"\"
        return series1.iloc[-1] > series2.iloc[-1] and series1.iloc[-2] <= series2.iloc[-2]
"""


@router.get("/", response_model=StrategyList)
async def list_strategies(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List all strategies for the current user."""
    # TODO: Implement with actual user auth and database
    return StrategyList(strategies=[], total=0)


@router.post("/", response_model=Strategy, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy: StrategyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new strategy."""
    # TODO: Validate Python code (sandbox)
    # TODO: Save to database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Strategy creation not yet implemented",
    )


@router.get("/templates")
async def get_strategy_templates():
    """Get built-in strategy templates."""
    return {
        "templates": [
            {
                "name": "SMA Crossover",
                "description": "Buy when fast SMA crosses above slow SMA, sell when it crosses below",
                "code": EXAMPLE_STRATEGY,
                "parameters": [
                    {"name": "fast_period", "type": "int", "default": 10, "min": 2, "max": 50},
                    {"name": "slow_period", "type": "int", "default": 20, "min": 10, "max": 200},
                ],
            }
        ]
    }


@router.get("/{strategy_id}", response_model=Strategy)
async def get_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific strategy by ID."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Strategy {strategy_id} not found",
    )


@router.put("/{strategy_id}", response_model=Strategy)
async def update_strategy(
    strategy_id: str,
    strategy: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a strategy."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Strategy {strategy_id} not found",
    )


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a strategy."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Strategy {strategy_id} not found",
    )
