"""
Generic CSV data loader for forex data.

Supports various CSV formats commonly used for forex data.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


class CSVLoader:
    """
    Generic CSV loader for forex OHLCV data.

    Supports various formats:
    - Standard: date, open, high, low, close, volume
    - MetaTrader: date, time, open, high, low, close, volume
    - TradingView export format
    """

    def __init__(self):
        pass

    def load(
        self,
        filepath: str | Path,
        date_column: str = "date",
        date_format: Optional[str] = None,
        time_column: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load CSV file with automatic format detection.

        Args:
            filepath: Path to CSV file
            date_column: Name of date column
            date_format: Optional strftime format for parsing dates
            time_column: Optional separate time column

        Returns:
            DataFrame with OHLCV data
        """
        filepath = Path(filepath)

        # Read CSV with auto-detection
        df = pd.read_csv(filepath)

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()

        # Handle datetime parsing
        if time_column and time_column.lower() in df.columns:
            # Combine date and time columns
            df["datetime"] = pd.to_datetime(
                df[date_column.lower()] + " " + df[time_column.lower()],
                format=date_format,
            )
        elif date_column.lower() in df.columns:
            df["datetime"] = pd.to_datetime(
                df[date_column.lower()],
                format=date_format,
            )
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        elif "timestamp" in df.columns:
            df["datetime"] = pd.to_datetime(df["timestamp"])
        else:
            # Try first column as datetime
            df["datetime"] = pd.to_datetime(df.iloc[:, 0])

        # Set index
        df.set_index("datetime", inplace=True)
        df.sort_index(inplace=True)

        # Normalize OHLCV column names
        column_mapping = {
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
            "vol": "volume",
        }
        df.rename(columns=column_mapping, inplace=True)

        # Ensure required columns exist
        required = ["open", "high", "low", "close"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Add volume if missing
        if "volume" not in df.columns:
            df["volume"] = 0.0

        # Select only OHLCV columns
        df = df[["open", "high", "low", "close", "volume"]]

        # Ensure numeric types
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def load_metatrader(self, filepath: str | Path) -> pd.DataFrame:
        """
        Load MetaTrader 4/5 exported CSV.

        MT4/MT5 format: Date, Time, Open, High, Low, Close, Volume
        """
        return self.load(
            filepath,
            date_column="date",
            time_column="time",
            date_format="%Y.%m.%d %H:%M",
        )

    def load_tradingview(self, filepath: str | Path) -> pd.DataFrame:
        """
        Load TradingView exported CSV.

        TradingView format: time, open, high, low, close, volume
        (time is Unix timestamp)
        """
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.lower()

        if "time" in df.columns:
            df["datetime"] = pd.to_datetime(df["time"], unit="s")
        else:
            df["datetime"] = pd.to_datetime(df.iloc[:, 0], unit="s")

        df.set_index("datetime", inplace=True)
        df.sort_index(inplace=True)

        return df[["open", "high", "low", "close", "volume"]]
