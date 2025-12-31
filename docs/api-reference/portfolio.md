# Portfolio API

Endpoints for portfolio summary, history, and performance metrics.

## Portfolio Summary

### GET `/portfolio/`

Get current portfolio summary.

**Response:**
```json
{
  "balance": 100450.00,
  "equity": 100650.00,
  "margin": 2170.00,
  "free_margin": 98480.00,
  "margin_level": 4637.79,
  "unrealized_pnl": 200.00,
  "positions_count": 2
}
```

**Fields:**

| Field | Description |
|-------|-------------|
| `balance` | Cash balance (excluding unrealized P&L) |
| `equity` | Balance + unrealized P&L |
| `margin` | Margin used by open positions |
| `free_margin` | Available margin for new positions |
| `margin_level` | Equity / Margin × 100 |
| `unrealized_pnl` | P&L of open positions |

---

## Portfolio History

### GET `/portfolio/history`

Get equity history over time.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | int | 30 | Number of days |

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "balance": 100000.00,
    "equity": 100000.00
  },
  {
    "timestamp": "2024-01-02T00:00:00Z",
    "balance": 100150.00,
    "equity": 100320.00
  }
]
```

---

## Performance Metrics

### GET `/portfolio/metrics`

Get trading performance statistics.

**Response:**
```json
{
  "total_trades": 45,
  "winning_trades": 22,
  "losing_trades": 23,
  "win_rate": 48.89,
  "profit_factor": 1.35,
  "total_pnl": 2450.00,
  "average_win": 185.50,
  "average_loss": 125.30,
  "largest_win": 520.00,
  "largest_loss": 280.00,
  "max_drawdown": 8.5,
  "sharpe_ratio": 1.25,
  "sortino_ratio": 1.82
}
```

**Key Metrics:**

| Metric | Description | Good Value |
|--------|-------------|------------|
| Win Rate | % of winning trades | > 50% |
| Profit Factor | Gross profit / Gross loss | > 1.5 |
| Max Drawdown | Largest peak-to-trough decline | < 20% |
| Sharpe Ratio | Risk-adjusted return | > 1.0 |

---

## Position Allocation

### GET `/portfolio/allocation`

Get position allocation by symbol.

**Response:**
```json
{
  "allocations": [
    {
      "symbol": "EURUSD",
      "positions": 1,
      "total_size": 0.2,
      "margin_used": 2170.00,
      "unrealized_pnl": 150.00,
      "percentage": 65.5
    },
    {
      "symbol": "GBPUSD",
      "positions": 1,
      "total_size": 0.1,
      "margin_used": 1270.00,
      "unrealized_pnl": 50.00,
      "percentage": 34.5
    }
  ],
  "total_margin": 3440.00,
  "total_unrealized_pnl": 200.00
}
```
