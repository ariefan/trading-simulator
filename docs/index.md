# Trading Simulator

An educational forex trading platform designed to test strategies and discover why most of them don't work.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Get Started in Minutes__

    ---

    Install the trading simulator and start paper trading or backtesting in under 5 minutes.

    [:octicons-arrow-right-24: Getting Started](getting-started/index.md)

-   :material-chart-line:{ .lg .middle } __Paper Trading__

    ---

    Practice trading with virtual money. Real-time price feeds, order management, and portfolio tracking.

    [:octicons-arrow-right-24: Paper Trading Guide](guides/paper-trading.md)

-   :material-history:{ .lg .middle } __Backtesting__

    ---

    Test your strategies against historical data. Compare with random and buy-and-hold benchmarks.

    [:octicons-arrow-right-24: Backtesting Guide](guides/backtesting.md)

-   :material-robot:{ .lg .middle } __AI Assistant__

    ---

    Chat with an AI trading assistant for portfolio insights, risk calculations, and trade analysis.

    [:octicons-arrow-right-24: AI Assistant](guides/ai-assistant.md)

</div>

---

## The Point

This simulator exists to demonstrate that most technical analysis strategies:

1. **Don't beat random chance** - The Random Strategy (coin flips) often performs similarly
2. **Don't beat buy-and-hold** - Simply holding is usually more profitable
3. **Look good in hindsight** - Overfitting to historical data is easy
4. **Fail after transaction costs** - Spreads and commissions eat into "profits"

The `/compare` endpoint is the educational core - it forces every strategy to be compared against these benchmarks and generates an honest conclusion.

---

## Features

### Paper Trading
- Real-time simulated price feeds via WebSocket
- Market, limit, and stop orders
- Position management with stop-loss and take-profit
- Portfolio tracking with equity curves
- Performance metrics (Sharpe ratio, win rate, drawdown)

### Backtesting Engine
- Built-in strategies (SMA Crossover, RSI, MACD)
- **Random Strategy** - the control group
- **Buy and Hold** - the benchmark to beat
- Custom strategy support with Python code
- Automatic comparison and honest conclusions

### AI Integration
- Chat assistant with trading tools
- Technical signal generation
- Pattern recognition
- Risk assessment
- Position sizing calculator

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ariefan/trading-simulator.git
cd trading-simulator

# Install dependencies
pnpm install

# Start the API
cd apps/api
pip install -r requirements.txt
uvicorn src.main:app --reload

# Start the frontend (new terminal)
pnpm --filter web dev
```

Open [http://localhost:3000](http://localhost:3000) to start trading!

---

## Tech Stack

=== "Frontend"

    | Package | Version |
    |---------|---------|
    | Next.js | ^16.1.0 |
    | React | ^19.2.0 |
    | Tailwind CSS | ^4.1.0 |
    | TanStack Query | ^5.0.0 |
    | Lightweight Charts | ^5.1.0 |

=== "Backend"

    | Package | Version |
    |---------|---------|
    | FastAPI | >=0.125.0 |
    | Uvicorn | >=0.39.0 |
    | Pydantic | >=2.12.0 |
    | NumPy | >=2.2.0 |
    | Pandas | >=2.3.0 |

=== "Infrastructure"

    | Component | Version |
    |-----------|---------|
    | PostgreSQL | 15 (TimescaleDB) |
    | Redis | 7 |
    | Celery | 5.5 |
    | Docker | 24+ |

---

## License

MIT License - Built to save people from losing money to fake trading gurus.
