# Backtesting Guide

Test your trading strategies against historical data and discover the truth about their performance.

## The Hard Truth

!!! warning "Most Strategies Fail"
    The backtesting system is designed to show you that most trading strategies:

    - Don't beat random chance
    - Don't beat buy-and-hold
    - Look good only because of overfitting
    - Fail after transaction costs

---

## Running a Backtest

### 1. Select a Strategy

| Strategy | Description |
|----------|-------------|
| SMA Crossover | Buy when fast SMA crosses above slow SMA |
| RSI | Buy oversold, sell overbought |
| MACD | Trade MACD/Signal line crossovers |
| Random | Coin flip decisions (the control) |
| Buy and Hold | Buy once and hold (the benchmark) |

### 2. Configure Parameters

```yaml
Symbol: EURUSD
Timeframe: 1H
Start Date: 2024-01-01
End Date: 2024-06-01
Initial Balance: $10,000
Leverage: 100
```

### 3. Run and Analyze

Click **Run Backtest** to execute. Results include:

- Equity curve
- Trade list
- Performance metrics
- Drawdown analysis

---

## Understanding Results

### Key Metrics

| Metric | Good | Bad | Description |
|--------|------|-----|-------------|
| Total Return | > 0% | < 0% | Overall profit/loss |
| Win Rate | > 50% | < 40% | Percentage of winning trades |
| Profit Factor | > 1.5 | < 1.0 | Gross profit / Gross loss |
| Sharpe Ratio | > 1.0 | < 0.5 | Risk-adjusted return |
| Max Drawdown | < 20% | > 30% | Largest peak-to-trough decline |

### The Comparison Feature

**This is the most important feature!**

Click **Compare with Random & Buy-and-Hold** to see honest results:

```
Strategy Results:     +15.2%
Random Strategy:      +12.8%
Buy and Hold:         +18.5%

Conclusion: Your strategy DOES NOT beat buy-and-hold.
Consider: Simply holding would have been more profitable.
```

---

## Built-in Strategies

### SMA Crossover

```python
# Buy when fast SMA > slow SMA
# Sell when fast SMA < slow SMA

Parameters:
- fast_period: 10 (default)
- slow_period: 20 (default)
```

**The Problem**: Works in trending markets, loses in ranging markets (most of the time).

### RSI Strategy

```python
# Buy when RSI < 30 (oversold)
# Sell when RSI > 70 (overbought)

Parameters:
- period: 14 (default)
- oversold: 30
- overbought: 70
```

**The Problem**: Markets can stay oversold/overbought longer than you can stay solvent.

### MACD Strategy

```python
# Buy when MACD crosses above signal line
# Sell when MACD crosses below signal line

Parameters:
- fast_period: 12
- slow_period: 26
- signal_period: 9
```

**The Problem**: Lagging indicator - by the time it signals, the move is often over.

### Random Strategy

```python
# Randomly decide to buy, sell, or hold
# 33% chance each

Parameters:
- seed: random (for reproducibility)
```

**The Purpose**: If your strategy doesn't beat random, it has no edge.

### Buy and Hold

```python
# Buy on first bar
# Hold until end

Parameters: None
```

**The Purpose**: The benchmark. If you can't beat this, why trade actively?

---

## Interpreting Comparisons

### Your Strategy Beats Both

```
Strategy: +25%
Random: +8%
Buy&Hold: +12%
```

!!! success "Potential Edge"
    Your strategy might have an edge, BUT:

    - Run multiple time periods
    - Check for overfitting
    - Test out-of-sample data
    - Account for transaction costs

### Your Strategy Beats Random Only

```
Strategy: +15%
Random: +5%
Buy&Hold: +20%
```

!!! warning "False Confidence"
    You're not adding value. Just holding would be better.

### Your Strategy Loses to Both

```
Strategy: +3%
Random: +8%
Buy&Hold: +18%
```

!!! danger "No Edge"
    Your strategy is destroying value. The market is random.

---

## Common Mistakes

### 1. Overfitting

Optimizing parameters until they work on historical data:

```python
# Bad: Tuned to perfection on past data
fast_period = 7
slow_period = 23
rsi_oversold = 28.5
```

**Solution**: Use out-of-sample testing.

### 2. Survivorship Bias

Only testing on pairs that still exist:

**Solution**: Include delisted pairs if possible.

### 3. Look-Ahead Bias

Using future data in signals:

```python
# Bad: Using tomorrow's close to decide today
signal = tomorrow_close > today_close
```

**Solution**: Only use data available at decision time.

### 4. Ignoring Transaction Costs

```python
# Gross return: +10%
# Spread costs: -3%
# Slippage: -2%
# Net return: +5%
```

**Solution**: Always include realistic costs.

---

## API Usage

### Run Backtest

```bash
POST /api/v1/backtests/
{
  "strategy_id": "sma_crossover",
  "symbol": "EURUSD",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-06-01",
  "initial_balance": 10000,
  "leverage": 100,
  "parameters": {
    "fast_period": 10,
    "slow_period": 20
  }
}
```

### Compare with Benchmarks

```bash
POST /api/v1/backtests/compare
{
  "strategy_id": "sma_crossover",
  "symbol": "EURUSD",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-06-01"
}
```

---

## Next Steps

- [Custom Strategies](custom-strategies.md) - Write your own strategies
- [AI Assistant](ai-assistant.md) - Get help analyzing results
