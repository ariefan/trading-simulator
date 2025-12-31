# Market Data API

Endpoints for currency pairs, candles, and price quotes.

## Currency Pairs

### GET `/market/pairs`

List all available currency pairs.

**Response:**
```json
[
  {
    "symbol": "EURUSD",
    "base_currency": "EUR",
    "quote_currency": "USD",
    "pip_value": 0.0001,
    "min_lot_size": 0.01,
    "max_lot_size": 100.0,
    "max_leverage": 100,
    "is_active": true
  },
  {
    "symbol": "GBPUSD",
    "base_currency": "GBP",
    "quote_currency": "USD",
    "pip_value": 0.0001,
    "min_lot_size": 0.01,
    "max_lot_size": 100.0,
    "max_leverage": 100,
    "is_active": true
  }
]
```

### GET `/market/pairs/{symbol}`

Get details for a specific currency pair.

**Response:**
```json
{
  "symbol": "EURUSD",
  "base_currency": "EUR",
  "quote_currency": "USD",
  "pip_value": 0.0001,
  "min_lot_size": 0.01,
  "max_lot_size": 100.0,
  "max_leverage": 100,
  "is_active": true
}
```

**Error (404):**
```json
{
  "detail": "Currency pair INVALID not found"
}
```

---

## Candle Data

### GET `/market/candles/{symbol}`

Get OHLCV candle data for a symbol.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeframe` | string | `1h` | Candle timeframe |
| `start` | string | - | Start datetime (ISO 8601) |
| `end` | string | - | End datetime (ISO 8601) |
| `limit` | int | 100 | Max candles to return |

**Timeframes:**

| Value | Description |
|-------|-------------|
| `1m` | 1 minute |
| `5m` | 5 minutes |
| `15m` | 15 minutes |
| `30m` | 30 minutes |
| `1h` | 1 hour |
| `4h` | 4 hours |
| `1d` | 1 day |

**Example:**
```bash
GET /market/candles/EURUSD?timeframe=1h&limit=24
```

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "1h",
  "candles": [
    {
      "timestamp": "2024-01-15T10:00:00Z",
      "open": 1.0845,
      "high": 1.0858,
      "low": 1.0840,
      "close": 1.0852,
      "volume": 15420
    },
    {
      "timestamp": "2024-01-15T11:00:00Z",
      "open": 1.0852,
      "high": 1.0865,
      "low": 1.0848,
      "close": 1.0860,
      "volume": 12350
    }
  ]
}
```

---

## Price Quotes

### GET `/market/quotes`

Get current bid/ask prices for all pairs.

**Response:**
```json
{
  "quotes": [
    {
      "symbol": "EURUSD",
      "bid": 1.0848,
      "ask": 1.0850,
      "spread": 0.0002,
      "timestamp": "2024-01-15T12:30:45Z"
    },
    {
      "symbol": "GBPUSD",
      "bid": 1.2698,
      "ask": 1.2700,
      "spread": 0.0002,
      "timestamp": "2024-01-15T12:30:45Z"
    }
  ],
  "timestamp": "2024-01-15T12:30:45Z"
}
```

---

## WebSocket Price Feed

### WS `/ws/prices`

Real-time price updates via WebSocket.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/prices');
```

**Subscribe to symbols:**
```javascript
ws.send(JSON.stringify({
  action: 'subscribe',
  symbols: ['EURUSD', 'GBPUSD']
}));
```

**Receive prices:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {
  //   "symbol": "EURUSD",
  //   "bid": 1.0848,
  //   "ask": 1.0850,
  //   "timestamp": "2024-01-15T12:30:45.123Z"
  // }
};
```

**Unsubscribe:**
```javascript
ws.send(JSON.stringify({
  action: 'unsubscribe',
  symbols: ['GBPUSD']
}));
```

**Price update frequency:** ~500ms
