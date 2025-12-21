"""
Historical forex data loader from HistData.com.

HistData provides free tick and 1-minute OHLC data for major forex pairs.
Data format: ASCII with M1 (1-minute) bars.

Reference: https://www.histdata.com/
"""
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd


class HistDataLoader:
    """
    Load historical forex data from HistData.com files.

    HistData provides free historical forex data in CSV format.
    Files can be downloaded from: https://www.histdata.com/download-free-forex-data/

    Supported pairs:
    - EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
    - EURGBP, EURJPY, GBPJPY, and more

    File format (ASCII):
    - Date format: YYYYMMDD HHMMSS
    - Columns: DateTime, Open, High, Low, Close, Volume
    """

    SUPPORTED_PAIRS = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
        "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
        "EURAUD", "EURCHF", "AUDCAD", "AUDCHF", "AUDJPY",
        "AUDNZD", "CADJPY", "CHFJPY", "EURCZK", "EURNOK",
        "EURSEK", "GBPCHF", "GBPJPY", "NZDJPY", "USDMXN",
        "USDNOK", "USDSEK", "USDSGD", "USDZAR",
    ]

    def __init__(self, data_dir: str = "./data/histdata"):
        """
        Initialize the loader.

        Args:
            data_dir: Directory to store/load data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_file(self, filepath: str | Path) -> pd.DataFrame:
        """
        Load a single HistData file (CSV or ZIP).

        Args:
            filepath: Path to the data file

        Returns:
            DataFrame with OHLCV data and DatetimeIndex
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Handle ZIP files
        if filepath.suffix.lower() == ".zip":
            return self._load_zip(filepath)

        # Handle CSV files
        return self._load_csv(filepath)

    def _load_zip(self, filepath: Path) -> pd.DataFrame:
        """Load data from a ZIP archive."""
        with zipfile.ZipFile(filepath, "r") as z:
            # Find CSV file in archive
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            if not csv_files:
                raise ValueError(f"No CSV file found in {filepath}")

            with z.open(csv_files[0]) as f:
                return self._parse_csv(f)

    def _load_csv(self, filepath: Path) -> pd.DataFrame:
        """Load data from a CSV file."""
        with open(filepath, "rb") as f:
            return self._parse_csv(f)

    def _parse_csv(self, file_obj) -> pd.DataFrame:
        """
        Parse HistData CSV format.

        HistData format varies slightly:
        - Some files: DateTime;Open;High;Low;Close;Volume
        - Some files: Date,Time,Open,High,Low,Close,Volume
        - Some files: YYYYMMDD HHMMSS,Open,High,Low,Close,Volume
        """
        # Try different delimiters and formats
        try:
            # First try: semicolon delimiter (common format)
            df = pd.read_csv(
                file_obj,
                sep=";",
                header=None,
                names=["datetime", "open", "high", "low", "close", "volume"],
            )
        except Exception:
            file_obj.seek(0)
            # Second try: comma delimiter
            df = pd.read_csv(
                file_obj,
                sep=",",
                header=None,
                names=["datetime", "open", "high", "low", "close", "volume"],
            )

        # Parse datetime
        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="%Y%m%d %H%M%S",
            errors="coerce",
        )

        # Drop rows with invalid dates
        df = df.dropna(subset=["datetime"])

        # Set datetime as index
        df.set_index("datetime", inplace=True)
        df.sort_index(inplace=True)

        # Ensure numeric types
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def load_directory(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Load all data files for a symbol from the data directory.

        Args:
            symbol: Currency pair (e.g., "EURUSD")
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Combined DataFrame with all data
        """
        symbol = symbol.upper()
        symbol_dir = self.data_dir / symbol

        if not symbol_dir.exists():
            raise FileNotFoundError(
                f"No data directory found for {symbol}. "
                f"Expected: {symbol_dir}"
            )

        # Find all data files
        files = list(symbol_dir.glob("*.zip")) + list(symbol_dir.glob("*.csv"))

        if not files:
            raise FileNotFoundError(f"No data files found in {symbol_dir}")

        # Load and combine all files
        dfs = []
        for f in sorted(files):
            try:
                df = self.load_file(f)
                dfs.append(df)
            except Exception as e:
                print(f"Warning: Failed to load {f}: {e}")

        if not dfs:
            raise ValueError(f"No valid data files found for {symbol}")

        # Combine and sort
        combined = pd.concat(dfs)
        combined = combined[~combined.index.duplicated(keep="first")]
        combined.sort_index(inplace=True)

        # Apply date filters
        if start_date:
            combined = combined[combined.index >= start_date]
        if end_date:
            combined = combined[combined.index <= end_date]

        return combined

    def resample(
        self,
        df: pd.DataFrame,
        timeframe: str,
    ) -> pd.DataFrame:
        """
        Resample 1-minute data to a higher timeframe.

        Args:
            df: DataFrame with 1-minute OHLCV data
            timeframe: Target timeframe (5M, 15M, 30M, 1H, 4H, 1D, 1W)

        Returns:
            Resampled DataFrame
        """
        # Map timeframe strings to pandas offset aliases
        tf_map = {
            "1M": "1min",
            "5M": "5min",
            "15M": "15min",
            "30M": "30min",
            "1H": "1h",
            "4H": "4h",
            "1D": "1D",
            "1W": "1W",
        }

        if timeframe not in tf_map:
            raise ValueError(f"Invalid timeframe: {timeframe}. Use: {list(tf_map.keys())}")

        offset = tf_map[timeframe]

        # Resample OHLCV
        resampled = df.resample(offset).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        })

        # Drop incomplete bars
        resampled = resampled.dropna()

        return resampled

    def get_available_symbols(self) -> list[str]:
        """Get list of symbols with data available locally."""
        symbols = []
        for d in self.data_dir.iterdir():
            if d.is_dir() and d.name.upper() in self.SUPPORTED_PAIRS:
                symbols.append(d.name.upper())
        return sorted(symbols)

    def get_date_range(self, symbol: str) -> tuple[datetime, datetime]:
        """Get the date range available for a symbol."""
        df = self.load_directory(symbol)
        return df.index.min().to_pydatetime(), df.index.max().to_pydatetime()
