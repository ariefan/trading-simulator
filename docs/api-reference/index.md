# API Reference

Complete reference for the Trading Simulator REST API.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints work without authentication for demo purposes. For user-specific data, use JWT tokens:

```bash
# Get a demo token
curl -X POST /api/v1/auth/demo -d '{"name": "Trader"}'

# Use the token
curl -H "Authorization: Bearer <token>" /api/v1/users/me
```

---

## Endpoints Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Authentication](authentication.md) | `/auth/*` | Login, tokens, verification |
| [Market Data](market.md) | `/market/*` | Pairs, candles, quotes |
| [Trading](trading.md) | `/trading/*` | Orders, positions, history |
| [Portfolio](portfolio.md) | `/portfolio/*` | Balance, metrics, allocation |
| [Backtesting](backtesting.md) | `/backtests/*`, `/strategies/*` | Run tests, manage strategies |
| [AI & Signals](ai-signals.md) | `/ai/*`, `/signals/*` | Chat, tools, analysis |

---

## Common Response Formats

### Success Response

```json
{
  "id": "abc123",
  "symbol": "EURUSD",
  "status": "success"
}
```

### Error Response

```json
{
  "detail": "Error message here"
}
```

### Paginated Response

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

---

## Rate Limiting

Currently no rate limiting in development mode.

Production recommendations:
- 100 requests per minute for most endpoints
- 10 requests per second for WebSocket subscriptions

---

## WebSocket

Real-time price feed:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/prices');

// Subscribe
ws.send(JSON.stringify({
  action: 'subscribe',
  symbols: ['EURUSD', 'GBPUSD']
}));

// Receive prices
ws.onmessage = (event) => {
  const price = JSON.parse(event.data);
  // { symbol, bid, ask, timestamp }
};
```

---

## Interactive Documentation

FastAPI provides automatic interactive docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
