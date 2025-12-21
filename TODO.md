# Trading Simulator - Development TODO

> An educational platform to test trading strategies and discover why most of them don't work.

---

## Phase 1: Foundation [COMPLETED]

- [x] Initialize Turborepo with pnpm workspace
- [x] Configure Next.js 16 with Tailwind + shadcn/ui
- [x] Configure FastAPI backend structure
- [x] Create Docker Compose setup (PostgreSQL, TimescaleDB, Redis, Celery)
- [x] Create SQLAlchemy models (User, Strategy, Backtest, CurrencyPair, Candle)
- [x] Setup Alembic migrations
- [x] Setup Google OAuth authentication (NextAuth v5)

---

## Phase 2: Backtesting System [IN PROGRESS - 90%]

### Backend (Completed)
- [x] Strategy base class with indicator support
- [x] Technical indicators library (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastic, ADX)
- [x] Backtesting engine with simulated broker
- [x] Performance metrics calculator (Sharpe, Sortino, Calmar, Max Drawdown, Win Rate)
- [x] Historical data loaders (HistData, CSV)
- [x] Data storage service for TimescaleDB
- [x] Backtest service layer
- [x] Built-in strategies:
  - [x] SMA Crossover
  - [x] RSI Overbought/Oversold
  - [x] MACD Signal Line
  - [x] **Random Strategy** (coin flip - the control group)
  - [x] **Buy and Hold** (the benchmark)
- [x] API endpoints:
  - [x] `GET /api/v1/backtests/strategies` - List strategies
  - [x] `POST /api/v1/backtests/` - Run backtest
  - [x] `POST /api/v1/backtests/compare` - Compare vs Random & Buy-and-Hold
  - [x] `GET /api/v1/backtests/{id}` - Get results

### Frontend (Completed)
- [x] Candlestick chart component (TradingView Lightweight Charts)
- [x] Backtest configuration page
- [x] Backtest results component with metrics display
- [x] Equity curve visualization
- [x] Trade list display
- [x] API client with React Query hooks

### Remaining
- [ ] Wire frontend backtest page to call actual API (currently uses mock data)
- [ ] Add "Compare with Random" button to UI
- [ ] Display comparison conclusion in results
- [ ] Add strategy code editor for custom strategies

---

## Phase 3: Paper Trading [60%]

### Frontend (Completed)
- [x] Trading page UI with order form
- [x] Watchlist component
- [x] Open positions table
- [x] Portfolio page with equity curve
- [x] Trade history page
- [x] Settings page
- [x] Help page

### Backend (Not Started)
- [ ] Trading engine
- [ ] Order manager (market, limit, stop-loss, take-profit)
- [ ] Position manager
- [ ] Margin calculator
- [ ] WebSocket for real-time price updates
- [ ] Portfolio tracking API

---

## Phase 4: AI Integration [NOT STARTED]

- [ ] OpenRouter + LangChain chat integration
- [ ] Trading chat assistant with custom tools
- [ ] Signal predictions (LSTM model)
- [ ] Pattern recognition
- [ ] Sentiment analysis (FinBERT)
- [ ] Risk assessment (VaR, position sizing)

---

## Infrastructure & Polish

- [ ] Add sample historical data download script
- [ ] Create database seed script
- [ ] Add unit tests for backtesting engine
- [ ] Add integration tests for API
- [ ] CI/CD pipeline
- [ ] Production Docker configuration
- [ ] Documentation site

---

## Quick Start

```bash
# Install dependencies
pnpm install

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d

# Run API
cd apps/api && uvicorn src.main:app --reload

# Run frontend
pnpm --filter web dev
```

---

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/backtests/strategies` | GET | List available strategies |
| `/api/v1/backtests/` | POST | Run a backtest |
| `/api/v1/backtests/compare` | POST | Compare strategy vs Random & Buy-and-Hold |
| `/api/v1/backtests/{id}` | GET | Get backtest results |
| `/api/v1/market/pairs` | GET | List currency pairs |
| `/api/v1/market/candles` | GET | Get OHLCV data |

---

## The Point

This simulator exists to demonstrate that most technical analysis strategies:

1. **Don't beat random chance** - The Random Strategy (coin flips) often performs similarly
2. **Don't beat buy-and-hold** - Simply holding is usually more profitable
3. **Look good in hindsight** - Overfitting to historical data is easy
4. **Fail after transaction costs** - Spreads and commissions eat into "profits"

The `/compare` endpoint is the educational core - it forces every strategy to be compared against these benchmarks and generates an honest conclusion.

---

*Built to save people from losing money to fake trading gurus.*
