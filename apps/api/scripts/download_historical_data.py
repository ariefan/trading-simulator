#!/usr/bin/env python3
"""
Historical data download script for Trading Simulator.

Downloads free forex data from various sources and saves to CSV.

Sources:
- HistData.com (free historical forex data)
- Dukascopy (free tick data)
- Yahoo Finance (limited forex data)

Usage:
    python scripts/download_historical_data.py --source histdata --pair EURUSD --year 2024
    python scripts/download_historical_data.py --source yahoo --pair EURUSD --days 365
    python scripts/download_historical_data.py --generate --pair EURUSD --days 365
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO

import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "historical"


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def download_from_histdata(pair: str, year: int, month: int = None) -> pd.DataFrame:
    """
    Download data from HistData.com.

    Note: HistData provides free 1-minute data in CSV format.
    You need to manually download from: https://www.histdata.com/download-free-forex-data/

    This function shows how to parse their CSV format.
    """
    import requests

    print(f"Note: HistData.com requires manual download.")
    print(f"Visit: https://www.histdata.com/download-free-forex-data/")
    print(f"Download {pair} data for {year} and place in {DATA_DIR}")

    # Check if file exists locally
    filename = f"{pair}_{year}.csv"
    filepath = DATA_DIR / filename

    if filepath.exists():
        print(f"Found local file: {filepath}")
        # HistData format: Date,Time,Open,High,Low,Close,Volume
        df = pd.read_csv(
            filepath,
            names=["date", "time", "open", "high", "low", "close", "volume"],
            parse_dates={"timestamp": ["date", "time"]},
        )
        df["symbol"] = pair
        return df

    return pd.DataFrame()


def download_from_yahoo(pair: str, days: int = 365) -> pd.DataFrame:
    """
    Download forex data from Yahoo Finance.

    Note: Yahoo has limited forex data availability.
    """
    try:
        import yfinance as yf
    except ImportError:
        print("Installing yfinance...")
        os.system("pip install yfinance")
        import yfinance as yf

    # Yahoo uses different symbol format for forex
    yahoo_symbol = f"{pair[:3]}{pair[3:]}=X"

    print(f"Downloading {pair} from Yahoo Finance...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    try:
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(start=start_date, end=end_date, interval="1h")

        if len(df) == 0:
            print(f"No data available for {pair} from Yahoo")
            return pd.DataFrame()

        df = df.reset_index()
        df = df.rename(columns={
            "Datetime": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })
        df["symbol"] = pair

        print(f"Downloaded {len(df)} candles")
        return df[["timestamp", "symbol", "open", "high", "low", "close", "volume"]]

    except Exception as e:
        print(f"Error downloading from Yahoo: {e}")
        return pd.DataFrame()


def generate_synthetic_data(
    pair: str,
    days: int = 365,
    timeframe: str = "1h",
) -> pd.DataFrame:
    """
    Generate realistic synthetic forex data.

    Uses geometric Brownian motion with mean reversion.
    """
    print(f"Generating synthetic data for {pair}...")

    # Base prices for different pairs
    base_prices = {
        "EURUSD": 1.0850,
        "GBPUSD": 1.2650,
        "USDJPY": 149.50,
        "USDCHF": 0.8750,
        "AUDUSD": 0.6550,
        "USDCAD": 1.3650,
        "NZDUSD": 0.6150,
        "EURGBP": 0.8580,
        "EURJPY": 162.20,
        "GBPJPY": 189.10,
    }

    base_price = base_prices.get(pair.upper(), 1.0)

    # Time parameters
    freq_map = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
    }
    freq = freq_map.get(timeframe, "1h")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    timestamps = pd.date_range(start=start_date, end=end_date, freq=freq)
    n_bars = len(timestamps)

    print(f"Generating {n_bars} candles...")

    # Model parameters
    np.random.seed(hash(pair) % 2**32)
    volatility = 0.0002  # Hourly volatility
    mean_reversion = 0.01
    trend = 0.00001  # Slight trend

    # Generate returns with regime changes
    returns = np.zeros(n_bars)
    regime = 0  # 0 = ranging, 1 = trending up, -1 = trending down

    for i in range(1, n_bars):
        # Regime change probability
        if np.random.random() < 0.01:  # 1% chance of regime change
            regime = np.random.choice([-1, 0, 1])

        # Mean reversion
        deviation = returns[:i].sum() * mean_reversion

        # Regime-adjusted return
        regime_drift = regime * 0.0001

        # Generate return
        returns[i] = np.random.normal(regime_drift - deviation, volatility)

    # Generate prices
    close_prices = base_price * np.exp(np.cumsum(returns))

    # Generate OHLC
    bar_volatility = volatility * 1.5
    high_factor = 1 + np.abs(np.random.normal(0, bar_volatility, n_bars))
    low_factor = 1 - np.abs(np.random.normal(0, bar_volatility, n_bars))

    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base_price
    high_prices = np.maximum(open_prices, close_prices) * high_factor
    low_prices = np.minimum(open_prices, close_prices) * low_factor

    # Volume with intraday pattern
    hour_of_day = np.array([t.hour for t in timestamps])
    volume_pattern = 1 + 0.5 * np.sin(2 * np.pi * hour_of_day / 24)  # Higher during day
    base_volume = 10000
    volume = (base_volume * volume_pattern * np.random.uniform(0.8, 1.2, n_bars)).astype(int)

    # Determine decimal places
    if "JPY" in pair:
        decimals = 3
    else:
        decimals = 5

    df = pd.DataFrame({
        "timestamp": timestamps,
        "symbol": pair.upper(),
        "open": np.round(open_prices, decimals),
        "high": np.round(high_prices, decimals),
        "low": np.round(low_prices, decimals),
        "close": np.round(close_prices, decimals),
        "volume": volume,
    })

    print(f"Generated {len(df)} candles from {df['timestamp'].min()} to {df['timestamp'].max()}")

    return df


def save_to_csv(df: pd.DataFrame, pair: str, timeframe: str = "1h"):
    """Save data to CSV file."""
    data_dir = ensure_data_dir()

    filename = f"{pair}_{timeframe}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = data_dir / filename

    df.to_csv(filepath, index=False)
    print(f"Saved to: {filepath}")

    return filepath


def save_to_database(df: pd.DataFrame, db_url: str):
    """Save data to database."""
    from sqlalchemy import create_engine, text

    print("Saving to database...")

    engine = create_engine(db_url)

    with engine.connect() as conn:
        for _, row in df.iterrows():
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

    print(f"Saved {len(df)} candles to database")


def main():
    parser = argparse.ArgumentParser(description="Download historical forex data")
    parser.add_argument("--source", choices=["histdata", "yahoo", "generate"],
                        default="generate", help="Data source")
    parser.add_argument("--pair", type=str, default="EURUSD", help="Currency pair")
    parser.add_argument("--days", type=int, default=365, help="Days of data")
    parser.add_argument("--year", type=int, help="Year for HistData")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    parser.add_argument("--output", choices=["csv", "db", "both"], default="csv",
                        help="Output format")
    parser.add_argument("--db-url", type=str,
                        default="postgresql://postgres:postgres@localhost:5432/trading_simulator",
                        help="Database URL")
    parser.add_argument("--all-pairs", action="store_true",
                        help="Download all major pairs")

    args = parser.parse_args()

    print("=" * 60)
    print("Trading Simulator - Historical Data Downloader")
    print("=" * 60)
    print()

    pairs = [args.pair.upper()]
    if args.all_pairs:
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
                 "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]

    for pair in pairs:
        print(f"\n{'='*40}")
        print(f"Processing {pair}")
        print(f"{'='*40}")

        # Download/generate data
        if args.source == "histdata":
            df = download_from_histdata(pair, args.year or 2024)
        elif args.source == "yahoo":
            df = download_from_yahoo(pair, args.days)
        else:  # generate
            df = generate_synthetic_data(pair, args.days, args.timeframe)

        if len(df) == 0:
            print(f"No data for {pair}, skipping...")
            continue

        # Save data
        if args.output in ["csv", "both"]:
            save_to_csv(df, pair, args.timeframe)

        if args.output in ["db", "both"]:
            try:
                save_to_database(df, args.db_url)
            except Exception as e:
                print(f"Could not save to database: {e}")

    print()
    print("=" * 60)
    print("Download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
