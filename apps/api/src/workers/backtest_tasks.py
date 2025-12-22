"""Celery tasks for backtesting."""
import uuid
from datetime import datetime

from celery import shared_task

from src.workers.celery_app import celery_app
from src.services.backtest_service import (
    backtest_service,
    generate_sample_data,
    BUILTIN_STRATEGIES,
)


@celery_app.task(bind=True, name="run_backtest")
def run_backtest(
    self,
    backtest_id: str,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    initial_balance: float,
    leverage: int,
    parameters: dict,
):
    """
    Execute a backtest in the background.

    This task:
    1. Validates the strategy exists
    2. Generates or fetches historical data
    3. Runs the backtest engine
    4. Returns results with progress updates
    """
    try:
        # Update status to running
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0.0,
                "current_date": start_date,
                "trades_executed": 0,
                "message": "Starting backtest...",
            },
        )

        # Validate strategy exists
        if strategy_id not in BUILTIN_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_id}")

        # Update progress - loading data
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0.1,
                "current_date": start_date,
                "trades_executed": 0,
                "message": "Loading historical data...",
            },
        )

        # Generate sample data (in production, load from database)
        data = generate_sample_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe,
        )

        if len(data) < 50:
            raise ValueError("Insufficient data for backtest. Need at least 50 bars.")

        # Update progress - running backtest
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0.2,
                "current_date": start_date,
                "trades_executed": 0,
                "message": f"Running {strategy_id} strategy...",
            },
        )

        # Run the actual backtest
        result = backtest_service.run_backtest(
            strategy_id=strategy_id,
            data=data,
            symbol=symbol,
            timeframe=timeframe,
            initial_balance=initial_balance,
            leverage=leverage,
            parameters=parameters or None,
        )

        # Update progress - completed
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 1.0,
                "current_date": end_date,
                "trades_executed": len(result.trades),
                "message": "Backtest completed!",
            },
        )

        # Build response
        metrics = None
        if result.metrics:
            metrics = {
                "total_return": result.final_balance - result.initial_balance,
                "total_return_percent": result.metrics.get("total_return_percent", 0),
                "max_drawdown": result.metrics.get("max_drawdown", 0),
                "sharpe_ratio": result.metrics.get("sharpe_ratio", 0),
                "sortino_ratio": result.metrics.get("sortino_ratio", 0),
                "win_rate": result.metrics.get("win_rate", 0),
                "profit_factor": result.metrics.get("profit_factor", 0),
                "total_trades": result.metrics.get("total_trades", 0),
                "winning_trades": result.metrics.get("winning_trades", 0),
                "losing_trades": result.metrics.get("losing_trades", 0),
                "average_win": result.metrics.get("average_win", 0),
                "average_loss": result.metrics.get("average_loss", 0),
                "largest_win": result.metrics.get("largest_win", 0),
                "largest_loss": result.metrics.get("largest_loss", 0),
            }

        trades = [
            {
                "id": str(uuid.uuid4()),
                "side": t.side,
                "size": t.size,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "entry_time": str(t.entry_time),
                "exit_time": str(t.exit_time),
                "pnl": t.pnl,
                "pnl_percent": t.pnl_percent,
            }
            for t in result.trades
        ]

        # Sample equity curve to reduce response size
        sample_rate = max(1, len(result.equity_curve) // 500)
        equity_curve = [
            {
                "timestamp": e["timestamp"],
                "equity": e["equity"],
                "drawdown": e["drawdown"],
            }
            for i, e in enumerate(result.equity_curve)
            if i % sample_rate == 0
        ]

        return {
            "status": "completed",
            "backtest_id": backtest_id,
            "strategy_id": strategy_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "initial_balance": initial_balance,
            "final_balance": result.final_balance,
            "metrics": metrics,
            "trades": trades,
            "equity_curve": equity_curve,
            "execution_time_ms": result.execution_time_ms,
        }

    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "message": f"Backtest failed: {str(e)}",
            },
        )
        raise


@celery_app.task(bind=True, name="run_comparison")
def run_comparison(
    self,
    comparison_id: str,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    initial_balance: float,
    leverage: int,
):
    """
    Run a comparison backtest against Random and Buy-and-Hold benchmarks.
    """
    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0.0,
                "message": "Starting comparison...",
            },
        )

        # Generate sample data
        data = generate_sample_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe,
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0.2,
                "message": "Running comparison backtests...",
            },
        )

        # Run comparison
        results = backtest_service.run_comparison(
            strategy_ids=[strategy_id],
            data=data,
            symbol=symbol,
            timeframe=timeframe,
            initial_balance=initial_balance,
            leverage=leverage,
        )

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 1.0,
                "message": "Comparison completed!",
            },
        )

        # Build response
        comparison = []
        for sid, result in results.items():
            comparison.append({
                "strategy_id": sid,
                "strategy_name": sid.replace("-", " ").title(),
                "final_balance": result.final_balance,
                "total_return_percent": result.metrics.get("total_return_percent", 0) if result.metrics else 0,
                "sharpe_ratio": result.metrics.get("sharpe_ratio", 0) if result.metrics else 0,
                "max_drawdown": result.metrics.get("max_drawdown", 0) if result.metrics else 0,
                "win_rate": result.metrics.get("win_rate", 0) if result.metrics else 0,
                "total_trades": result.metrics.get("total_trades", 0) if result.metrics else 0,
                "error": result.error_message,
            })

        comparison.sort(key=lambda x: x["total_return_percent"], reverse=True)

        return {
            "status": "completed",
            "comparison_id": comparison_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "period": f"{start_date} to {end_date}",
            "initial_balance": initial_balance,
            "results": comparison,
        }

    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "message": f"Comparison failed: {str(e)}",
            },
        )
        raise
