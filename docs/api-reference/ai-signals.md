# AI & Signals API

Endpoints for AI assistant and trading signals.

## AI Chat

### POST `/ai/chat`

Chat with the AI trading assistant.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "What's my portfolio balance?"}
  ]
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "Your current portfolio balance is $100,000..."
  },
  "tool_calls": []
}
```

### GET `/ai/tools`

List available AI tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "get_portfolio",
      "description": "Get current portfolio summary",
      "parameters": {}
    },
    {
      "name": "calculate_position_size",
      "description": "Calculate optimal position size",
      "parameters": {
        "account_balance": "float",
        "risk_percent": "float",
        "stop_loss_pips": "float"
      }
    }
  ]
}
```

### POST `/ai/tools/{name}`

Execute a specific AI tool.

**Example - Position Size Calculator:**
```bash
POST /ai/tools/calculate_position_size
{
  "account_balance": 10000,
  "risk_percent": 1,
  "stop_loss_pips": 20
}
```

**Response:**
```json
{
  "tool": "calculate_position_size",
  "result": {
    "recommended_lots": 0.5,
    "risk_amount": 100,
    "pip_value_per_lot": 10
  },
  "success": true
}
```

---

## Trading Signals

### GET `/signals/`

Get signals for all symbols.

**Response:**
```json
[
  {
    "symbol": "EURUSD",
    "signal": "buy",
    "strength": 0.75,
    "indicators": {
      "rsi": 35,
      "macd": "bullish",
      "sma_trend": "up"
    }
  }
]
```

### GET `/signals/{symbol}`

Get signal for a specific symbol.

### GET `/signals/{symbol}/patterns`

Get detected chart patterns.

**Response:**
```json
{
  "symbol": "EURUSD",
  "patterns": [
    {
      "name": "Double Bottom",
      "confidence": 0.85,
      "direction": "bullish",
      "target": 1.0920
    }
  ]
}
```

### GET `/signals/{symbol}/risk`

Get risk assessment.

**Response:**
```json
{
  "symbol": "EURUSD",
  "volatility": "medium",
  "atr": 0.0045,
  "recommended_stop_pips": 25,
  "max_position_size": 0.5
}
```

### GET `/signals/{symbol}/analysis`

Get comprehensive analysis.

**Response:**
```json
{
  "symbol": "EURUSD",
  "signals": {...},
  "patterns": [...],
  "risk": {...},
  "sentiment": {
    "retail": "bearish",
    "institutional": "neutral"
  },
  "recommendation": "Wait for confirmation"
}
```
