"""Portfolio API endpoints."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class PortfolioResponse(BaseModel):
    """Portfolio summary response."""
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: Optional[float]  # equity / margin * 100, None if no margin used
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    total_pnl_percent: float


class PortfolioSnapshot(BaseModel):
    """Historical portfolio snapshot."""
    timestamp: str
    balance: float
    equity: float


class PerformanceMetrics(BaseModel):
    """Trading performance metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    average_trade: float
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float


class AllocationItem(BaseModel):
    """Position allocation by symbol."""
    symbol: str
    side: str
    size: float
    margin_used: float
    unrealized_pnl: float
    allocation_percent: float


# Import trading state from trading module
def _get_trading_state():
    from src.api.v1.endpoints.trading import _trading_state
    return _trading_state


@router.get("/", response_model=PortfolioResponse)
async def get_portfolio():
    """Get portfolio summary."""
    state = _get_trading_state()

    equity = state.calculate_equity()
    margin_used = state.calculate_margin_used()
    free_margin = state.calculate_free_margin()

    unrealized_pnl = sum(
        state._calculate_position_pnl(pos)
        for pos in state.positions.values()
    )

    realized_pnl = sum(
        trade["pnl"]
        for trade in state.closed_trades
    )

    total_pnl = unrealized_pnl + realized_pnl
    total_pnl_percent = (total_pnl / state.initial_balance) * 100

    margin_level = None
    if margin_used > 0:
        margin_level = (equity / margin_used) * 100

    return PortfolioResponse(
        balance=state.balance,
        equity=equity,
        margin=margin_used,
        free_margin=free_margin,
        margin_level=margin_level,
        unrealized_pnl=unrealized_pnl,
        realized_pnl=realized_pnl,
        total_pnl=total_pnl,
        total_pnl_percent=round(total_pnl_percent, 2),
    )


@router.get("/history", response_model=list[PortfolioSnapshot])
async def get_portfolio_history(
    days: int = Query(30, ge=1, le=365),
):
    """Get portfolio equity history."""
    state = _get_trading_state()

    # Generate simulated history based on closed trades
    # In production, this would come from stored snapshots
    history = []
    now = datetime.now()

    # Start from initial balance and apply trades chronologically
    running_balance = state.initial_balance

    # Create daily snapshots
    for i in range(days, -1, -1):
        date = now - timedelta(days=i)

        # Apply any trades that occurred on or before this date
        trades_up_to_date = [
            t for t in state.closed_trades
            if datetime.fromisoformat(t["closed_at"]) <= date
        ]

        balance = state.initial_balance + sum(t["pnl"] for t in trades_up_to_date)

        # Add some variation for demo purposes
        import random
        variation = random.uniform(-0.005, 0.005) * balance if i > 0 else 0

        history.append(PortfolioSnapshot(
            timestamp=date.isoformat(),
            balance=round(balance + variation, 2),
            equity=round(balance + variation, 2),  # Simplified for demo
        ))

    return history


@router.get("/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """Get trading performance metrics."""
    state = _get_trading_state()

    trades = state.closed_trades

    if not trades:
        return PerformanceMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            profit_factor=0.0,
            average_win=0.0,
            average_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            average_trade=0.0,
            total_pnl=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
        )

    winning_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]

    total_trades = len(trades)
    win_count = len(winning_trades)
    loss_count = len(losing_trades)
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0

    gross_profit = sum(t["pnl"] for t in winning_trades)
    gross_loss = abs(sum(t["pnl"] for t in losing_trades))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit

    average_win = gross_profit / win_count if win_count > 0 else 0
    average_loss = gross_loss / loss_count if loss_count > 0 else 0

    largest_win = max((t["pnl"] for t in trades), default=0)
    largest_loss = min((t["pnl"] for t in trades), default=0)

    total_pnl = sum(t["pnl"] for t in trades)
    average_trade = total_pnl / total_trades if total_trades > 0 else 0

    # Calculate Sharpe ratio (simplified)
    returns = [t["pnl"] for t in trades]
    if len(returns) > 1:
        import statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        sharpe_ratio = (mean_return / std_return) * (252 ** 0.5) if std_return > 0 else 0
    else:
        sharpe_ratio = 0

    # Calculate max drawdown
    equity_curve = []
    running_equity = state.initial_balance
    peak = running_equity

    for trade in sorted(trades, key=lambda t: t["closed_at"]):
        running_equity += trade["pnl"]
        equity_curve.append(running_equity)
        peak = max(peak, running_equity)

    if equity_curve:
        max_drawdown = min((eq - peak) / peak * 100 for eq, peak in
                          [(eq, max(equity_curve[:i+1])) for i, eq in enumerate(equity_curve)])
    else:
        max_drawdown = 0

    return PerformanceMetrics(
        total_trades=total_trades,
        winning_trades=win_count,
        losing_trades=loss_count,
        win_rate=round(win_rate, 2),
        profit_factor=round(profit_factor, 2),
        average_win=round(average_win, 2),
        average_loss=round(average_loss, 2),
        largest_win=round(largest_win, 2),
        largest_loss=round(largest_loss, 2),
        average_trade=round(average_trade, 2),
        total_pnl=round(total_pnl, 2),
        sharpe_ratio=round(sharpe_ratio, 2),
        max_drawdown=round(abs(max_drawdown), 2),
    )


@router.get("/allocation", response_model=list[AllocationItem])
async def get_allocation():
    """Get position allocation by symbol."""
    state = _get_trading_state()

    total_margin = state.calculate_margin_used()
    if total_margin == 0:
        return []

    allocations = []
    for pos_id, pos in state.positions.items():
        margin_used = state.calculate_margin(pos["symbol"], pos["size"])
        pnl = state._calculate_position_pnl(pos)

        allocations.append(AllocationItem(
            symbol=pos["symbol"],
            side=pos["side"],
            size=pos["size"],
            margin_used=round(margin_used, 2),
            unrealized_pnl=round(pnl, 2),
            allocation_percent=round((margin_used / total_margin) * 100, 2),
        ))

    return sorted(allocations, key=lambda x: x.margin_used, reverse=True)
