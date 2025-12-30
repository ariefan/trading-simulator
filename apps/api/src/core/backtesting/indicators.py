"""
Technical indicators for trading strategies.

All indicators return pandas Series or numpy arrays
aligned with the input data for easy use in strategies.
"""
import numpy as np
import pandas as pd


class Indicators:
    """Collection of technical indicator functions."""

    @staticmethod
    def SMA(data: pd.Series, period: int) -> pd.Series:
        """
        Simple Moving Average.

        Args:
            data: Price series (typically close prices)
            period: Number of periods

        Returns:
            Series of SMA values
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def EMA(data: pd.Series, period: int) -> pd.Series:
        """
        Exponential Moving Average.

        Args:
            data: Price series
            period: Number of periods

        Returns:
            Series of EMA values
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def RSI(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index.

        Args:
            data: Price series (typically close prices)
            period: RSI period (default: 14)

        Returns:
            Series of RSI values (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def MACD(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        Moving Average Convergence Divergence.

        Args:
            data: Price series
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = data.ewm(span=fast_period, adjust=False).mean()
        slow_ema = data.ewm(span=slow_period, adjust=False).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def BOLLINGER_BANDS(
        data: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands.

        Args:
            data: Price series
            period: SMA period
            std_dev: Standard deviation multiplier

        Returns:
            Tuple of (Upper band, Middle band (SMA), Lower band)
        """
        middle = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    @staticmethod
    def ATR(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Average True Range.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period

        Returns:
            Series of ATR values
        """
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def STOCHASTIC(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3,
    ) -> tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            k_period: %K period
            d_period: %D period (smoothing)

        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()

        return k, d

    @staticmethod
    def ADX(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Average Directional Index.

        Measures trend strength (not direction).

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ADX period

        Returns:
            Series of ADX values
        """
        plus_dm = high.diff()
        minus_dm = low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr = Indicators.ATR(high, low, close, 1)  # True range for 1 period

        plus_di = 100 * (plus_dm.ewm(alpha=1 / period).mean() / tr.ewm(alpha=1 / period).mean())
        minus_di = 100 * (
            abs(minus_dm).ewm(alpha=1 / period).mean() / tr.ewm(alpha=1 / period).mean()
        )

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1 / period).mean()

        return adx

    @staticmethod
    def OBV(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On-Balance Volume.

        Args:
            close: Close prices
            volume: Volume

        Returns:
            Series of OBV values
        """
        direction = np.where(close > close.shift(1), 1, np.where(close < close.shift(1), -1, 0))
        obv = (direction * volume).cumsum()
        return pd.Series(obv, index=close.index)

    @staticmethod
    def VWAP(
        high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
    ) -> pd.Series:
        """
        Volume Weighted Average Price.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume

        Returns:
            Series of VWAP values
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap

    @staticmethod
    def PIVOT_POINTS(
        high: pd.Series, low: pd.Series, close: pd.Series
    ) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        Pivot Points (Standard).

        Args:
            high: High prices
            low: Low prices
            close: Close prices

        Returns:
            Tuple of (Pivot, R1, R2, S1, S2)
        """
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)

        return pivot, r1, r2, s1, s2


# Convenience aliases
SMA = Indicators.SMA
EMA = Indicators.EMA
RSI = Indicators.RSI
MACD = Indicators.MACD
BOLLINGER_BANDS = Indicators.BOLLINGER_BANDS
ATR = Indicators.ATR
STOCHASTIC = Indicators.STOCHASTIC
ADX = Indicators.ADX
OBV = Indicators.OBV
VWAP = Indicators.VWAP


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect crossover events between two series.

    Returns True when series1 crosses above series2.

    Args:
        series1: First series (e.g., fast MA)
        series2: Second series (e.g., slow MA)

    Returns:
        Boolean series where True indicates a crossover event
    """
    return (series1 > series2) & (series1.shift(1) <= series2.shift(1))


def crossunder(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Detect crossunder events between two series.

    Returns True when series1 crosses below series2.

    Args:
        series1: First series (e.g., fast MA)
        series2: Second series (e.g., slow MA)

    Returns:
        Boolean series where True indicates a crossunder event
    """
    return (series1 < series2) & (series1.shift(1) >= series2.shift(1))
