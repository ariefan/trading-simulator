# Trading Simulator - Development TODO

> An educational platform to test trading strategies and discover why most of them don't work.

---

## Phase 1: Foundation [COMPLETED]

- [x] Initialize Turborepo with pnpm workspace
- [x] Configure Next.js 16 with Tailwind CSS 4 + shadcn/ui
- [x] Configure FastAPI backend structure
- [x] Create Docker Compose setup (PostgreSQL, TimescaleDB, Redis, Celery)
- [x] Create SQLAlchemy models (User, Strategy, Backtest, CurrencyPair, Candle)
- [x] Setup Alembic migrations
- [x] Setup Google OAuth authentication (NextAuth v5 frontend skeleton - backend verification not implemented)

---

## Phase 2: Backtesting System [COMPLETED]

### Backend (Completed)
- [x] Strategy base class with indicator support
- [x] Technical indicators library (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Stochastic, ADX, OBV, VWAP, Pivot Points)
- [x] Backtesting engine with simulated broker
- [x] Performance metrics calculator (Sharpe, Sortino, Calmar, Max Drawdown, Win Rate)
- [x] Historical data loaders (CSV loader complete, HistData stub)
- [x] Data storage service for TimescaleDB (structure only - uses synthetic data)
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
- [x] Celery backtest task (runs actual backtest engine)
- [x] Custom strategy CRUD endpoints:
  - [x] `GET /api/v1/strategies/` - List custom strategies
  - [x] `POST /api/v1/strategies/` - Create strategy with code validation
  - [x] `GET /api/v1/strategies/{id}` - Get strategy
  - [x] `PUT /api/v1/strategies/{id}` - Update strategy
  - [x] `DELETE /api/v1/strategies/{id}` - Delete strategy
  - [x] `GET /api/v1/strategies/templates` - Get strategy templates

### Frontend (Completed)
- [x] Candlestick chart component (TradingView Lightweight Charts)
- [x] Backtest configuration page
- [x] Backtest results component with metrics display
- [x] Equity curve visualization
- [x] Trade list display
- [x] API client with React Query hooks
- [x] Frontend wired to actual backend API
- [x] "Compare with Random & Buy-and-Hold" button
- [x] Comparison results table with conclusion display
- [x] Strategy code editor with templates
- [x] Strategy CRUD UI (create, edit, delete, list)

---

## Phase 3: Paper Trading [COMPLETED]

### Frontend (Completed)
- [x] Trading page UI with order form
- [x] Watchlist component with live bid/ask prices
- [x] Open positions table
- [x] Portfolio page with equity curve
- [x] Trade history page
- [x] Settings page
- [x] Help page
- [x] Frontend wired to actual trading API
- [x] Frontend wired to actual portfolio API
- [x] WebSocket client with auto-reconnect

### Backend (Completed)
- [x] Trading engine (in-memory state management)
- [x] Order manager (market, limit, stop-loss, take-profit)
- [x] Position manager with P&L calculation
- [x] Margin calculator (leverage-based)
- [x] Portfolio tracking API (summary, history, metrics, allocation)
- [x] WebSocket for real-time price updates (simulated tick data)

### API Endpoints (Trading)
- [x] `POST /api/v1/trading/orders` - Place order
- [x] `GET /api/v1/trading/orders` - List orders
- [x] `DELETE /api/v1/trading/orders/{id}` - Cancel order
- [x] `GET /api/v1/trading/positions` - List positions
- [x] `POST /api/v1/trading/positions/{id}/close` - Close position
- [x] `GET /api/v1/trading/history` - Trade history
- [x] `POST /api/v1/trading/reset` - Reset account

### API Endpoints (Portfolio)
- [x] `GET /api/v1/portfolio/` - Portfolio summary
- [x] `GET /api/v1/portfolio/history` - Equity history
- [x] `GET /api/v1/portfolio/metrics` - Performance metrics
- [x] `GET /api/v1/portfolio/allocation` - Position allocation

