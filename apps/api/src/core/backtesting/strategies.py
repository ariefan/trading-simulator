from typing import Any
import numpy as np
from src.core.backtesting.strategy_base import Strategy
from src.core.backtesting.indicators import SMA, EMA, RSI, MACD, crossover

class SMACrossoverStrategy(Strategy):
    """Simple Moving Average Crossover Strategy."""

    fast_period = 10
    slow_period = 20

    def init(self):
        self.sma_fast = self.I(SMA, self.data["close"], self.fast_period)
        self.sma_slow = self.I(SMA, self.data["close"], self.slow_period)

    def next(self):
        if self._current_bar < 2:
            return

        # Check for crossover at current bar
        i = self._current_bar
        cross_up = self.sma_fast[i] > self.sma_slow[i] and self.sma_fast[i-1] <= self.sma_slow[i-1]
        cross_down = self.sma_slow[i] > self.sma_fast[i] and self.sma_slow[i-1] <= self.sma_fast[i-1]

        if cross_up:
            if self.position <= 0:
                self.buy()
        elif cross_down:
            if self.position >= 0:
                self.sell()


class RSIOverboughtStrategy(Strategy):
    """RSI Overbought/Oversold Strategy."""

    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        self.rsi = self.I(RSI, self.data["close"], self.rsi_period)

    def next(self):
        if self._current_bar < 1:
            return

        current_rsi = self.rsi[self._current_bar]

        if current_rsi < self.oversold:
            if self.position <= 0:
                self.buy()
        elif current_rsi > self.overbought:
            if self.position >= 0:
                self.sell()


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
        if self._current_bar < 2:
            return

        i = self._current_bar
        cross_up = self.macd[i] > self.signal[i] and self.macd[i-1] <= self.signal[i-1]
        cross_down = self.signal[i] > self.macd[i] and self.signal[i-1] <= self.macd[i-1]

        if cross_up:
            if self.position <= 0:
                self.buy()
        elif cross_down:
            if self.position >= 0:
                self.sell()


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
