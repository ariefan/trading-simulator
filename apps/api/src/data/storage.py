"""
Data storage service for saving and retrieving OHLCV data from database.
"""
from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DataStorage:
    """
    Service for storing and retrieving OHLCV data in TimescaleDB.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_candles(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
        batch_size: int = 1000,
    ) -> int:
        """
        Save OHLCV data to database.

        Args:
            df: DataFrame with OHLCV data and DatetimeIndex
            symbol: Currency pair symbol
            timeframe: Timeframe string (1M, 5M, 1H, etc.)
            batch_size: Number of rows per batch insert

        Returns:
            Number of rows inserted
        """
        symbol = symbol.upper()
        total_inserted = 0

        # Prepare data for insertion
        records = []
        for timestamp, row in df.iterrows():
            records.append({
                "time": timestamp,
                "symbol": symbol,
                "timeframe": timeframe,
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row.get("volume", 0)),
            })

        # Insert in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]

            # Use ON CONFLICT to handle duplicates
            query = text("""
                INSERT INTO candles (time, symbol, timeframe, open, high, low, close, volume)
                VALUES (:time, :symbol, :timeframe, :open, :high, :low, :close, :volume)
                ON CONFLICT (time, symbol, timeframe) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
            """)

            for record in batch:
                await self.db.execute(query, record)

            total_inserted += len(batch)

        await self.db.commit()
        return total_inserted

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 5000,
    ) -> pd.DataFrame:
        """
        Retrieve OHLCV data from database.

        Args:
            symbol: Currency pair symbol
            timeframe: Timeframe string
            start: Start datetime (inclusive)
            end: End datetime (inclusive)
            limit: Maximum rows to return

        Returns:
            DataFrame with OHLCV data
        """
        symbol = symbol.upper()

        # Build query
        conditions = ["symbol = :symbol", "timeframe = :timeframe"]
        params = {"symbol": symbol, "timeframe": timeframe, "limit": limit}

        if start:
            conditions.append("time >= :start")
            params["start"] = start

        if end:
            conditions.append("time <= :end")
            params["end"] = end

        where_clause = " AND ".join(conditions)

        query = text(f"""
            SELECT time, open, high, low, close, volume
            FROM candles
            WHERE {where_clause}
            ORDER BY time ASC
            LIMIT :limit
        """)

        result = await self.db.execute(query, params)
        rows = result.fetchall()

        if not rows:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        # Convert to DataFrame
        df = pd.DataFrame(
            rows,
            columns=["time", "open", "high", "low", "close", "volume"],
        )
        df.set_index("time", inplace=True)

        return df

    async def get_date_range(
        self,
        symbol: str,
        timeframe: str,
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the available date range for a symbol/timeframe.

        Returns:
            Tuple of (earliest_date, latest_date) or (None, None) if no data
        """
        query = text("""
            SELECT MIN(time), MAX(time)
            FROM candles
            WHERE symbol = :symbol AND timeframe = :timeframe
        """)

        result = await self.db.execute(
            query,
            {"symbol": symbol.upper(), "timeframe": timeframe},
        )
        row = result.fetchone()

        if row and row[0] and row[1]:
            return row[0], row[1]

        return None, None

    async def get_available_data(self) -> list[dict]:
        """
        Get summary of available data in database.

        Returns:
            List of dicts with symbol, timeframe, count, start, end
        """
        query = text("""
            SELECT
                symbol,
                timeframe,
                COUNT(*) as count,
                MIN(time) as start_time,
                MAX(time) as end_time
            FROM candles
            GROUP BY symbol, timeframe
            ORDER BY symbol, timeframe
        """)

        result = await self.db.execute(query)
        rows = result.fetchall()

        return [
            {
                "symbol": row[0],
                "timeframe": row[1],
                "count": row[2],
                "start": row[3].isoformat() if row[3] else None,
                "end": row[4].isoformat() if row[4] else None,
            }
            for row in rows
        ]

    async def delete_candles(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> int:
        """
        Delete candles from database.

        Args:
            symbol: Currency pair symbol
            timeframe: Timeframe string
            start: Optional start datetime
            end: Optional end datetime

        Returns:
            Number of rows deleted
        """
        conditions = ["symbol = :symbol", "timeframe = :timeframe"]
        params = {"symbol": symbol.upper(), "timeframe": timeframe}

        if start:
            conditions.append("time >= :start")
            params["start"] = start

        if end:
            conditions.append("time <= :end")
            params["end"] = end

        where_clause = " AND ".join(conditions)

        query = text(f"DELETE FROM candles WHERE {where_clause}")
        result = await self.db.execute(query, params)
        await self.db.commit()

        return result.rowcount
