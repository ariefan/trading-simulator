# Installation

This guide covers the installation process for the Trading Simulator.

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Node.js | 20+ | Frontend runtime |
| pnpm | 9+ | Package manager |
| Python | 3.11+ | Backend runtime |
| pip | Latest | Python packages |

### Optional Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 24+ | Database services |
| PostgreSQL | 15+ | Persistent storage |
| Redis | 7+ | Caching & queues |

---

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ariefan/trading-simulator.git
cd trading-simulator
```

### 2. Install Frontend Dependencies

```bash
# Install pnpm if you haven't
npm install -g pnpm@9

# Install all dependencies
pnpm install
```

### 3. Install Backend Dependencies

```bash
cd apps/api

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Start the Services

=== "Development (No Docker)"

    ```bash
    # Terminal 1: Start API
    cd apps/api
    source .venv/bin/activate
    uvicorn src.main:app --reload --port 8000

    # Terminal 2: Start Frontend
    pnpm --filter web dev
    ```

=== "With Docker"

    ```bash
    # Start all services
    docker-compose up -d

    # Or just the databases
    docker-compose up -d db redis

    # Then start API and frontend manually
    ```

---

## Detailed Installation

### Frontend Setup

The frontend is a Next.js 16 application with React 19.

```bash
# From project root
pnpm install

# Verify installation
pnpm --filter web build
```

#### Environment Variables

Create `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Setup

The backend is a FastAPI application with Python 3.11+.

```bash
cd apps/api

# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate

# Install main dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing)
pip install pytest pytest-asyncio pytest-cov httpx ruff mypy
```

#### Environment Variables

Create `apps/api/.env`:

```env
# Database (optional - uses in-memory by default)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading_simulator

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Docker Installation

For the full production-like setup:

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Services Started

| Service | Port | Description |
|---------|------|-------------|
| api | 8000 | FastAPI backend |
| web | 3000 | Next.js frontend |
| db | 5432 | PostgreSQL + TimescaleDB |
| redis | 6379 | Redis cache |
| celery | - | Background workers |

---

## Verify Installation

### Check API

```bash
curl http://localhost:8000/
# Should return: {"message": "Trading Simulator API"}

curl http://localhost:8000/api/v1/market/pairs
# Should return list of currency pairs
```

### Check Frontend

Open [http://localhost:3000](http://localhost:3000) in your browser.

You should see the trading dashboard.

---

## Troubleshooting

### Common Issues

??? failure "ModuleNotFoundError: No module named 'src'"

    Make sure you're running from the `apps/api` directory and the virtual environment is activated.

    ```bash
    cd apps/api
    source .venv/bin/activate
    export PYTHONPATH=/path/to/apps/api
    uvicorn src.main:app --reload
    ```

??? failure "pnpm: command not found"

    Install pnpm globally:

    ```bash
    npm install -g pnpm@9
    ```

??? failure "Port 8000 already in use"

    Kill the process using the port:

    ```bash
    # Find the process
    lsof -i :8000

    # Kill it
    kill -9 <PID>
    ```

??? failure "Docker permission denied"

    Add your user to the docker group:

    ```bash
    sudo usermod -aG docker $USER
    # Log out and back in
    ```

---

## Next Steps

Now that you have the simulator installed:

- [Quick Start Guide](quickstart.md) - Start trading in 5 minutes
- [Configuration](configuration.md) - Customize your setup
