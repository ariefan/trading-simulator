#!/usr/bin/env python3
"""
Database seed script for Trading Simulator.

This script populates the database with:
- Sample currency pairs
- Sample historical candle data
- Demo user accounts
- Sample strategies

Usage:
    python scripts/seed_database.py
    python scripts/seed_database.py --drop  # Drop and recreate tables first
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# Configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/trading_simulator"

# Currency pairs to seed
CURRENCY_PAIRS = [
    {"symbol": "EURUSD", "base": "EUR", "quote": "USD", "pip": 0.0001, "base_price": 1.0850},
    {"symbol": "GBPUSD", "base": "GBP", "quote": "USD", "pip": 0.0001, "base_price": 1.2650},
    {"symbol": "USDJPY", "base": "USD", "quote": "JPY", "pip": 0.01, "base_price": 149.50},
    {"symbol": "USDCHF", "base": "USD", "quote": "CHF", "pip": 0.0001, "base_price": 0.8750},
    {"symbol": "AUDUSD", "base": "AUD", "quote": "USD", "pip": 0.0001, "base_price": 0.6550},
    {"symbol": "USDCAD", "base": "USD", "quote": "CAD", "pip": 0.0001, "base_price": 1.3650},
    {"symbol": "NZDUSD", "base": "NZD", "quote": "USD", "pip": 0.0001, "base_price": 0.6150},
    {"symbol": "EURGBP", "base": "EUR", "quote": "GBP", "pip": 0.0001, "base_price": 0.8580},
    {"symbol": "EURJPY", "base": "EUR", "quote": "JPY", "pip": 0.01, "base_price": 162.20},
    {"symbol": "GBPJPY", "base": "GBP", "quote": "JPY", "pip": 0.01, "base_price": 189.10},
]

# Sample strategies
SAMPLE_STRATEGIES = [
    {
        "name": "Golden Cross",
        "description": "Buy when 50 SMA crosses above 200 SMA, sell when it crosses below",
        "code": '''
def generate_signals(data):
    sma_50 = data["close"].rolling(50).mean()
    sma_200 = data["close"].rolling(200).mean()

    signals = pd.Series(0, index=data.index)
    signals[(sma_50 > sma_200) & (sma_50.shift(1) <= sma_200.shift(1))] = 1
    signals[(sma_50 < sma_200) & (sma_50.shift(1) >= sma_200.shift(1))] = -1

    return signals
''',
        "parameters": {"fast_period": 50, "slow_period": 200},
    },
    {
        "name": "RSI Mean Reversion",
        "description": "Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)",
        "code": '''
def generate_signals(data):
    delta = data["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    signals = pd.Series(0, index=data.index)
    signals[rsi < 30] = 1
    signals[rsi > 70] = -1

    return signals
''',
        "parameters": {"period": 14, "oversold": 30, "overbought": 70},
    },
]


def generate_candle_data(
    symbol: str,
    base_price: float,
    start_date: datetime,
    end_date: datetime,
    timeframe: str = "1h",
) -> pd.DataFrame:
    """Generate realistic synthetic candle data."""

    # Determine frequency
    freq_map = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
    }
    freq = freq_map.get(timeframe, "1h")

    # Generate timestamps
    timestamps = pd.date_range(start=start_date, end=end_date, freq=freq)
    n_bars = len(timestamps)

    if n_bars == 0:
        return pd.DataFrame()

    # Generate price movement with mean reversion
    np.random.seed(hash(symbol) % 2**32)

    volatility = 0.0002  # Base volatility
    mean_reversion = 0.01  # Strength of mean reversion

    returns = np.zeros(n_bars)
    for i in range(1, n_bars):
        # Mean reversion component
        deviation = (returns[:i].sum()) * mean_reversion
        # Random component
        random_return = np.random.normal(-deviation, volatility)
        returns[i] = random_return

    # Generate close prices
    close_prices = base_price * np.exp(np.cumsum(returns))

    # Generate OHLC from close
    daily_volatility = volatility * 2
    high_prices = close_prices * (1 + np.abs(np.random.normal(0, daily_volatility, n_bars)))
    low_prices = close_prices * (1 - np.abs(np.random.normal(0, daily_volatility, n_bars)))
    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base_price

    # Ensure OHLC consistency
    high_prices = np.maximum(high_prices, np.maximum(open_prices, close_prices))
    low_prices = np.minimum(low_prices, np.minimum(open_prices, close_prices))

    # Generate volume
    base_volume = 10000
    volume = np.random.randint(base_volume // 2, base_volume * 2, n_bars)

    return pd.DataFrame({
        "timestamp": timestamps,
        "symbol": symbol,
        "open": np.round(open_prices, 5),
        "high": np.round(high_prices, 5),
        "low": np.round(low_prices, 5),
        "close": np.round(close_prices, 5),
        "volume": volume,
    })


def seed_currency_pairs(engine):
    """Seed currency pairs table."""
    print("Seeding currency pairs...")

    with engine.connect() as conn:
        for pair in CURRENCY_PAIRS:
            conn.execute(text("""
                INSERT INTO currency_pairs (symbol, base_currency, quote_currency, pip_value, is_active)
                VALUES (:symbol, :base, :quote, :pip, true)
                ON CONFLICT (symbol) DO UPDATE SET
                    base_currency = EXCLUDED.base_currency,
                    quote_currency = EXCLUDED.quote_currency,
                    pip_value = EXCLUDED.pip_value
            """), {
                "symbol": pair["symbol"],
                "base": pair["base"],
                "quote": pair["quote"],
                "pip": pair["pip"],
            })
        conn.commit()

    print(f"  Seeded {len(CURRENCY_PAIRS)} currency pairs")


def seed_candle_data(engine, days: int = 365):
    """Seed historical candle data."""
    print(f"Seeding {days} days of candle data...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    total_candles = 0

    with engine.connect() as conn:
        for pair in CURRENCY_PAIRS:
            # Generate 1h candles
            candles = generate_candle_data(
                symbol=pair["symbol"],
                base_price=pair["base_price"],
                start_date=start_date,
                end_date=end_date,
                timeframe="1h",
            )

            if len(candles) == 0:
                continue

            # Insert in batches
            batch_size = 1000
            for i in range(0, len(candles), batch_size):
                batch = candles.iloc[i:i+batch_size]
                for _, row in batch.iterrows():
                    conn.execute(text("""
                        INSERT INTO candles (symbol, timestamp, timeframe, open, high, low, close, volume)
                        VALUES (:symbol, :timestamp, '1h', :open, :high, :low, :close, :volume)
                        ON CONFLICT (symbol, timestamp, timeframe) DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume
                    """), {
                        "symbol": row["symbol"],
                        "timestamp": row["timestamp"],
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]),
                    })
                conn.commit()

            total_candles += len(candles)
            print(f"  {pair['symbol']}: {len(candles)} candles")

    print(f"  Total: {total_candles} candles")


def seed_demo_users(engine):
    """Seed demo user accounts."""
    print("Seeding demo users...")

    demo_users = [
        {"email": "demo@trading.local", "name": "Demo Trader", "balance": 100000},
        {"email": "test@trading.local", "name": "Test User", "balance": 50000},
    ]

    with engine.connect() as conn:
        for user in demo_users:
            conn.execute(text("""
                INSERT INTO users (email, name, initial_balance, created_at)
                VALUES (:email, :name, :balance, NOW())
                ON CONFLICT (email) DO UPDATE SET
                    name = EXCLUDED.name,
                    initial_balance = EXCLUDED.initial_balance
            """), user)
        conn.commit()

    print(f"  Seeded {len(demo_users)} demo users")


def seed_strategies(engine):
    """Seed sample strategies."""
    print("Seeding sample strategies...")

    with engine.connect() as conn:
        for strategy in SAMPLE_STRATEGIES:
            conn.execute(text("""
                INSERT INTO strategies (name, description, code, parameters, created_at, updated_at)
                VALUES (:name, :description, :code, :parameters, NOW(), NOW())
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    code = EXCLUDED.code,
                    parameters = EXCLUDED.parameters,
                    updated_at = NOW()
            """), {
                "name": strategy["name"],
                "description": strategy["description"],
                "code": strategy["code"],
                "parameters": str(strategy["parameters"]),
            })
        conn.commit()

    print(f"  Seeded {len(SAMPLE_STRATEGIES)} strategies")


def drop_tables(engine):
    """Drop all tables (for fresh start)."""
    print("Dropping existing tables...")

    tables = ["candles", "trades", "positions", "orders", "backtests", "strategies", "users", "currency_pairs"]

    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            except Exception as e:
                print(f"  Warning: Could not drop {table}: {e}")
        conn.commit()

    print("  Tables dropped")


def main():
    parser = argparse.ArgumentParser(description="Seed the trading simulator database")
    parser.add_argument("--drop", action="store_true", help="Drop tables before seeding")
    parser.add_argument("--days", type=int, default=365, help="Days of historical data to generate")
    parser.add_argument("--db-url", type=str, default=DATABASE_URL, help="Database URL")
    args = parser.parse_args()

    print("=" * 60)
    print("Trading Simulator - Database Seeder")
    print("=" * 60)
    print(f"Database: {args.db_url.split('@')[-1] if '@' in args.db_url else args.db_url}")
    print()

    try:
        engine = create_engine(args.db_url)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful")
        print()

        if args.drop:
            drop_tables(engine)
            print()

        # Run seeds
        seed_currency_pairs(engine)
        seed_candle_data(engine, days=args.days)
        seed_demo_users(engine)
        seed_strategies(engine)

        print()
        print("=" * 60)
        print("Seeding complete!")
        print("=" * 60)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
        print()
        print("Make sure the database is running and the tables exist.")
        print("Run 'alembic upgrade head' to create tables.")
        sys.exit(1)


if __name__ == "__main__":
    main()
