# Forex Trading Simulator

**An educational platform to test trading strategies and discover why most of them don't work.**

## Why This Exists

The internet is full of trading "gurus" selling courses, signals, and dreams of financial freedom. They show cherry-picked wins, fancy charts, and promise that *their* strategy is the one that works.

This project exists to let you test those claims yourself.

Backtest any strategy on real historical data. See the actual win rate, drawdowns, and risk-adjusted returns. Compare your carefully crafted technical analysis against a coin flip.

**Spoiler:** The coin flip often wins.

## What You'll Learn

- Most technical analysis strategies perform no better than random chance
- Past performance genuinely does not predict future results
- Transaction costs and spreads eat into "profitable" strategies
- Survivorship bias explains why your favorite YouTuber seems successful
- The house (brokers, course sellers) always wins

## Features

### Backtesting Engine
Test strategies on historical forex data. Get real metrics:
- **Sharpe Ratio** - Risk-adjusted returns (spoiler: usually bad)
- **Maximum Drawdown** - How much you would have lost at the worst point
- **Win Rate** - Often around 50%, just like random
- **Profit Factor** - Usually close to 1.0 after costs

### Built-in Strategies
We include the classics so you can watch them fail:
- SMA Crossover
- RSI Overbought/Oversold
- MACD Signal Line
- Bollinger Band Breakout
- *Random Strategy* - For comparison (surprisingly competitive)

### Paper Trading
Practice trading with fake money. Experience the emotional rollercoaster without the financial ruin.

### Honest Metrics
No cherry-picked results. Full equity curves showing every drawdown. Monthly returns including the bad months.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + TimescaleDB |
| Task Queue | Celery + Redis |
| Monorepo | Turborepo + pnpm |
| Auth | Google OAuth |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- pnpm (`npm install -g pnpm`)

### Setup

```bash
# Clone and install
git clone <repo-url>
cd trading-simulator
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with your credentials (Google OAuth, etc.)

# Start everything
docker-compose up -d

# Or start services individually for development:
docker-compose up -d db redis    # Database and cache
cd apps/api && uvicorn src.main:app --reload  # Backend
pnpm --filter web dev            # Frontend
```

### Access
- **App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
trading-simulator/
├── apps/
│   ├── web/                 # Next.js frontend
│   │   ├── src/app/         # Pages (App Router)
│   │   └── src/components/  # React components
│   └── api/                 # FastAPI backend
│       ├── src/core/        # Backtesting engine
│       ├── src/models/      # Database models
│       └── src/api/         # REST endpoints
├── docker-compose.yml       # Full stack orchestration
└── turbo.json               # Monorepo config
```

## Example: Testing a Strategy

```python
from src.core.backtesting import Strategy, SMA, crossover

class SMACrossover(Strategy):
    """
    The classic "golden cross" strategy.
    Beloved by YouTube traders. Let's see how it actually performs.
    """
    fast_period = 10
    slow_period = 20

    def init(self):
        self.sma_fast = self.I(SMA, self.data['close'], self.fast_period)
        self.sma_slow = self.I(SMA, self.data['close'], self.slow_period)

    def next(self):
        if crossover(self.sma_fast, self.sma_slow):
            self.buy()
        elif crossover(self.sma_slow, self.sma_fast):
            self.sell()

# Typical results after backtesting:
# - Total Return: -3.2%
# - Sharpe Ratio: 0.12
# - Win Rate: 48%
# - Max Drawdown: 18%
#
# Meanwhile, buy-and-hold: +7%
```

## The Hard Truth

If technical analysis consistently worked:
- Banks would use it (they don't, they use information advantages)
- Algorithms would have arbitraged it away decades ago
- The people selling courses would be trading, not teaching

This simulator won't make you rich. It might save you from losing money chasing patterns that don't exist.

## FAQ

**Q: But I saw someone make money with technical analysis!**
A: Survivorship bias. You don't see the thousands who lost. Also, some people win at casinos.

**Q: What about [specific indicator]?**
A: Add it to the simulator and test it. That's the point.

**Q: Are you saying all trading is gambling?**
A: No. Informed trading based on fundamental analysis, market structure, and information edges can work. Drawing lines on charts and expecting them to predict the future is the problem.

**Q: This is depressing.**
A: Knowing the truth before losing your savings is less depressing than the alternative.

## Contributing

Found a strategy that actually works consistently? Open a PR. We'd love to be proven wrong.

More likely: found a bug, have a feature idea, or want to add more indicators to test? Contributions welcome.

## License

MIT - Use this however you want. Teach others. Save someone from a bad trade.

---

*Built by a nerd who got tired of seeing people lose money to fake gurus.*
