"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ohlcv_data() -> pd.DataFrame:
    """Generate sample OHLCV data for testing."""
    np.random.seed(42)
    n_bars = 100

    dates = pd.date_range(start="2024-01-01", periods=n_bars, freq="1h")

    # Generate realistic price movement
    base_price = 1.1000
    returns = np.random.normal(0, 0.001, n_bars)
    close_prices = base_price * np.exp(np.cumsum(returns))

    # Generate OHLC from close
    high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.0005, n_bars)))
    low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.0005, n_bars)))
    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base_price

    # Volume
    volume = np.random.randint(1000, 10000, n_bars)

    return pd.DataFrame({
        "timestamp": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volume,
    })


@pytest.fixture
def trending_up_data() -> pd.DataFrame:
    """Generate uptrending price data."""
    n_bars = 50
    dates = pd.date_range(start="2024-01-01", periods=n_bars, freq="1h")

    # Strong uptrend
    close_prices = 1.1000 + np.linspace(0, 0.05, n_bars) + np.random.normal(0, 0.001, n_bars)

    return pd.DataFrame({
        "timestamp": dates,
        "open": close_prices - 0.0002,
        "high": close_prices + 0.0005,
        "low": close_prices - 0.0005,
        "close": close_prices,
        "volume": np.random.randint(1000, 10000, n_bars),
    })


@pytest.fixture
def trending_down_data() -> pd.DataFrame:
    """Generate downtrending price data."""
    n_bars = 50
    dates = pd.date_range(start="2024-01-01", periods=n_bars, freq="1h")

    # Strong downtrend
    close_prices = 1.1500 - np.linspace(0, 0.05, n_bars) + np.random.normal(0, 0.001, n_bars)

    return pd.DataFrame({
        "timestamp": dates,
        "open": close_prices + 0.0002,
        "high": close_prices + 0.0005,
        "low": close_prices - 0.0005,
        "close": close_prices,
        "volume": np.random.randint(1000, 10000, n_bars),
    })


@pytest.fixture
def sideways_data() -> pd.DataFrame:
    """Generate sideways/ranging price data."""
    n_bars = 50
    dates = pd.date_range(start="2024-01-01", periods=n_bars, freq="1h")

    # Oscillating around mean
    close_prices = 1.1000 + 0.002 * np.sin(np.linspace(0, 4 * np.pi, n_bars))
    close_prices += np.random.normal(0, 0.0005, n_bars)

    return pd.DataFrame({
        "timestamp": dates,
        "open": close_prices - 0.0001,
        "high": close_prices + 0.0003,
        "low": close_prices - 0.0003,
        "close": close_prices,
        "volume": np.random.randint(1000, 10000, n_bars),
    })
