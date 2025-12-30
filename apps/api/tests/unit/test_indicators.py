"""Unit tests for technical indicators."""

import pytest
import pandas as pd
import numpy as np

from src.core.backtesting.indicators import (
    SMA, EMA, RSI, MACD, BOLLINGER_BANDS, ATR, STOCHASTIC, ADX,
    crossover, crossunder
)


class TestSMA:
    """Tests for Simple Moving Average."""

    def test_sma_basic(self, sample_ohlcv_data):
        """Test basic SMA calculation."""
        close = sample_ohlcv_data["close"]
        sma = SMA(close, period=10)

        assert len(sma) == len(close)
        assert sma.isna().sum() == 9  # First 9 values should be NaN
        assert not sma.iloc[-1:].isna().any()

    def test_sma_period_20(self, sample_ohlcv_data):
        """Test SMA with period 20."""
        close = sample_ohlcv_data["close"]
        sma = SMA(close, period=20)

        assert sma.isna().sum() == 19

    def test_sma_values(self):
        """Test SMA calculation accuracy."""
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        sma = SMA(data, period=5)

        # SMA of [1,2,3,4,5] = 3.0
        assert sma.iloc[4] == 3.0
        # SMA of [6,7,8,9,10] = 8.0
        assert sma.iloc[9] == 8.0


class TestEMA:
    """Tests for Exponential Moving Average."""

    def test_ema_basic(self, sample_ohlcv_data):
        """Test basic EMA calculation."""
        close = sample_ohlcv_data["close"]
        ema = EMA(close, period=10)

        assert len(ema) == len(close)
        # EMA starts calculating from first value
        assert not ema.iloc[-1:].isna().any()

    def test_ema_responds_faster_than_sma(self, trending_up_data):
        """Test that EMA responds faster to price changes than SMA."""
        close = trending_up_data["close"]
        sma = SMA(close, period=10)
        ema = EMA(close, period=10)

        # In uptrend, EMA should be higher than SMA (responds faster)
        last_10 = slice(-10, None)
        assert (ema[last_10] > sma[last_10]).mean() > 0.5


class TestRSI:
    """Tests for Relative Strength Index."""

    def test_rsi_range(self, sample_ohlcv_data):
        """Test RSI values are between 0 and 100."""
        close = sample_ohlcv_data["close"]
        rsi = RSI(close, period=14)

        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_rsi_overbought_in_uptrend(self, trending_up_data):
        """Test RSI is high in strong uptrend."""
        close = trending_up_data["close"]
        rsi = RSI(close, period=14)

        # In strong uptrend, RSI should be above 50 on average
        valid_rsi = rsi.dropna()
        assert valid_rsi.mean() > 50

    def test_rsi_oversold_in_downtrend(self, trending_down_data):
        """Test RSI is low in strong downtrend."""
        close = trending_down_data["close"]
        rsi = RSI(close, period=14)

        # In strong downtrend, RSI should be below 50 on average
        valid_rsi = rsi.dropna()
        assert valid_rsi.mean() < 50


class TestMACD:
    """Tests for MACD indicator."""

    def test_macd_output_shape(self, sample_ohlcv_data):
        """Test MACD returns three series."""
        close = sample_ohlcv_data["close"]
        macd_line, signal_line, histogram = MACD(close)

        assert len(macd_line) == len(close)
        assert len(signal_line) == len(close)
        assert len(histogram) == len(close)

    def test_histogram_is_difference(self, sample_ohlcv_data):
        """Test histogram is MACD line minus signal line."""
        close = sample_ohlcv_data["close"]
        macd_line, signal_line, histogram = MACD(close)

        # Histogram should equal MACD - Signal
        diff = macd_line - signal_line
        np.testing.assert_array_almost_equal(histogram.values, diff.values)

    def test_macd_positive_in_uptrend(self, trending_up_data):
        """Test MACD line is positive in uptrend."""
        close = trending_up_data["close"]
        macd_line, _, _ = MACD(close)

        # In uptrend, MACD should be positive toward the end
        assert macd_line.iloc[-10:].mean() > 0


