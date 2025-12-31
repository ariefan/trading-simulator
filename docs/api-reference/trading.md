# Trading API

Endpoints for order management and position handling.

## Orders

### GET `/trading/orders`

List all pending orders.

**Response:**
```json
[
  {
    "id": "ord_123",
    "symbol": "EURUSD",
    "side": "buy",
    "type": "limit",
    "size": 0.1,
    "price": 1.0800,
    "stop_loss": 1.0750,
    "take_profit": 1.0900,
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST `/trading/orders`

Place a new order.

**Request:**
```json
{
  "symbol": "EURUSD",
  "side": "buy",
  "type": "market",
  "size": 0.1,
  "stop_loss": 1.0800,
  "take_profit": 1.0950
}
```

**Order Types:**

| Type | Description |
|------|-------------|
| `market` | Execute immediately at current price |
| `limit` | Execute at specified price or better |
| `stop` | Execute when price reaches trigger level |

**Response:**
```json
{
  "id": "ord_456",
  "symbol": "EURUSD",
  "side": "buy",
  "type": "market",
  "size": 0.1,
  "entry_price": 1.0850,
  "stop_loss": 1.0800,
  "take_profit": 1.0950,
  "status": "filled",
  "position_id": "pos_789"
}
```

### DELETE `/trading/orders/{id}`

Cancel a pending order.

**Response:**
```json
{
  "success": true,
  "message": "Order cancelled"
}
```

---

## Positions

### GET `/trading/positions`

List all open positions.

**Response:**
```json
[
  {
    "id": "pos_789",
    "symbol": "EURUSD",
    "side": "long",
    "size": 0.1,
    "entry_price": 1.0850,
    "current_price": 1.0870,
    "unrealized_pnl": 20.00,
    "stop_loss": 1.0800,
    "take_profit": 1.0950,
    "margin_used": 108.50,
    "opened_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST `/trading/positions/{id}/close`

Close an open position.

**Response:**
```json
{
  "success": true,
  "position_id": "pos_789",
  "exit_price": 1.0870,
  "pnl": 20.00,
  "closed_at": "2024-01-15T11:45:00Z"
}
```

---

## Trade History

### GET `/trading/history`

Get closed trade history.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 50 | Max trades to return |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
[
  {
    "id": "trade_001",
    "symbol": "EURUSD",
    "side": "long",
    "size": 0.1,
    "entry_price": 1.0850,
    "exit_price": 1.0870,
    "pnl": 20.00,
    "pnl_percent": 0.18,
    "opened_at": "2024-01-15T10:30:00Z",
    "closed_at": "2024-01-15T11:45:00Z",
    "duration_minutes": 75
  }
]
```

---

## Account Reset

### POST `/trading/reset`

Reset paper trading account to initial state.

**Response:**
```json
{
  "success": true,
  "message": "Account reset to $100,000",
  "new_balance": 100000
}
```

!!! warning
    This clears all positions and trade history.
