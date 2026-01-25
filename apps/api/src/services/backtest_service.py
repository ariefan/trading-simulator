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
from src.core.backtesting.indicators import (
    SMA, EMA, RSI, MACD, BOLLINGER_BANDS, 
    ATR, STOCHASTIC, ADX, crossover, crossunder
)


from src.core.backtesting.strategies import (
    SMACrossoverStrategy,
    RSIOverboughtStrategy,
    MACDSignalStrategy,
    RandomStrategy,
    BuyAndHoldStrategy,
)

# Built-in strategies registry
BUILTIN_STRATEGIES: dict[str, type[Strategy]] = {
    "sma-crossover": SMACrossoverStrategy,
    "rsi-overbought": RSIOverboughtStrategy,
    "macd-signal": MACDSignalStrategy,
    "random": RandomStrategy,
    "buy-and-hold": BuyAndHoldStrategy,
}

def register_strategy(name: str):
    """Decorator to register a built-in strategy."""
    def decorator(cls):
        BUILTIN_STRATEGIES[name] = cls
        return cls
    return decorator



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

    def _load_custom_strategy(self, code: str) -> type[Strategy]:
        """
        Dynamically load a strategy class from Python code.
        
        Args:
            code: Python code string defining the strategy class
            
        Returns:
            The first class found in the code that inherits from Strategy
        """
        # Prepare execution context with all indicators and base class
        globals_dict = {
            "Strategy": Strategy,
            "SMA": SMA,
            "EMA": EMA,
            "RSI": RSI,
            "MACD": MACD,
            "BOLLINGER_BANDS": BOLLINGER_BANDS,
            "ATR": ATR,
            "STOCHASTIC": STOCHASTIC,
            "ADX": ADX,
            "crossover": crossover,
            "crossunder": crossunder,
            "pd": pd,
            "np": np,
        }
        
        # Execute the code
        try:
            exec(code, globals_dict)
        except Exception as e:
            raise ValueError(f"Failed to execute strategy code: {str(e)}")
            
        # Find the strategy class
        strategy_class = None
        for item in globals_dict.values():
            if (
                isinstance(item, type) 
                and issubclass(item, Strategy) 
                and item is not Strategy
            ):
                strategy_class = item
                break
                
        if not strategy_class:
            raise ValueError("No class inheriting from Strategy found in code")
            
        return strategy_class

    def run_backtest(
        self,
        strategy_id: str,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str = "1H",
        initial_balance: float = 100_000.0,
        leverage: int = 100,
        parameters: Optional[dict[str, Any]] = None,
        custom_code: Optional[str] = None,
    ) -> BacktestResult:
        """
        Run a backtest synchronously.

        Args:
            strategy_id: Built-in strategy ID or unique ID for custom
            data: OHLCV DataFrame
            symbol: Currency pair symbol
            timeframe: Timeframe string
            initial_balance: Starting balance
            leverage: Leverage ratio
            parameters: Strategy parameter overrides
            custom_code: Optional Python code for custom strategies

        Returns:
            BacktestResult with full results
        """
        # Get strategy class
        if custom_code:
            strategy_class = self._load_custom_strategy(custom_code)
        elif strategy_id in BUILTIN_STRATEGIES:
            strategy_class = BUILTIN_STRATEGIES[strategy_id]
        else:
            raise ValueError(f"Unknown strategy: {strategy_id}")

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
        "XAUUSD": 2050.0,
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