class TestBollingerBands:
    """Tests for Bollinger Bands."""

    def test_bollinger_output_shape(self, sample_ohlcv_data):
        """Test Bollinger Bands returns three series."""
        close = sample_ohlcv_data["close"]
        upper, middle, lower = BOLLINGER_BANDS(close, period=20)

        assert len(upper) == len(close)
        assert len(middle) == len(close)
        assert len(lower) == len(close)

    def test_band_ordering(self, sample_ohlcv_data):
        """Test upper > middle > lower."""
        close = sample_ohlcv_data["close"]
        upper, middle, lower = BOLLINGER_BANDS(close, period=20)

        valid_idx = ~upper.isna()
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()

    def test_middle_is_sma(self, sample_ohlcv_data):
        """Test middle band equals SMA."""
        close = sample_ohlcv_data["close"]
        _, middle, _ = BOLLINGER_BANDS(close, period=20)
        sma = SMA(close, period=20)

        pd.testing.assert_series_equal(middle, sma)


class TestATR:
    """Tests for Average True Range."""

    def test_atr_positive(self, sample_ohlcv_data):
        """Test ATR is always positive."""
        high = sample_ohlcv_data["high"]
        low = sample_ohlcv_data["low"]
        close = sample_ohlcv_data["close"]

        atr = ATR(high, low, close, period=14)
        valid_atr = atr.dropna()

        assert (valid_atr >= 0).all()

    def test_atr_higher_in_volatile_market(self):
        """Test ATR is higher when volatility is higher."""
        n = 50

        # Low volatility data
        low_vol_close = pd.Series(1.1 + np.random.normal(0, 0.0001, n))
        low_vol_high = low_vol_close + 0.0002
        low_vol_low = low_vol_close - 0.0002

        # High volatility data
        high_vol_close = pd.Series(1.1 + np.random.normal(0, 0.01, n))
        high_vol_high = high_vol_close + 0.02
        high_vol_low = high_vol_close - 0.02

        low_atr = ATR(low_vol_high, low_vol_low, low_vol_close, period=14)
        high_atr = ATR(high_vol_high, high_vol_low, high_vol_close, period=14)

        assert high_atr.dropna().mean() > low_atr.dropna().mean()


class TestStochastic:
    """Tests for Stochastic Oscillator."""

    def test_stochastic_range(self, sample_ohlcv_data):
        """Test Stochastic values are between 0 and 100."""
        high = sample_ohlcv_data["high"]
        low = sample_ohlcv_data["low"]
        close = sample_ohlcv_data["close"]

        k, d = STOCHASTIC(high, low, close, k_period=14, d_period=3)

        valid_k = k.dropna()
        valid_d = d.dropna()

        assert (valid_k >= 0).all() and (valid_k <= 100).all()
        assert (valid_d >= 0).all() and (valid_d <= 100).all()


class TestCrossover:
    """Tests for crossover/crossunder functions."""

    def test_crossover_detection(self):
        """Test crossover is detected correctly."""
        series1 = pd.Series([1, 2, 3, 4, 5])
        series2 = pd.Series([2, 2, 2, 2, 2])

        cross = crossover(series1, series2)

        # Crossover happens when series1 goes from <= to >
        # At index 2: series1[2]=3 > series2[2]=2, series1[1]=2 <= series2[1]=2
        assert cross.iloc[2] == True
        assert cross.iloc[0] == False
        assert cross.iloc[4] == False

    def test_crossunder_detection(self):
        """Test crossunder is detected correctly."""
        series1 = pd.Series([5, 4, 3, 2, 1])
        series2 = pd.Series([3, 3, 3, 3, 3])

        cross = crossunder(series1, series2)

        # Crossunder happens when series1 goes from >= to <
        # At index 3: series1[3]=2 < series2[3]=3, series1[2]=3 >= series2[2]=3
        assert cross.iloc[3] == True
        assert cross.iloc[0] == False
        assert cross.iloc[1] == False

    def test_sma_crossover_in_uptrend(self, trending_up_data):
        """Test fast SMA crosses above slow SMA in uptrend."""
        close = trending_up_data["close"]
        fast_sma = SMA(close, period=5)
        slow_sma = SMA(close, period=20)

        crosses = crossover(fast_sma, slow_sma)

        # Should have at least one crossover in uptrend
        assert crosses.sum() >= 1
