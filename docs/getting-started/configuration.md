# Configuration

Configure the Trading Simulator for your needs.

## Environment Variables

### Frontend (`apps/web/.env.local`)

```env
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```

### Backend (`apps/api/.env`)

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading_simulator

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Trading Settings
DEFAULT_LEVERAGE=100
DEFAULT_INITIAL_BALANCE=100000
```

---

## Trading Settings

### Default Values

| Setting | Default | Description |
|---------|---------|-------------|
| Initial Balance | $100,000 | Starting paper trading balance |
| Leverage | 100:1 | Maximum leverage |
| Default Lot Size | 0.1 | Default order size |
| Spread | 0.01% | Simulated bid/ask spread |

### Modifying Defaults

Edit `apps/api/src/api/v1/endpoints/trading.py`:

```python
class TradingState:
    def __init__(self):
        self.balance = 100000.0  # Change this
        self.leverage = 100      # Change this
```

---

## Database Configuration

### In-Memory Mode (Default)

By default, the simulator uses in-memory storage:

- Fast and simple
- Data lost on restart
- Perfect for development

### PostgreSQL Mode

For persistent storage:

1. Start PostgreSQL:
   ```bash
   docker-compose up -d db
   ```

2. Set the database URL:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading_simulator
   ```

3. Run migrations:
   ```bash
   cd apps/api
   alembic upgrade head
   ```

4. Seed the database:
   ```bash
   python scripts/seed_database.py
   ```

---

## WebSocket Configuration

Real-time price updates are delivered via WebSocket.

### Client Configuration

```typescript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/prices');

ws.onopen = () => {
  // Subscribe to symbols
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['EURUSD', 'GBPUSD']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { symbol: 'EURUSD', bid: 1.0850, ask: 1.0851, timestamp: '...' }
};
```

### Server Configuration

Edit tick rate in `apps/api/src/api/v1/endpoints/websocket.py`:

```python
async def price_broadcaster():
    while True:
        await asyncio.sleep(0.5)  # 500ms tick rate
        # ...
```

---

## Logging Configuration

### Backend Logging

```python
# In src/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Log Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed debugging |
| INFO | General information |
| WARNING | Warning messages |
| ERROR | Error conditions |

---

## CORS Configuration

For production, restrict CORS origins:

```python
# In src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Next Steps

- [Paper Trading Guide](../guides/paper-trading.md)
- [Deployment Guide](../deployment/index.md)
