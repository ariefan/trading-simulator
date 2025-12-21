#!/usr/bin/env python3
"""
Script to download and import historical forex data.
Downloads data from HistData.com (free forex data).
"""

import os
import sys
import zipfile
import asyncio
from datetime import datetime
from pathlib import Path
from io import BytesIO

import httpx
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.database import async_session
from src.models.market import Candle, CurrencyPair

# HistData.com base URL format
HISTDATA_URL = "http://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{symbol}/{year}"

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "historical"

SYMBOLS = ["eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd"]
YEARS = [2022, 2023, 2024]


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def parse_histdata_csv(filepath: Path, symbol: str) -> pd.DataFrame:
    """Parse HistData.com CSV format."""
    # HistData format: Date Time;Open;High;Low;Close;Volume
    # or: YYYYMMDD HHMMSS;Open;High;Low;Close;Volume

    try:
        df = pd.read_csv(
            filepath,
            sep=';',
            header=None,
            names=['datetime', 'open', 'high', 'low', 'close', 'volume'],
        )
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return pd.DataFrame()

    # Parse datetime
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H%M%S', errors='coerce')
    df = df.dropna(subset=['datetime'])

    # Add symbol column
    df['symbol'] = symbol.upper()

    # Ensure numeric columns
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()

    return df


def resample_to_timeframe(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample 1-minute data to other timeframes."""
    if df.empty:
        return df

    timeframe_map = {
        '1M': '1min',
        '5M': '5min',
        '15M': '15min',
        '1H': '1h',
        '4H': '4h',
        '1D': '1D',
    }

    resample_rule = timeframe_map.get(timeframe)
    if not resample_rule or timeframe == '1M':
        return df

    df = df.set_index('datetime')

    resampled = df.groupby('symbol').resample(resample_rule).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
    }).dropna()

    resampled = resampled.reset_index()
    return resampled


def generate_sample_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Generate sample data for demo purposes."""
    import numpy as np

    # Base prices for different pairs
    base_prices = {
        'EURUSD': 1.08,
        'GBPUSD': 1.26,
        'USDJPY': 149.0,
        'USDCHF': 0.88,
        'AUDUSD': 0.65,
        'USDCAD': 1.35,
        'NZDUSD': 0.60,
    }

    base_price = base_prices.get(symbol.upper(), 1.0)

    # Generate date range (1-hour intervals)
    dates = pd.date_range(start=start_date, end=end_date, freq='1h')

    # Generate random walk
    np.random.seed(42)  # For reproducibility
    returns = np.random.normal(0, 0.0002, len(dates))
    price = base_price * np.exp(np.cumsum(returns))

    # Generate OHLCV
    data = []
    for i, (dt, p) in enumerate(zip(dates, price)):
        volatility = 0.0005 * base_price
        high = p + np.random.uniform(0, volatility)
        low = p - np.random.uniform(0, volatility)
        open_price = p + np.random.uniform(-volatility/2, volatility/2)
        close_price = p + np.random.uniform(-volatility/2, volatility/2)

        data.append({
            'datetime': dt,
            'symbol': symbol.upper(),
            'open': round(open_price, 5),
            'high': round(max(high, open_price, close_price), 5),
            'low': round(min(low, open_price, close_price), 5),
            'close': round(close_price, 5),
            'volume': np.random.randint(1000, 10000),
        })

    return pd.DataFrame(data)


async def init_currency_pairs(session):
    """Initialize currency pairs in database."""
    from sqlalchemy import select

    pairs = [
        {'symbol': 'EURUSD', 'base_currency': 'EUR', 'quote_currency': 'USD', 'pip_value': 0.0001},
        {'symbol': 'GBPUSD', 'base_currency': 'GBP', 'quote_currency': 'USD', 'pip_value': 0.0001},
        {'symbol': 'USDJPY', 'base_currency': 'USD', 'quote_currency': 'JPY', 'pip_value': 0.01},
        {'symbol': 'USDCHF', 'base_currency': 'USD', 'quote_currency': 'CHF', 'pip_value': 0.0001},
        {'symbol': 'AUDUSD', 'base_currency': 'AUD', 'quote_currency': 'USD', 'pip_value': 0.0001},
        {'symbol': 'USDCAD', 'base_currency': 'USD', 'quote_currency': 'CAD', 'pip_value': 0.0001},
        {'symbol': 'NZDUSD', 'base_currency': 'NZD', 'quote_currency': 'USD', 'pip_value': 0.0001},
    ]

    for pair_data in pairs:
        result = await session.execute(
            select(CurrencyPair).where(CurrencyPair.symbol == pair_data['symbol'])
        )
        existing = result.scalar_one_or_none()

        if not existing:
            pair = CurrencyPair(**pair_data)
            session.add(pair)
            print(f"Added currency pair: {pair_data['symbol']}")

    await session.commit()


async def import_candles(session, df: pd.DataFrame, timeframe: str):
    """Import candle data to database."""
    from sqlalchemy.dialects.postgresql import insert

    if df.empty:
        return

    # Prepare records
    records = []
    for _, row in df.iterrows():
        records.append({
            'time': row['datetime'],
            'symbol': row['symbol'],
            'timeframe': timeframe,
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': int(row['volume']),
        })

    # Use upsert (insert or update on conflict)
    stmt = insert(Candle).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=['time', 'symbol', 'timeframe'],
        set_={
            'open': stmt.excluded.open,
            'high': stmt.excluded.high,
            'low': stmt.excluded.low,
            'close': stmt.excluded.close,
            'volume': stmt.excluded.volume,
        }
    )

    await session.execute(stmt)
    await session.commit()

    print(f"Imported {len(records)} candles for {df['symbol'].iloc[0]} ({timeframe})")


async def main():
    """Main entry point."""
    print("=" * 50)
    print("Forex Historical Data Import Script")
    print("=" * 50)

    ensure_data_dir()

    # Check for command line arguments
    use_sample = "--sample" in sys.argv or "-s" in sys.argv

    async with async_session() as session:
        # Initialize currency pairs
        print("\nInitializing currency pairs...")
        await init_currency_pairs(session)

        if use_sample:
            print("\nGenerating sample data...")
            for symbol in ['EURUSD', 'GBPUSD', 'USDJPY']:
                print(f"Generating data for {symbol}...")
                df = generate_sample_data(symbol, '2023-01-01', '2023-12-31')

                for timeframe in ['1H', '4H', '1D']:
                    resampled = resample_to_timeframe(df.copy(), timeframe)
                    await import_candles(session, resampled, timeframe)

            print("\nSample data import complete!")
        else:
            print("\nNote: For real historical data, download from HistData.com")
            print("and place CSV files in: " + str(DATA_DIR))
            print("\nTo generate sample data, run with --sample flag:")
            print("  python download_data.py --sample")

            # Check for existing CSV files
            csv_files = list(DATA_DIR.glob("*.csv"))
            if csv_files:
                print(f"\nFound {len(csv_files)} CSV files to import...")
                for csv_file in csv_files:
                    symbol = csv_file.stem.split('_')[0].upper()
                    print(f"Importing {csv_file.name}...")
                    df = parse_histdata_csv(csv_file, symbol)

                    if not df.empty:
                        for timeframe in ['1M', '5M', '15M', '1H', '4H', '1D']:
                            resampled = resample_to_timeframe(df.copy(), timeframe)
                            await import_candles(session, resampled, timeframe)

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
