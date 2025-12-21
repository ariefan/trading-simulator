"""
Base class for trading strategies.

Users extend this class to define their trading logic.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd


@dataclass
class Order:
    """Pending order."""

    side: str  # 'buy' or 'sell'
    size: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    bar_index: int = 0


@dataclass
class Position:
    """Open position."""

    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    entry_bar: int
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
    """Completed trade."""

    side: str
    size: float
    entry_price: float
    exit_price: float
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    pnl: float
    pnl_percent: float
    commission: float
    bars_held: int


class Strategy(ABC):
    """
    Base class for defining trading strategies.

    Users extend this class and implement:
    - init(): Initialize indicators
    - next(): Logic executed on each bar

    Available in strategy:
    - self.data: OHLCV DataFrame
    - self.position: Current position (positive=long, negative=short, 0=flat)
    - self.equity: Current account equity
    - self.buy() / self.sell(): Place orders

    Example:
        class SMAcrossover(Strategy):
            fast_period = 10
            slow_period = 20

            def init(self):
                self.sma_fast = self.I(SMA, self.data['close'], self.fast_period)
                self.sma_slow = self.I(SMA, self.data['close'], self.slow_period)

            def next(self):
                if self.sma_fast[-1] > self.sma_slow[-1]:
                    if not self.position:
                        self.buy()
                elif self.sma_fast[-1] < self.sma_slow[-1]:
                    if self.position:
                        self.sell()
    """

    # Strategy parameters (override in subclass)
    # These can be optimized during backtesting

    def __init__(self):
        self._data: Optional[pd.DataFrame] = None
        self._broker: Any = None
        self._current_bar: int = 0
        self._indicators: dict[str, np.ndarray] = {}
        self._orders: list[Order] = []

    @property
    def data(self) -> pd.DataFrame:
        """OHLCV data as DataFrame with columns: open, high, low, close, volume."""
        return self._data

    @data.setter
    def data(self, value: pd.DataFrame):
        self._data = value

    @property
    def position(self) -> float:
        """
        Current position size.
        Positive = long, negative = short, zero = flat.
        """
        if self._broker is None:
            return 0.0
        return self._broker.position

    @property
    def equity(self) -> float:
        """Current account equity (balance + unrealized P&L)."""
        if self._broker is None:
            return 0.0
        return self._broker.equity

    @property
    def balance(self) -> float:
        """Current cash balance."""
        if self._broker is None:
            return 0.0
        return self._broker.balance

    def I(self, indicator_func: Callable, *args, **kwargs) -> np.ndarray:
        """
        Register an indicator.

        The indicator function is called once with the full data series.
        Returns array of indicator values aligned with price data.

        Args:
            indicator_func: Function that computes indicator values
            *args: Arguments passed to indicator function

        Returns:
            Numpy array of indicator values
        """
        # Generate unique name for this indicator instance
        name = f"{indicator_func.__name__}_{len(self._indicators)}"

        # Compute indicator values
        values = indicator_func(*args, **kwargs)

        # Convert to numpy array if needed
        if isinstance(values, pd.Series):
            values = values.values
        elif not isinstance(values, np.ndarray):
            values = np.array(values)

        self._indicators[name] = values
        return values

    def buy(
        self,
        size: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
    ) -> None:
        """
        Place a buy order.

        Args:
            size: Position size in lots (default: calculated from equity)
            limit: Limit price for limit order (None = market order)
            stop: Stop price for stop entry order
            sl: Stop-loss price
            tp: Take-profit price
        """
        order = Order(
            side="buy",
            size=size,
            limit_price=limit,
            stop_price=stop,
            stop_loss=sl,
            take_profit=tp,
            bar_index=self._current_bar,
        )
        self._orders.append(order)

    def sell(
        self,
        size: Optional[float] = None,
        limit: Optional[float] = None,
        stop: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
    ) -> None:
        """
        Place a sell order.

        If in a long position, this closes the position.
        If flat, this opens a short position.

        Args:
            size: Position size in lots (default: close full position or calculated)
            limit: Limit price for limit order (None = market order)
            stop: Stop price for stop entry order
            sl: Stop-loss price
            tp: Take-profit price
        """
        order = Order(
            side="sell",
            size=size,
            limit_price=limit,
            stop_price=stop,
            stop_loss=sl,
            take_profit=tp,
            bar_index=self._current_bar,
        )
        self._orders.append(order)

    def close(self, size: Optional[float] = None) -> None:
        """
        Close current position.

        Args:
            size: Partial size to close (None = close all)
        """
        if self.position > 0:
            self.sell(size=size or abs(self.position))
        elif self.position < 0:
            self.buy(size=size or abs(self.position))

    @abstractmethod
    def init(self) -> None:
        """
        Initialize strategy indicators.

        Called once before backtesting starts.
        Use self.I() to register indicators.

        Example:
            def init(self):
                self.sma = self.I(SMA, self.data['close'], 20)
        """
        pass

    @abstractmethod
    def next(self) -> None:
        """
        Execute strategy logic for current bar.

        Called on each new bar during backtesting.
        Access current values with [-1] indexing.

        Example:
            def next(self):
                if self.data['close'].iloc[-1] > self.sma[-1]:
                    self.buy()
        """
        pass

    # Utility methods for strategies

    @staticmethod
    def crossover(series1: np.ndarray, series2: np.ndarray) -> bool:
        """Check if series1 crosses above series2 on the current bar."""
        if len(series1) < 2 or len(series2) < 2:
            return False
        return series1[-1] > series2[-1] and series1[-2] <= series2[-2]

    @staticmethod
    def crossunder(series1: np.ndarray, series2: np.ndarray) -> bool:
        """Check if series1 crosses below series2 on the current bar."""
        if len(series1) < 2 or len(series2) < 2:
            return False
        return series1[-1] < series2[-1] and series1[-2] >= series2[-2]
