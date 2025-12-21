"""
Backtest service - orchestrates backtest execution.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

import pandas as pd
import numpy as np

from src.core.backtesting.engine import BacktestEngine, BacktestResult
from src.core.backtesting.strategy_base import Strategy
from src.core.backtesting.indicators import SMA, EMA, RSI, MACD, crossover


# Built-in strategies registry
BUILTIN_STRATEGIES: dict[str, type[Strategy]] = {}


def register_strategy(name: str):
    """Decorator to register a built-in strategy."""
    def decorator(cls):
        BUILTIN_STRATEGIES[name] = cls
        return cls
    return decorator


@register_strategy("sma-crossover")
class SMACrossoverStrategy(Strategy):
    """Simple Moving Average Crossover Strategy."""

    fast_period = 10
    slow_period = 20

    def init(self):
        self.sma_fast = self.I(SMA, self.data["close"], self.fast_period)
        self.sma_slow = self.I(SMA, self.data["close"], self.slow_period)

    def next(self):
        if len(self.sma_fast) < 2:
            return

        if crossover(self.sma_fast, self.sma_slow):
            if self.position <= 0:
                self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            if self.position >= 0:
                self.sell()


@register_strategy("rsi-overbought")
class RSIOverboughtStrategy(Strategy):
    """RSI Overbought/Oversold Strategy."""

    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        self.rsi = self.I(RSI, self.data["close"], self.rsi_period)

    def next(self):
        if len(self.rsi) < 1:
            return

        current_rsi = self.rsi.iloc[-1]

        if current_rsi < self.oversold:
            if self.position <= 0:
                self.buy()
        elif current_rsi > self.overbought:
            if self.position >= 0:
                self.sell()


@register_strategy("macd-signal")
class MACDSignalStrategy(Strategy):
    """MACD Signal Line Crossover Strategy."""

    fast_period = 12
    slow_period = 26
    signal_period = 9

    def init(self):
        macd_line, signal_line, histogram = MACD(
            self.data["close"],
            self.fast_period,
            self.slow_period,
            self.signal_period
        )
        self.macd = self.I(lambda x: macd_line, self.data["close"])
        self.signal = self.I(lambda x: signal_line, self.data["close"])

    def next(self):
        if len(self.macd) < 2:
            return

        if crossover(self.macd, self.signal):
            if self.position <= 0:
                self.buy()
        elif crossover(self.signal, self.macd):
            if self.position >= 0:
                self.sell()


@register_strategy("random")
class RandomStrategy(Strategy):
    """
    Random Strategy - buys and sells on coin flips.

    This is the control group. If your fancy TA strategy can't beat
    random chance, it's not actually working.
    """

    trade_probability = 0.02  # 2% chance to trade each bar
    seed = 42

    def init(self):
        np.random.seed(self.seed)
        self.random_values = np.random.random(len(self.data))

    def next(self):
        idx = self._current_bar

        if self.random_values[idx] < self.trade_probability:
            # Coin flip for direction
            if np.random.random() > 0.5:
                if self.position <= 0:
                    self.buy()
            else:
                if self.position >= 0:
                    self.sell()


@register_strategy("buy-and-hold")
class BuyAndHoldStrategy(Strategy):
    """
    Buy and Hold Strategy - the benchmark.

    Buys on the first bar and holds until the end.
    Most active strategies fail to beat this.
    """

    def init(self):
        pass

    def next(self):
        if self._current_bar == 0:
            self.buy()


class BacktestService:
    """Service for running backtests."""

    def __init__(self):
        self.engine = BacktestEngine()
        self._running_backtests: dict[str, dict] = {}

    def get_available_strategies(self) -> list[dict]:
        """Get list of available built-in strategies."""
        return [
            {
                "id": name,
                "name": name.replace("-", " ").title(),
                "description": cls.__doc__ or "",
                "parameters": self._get_strategy_parameters(cls),
            }
            for name, cls in BUILTIN_STRATEGIES.items()
        ]

    def _get_strategy_parameters(self, cls: type[Strategy]) -> list[dict]:
        """Extract configurable parameters from strategy class."""
        params = []
        for attr in dir(cls):
            if not attr.startswith("_") and not callable(getattr(cls, attr)):
                value = getattr(cls, attr)
                if isinstance(value, (int, float, str, bool)):
                    params.append({
                        "name": attr,
                        "type": type(value).__name__,
                        "default": value,
                    })
        return params

    def run_backtest(
        self,
        strategy_id: str,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str = "1H",
        initial_balance: float = 100_000.0,
        leverage: int = 100,
        parameters: Optional[dict[str, Any]] = None,
    ) -> BacktestResult:
        """
        Run a backtest synchronously.

        Args:
            strategy_id: Built-in strategy ID or 'custom'
            data: OHLCV DataFrame
            symbol: Currency pair symbol
            timeframe: Timeframe string
            initial_balance: Starting balance
            leverage: Leverage ratio
            parameters: Strategy parameter overrides

        Returns:
            BacktestResult with full results
        """
        # Get strategy class
        if strategy_id not in BUILTIN_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_id}")

        strategy_class = BUILTIN_STRATEGIES[strategy_id]

        # Configure engine
        self.engine.initial_balance = initial_balance
        self.engine.leverage = leverage

        # Run backtest
        result = self.engine.run(
            strategy_class=strategy_class,
            data=data,
            symbol=symbol,
            timeframe=timeframe,
            parameters=parameters,
        )

        return result

    def run_comparison(
        self,
        strategy_ids: list[str],
        data: pd.DataFrame,
        symbol: str,
        timeframe: str = "1H",
        initial_balance: float = 100_000.0,
        leverage: int = 100,
    ) -> dict[str, BacktestResult]:
        """
        Run multiple strategies on the same data for comparison.

        Always includes 'random' and 'buy-and-hold' as benchmarks.
        """
        # Ensure benchmarks are included
        all_strategies = list(set(strategy_ids + ["random", "buy-and-hold"]))

        results = {}
        for strategy_id in all_strategies:
            try:
                result = self.run_backtest(
                    strategy_id=strategy_id,
                    data=data,
                    symbol=symbol,
                    timeframe=timeframe,
                    initial_balance=initial_balance,
                    leverage=leverage,
                )
                results[strategy_id] = result
            except Exception as e:
                results[strategy_id] = BacktestResult(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=data.index[0],
                    end_date=data.index[-1],
                    initial_balance=initial_balance,
                    final_balance=initial_balance,
                    error_message=str(e),
                )

        return results


def generate_sample_data(
    symbol: str = "EURUSD",
    start_date: str = "2023-01-01",
    end_date: str = "2023-12-31",
    timeframe: str = "1H",
) -> pd.DataFrame:
    """Generate sample OHLCV data for testing."""

    # Base prices
    base_prices = {
        "EURUSD": 1.08,
        "GBPUSD": 1.26,
        "USDJPY": 149.0,
        "USDCHF": 0.88,
        "AUDUSD": 0.65,
    }
    base_price = base_prices.get(symbol, 1.0)

    # Generate date range
    freq_map = {
        "1M": "1min",
        "5M": "5min",
        "15M": "15min",
        "1H": "1h",
        "4H": "4h",
        "1D": "1D",
    }
    freq = freq_map.get(timeframe, "1h")

    dates = pd.date_range(start=start_date, end=end_date, freq=freq)

    # Generate random walk prices
    np.random.seed(42)
    returns = np.random.normal(0, 0.0002, len(dates))
    prices = base_price * np.exp(np.cumsum(returns))

    # Generate OHLCV
    data = []
    for i, (dt, price) in enumerate(zip(dates, prices)):
        volatility = 0.0005 * base_price
        high = price + np.random.uniform(0, volatility)
        low = price - np.random.uniform(0, volatility)
        open_price = price + np.random.uniform(-volatility / 2, volatility / 2)
        close_price = price + np.random.uniform(-volatility / 2, volatility / 2)

        data.append({
            "open": open_price,
            "high": max(high, open_price, close_price),
            "low": min(low, open_price, close_price),
            "close": close_price,
            "volume": np.random.randint(1000, 10000),
        })

    df = pd.DataFrame(data, index=dates)
    return df


# Singleton instance
backtest_service = BacktestService()