### WebSocket Endpoints
- [x] `WS /api/v1/ws/prices` - Real-time price feed (subscribe/unsubscribe)

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

- [ ] Implement backend Google OAuth verification (auth.py returns 501)
- [ ] Implement user profile endpoints (users.py returns 401)
- [ ] Add real market data fetching (market.py returns empty data)
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

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/v1/backtests/strategies` | GET | List available strategies | ✅ Working |
| `/api/v1/backtests/` | POST | Run a backtest | ✅ Working |
| `/api/v1/backtests/compare` | POST | Compare strategy vs Random & Buy-and-Hold | ✅ Working |
| `/api/v1/backtests/{id}` | GET | Get backtest results | ✅ Working |
| `/api/v1/strategies/` | GET | List custom strategies | ✅ Working |
| `/api/v1/strategies/` | POST | Create custom strategy | ✅ Working |
| `/api/v1/strategies/{id}` | GET/PUT/DELETE | Strategy CRUD | ✅ Working |
| `/api/v1/strategies/templates` | GET | Get strategy templates | ✅ Working |
| `/api/v1/trading/orders` | GET/POST | List/Place orders | ✅ Working |
| `/api/v1/trading/orders/{id}` | DELETE | Cancel order | ✅ Working |
| `/api/v1/trading/positions` | GET | List open positions | ✅ Working |
| `/api/v1/trading/positions/{id}/close` | POST | Close position | ✅ Working |
| `/api/v1/trading/history` | GET | Trade history | ✅ Working |
| `/api/v1/portfolio/` | GET | Portfolio summary | ✅ Working |
| `/api/v1/portfolio/history` | GET | Equity history | ✅ Working |
| `/api/v1/portfolio/metrics` | GET | Performance metrics | ✅ Working |
| `/api/v1/portfolio/allocation` | GET | Position allocation | ✅ Working |
| `/api/v1/ws/prices` | WebSocket | Real-time price feed | ✅ Working |
| `/api/v1/market/pairs` | GET | List currency pairs | ⚠️ Stub |
| `/api/v1/market/candles` | GET | Get OHLCV data | ⚠️ Stub (returns empty) |
| `/api/v1/auth/google` | POST | Google OAuth verification | ❌ 501 Not Implemented |
| `/api/v1/users/me` | GET | Get current user | ❌ 401 (no auth) |

---

## The Point

This simulator exists to demonstrate that most technical analysis strategies:

1. **Don't beat random chance** - The Random Strategy (coin flips) often performs similarly
2. **Don't beat buy-and-hold** - Simply holding is usually more profitable
3. **Look good in hindsight** - Overfitting to historical data is easy
4. **Fail after transaction costs** - Spreads and commissions eat into "profits"

The `/compare` endpoint is the educational core - it forces every strategy to be compared against these benchmarks and generates an honest conclusion.

---

## Tech Stack

### Frontend (apps/web)
| Package | Version |
|---------|---------|
| Next.js | ^16.1.0 |
| React | ^19.2.0 |
| Tailwind CSS | ^4.1.0 |
| Zustand | ^5.0.0 |
| TanStack Query | ^5.0.0 |
| Recharts | ^3.6.0 |
| Lightweight Charts | ^5.1.0 |
| Lucide React | ^0.561.0 |
| NextAuth | ^5.0.0 |

### Backend (apps/api)
| Package | Version |
|---------|---------|
| FastAPI | >=0.125.0 |
| Uvicorn | >=0.39.0 |
| Pydantic | >=2.12.0 |
| SQLAlchemy | >=2.0.0 |
| Celery | >=5.5.0 |
| Redis | >=7.1.0 |
| NumPy | >=2.2.0 |
| Pandas | >=2.3.0 |
| Python | >=3.11 |

### Build Tools
| Package | Version |
|---------|---------|
| Turborepo | ^2.7.0 |
| pnpm | 9.0.0 |
| TypeScript | ^5.7.0 |

---

*Built to save people from losing money to fake trading gurus.*
