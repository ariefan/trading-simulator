"""Unit tests for backtesting engine."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.core.backtesting.engine import BacktestEngine
from src.core.backtesting.strategies import (
    SMAcrossoverStrategy,
    RSIStrategy,
    MACDStrategy,
    RandomStrategy,
    BuyAndHoldStrategy,
)
from src.core.backtesting.broker import SimulatedBroker
from src.core.backtesting.metrics import PerformanceMetrics


class TestSimulatedBroker:
    """Tests for SimulatedBroker."""

    def test_broker_initialization(self):
        """Test broker initializes with correct balance."""
        broker = SimulatedBroker(initial_balance=50000, leverage=50)

        assert broker.balance == 50000
        assert broker.leverage == 50
        assert broker.equity == 50000
        assert len(broker.positions) == 0

    def test_open_long_position(self):
        """Test opening a long position."""
        broker = SimulatedBroker(initial_balance=100000, leverage=100)

        position = broker.open_position(
            symbol="EURUSD",
            side="long",
            size=1.0,
            price=1.1000,
            timestamp=datetime.now(),
        )

        assert position is not None
        assert position["side"] == "long"
        assert position["size"] == 1.0
        assert position["entry_price"] == 1.1000
        assert len(broker.positions) == 1

    def test_open_short_position(self):
        """Test opening a short position."""
        broker = SimulatedBroker(initial_balance=100000, leverage=100)

        position = broker.open_position(
            symbol="EURUSD",
            side="short",
            size=0.5,
            price=1.1500,
            timestamp=datetime.now(),
        )

        assert position is not None
        assert position["side"] == "short"
        assert position["size"] == 0.5

    def test_close_position_profit(self):
        """Test closing position with profit."""
        broker = SimulatedBroker(initial_balance=100000, leverage=100)

        # Open long at 1.1000
        position = broker.open_position(
            symbol="EURUSD",
            side="long",
            size=1.0,
            price=1.1000,
            timestamp=datetime.now(),
        )

        # Close at 1.1050 (50 pips profit)
        trade = broker.close_position(
            position_id=position["id"],
            price=1.1050,
            timestamp=datetime.now(),
        )

        assert trade is not None
        assert trade["pnl"] > 0
        assert broker.balance > 100000
        assert len(broker.positions) == 0

    def test_close_position_loss(self):
        """Test closing position with loss."""
        broker = SimulatedBroker(initial_balance=100000, leverage=100)

        # Open long at 1.1000
        position = broker.open_position(
            symbol="EURUSD",
            side="long",
            size=1.0,
            price=1.1000,
            timestamp=datetime.now(),
        )

        # Close at 1.0950 (50 pips loss)
        trade = broker.close_position(
            position_id=position["id"],
            price=1.0950,
            timestamp=datetime.now(),
        )

        assert trade is not None
        assert trade["pnl"] < 0
        assert broker.balance < 100000

    def test_margin_calculation(self):
        """Test margin is calculated correctly."""
        broker = SimulatedBroker(initial_balance=10000, leverage=100)

        # 1 lot EURUSD at 1.1000 = $110,000 notional
        # With 100:1 leverage = $1,100 margin
        broker.open_position(
            symbol="EURUSD",
            side="long",
            size=1.0,
            price=1.1000,
            timestamp=datetime.now(),
        )

        assert broker.margin_used > 0
        assert broker.free_margin < broker.balance

    def test_insufficient_margin(self):
        """Test position rejected when insufficient margin."""
        broker = SimulatedBroker(initial_balance=1000, leverage=100)

        # Try to open 10 lots (way too much for $1000)
        position = broker.open_position(
            symbol="EURUSD",
            side="long",
            size=10.0,
            price=1.1000,
            timestamp=datetime.now(),
        )

        # Should be rejected or limited
        assert position is None or position["size"] < 10.0


class TestPerformanceMetrics:
    """Tests for performance metrics calculation."""

    def test_metrics_with_no_trades(self):
        """Test metrics with empty trade list."""
        metrics = PerformanceMetrics.calculate([], initial_balance=100000)

        assert metrics["total_trades"] == 0
        assert metrics["win_rate"] == 0

    def test_metrics_with_winning_trades(self):
        """Test metrics with all winning trades."""
        trades = [
            {"pnl": 100, "pnl_percent": 0.1},
            {"pnl": 200, "pnl_percent": 0.2},
            {"pnl": 150, "pnl_percent": 0.15},
        ]
        metrics = PerformanceMetrics.calculate(trades, initial_balance=100000)

        assert metrics["total_trades"] == 3
        assert metrics["win_rate"] == 100.0
        assert metrics["winning_trades"] == 3
        assert metrics["losing_trades"] == 0

    def test_metrics_with_losing_trades(self):
        """Test metrics with all losing trades."""
        trades = [
            {"pnl": -100, "pnl_percent": -0.1},
            {"pnl": -50, "pnl_percent": -0.05},
        ]
        metrics = PerformanceMetrics.calculate(trades, initial_balance=100000)

        assert metrics["total_trades"] == 2
        assert metrics["win_rate"] == 0.0
        assert metrics["winning_trades"] == 0
        assert metrics["losing_trades"] == 2

    def test_profit_factor(self):
        """Test profit factor calculation."""
        trades = [
            {"pnl": 200, "pnl_percent": 0.2},
            {"pnl": -100, "pnl_percent": -0.1},
        ]
        metrics = PerformanceMetrics.calculate(trades, initial_balance=100000)

        # Profit factor = gross profit / gross loss = 200 / 100 = 2.0
        assert metrics["profit_factor"] == 2.0


class TestStrategies:
    """Tests for built-in strategies."""

    def test_sma_crossover_generates_signals(self, sample_ohlcv_data):
        """Test SMA crossover strategy generates signals."""
        strategy = SMAcrossoverStrategy(fast_period=5, slow_period=20)
        signals = strategy.generate_signals(sample_ohlcv_data)

        assert len(signals) == len(sample_ohlcv_data)
        # Should have at least some non-zero signals
        assert (signals != 0).any()

    def test_rsi_strategy_generates_signals(self, sample_ohlcv_data):
        """Test RSI strategy generates signals."""
        strategy = RSIStrategy(period=14, overbought=70, oversold=30)
        signals = strategy.generate_signals(sample_ohlcv_data)

        assert len(signals) == len(sample_ohlcv_data)

    def test_macd_strategy_generates_signals(self, sample_ohlcv_data):
        """Test MACD strategy generates signals."""
        strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
        signals = strategy.generate_signals(sample_ohlcv_data)

        assert len(signals) == len(sample_ohlcv_data)

    def test_random_strategy_is_random(self, sample_ohlcv_data):
        """Test random strategy produces different results."""
        strategy1 = RandomStrategy(seed=42)
        strategy2 = RandomStrategy(seed=123)

        signals1 = strategy1.generate_signals(sample_ohlcv_data)
        signals2 = strategy2.generate_signals(sample_ohlcv_data)

        # Different seeds should produce different signals
        assert not (signals1 == signals2).all()

    def test_buy_and_hold_strategy(self, sample_ohlcv_data):
        """Test buy and hold strategy."""
        strategy = BuyAndHoldStrategy()
        signals = strategy.generate_signals(sample_ohlcv_data)

        # Should buy at start (signal = 1) and hold
        assert signals.iloc[0] == 1
        # Rest should be hold (0)
        assert (signals.iloc[1:] == 0).all()


class TestBacktestEngine:
    """Tests for BacktestEngine."""

    def test_engine_initialization(self, sample_ohlcv_data):
        """Test engine initializes correctly."""
        strategy = SMAcrossoverStrategy(fast_period=5, slow_period=20)
        engine = BacktestEngine(
            data=sample_ohlcv_data,
            strategy=strategy,
            initial_balance=100000,
            leverage=100,
        )

        assert engine.initial_balance == 100000
        assert engine.leverage == 100

    def test_engine_runs_backtest(self, sample_ohlcv_data):
        """Test engine runs backtest without errors."""
        strategy = SMAcrossoverStrategy(fast_period=5, slow_period=20)
        engine = BacktestEngine(
            data=sample_ohlcv_data,
            strategy=strategy,
            initial_balance=100000,
            leverage=100,
        )

        results = engine.run()

        assert results is not None
        assert "metrics" in results
        assert "trades" in results
        assert "equity_curve" in results

    def test_engine_with_buy_and_hold(self, trending_up_data):
        """Test engine with buy and hold in uptrend."""
        strategy = BuyAndHoldStrategy()
        engine = BacktestEngine(
            data=trending_up_data,
            strategy=strategy,
            initial_balance=100000,
            leverage=100,
        )

        results = engine.run()

        # In uptrend, buy and hold should be profitable
        assert results["metrics"]["total_return_percent"] > 0

    def test_engine_generates_equity_curve(self, sample_ohlcv_data):
        """Test engine generates equity curve."""
        strategy = SMAcrossoverStrategy(fast_period=5, slow_period=20)
        engine = BacktestEngine(
            data=sample_ohlcv_data,
            strategy=strategy,
            initial_balance=100000,
            leverage=100,
        )

        results = engine.run()

        equity_curve = results["equity_curve"]
        assert len(equity_curve) > 0
        # First equity should be initial balance
        assert equity_curve[0]["equity"] == 100000

    def test_compare_with_benchmarks(self, sample_ohlcv_data):
        """Test comparing strategy with benchmarks."""
        strategy = SMAcrossoverStrategy(fast_period=5, slow_period=20)
        engine = BacktestEngine(
            data=sample_ohlcv_data,
            strategy=strategy,
            initial_balance=100000,
            leverage=100,
        )

        comparison = engine.compare_with_benchmarks()

        assert "strategy" in comparison
        assert "random" in comparison
        assert "buy_and_hold" in comparison
        assert "conclusion" in comparison
