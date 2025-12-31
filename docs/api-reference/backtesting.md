# Backtesting API

Endpoints for running backtests and managing strategies.

## Run Backtest

### POST `/backtests/`

Run a new backtest.

**Request:**
```json
{
  "strategy_id": "sma_crossover",
  "symbol": "EURUSD",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-03-01",
  "initial_balance": 10000,
  "leverage": 100,
  "parameters": {
    "fast_period": 10,
    "slow_period": 20
  }
}
```

**Response:**
```json
{
  "id": "bt_123",
  "status": "completed",
  "metrics": {
    "total_return_percent": 12.5,
    "total_trades": 25,
    "winning_trades": 14,
    "losing_trades": 11,
    "win_rate": 56.0,
    "profit_factor": 1.65,
    "sharpe_ratio": 1.2,
    "max_drawdown": 8.5
  },
  "trades": [...],
  "equity_curve": [...]
}
```

---

## Compare with Benchmarks

### POST `/backtests/compare`

Compare strategy with Random and Buy-and-Hold.

**Request:**
```json
{
  "strategy_id": "sma_crossover",
  "symbol": "EURUSD",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-03-01",
  "parameters": {}
}
```

**Response:**
```json
{
  "strategy": {
    "name": "SMA Crossover",
    "return_percent": 12.5,
    "sharpe_ratio": 1.2,
    "max_drawdown": 8.5
  },
  "random": {
    "name": "Random Strategy",
    "return_percent": 8.2,
    "sharpe_ratio": 0.6,
    "max_drawdown": 12.3
  },
  "buy_and_hold": {
    "name": "Buy and Hold",
    "return_percent": 15.8,
    "sharpe_ratio": 1.4,
    "max_drawdown": 6.2
  },
  "conclusion": {
    "beats_random": true,
    "beats_buy_hold": false,
    "recommendation": "Your strategy beats random but not buy-and-hold. Consider if active trading is worth the effort."
  }
}
```

---

## List Strategies

### GET `/backtests/strategies`

List available built-in strategies.

**Response:**
```json
[
  {
    "id": "sma_crossover",
    "name": "SMA Crossover",
    "description": "Buy when fast SMA crosses above slow SMA",
    "parameters": {
      "fast_period": {"type": "int", "default": 10},
      "slow_period": {"type": "int", "default": 20}
    }
  },
  {
    "id": "rsi",
    "name": "RSI Strategy",
    "description": "Trade overbought/oversold conditions",
    "parameters": {
      "period": {"type": "int", "default": 14},
      "overbought": {"type": "int", "default": 70},
      "oversold": {"type": "int", "default": 30}
    }
  }
]
```

---

## Custom Strategies

### GET `/strategies/`

List custom strategies.

### POST `/strategies/`

Create a custom strategy.

**Request:**
```json
{
  "name": "My Strategy",
  "description": "A custom trading strategy",
  "code": "def generate_signals(data):\n    ...",
  "parameters": {"period": 14}
}
```

### GET `/strategies/{id}`

Get a specific strategy.

### PUT `/strategies/{id}`

Update a strategy.

### DELETE `/strategies/{id}`

Delete a strategy.

### GET `/strategies/templates`

Get strategy code templates.
