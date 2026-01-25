"""
Backtesting execution engine.

Runs trading strategies on historical data and tracks performance.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Type

import numpy as np
import pandas as pd

from src.core.backtesting.strategy_base import Strategy, Order, Trade
from src.core.backtesting.metrics import PerformanceMetrics


@dataclass
class BacktestResult:
    """Container for backtest results."""

    # Configuration
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float

    # Results
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[dict] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)

    # Metadata
    execution_time_ms: int = 0
    bars_processed: int = 0
    error_message: Optional[str] = None


class SimulatedBroker:
    """
    Simulated broker for backtesting.

    Handles order execution, position tracking, and P&L calculation.
    """

    LOT_SIZE = 100_000  # Standard forex lot size

    def __init__(
        self,
        initial_balance: float,
        leverage: int = 100,
        commission_per_lot: float = 7.0,
        spread_pips: float = 1.0,
        pip_value: float = 0.0001,
    ):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.leverage = leverage
        self.commission_per_lot = commission_per_lot
        self.spread_pips = spread_pips
        self.pip_value = pip_value

        # Position state
        self.position: float = 0.0  # Positive = long, negative = short
        self.position_price: float = 0.0
        self.position_bar: int = 0
        self.stop_loss: Optional[float] = None
        self.take_profit: Optional[float] = None

        # Current price
        self.current_price: float = 0.0
        self.current_bar: int = 0
        self.current_time: Optional[pd.Timestamp] = None

        # Tracking
        self.trades: list[Trade] = []
        self.pending_orders: list[Order] = []
        self.unrealized_pnl: float = 0.0

    @property
    def equity(self) -> float:
        """Current equity (balance + unrealized P&L)."""
        return self.balance + self.unrealized_pnl

    def update_price(
        self,
        open_price: float,
        high: float,
        low: float,
        close: float,
        bar_index: int,
        timestamp: pd.Timestamp,
    ) -> list[Trade]:
        """
        Update broker with new price bar.

        Checks stop-loss/take-profit and pending orders.

        Returns:
            List of trades executed on this bar
        """
        self.current_price = close
        self.current_bar = bar_index
        self.current_time = timestamp

        executed_trades = []

        # Update unrealized P&L
        if self.position != 0:
            self._update_unrealized_pnl()

            # Check stop-loss
            if self.stop_loss is not None:
                if self.position > 0 and low <= self.stop_loss:
                    # Long position hit stop-loss
                    trade = self._close_position(self.stop_loss)
                    executed_trades.append(trade)
                elif self.position < 0 and high >= self.stop_loss:
                    # Short position hit stop-loss
                    trade = self._close_position(self.stop_loss)
                    executed_trades.append(trade)

            # Check take-profit
            if self.take_profit is not None and self.position != 0:
                if self.position > 0 and high >= self.take_profit:
                    # Long position hit take-profit
                    trade = self._close_position(self.take_profit)
                    executed_trades.append(trade)
                elif self.position < 0 and low <= self.take_profit:
                    # Short position hit take-profit
                    trade = self._close_position(self.take_profit)
                    executed_trades.append(trade)

        # Process pending orders
        for order in self.pending_orders[:]:
            executed = self._process_pending_order(order, high, low, close)
            if executed:
                self.pending_orders.remove(order)
                if isinstance(executed, Trade):
                    executed_trades.append(executed)

        return executed_trades

    def process_orders(self, orders: list[Order]) -> list[Trade]:
        """
        Process new orders from strategy.

        Returns:
            List of trades executed
        """
        executed_trades = []

        for order in orders:
            # Market order - execute immediately
            if order.limit_price is None and order.stop_price is None:
                trade = self._execute_market_order(order)
                if trade:
                    executed_trades.append(trade)
            else:
                # Pending order - add to queue
                self.pending_orders.append(order)

        return executed_trades

    def _execute_market_order(self, order: Order) -> Optional[Trade]:
        """Execute a market order at current price."""
        # Apply spread
        if order.side == "buy":
            exec_price = self.current_price + (self.spread_pips * self.pip_value / 2)
        else:
            exec_price = self.current_price - (self.spread_pips * self.pip_value / 2)

        # Determine size
        size = order.size or self._calculate_default_size()

        # Check if we're closing existing position
        if order.side == "buy" and self.position < 0:
            # Closing short position
            trade = self._close_position(exec_price)
            return trade
        elif order.side == "sell" and self.position > 0:
            # Closing long position
            trade = self._close_position(exec_price)
            return trade
        elif order.side == "buy" and self.position >= 0:
            # Opening/adding to long
            self._open_position(size, exec_price, order.stop_loss, order.take_profit)
            return None
        elif order.side == "sell" and self.position <= 0:
            # Opening/adding to short
            self._open_position(-size, exec_price, order.stop_loss, order.take_profit)
            return None

        return None

    def _open_position(
        self,
        size: float,
        price: float,
        stop_loss: Optional[float],
        take_profit: Optional[float],
    ) -> None:
        """Open a new position."""
        # Calculate commission
        commission = abs(size) * self.commission_per_lot
        self.balance -= commission

        self.position = size
        self.position_price = price
        self.position_bar = self.current_bar
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def _close_position(self, exit_price: float) -> Trade:
        """Close current position and record trade."""
        # Calculate P&L
        if self.position > 0:
            pnl = (exit_price - self.position_price) * abs(self.position) * self.LOT_SIZE
        else:
            pnl = (self.position_price - exit_price) * abs(self.position) * self.LOT_SIZE

        # Commission for closing
        commission = abs(self.position) * self.commission_per_lot
        pnl -= commission

        # Calculate P&L percentage
        position_value = abs(self.position) * self.position_price * self.LOT_SIZE
        pnl_percent = (pnl / position_value) * 100 if position_value > 0 else 0

        # Create trade record
        trade = Trade(
            side="long" if self.position > 0 else "short",
            size=abs(self.position),
            entry_price=self.position_price,
            exit_price=exit_price,
            entry_time=pd.Timestamp.now(),  # Would be from position_bar
            exit_time=self.current_time,
            pnl=pnl,
            pnl_percent=pnl_percent,
            commission=commission * 2,  # Entry + exit
            bars_held=self.current_bar - self.position_bar,
        )

        # Update balance
        self.balance += pnl

        # Reset position
        self.position = 0.0
        self.position_price = 0.0
        self.stop_loss = None
        self.take_profit = None
        self.unrealized_pnl = 0.0

        self.trades.append(trade)
        return trade

    def _update_unrealized_pnl(self) -> None:
        """Update unrealized P&L based on current price."""
        if self.position > 0:
            self.unrealized_pnl = (
                (self.current_price - self.position_price) * self.position * self.LOT_SIZE
            )
        elif self.position < 0:
            self.unrealized_pnl = (
                (self.position_price - self.current_price) * abs(self.position) * self.LOT_SIZE
            )
        else:
            self.unrealized_pnl = 0.0

    def _calculate_default_size(self) -> float:
        """Calculate default position size (1% risk)."""
        risk_amount = self.equity * 0.01
        return max(0.01, min(risk_amount / 1000, 1.0))  # 0.01 to 1.0 lots

    def _process_pending_order(
        self, order: Order, high: float, low: float, close: float
    ) -> Optional[Trade]:
        """Process a pending limit/stop order."""
        # Limit order
        if order.limit_price is not None:
            if order.side == "buy" and low <= order.limit_price:
                return self._execute_at_price(order, order.limit_price)
            elif order.side == "sell" and high >= order.limit_price:
                return self._execute_at_price(order, order.limit_price)

        # Stop order
        if order.stop_price is not None:
            if order.side == "buy" and high >= order.stop_price:
                return self._execute_at_price(order, order.stop_price)
            elif order.side == "sell" and low <= order.stop_price:
                return self._execute_at_price(order, order.stop_price)

        return None

    def _execute_at_price(self, order: Order, price: float) -> Optional[Trade]:
        """Execute order at specified price."""
        original_price = self.current_price
        self.current_price = price
        trade = self._execute_market_order(order)
        self.current_price = original_price
        return trade


class BacktestEngine:
    """
    Main backtesting execution engine.

    Runs a strategy on historical data and generates performance report.
    """

    def __init__(
        self,
        initial_balance: float = 100_000.0,
        leverage: int = 100,
        commission: float = 7.0,
        spread_pips: float = 1.0,
    ):
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.commission = commission
        self.spread_pips = spread_pips
        self.metrics_calculator = PerformanceMetrics()

    def run(
        self,
        strategy_class: Type[Strategy],
        data: pd.DataFrame,
        symbol: str,
        timeframe: str = "1H",
        parameters: Optional[dict[str, Any]] = None,
    ) -> BacktestResult:
        """
        Execute backtest for a strategy on historical data.

        Args:
            strategy_class: Strategy class (not instance)
            data: OHLCV DataFrame with columns [open, high, low, close, volume]
            symbol: Currency pair symbol
            timeframe: Timeframe string (e.g., "1H", "4H", "1D")
            parameters: Strategy parameter overrides

        Returns:
            BacktestResult with trades, equity curve, and metrics
        """
        import time

        start_time = time.time()

        # Determine pip value based on symbol
        pip_value = 0.01 if "JPY" in symbol or "XAU" in symbol else 0.0001

        # Initialize strategy
        strategy = strategy_class()
        if parameters:
            for key, value in parameters.items():
                if hasattr(strategy, key):
                    setattr(strategy, key, value)

        strategy.data = data

        # Initialize broker
        broker = SimulatedBroker(
            initial_balance=self.initial_balance,
            leverage=self.leverage,
            commission_per_lot=self.commission,
            spread_pips=self.spread_pips,
            pip_value=pip_value,
        )
        strategy._broker = broker

        # Initialize strategy indicators
        strategy.init()

        # Equity curve tracking
        equity_curve = []

        # Main backtest loop
        for i in range(len(data)):
            strategy._current_bar = i

            # Get current bar data
            bar = data.iloc[i]
            timestamp = data.index[i]

            # Update broker with current prices (checks SL/TP)
            broker.update_price(
                open_price=bar["open"],
                high=bar["high"],
                low=bar["low"],
                close=bar["close"],
                bar_index=i,
                timestamp=timestamp,
            )

            # Clear previous bar's orders
            strategy._orders = []

            # Execute strategy logic
            strategy.next()

            # Process new orders from strategy
            broker.process_orders(strategy._orders)

            # Record equity
            equity_curve.append(
                {
                    "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp),
                    "equity": broker.equity,
                    "balance": broker.balance,
                    "position": broker.position,
                    "drawdown": 0.0,  # Calculated later
                }
            )

        # Close any remaining position at end
        if broker.position != 0:
            broker._close_position(data.iloc[-1]["close"])

        # Calculate drawdown for equity curve
        equity_values = [e["equity"] for e in equity_curve]
        peak = pd.Series(equity_values).expanding().max()
        drawdown = (pd.Series(equity_values) - peak) / peak * 100

        for i, dd in enumerate(drawdown):
            equity_curve[i]["drawdown"] = dd

        # Calculate performance metrics
        metrics = self.metrics_calculator.calculate_all(
            trades=broker.trades,
            equity_curve=equity_curve,
            initial_balance=self.initial_balance,
        )

        execution_time = int((time.time() - start_time) * 1000)

        # Build result
        result = BacktestResult(
            symbol=symbol,
            timeframe=timeframe,
            start_date=data.index[0].to_pydatetime() if hasattr(data.index[0], "to_pydatetime") else data.index[0],
            end_date=data.index[-1].to_pydatetime() if hasattr(data.index[-1], "to_pydatetime") else data.index[-1],
            initial_balance=self.initial_balance,
            final_balance=broker.balance,
            trades=[
                Trade(
                    side=t.side,
                    size=t.size,
                    entry_price=t.entry_price,
                    exit_price=t.exit_price,
                    entry_time=t.entry_time,
                    exit_time=t.exit_time,
                    pnl=t.pnl,
                    pnl_percent=t.pnl_percent,
                    commission=t.commission,
                    bars_held=t.bars_held,
                )
                for t in broker.trades
            ],
            equity_curve=equity_curve,
            metrics=metrics,
            parameters=parameters or {},
            execution_time_ms=execution_time,
            bars_processed=len(data),
        )

        return result
