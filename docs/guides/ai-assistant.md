# AI Assistant Guide

The AI trading assistant helps you with portfolio analysis, position sizing, and trade planning.

## Overview

The assistant can:

- Query your portfolio and positions
- Calculate position sizes based on risk
- Analyze trade setups
- Provide performance metrics
- Answer trading questions

---

## Chatting with the Assistant

### Portfolio Queries

**"What's my portfolio balance?"**

```
Account Summary:
- Balance: $100,000.00
- Equity: $100,450.00
- Free Margin: $98,450.00
- Margin Used: $2,000.00
- Unrealized P&L: +$450.00
```

**"Show my open positions"**

```
Open Positions:
- EURUSD LONG: 0.2 lots @ 1.0850 → P&L: +$450.00
- GBPUSD SHORT: 0.1 lots @ 1.2700 → P&L: -$120.00
```

### Performance Analysis

**"Show my trading performance"**

```
Trading Performance:
- Total Trades: 25
- Win Rate: 48%
- Profit Factor: 1.35
- Average Win: $285
- Average Loss: $210
- Max Drawdown: 8.5%
```

---

## Position Sizing

### The 1% Rule

Never risk more than 1-2% of your account on a single trade.

**"Calculate position size for $10,000 account, 1% risk, 20 pip stop loss"**

```
Position Size Calculation:
- Account Balance: $10,000
- Risk: 1% ($100)
- Stop Loss: 20 pips
- Recommended Size: 0.5 lots

This ensures you only risk 1% on this trade.
```

### Formula

```
Position Size = Risk Amount / (Stop Loss Pips × Pip Value)

Example:
Risk Amount = $10,000 × 1% = $100
Stop Loss = 20 pips
Pip Value = $10 per standard lot

Size = $100 / (20 × $10) = 0.5 lots
```

---

## Trade Analysis

### Risk/Reward Analysis

**"Analyze trade: buy EURUSD at 1.0850, SL 1.0800, TP 1.0950"**

```
Trade Analysis:
- Symbol: EURUSD
- Side: BUY
- Entry: 1.0850
- Stop Loss: 1.0800 (50 pips)
- Take Profit: 1.0950 (100 pips)
- Risk/Reward: 2.0:1

Analysis:
✓ Good risk/reward ratio (2:1 or better)
✓ Reasonable stop loss distance
```

### What Makes a Good Trade?

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Risk/Reward | 3:1+ | 2:1 | <1:1 |
| Stop Loss | 20-50 pips | 50-100 pips | >100 pips |
| Win Rate Needed | 25%+ | 33%+ | 50%+ |

---

## Available Tools

The AI has access to these tools:

### Portfolio Tools

| Tool | Description |
|------|-------------|
| `get_portfolio` | Account summary |
| `get_positions` | Open positions |
| `get_trade_history` | Closed trades |
| `get_performance_metrics` | Trading statistics |

### Trading Tools

| Tool | Description |
|------|-------------|
| `place_order` | Open a new position |
| `close_position` | Close an existing position |
| `get_market_prices` | Current bid/ask prices |

### Analysis Tools

| Tool | Description |
|------|-------------|
| `calculate_position_size` | Risk-based sizing |
| `analyze_trade` | Risk/reward analysis |

---

## Example Conversations

### Planning a Trade

```
You: I want to buy EURUSD. Current price is 1.0850.
     What position size for 1% risk with 30 pip stop?

AI: For a 1% risk trade with 30 pip stop loss:

    Account Balance: $100,000
    Risk Amount: $1,000 (1%)
    Stop Loss: 30 pips = $300 per lot

    Recommended Size: 0.33 lots

    This will risk exactly $1,000 if stopped out.
```

### Reviewing Performance

```
You: How am I doing this month?

AI: Your Trading Performance:
    - Total Trades: 12
    - Winning: 5 (41.7%)
    - Losing: 7 (58.3%)
    - Net P&L: -$450

    Analysis: Your win rate is below 50%, but that's okay
    if your winners are bigger than your losers.

    Average Win: $380
    Average Loss: $285
    Profit Factor: 0.95

    Recommendation: Focus on improving your entry timing
    or widening your take profit targets.
```

### Quick Price Check

```
You: What are current prices?

AI: Current Market Prices:
    - EURUSD: 1.0848 / 1.0850
    - GBPUSD: 1.2698 / 1.2700
    - USDJPY: 149.48 / 149.50
    - AUDUSD: 0.6548 / 0.6550
```

---

## API Usage

### Chat Endpoint

```bash
POST /api/v1/ai/chat
{
  "messages": [
    {"role": "user", "content": "What's my portfolio balance?"}
  ]
}
```

### Direct Tool Execution

```bash
POST /api/v1/ai/tools/calculate_position_size
{
  "account_balance": 10000,
  "risk_percent": 1,
  "stop_loss_pips": 20,
  "symbol": "EURUSD"
}
```

### List Available Tools

```bash
GET /api/v1/ai/tools
```

---

## Limitations

!!! warning "Not Financial Advice"
    The AI assistant is for educational purposes only:

    - It does NOT predict market direction
    - It does NOT recommend specific trades
    - It provides calculations and analysis only
    - Always do your own research

---

## Next Steps

- [Paper Trading](paper-trading.md) - Practice with virtual money
- [Backtesting](backtesting.md) - Test your strategies
