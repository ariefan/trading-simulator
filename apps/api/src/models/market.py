import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class CurrencyPair(Base):
    """Currency pair configuration."""

    __tablename__ = "currency_pairs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    symbol: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)

    # Trading parameters
    pip_value: Mapped[float] = mapped_column(Float, nullable=False)
    min_lot_size: Mapped[float] = mapped_column(Float, default=0.01)
    max_lot_size: Mapped[float] = mapped_column(Float, default=100.0)
    max_leverage: Mapped[int] = mapped_column(Integer, default=100)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<CurrencyPair {self.symbol}>"


class Candle(Base):
    """
    OHLCV candle data.

    This table uses TimescaleDB hypertable for efficient time-series queries.
    """

    __tablename__ = "candles"

    # Composite primary key: time + symbol + timeframe
    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
    )
    timeframe: Mapped[str] = mapped_column(
        String(5),
        primary_key=True,
    )

    # OHLCV data
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=0.0)

    # Indexes for common query patterns
    __table_args__ = (
        Index("idx_candles_symbol_timeframe_time", "symbol", "timeframe", "time"),
    )

    def __repr__(self) -> str:
        return f"<Candle {self.symbol} {self.timeframe} @ {self.time}>"
