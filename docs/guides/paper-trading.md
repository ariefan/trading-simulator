# Paper Trading Guide

Paper trading allows you to practice trading with virtual money in real-time market conditions.

## Overview

- **Starting Balance**: $100,000 (configurable)
- **Leverage**: Up to 100:1
- **Real-time Prices**: WebSocket-based live feeds
- **Full Order Types**: Market, limit, stop orders

---

## The Trading Interface

### Price Chart

The main chart shows:

- Candlestick price data
- Current bid/ask prices
- Your entry/exit levels (when in a position)

### Order Panel

| Field | Description |
|-------|-------------|
| Symbol | Currency pair to trade |
| Side | Buy (long) or Sell (short) |
| Size | Position size in lots |
| Type | Market, Limit, or Stop |
| Stop Loss | Automatic loss limit |
| Take Profit | Automatic profit target |

### Positions Table

Shows all open positions with:

- Symbol and direction
- Entry price
- Current price
- Unrealized P&L
- Close button

---

## Placing Orders

### Market Order

Executes immediately at current market price.

```
Symbol: EURUSD
Side: Buy
Size: 0.1 lots
Type: Market
→ Filled at 1.0850
```

### Limit Order

Executes when price reaches your level.

```
Symbol: EURUSD
Side: Buy
Size: 0.1 lots
Type: Limit
Price: 1.0800  # Below current price
→ Pending until price hits 1.0800
```

### Stop Order

Executes when price moves against you.

```
Symbol: EURUSD
Side: Sell
Size: 0.1 lots
Type: Stop
Price: 1.0900  # Above current price
→ Triggers sell if price rises to 1.0900
```

---

## Position Management

### Stop Loss

Automatically closes position at a loss limit:

```
Position: Long EURUSD at 1.0850
Stop Loss: 1.0800 (50 pips)
Risk: 0.1 lots × 50 pips × $10 = $50
```

### Take Profit

Automatically closes position at a profit target:

```
Position: Long EURUSD at 1.0850
Take Profit: 1.0950 (100 pips)
Potential: 0.1 lots × 100 pips × $10 = $100
```

### Risk/Reward Ratio

!!! tip "Aim for 2:1 or better"
    A 2:1 risk/reward means you need to win only 33% of trades to break even.

---

## Understanding P&L

### Pip Value Calculation

For EUR/USD (standard lot = 100,000 units):

```
1 pip = 0.0001
Pip value = 100,000 × 0.0001 = $10 per lot
```

### Example P&L

```
Position: 0.1 lots Long EURUSD
Entry: 1.0850
Exit: 1.0870

Pips gained: 20 pips
P&L = 0.1 × 20 × $10 = $20
```

---

## Margin & Leverage

### How Leverage Works

With 100:1 leverage:

```
Position value: 1 lot × $108,500 = $108,500
Required margin: $108,500 / 100 = $1,085
```

### Margin Call

If your equity falls below required margin:

!!! danger "Margin Call"
    Positions may be automatically closed to prevent negative balance.

### Safe Position Sizing

Never risk more than 1-2% per trade:

```
Account: $10,000
Risk per trade: 1% = $100
Stop loss: 20 pips = $20 per 0.1 lot
Max size: $100 / $20 = 0.5 lots
```

---

## Best Practices

1. **Start Small**: Use 0.1 lots until you understand the mechanics
2. **Always Use Stop Losses**: Protect your capital
3. **Track Your Performance**: Review your trading history
4. **Don't Overtrade**: Quality over quantity
5. **Keep a Trading Journal**: Learn from your mistakes

---

## API Endpoints

### Place Order

```bash
POST /api/v1/trading/orders
{
  "symbol": "EURUSD",
  "side": "buy",
  "type": "market",
  "size": 0.1,
  "stop_loss": 1.0800,
  "take_profit": 1.0950
}
```

### Close Position

```bash
POST /api/v1/trading/positions/{id}/close
```

### Get Positions

```bash
GET /api/v1/trading/positions
```

---

## Next Steps

- [Backtesting Guide](backtesting.md) - Test strategies before trading
- [AI Assistant](ai-assistant.md) - Get help with position sizing
