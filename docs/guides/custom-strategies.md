# Custom Strategies

Write your own trading strategies in Python and test them against the benchmarks.

## Strategy Structure

Every strategy must implement a `generate_signals` function:

```python
import pandas as pd

def generate_signals(data: pd.DataFrame) -> pd.Series:
    """
    Generate trading signals from OHLCV data.

    Args:
        data: DataFrame with columns: open, high, low, close, volume

    Returns:
        Series of signals: 1 (buy), -1 (sell), 0 (hold)
    """
    signals = pd.Series(0, index=data.index)

    # Your logic here

    return signals
```

---

## Available Data

The `data` DataFrame contains:

| Column | Type | Description |
|--------|------|-------------|
| `open` | float | Opening price |
| `high` | float | Highest price |
| `low` | float | Lowest price |
| `close` | float | Closing price |
| `volume` | int | Trading volume |

The index is a DatetimeIndex.

---

## Available Indicators

Import from the indicators module:

```python
from src.core.backtesting.indicators import (
    SMA, EMA, RSI, MACD, BOLLINGER_BANDS,
    ATR, STOCHASTIC, ADX, OBV, VWAP,
    crossover, crossunder
)
```

### Moving Averages

```python
# Simple Moving Average
sma_20 = SMA(data['close'], period=20)

# Exponential Moving Average
ema_12 = EMA(data['close'], period=12)
```

### RSI

```python
rsi = RSI(data['close'], period=14)
# Returns values 0-100
```

### MACD

```python
macd_line, signal_line, histogram = MACD(
    data['close'],
    fast_period=12,
    slow_period=26,
    signal_period=9
)
```

### Bollinger Bands

```python
upper, middle, lower = BOLLINGER_BANDS(
    data['close'],
    period=20,
    std_dev=2.0
)
```

### Crossover Detection

```python
# True when series1 crosses above series2
buy_signal = crossover(fast_sma, slow_sma)

# True when series1 crosses below series2
sell_signal = crossunder(fast_sma, slow_sma)
```

---

## Example Strategies

### Golden Cross

```python
def generate_signals(data):
    """Golden Cross: 50 SMA crosses 200 SMA."""
    sma_50 = SMA(data['close'], 50)
    sma_200 = SMA(data['close'], 200)

    signals = pd.Series(0, index=data.index)
    signals[crossover(sma_50, sma_200)] = 1   # Buy
    signals[crossunder(sma_50, sma_200)] = -1  # Sell

    return signals
```

### RSI Mean Reversion

```python
def generate_signals(data):
    """Buy oversold, sell overbought."""
    rsi = RSI(data['close'], period=14)

    signals = pd.Series(0, index=data.index)
    signals[rsi < 30] = 1   # Oversold - buy
    signals[rsi > 70] = -1  # Overbought - sell

    return signals
```

### Bollinger Band Breakout

```python
def generate_signals(data):
    """Trade breakouts from Bollinger Bands."""
    upper, middle, lower = BOLLINGER_BANDS(data['close'], 20, 2.0)

    signals = pd.Series(0, index=data.index)

    # Breakout above upper band
    signals[data['close'] > upper] = 1

    # Breakdown below lower band
    signals[data['close'] < lower] = -1

    return signals
```

### Multi-Indicator Confluence

```python
def generate_signals(data):
    """Require multiple indicators to agree."""
    # Trend filter
    sma_50 = SMA(data['close'], 50)
    sma_200 = SMA(data['close'], 200)
    uptrend = sma_50 > sma_200

    # Entry signal
    rsi = RSI(data['close'], 14)
    oversold = rsi < 40

    # MACD confirmation
    macd, signal, _ = MACD(data['close'])
    macd_bullish = macd > signal

    signals = pd.Series(0, index=data.index)

    # Buy only when all conditions align
    buy_condition = uptrend & oversold & macd_bullish
    signals[buy_condition] = 1

    # Sell when trend reverses
    signals[~uptrend & (rsi > 60)] = -1

    return signals
```

---

## Creating via API

### Create Strategy

```bash
POST /api/v1/strategies/
{
  "name": "My Custom Strategy",
  "description": "A multi-indicator approach",
  "code": "def generate_signals(data):\n    ...",
  "parameters": {
    "rsi_period": 14,
    "sma_period": 20
  }
}
```

### List Strategies

```bash
GET /api/v1/strategies/
```

### Get Templates

```bash
GET /api/v1/strategies/templates
```

---

## Testing Your Strategy

### Via UI

1. Go to **Strategies** page
2. Click **Create New Strategy**
3. Write your code
4. Click **Validate** to check syntax
5. Save and run a backtest

### Via API

```bash
# Create strategy
curl -X POST /api/v1/strategies/ -d '{
  "name": "Test Strategy",
  "code": "..."
}'

# Run backtest
curl -X POST /api/v1/backtests/ -d '{
  "strategy_id": "test-strategy-id",
  "symbol": "EURUSD",
  "timeframe": "1h",
  ...
}'
```

---

## Best Practices

### 1. Handle NaN Values

Indicators produce NaN for initial periods:

```python
def generate_signals(data):
    sma = SMA(data['close'], 20)
    signals = pd.Series(0, index=data.index)

    # Only generate signals where indicator is valid
    valid = ~sma.isna()
    signals[valid & (data['close'] > sma)] = 1

    return signals
```

### 2. Avoid Look-Ahead Bias

Never use future data:

```python
# Bad - uses future data
signals[data['close'].shift(-1) > data['close']] = 1

# Good - only uses past/current data
signals[data['close'] > data['close'].shift(1)] = 1
```

### 3. Keep It Simple

Complex strategies are more likely to overfit:

```python
# Bad - too many parameters
if rsi < 28.5 and sma_7 > sma_23 and adx > 25.3:
    ...

# Good - simple and robust
if rsi < 30 and sma_10 > sma_20:
    ...
```

---

## Debugging

### Print Intermediate Values

```python
def generate_signals(data):
    rsi = RSI(data['close'], 14)
    print(f"RSI range: {rsi.min():.2f} - {rsi.max():.2f}")

    signals = pd.Series(0, index=data.index)
    signals[rsi < 30] = 1

    print(f"Buy signals: {(signals == 1).sum()}")
    return signals
```

### Check Signal Distribution

A good strategy should have reasonable signal frequency:

- Too few signals: Not enough trades to be statistically significant
- Too many signals: Probably noise, high transaction costs

---

## Next Steps

- [Backtesting Guide](backtesting.md) - Test your strategy
- [AI Assistant](ai-assistant.md) - Get help analyzing results
