"""
Performance metrics calculator for backtesting.

Implements key trading performance metrics including:
- Return metrics (total, annualized)
- Risk metrics (volatility, max drawdown)
- Risk-adjusted returns (Sharpe, Sortino, Calmar)
- Trade statistics (win rate, profit factor)
"""
from typing import Any

import numpy as np
import pandas as pd

from src.core.backtesting.strategy_base import Trade


class PerformanceMetrics:
    """Calculate trading performance metrics."""

    TRADING_DAYS_PER_YEAR = 252
    RISK_FREE_RATE = 0.02  # 2% annual

    def calculate_all(
        self,
        trades: list[Trade],
        equity_curve: list[dict],
        initial_balance: float,
    ) -> dict[str, Any]:
        """Calculate all performance metrics."""
        if not trades:
            return self._empty_metrics()

        # Convert to DataFrame for easier calculation
        trades_df = pd.DataFrame(
            [
                {
                    "side": t.side,
                    "size": t.size,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl": t.pnl,
                    "pnl_percent": t.pnl_percent,
                    "commission": t.commission,
                    "bars_held": t.bars_held,
                }
                for t in trades
            ]
        )

        equity_df = pd.DataFrame(equity_curve)
        returns = equity_df["equity"].pct_change().dropna()

        metrics = {
            # Return metrics
            "total_return": self._total_return(equity_df, initial_balance),
            "total_return_percent": self._total_return_percent(equity_df, initial_balance),
            "annualized_return": self._annualized_return(returns),
            # Risk metrics
            "volatility": self._volatility(returns),
            "max_drawdown": self._max_drawdown(equity_df),
            "max_drawdown_duration_days": self._max_drawdown_duration(equity_df),
            # Risk-adjusted returns
            "sharpe_ratio": self._sharpe_ratio(returns),
            "sortino_ratio": self._sortino_ratio(returns),
            "calmar_ratio": self._calmar_ratio(returns, equity_df),
            # Trade statistics
            "total_trades": len(trades_df),
            "winning_trades": self._winning_trades(trades_df),
            "losing_trades": self._losing_trades(trades_df),
            "win_rate": self._win_rate(trades_df),
            "profit_factor": self._profit_factor(trades_df),
            "average_win": self._average_win(trades_df),
            "average_loss": self._average_loss(trades_df),
            "largest_win": self._largest_win(trades_df),
            "largest_loss": self._largest_loss(trades_df),
            "average_trade": self._average_trade(trades_df),
            "average_bars_held": self._average_bars_held(trades_df),
            # Exposure
            "exposure_time": self._exposure_time(equity_df),
        }

        return metrics

    def _total_return(self, equity_df: pd.DataFrame, initial_balance: float) -> float:
        """Absolute total return."""
        final_equity = equity_df["equity"].iloc[-1]
        return float(final_equity - initial_balance)

    def _total_return_percent(self, equity_df: pd.DataFrame, initial_balance: float) -> float:
        """Total return as percentage."""
        final_equity = equity_df["equity"].iloc[-1]
        return ((final_equity - initial_balance) / initial_balance) * 100

    def _annualized_return(self, returns: pd.Series) -> float:
        """Annualized return percentage."""
        if len(returns) < 2:
            return 0.0

        total_return = (1 + returns).prod() - 1
        days = len(returns)

        if days < self.TRADING_DAYS_PER_YEAR:
            # Less than a year of data
            annualized = total_return * (self.TRADING_DAYS_PER_YEAR / days)
        else:
            annualized = ((1 + total_return) ** (self.TRADING_DAYS_PER_YEAR / days)) - 1

        return annualized * 100

    def _volatility(self, returns: pd.Series) -> float:
        """Annualized volatility (standard deviation of returns)."""
        if len(returns) < 2:
            return 0.0
        return returns.std() * np.sqrt(self.TRADING_DAYS_PER_YEAR) * 100

    def _max_drawdown(self, equity_df: pd.DataFrame) -> float:
        """Maximum drawdown percentage."""
        equity = equity_df["equity"]
        peak = equity.expanding(min_periods=1).max()
        drawdown = (equity - peak) / peak
        return abs(drawdown.min()) * 100

    def _max_drawdown_duration(self, equity_df: pd.DataFrame) -> int:
        """Duration of longest drawdown in bars."""
        equity = equity_df["equity"]
        peak = equity.expanding(min_periods=1).max()
        in_drawdown = equity < peak

        if not in_drawdown.any():
            return 0

        # Find consecutive drawdown periods
        drawdown_groups = (in_drawdown != in_drawdown.shift()).cumsum()
        drawdown_lengths = in_drawdown.groupby(drawdown_groups).sum()

        return int(drawdown_lengths.max())

    def _sharpe_ratio(self, returns: pd.Series) -> float:
        """
        Sharpe Ratio.

        Formula: (mean_return - risk_free_rate) / std_return * sqrt(252)
        """
        if len(returns) < 2 or returns.std() == 0:
            return 0.0

        daily_rf = self.RISK_FREE_RATE / self.TRADING_DAYS_PER_YEAR
        excess_returns = returns.mean() - daily_rf
        sharpe = (excess_returns / returns.std()) * np.sqrt(self.TRADING_DAYS_PER_YEAR)

        return float(sharpe)

    def _sortino_ratio(self, returns: pd.Series) -> float:
        """
        Sortino Ratio.

        Like Sharpe but only penalizes downside volatility.
        """
        if len(returns) < 2:
            return 0.0

        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float("inf") if returns.mean() > 0 else 0.0

        daily_rf = self.RISK_FREE_RATE / self.TRADING_DAYS_PER_YEAR
        excess_returns = returns.mean() - daily_rf
        sortino = (excess_returns / downside_returns.std()) * np.sqrt(self.TRADING_DAYS_PER_YEAR)

        return float(sortino)

    def _calmar_ratio(self, returns: pd.Series, equity_df: pd.DataFrame) -> float:
        """Calmar Ratio: annualized return / max drawdown."""
        ann_return = self._annualized_return(returns)
        max_dd = self._max_drawdown(equity_df)

        if max_dd == 0:
            return float("inf") if ann_return > 0 else 0.0

        return ann_return / max_dd

    def _winning_trades(self, trades_df: pd.DataFrame) -> int:
        """Number of winning trades."""
        return int((trades_df["pnl"] > 0).sum())

    def _losing_trades(self, trades_df: pd.DataFrame) -> int:
        """Number of losing trades."""
        return int((trades_df["pnl"] < 0).sum())

    def _win_rate(self, trades_df: pd.DataFrame) -> float:
        """Win rate percentage."""
        if len(trades_df) == 0:
            return 0.0
        winners = (trades_df["pnl"] > 0).sum()
        return (winners / len(trades_df)) * 100

    def _profit_factor(self, trades_df: pd.DataFrame) -> float:
        """
        Profit Factor: gross profit / gross loss.

        > 1.0 = profitable
        > 1.5 = good
        > 2.0 = excellent
        """
        gross_profit = trades_df[trades_df["pnl"] > 0]["pnl"].sum()
        gross_loss = abs(trades_df[trades_df["pnl"] < 0]["pnl"].sum())

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def _average_win(self, trades_df: pd.DataFrame) -> float:
        """Average winning trade P&L."""
        winners = trades_df[trades_df["pnl"] > 0]
        return float(winners["pnl"].mean()) if len(winners) > 0 else 0.0

    def _average_loss(self, trades_df: pd.DataFrame) -> float:
        """Average losing trade P&L (negative value)."""
        losers = trades_df[trades_df["pnl"] < 0]
        return float(losers["pnl"].mean()) if len(losers) > 0 else 0.0

    def _largest_win(self, trades_df: pd.DataFrame) -> float:
        """Largest winning trade."""
        return float(trades_df["pnl"].max()) if len(trades_df) > 0 else 0.0

    def _largest_loss(self, trades_df: pd.DataFrame) -> float:
        """Largest losing trade (negative value)."""
        return float(trades_df["pnl"].min()) if len(trades_df) > 0 else 0.0

    def _average_trade(self, trades_df: pd.DataFrame) -> float:
        """Average trade P&L."""
        return float(trades_df["pnl"].mean()) if len(trades_df) > 0 else 0.0

    def _average_bars_held(self, trades_df: pd.DataFrame) -> float:
        """Average number of bars trades are held."""
        return float(trades_df["bars_held"].mean()) if len(trades_df) > 0 else 0.0

    def _exposure_time(self, equity_df: pd.DataFrame) -> float:
        """Percentage of time with open position."""
        in_position = equity_df["position"] != 0
        return (in_position.sum() / len(equity_df)) * 100

    def _empty_metrics(self) -> dict[str, Any]:
        """Return empty metrics when no trades."""
        return {
            "total_return": 0.0,
            "total_return_percent": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_duration_days": 0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "average_trade": 0.0,
            "average_bars_held": 0.0,
            "exposure_time": 0.0,
        }
