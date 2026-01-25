"""
Backtest API endpoints.

Provides endpoints for running backtests, comparing strategies,
and retrieving results.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.backtest_service import (
    backtest_service,
    generate_sample_data,
    BUILTIN_STRATEGIES,
)
from src.services.strategy_service import strategy_service

router = APIRouter()

# In-memory storage for demo (replace with database in production)
_backtests_store: dict[str, dict] = {}


class BacktestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BacktestCreate(BaseModel):
    """Request body for creating a backtest."""

    strategy_id: str = Field(..., description="Strategy ID (e.g., 'sma-crossover', 'random')")
    symbol: str = Field("EURUSD", pattern="^[A-Z]{6}$")
    timeframe: str = Field("1H", pattern="^(1M|5M|15M|1H|4H|1D)$")
    start_date: str = Field("2023-01-01", description="Start date YYYY-MM-DD")
    end_date: str = Field("2023-12-31", description="End date YYYY-MM-DD")
    initial_balance: float = Field(100000.0, gt=0)
    leverage: int = Field(100, ge=1, le=500)
    parameters: dict[str, Any] = Field(default_factory=dict)


class BacktestTrade(BaseModel):
    id: str
    side: str
    size: float
    entry_price: float
    exit_price: float
    entry_time: str
    exit_time: str
    pnl: float
    pnl_percent: float


class BacktestMetrics(BaseModel):
    total_return: float
    total_return_percent: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float


class EquityPoint(BaseModel):
    timestamp: str
    equity: float
    drawdown: float


class BacktestResponse(BaseModel):
    id: str
    strategy_id: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    initial_balance: float
    final_balance: float
    status: BacktestStatus
    metrics: Optional[BacktestMetrics] = None
    trades: list[BacktestTrade] = []
    equity_curve: list[EquityPoint] = []
    created_at: str
    execution_time_ms: int = 0
    error_message: Optional[str] = None


class StrategyInfo(BaseModel):
    id: str
    name: str
    description: str
    parameters: list[dict]


class ComparisonResult(BaseModel):
    strategy_id: str
    strategy_name: str
    final_balance: float
    total_return_percent: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    error: Optional[str] = None


class ComparisonResponse(BaseModel):
    symbol: str
    timeframe: str
    period: str
    initial_balance: float
    results: list[ComparisonResult]
    conclusion: str


@router.get("/strategies", response_model=list[StrategyInfo])
async def list_strategies():
    """
    List available strategies (built-in + custom).

    Includes the Random and Buy-and-Hold strategies for comparison.
    """
    # Get built-in strategies
    builtin_data = backtest_service.get_available_strategies()
    strategies = [StrategyInfo(**s) for s in builtin_data]
    
    # Add custom user strategies
    custom_strategies, _ = strategy_service.list_strategies(limit=100)
    for s in custom_strategies:
        strategies.append(StrategyInfo(
            id=s["id"],
            name=s["name"],
            description=s["description"] or "User-defined strategy",
            parameters=s["parameters"]
        ))
        
    return strategies


@router.post("/", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Run a backtest with specified strategy and parameters.

    Returns full results including trades, equity curve, and metrics.
    """
    custom_code = None
    
    # Validate strategy exists (either built-in or custom)
    if request.strategy_id not in BUILTIN_STRATEGIES:
        # Check if it's a custom strategy
        custom_strategy = strategy_service.get_strategy(request.strategy_id)
        if not custom_strategy:
            available = list(BUILTIN_STRATEGIES.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown strategy: {request.strategy_id}. Available built-ins: {available}",
            )
        custom_code = custom_strategy["code"]

    # Parse and validate dates
    try:
        start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(request.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )

    if start_dt >= end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date",
        )

    # Generate sample data (in production, load from database)
    data = generate_sample_data(
        symbol=request.symbol,
        start_date=request.start_date,
        end_date=request.end_date,
        timeframe=request.timeframe,
    )

    if len(data) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient data for backtest. Need at least 50 bars.",
        )

    # Run backtest
    try:
        result = backtest_service.run_backtest(
            strategy_id=request.strategy_id,
            data=data,
            symbol=request.symbol,
            timeframe=request.timeframe,
            initial_balance=request.initial_balance,
            leverage=request.leverage,
            parameters=request.parameters or None,
            custom_code=custom_code,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest execution failed: {str(e)}",
        )

    # Build response
    backtest_id = str(uuid.uuid4())

    metrics = None
    if result.metrics:
        metrics = BacktestMetrics(
            total_return=result.final_balance - result.initial_balance,
            total_return_percent=result.metrics.get("total_return_percent", 0),
            max_drawdown=result.metrics.get("max_drawdown", 0),
            sharpe_ratio=result.metrics.get("sharpe_ratio", 0),
            sortino_ratio=result.metrics.get("sortino_ratio", 0),
            win_rate=result.metrics.get("win_rate", 0),
            profit_factor=result.metrics.get("profit_factor", 0),
            total_trades=result.metrics.get("total_trades", 0),
            winning_trades=result.metrics.get("winning_trades", 0),
            losing_trades=result.metrics.get("losing_trades", 0),
            average_win=result.metrics.get("average_win", 0),
            average_loss=result.metrics.get("average_loss", 0),
            largest_win=result.metrics.get("largest_win", 0),
            largest_loss=result.metrics.get("largest_loss", 0),
        )

    trades = [
        BacktestTrade(
            id=str(uuid.uuid4()),
            side=t.side,
            size=t.size,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            entry_time=str(t.entry_time),
            exit_time=str(t.exit_time),
            pnl=t.pnl,
            pnl_percent=t.pnl_percent,
        )
        for t in result.trades
    ]

    # Sample equity curve to reduce response size
    sample_rate = max(1, len(result.equity_curve) // 500)
    equity_curve = [
        EquityPoint(
            timestamp=e["timestamp"],
            equity=e["equity"],
            drawdown=e["drawdown"],
        )
        for i, e in enumerate(result.equity_curve)
        if i % sample_rate == 0
    ]

    response = BacktestResponse(
        id=backtest_id,
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        timeframe=request.timeframe,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_balance=request.initial_balance,
        final_balance=result.final_balance,
        status=BacktestStatus.COMPLETED,
        metrics=metrics,
        trades=trades,
        equity_curve=equity_curve,
        created_at=datetime.now().isoformat(),
        execution_time_ms=result.execution_time_ms,
    )

    _backtests_store[backtest_id] = response.model_dump()
    return response


@router.post("/compare", response_model=ComparisonResponse)
async def compare_strategies(
    request: BacktestCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Compare your strategy against Random and Buy-and-Hold benchmarks.

    This is the reality check. If your strategy can't beat random chance,
    it's not actually working.
    """
    # Generate sample data
    data = generate_sample_data(
        symbol=request.symbol,
        start_date=request.start_date,
        end_date=request.end_date,
        timeframe=request.timeframe,
    )

    # Run comparison
    results = backtest_service.run_comparison(
        strategy_ids=[request.strategy_id],
        data=data,
        symbol=request.symbol,
        timeframe=request.timeframe,
        initial_balance=request.initial_balance,
        leverage=request.leverage,
    )

    # Build response
    comparison = []
    for strategy_id, result in results.items():
        comparison.append(ComparisonResult(
            strategy_id=strategy_id,
            strategy_name=strategy_id.replace("-", " ").title(),
            final_balance=result.final_balance,
            total_return_percent=result.metrics.get("total_return_percent", 0) if result.metrics else 0,
            sharpe_ratio=result.metrics.get("sharpe_ratio", 0) if result.metrics else 0,
            max_drawdown=result.metrics.get("max_drawdown", 0) if result.metrics else 0,
            win_rate=result.metrics.get("win_rate", 0) if result.metrics else 0,
            total_trades=result.metrics.get("total_trades", 0) if result.metrics else 0,
            error=result.error_message,
        ))

    comparison.sort(key=lambda x: x.total_return_percent, reverse=True)

    return ComparisonResponse(
        symbol=request.symbol,
        timeframe=request.timeframe,
        period=f"{request.start_date} to {request.end_date}",
        initial_balance=request.initial_balance,
        results=comparison,
        conclusion=_generate_conclusion(comparison, request.strategy_id),
    )


def _generate_conclusion(comparison: list[ComparisonResult], user_strategy_id: str) -> str:
    """Generate educational conclusion based on comparison."""
    user = next((r for r in comparison if r.strategy_id == user_strategy_id), None)
    random_r = next((r for r in comparison if r.strategy_id == "random"), None)
    buyhold = next((r for r in comparison if r.strategy_id == "buy-and-hold"), None)

    if not user:
        return "No user strategy to evaluate."

    parts = []

    if random_r:
        diff = user.total_return_percent - random_r.total_return_percent
        if diff > 0:
            parts.append(f"Your strategy beat random by {diff:.2f}%.")
        else:
            parts.append(
                f"Your strategy LOST to random chance by {abs(diff):.2f}%. "
                "A coin flip would have performed better."
            )

    if buyhold:
        diff = user.total_return_percent - buyhold.total_return_percent
        if diff > 0:
            parts.append(f"It also beat buy-and-hold by {diff:.2f}%.")
        else:
            parts.append(
                f"It LOST to buy-and-hold by {abs(diff):.2f}%. "
                "Simply holding would have been more profitable."
            )

    if user.total_return_percent < 0:
        parts.append("Overall, this strategy lost money.")

    return " ".join(parts) if parts else "Results inconclusive."


@router.get("/")
async def list_backtests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List stored backtests."""
    backtests = list(_backtests_store.values())
    return backtests[skip:skip + limit]


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get backtest by ID."""
    if backtest_id not in _backtests_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest {backtest_id} not found",
        )
    return _backtests_store[backtest_id]


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(
    backtest_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a backtest."""
    if backtest_id in _backtests_store:
        del _backtests_store[backtest_id]
