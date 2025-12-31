# Quick Start

Get up and trading in 5 minutes!

## Start the Services

```bash
# Terminal 1: Start API
cd apps/api
source .venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Start Frontend
pnpm --filter web dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Your First Trade

### 1. Open the Trading Page

Navigate to the **Trading** page from the sidebar. You'll see:

- Real-time price chart for EUR/USD
- Order form on the right
- Your positions below

### 2. Place a Market Order

1. Select a currency pair (e.g., EUR/USD)
2. Choose **Buy** or **Sell**
3. Enter position size (e.g., 0.1 lots)
4. Optionally set Stop Loss and Take Profit
5. Click **Place Order**

!!! tip "Start Small"
    Begin with 0.1 lots to understand how position sizing affects your P&L.

### 3. Monitor Your Position

Your position will appear in the **Open Positions** table with:

- Current price
- Unrealized P&L
- Entry price
- Position size

### 4. Close the Position

Click **Close** on your position to realize the profit or loss.

---

## Your First Backtest

### 1. Open the Backtest Page

Navigate to **Backtest** from the sidebar.

### 2. Configure the Backtest

| Setting | Value |
|---------|-------|
| Strategy | SMA Crossover |
| Symbol | EUR/USD |
| Timeframe | 1H |
| Start Date | 2024-01-01 |
| End Date | 2024-03-01 |
| Initial Balance | $10,000 |

### 3. Run the Backtest

Click **Run Backtest** and wait for results.

### 4. Compare with Benchmarks

Click **Compare with Random & Buy-and-Hold** to see how your strategy performs against:

- **Random Strategy**: Makes random buy/sell decisions
- **Buy and Hold**: Simply buys and holds

!!! warning "The Truth Hurts"
    Most strategies don't beat random chance or buy-and-hold. That's the point of this simulator!

---

## Using the AI Assistant

### 1. Open the Assistant

Navigate to **AI Assistant** from the sidebar.

### 2. Ask Questions

Try these prompts:

- "What's my portfolio balance?"
- "Show my open positions"
- "Calculate position size for $10,000 account, 1% risk, 20 pip stop loss"
- "Analyze trade: buy EURUSD at 1.0850, SL 1.0800, TP 1.0950"

### 3. Get Insights

The AI can help with:

- Portfolio summary
- Position sizing
- Risk/reward analysis
- Performance metrics

---

## Key Concepts

### Paper Trading

Paper trading uses **virtual money** (default: $100,000) to practice trading without risk.

- Prices are simulated but realistic
- All orders execute at market prices
- P&L is calculated in real-time

### Leverage

The simulator uses **100:1 leverage** by default:

- 1 standard lot (100,000 units) requires $1,000 margin
- Profits and losses are magnified
- Margin calls occur if equity falls too low

### Pip Values

| Pair | 1 Pip | Value per Lot |
|------|-------|---------------|
| EUR/USD | 0.0001 | $10 |
| GBP/USD | 0.0001 | $10 |
| USD/JPY | 0.01 | ~$7 |

---

## Next Steps

<div class="grid cards" markdown>

-   [:material-chart-line: Paper Trading Guide](../guides/paper-trading.md)

    Learn advanced trading features

-   [:material-history: Backtesting Guide](../guides/backtesting.md)

    Test and compare strategies

-   [:material-code-braces: Custom Strategies](../guides/custom-strategies.md)

    Write your own trading strategies

</div>
