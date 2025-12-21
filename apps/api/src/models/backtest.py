import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.strategy import Strategy


class BacktestStatus(str, Enum):
    """Backtest execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Backtest(Base):
    """Backtest execution record."""

    __tablename__ = "backtests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    strategy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Configuration
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(5), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    initial_balance: Mapped[float] = mapped_column(Float, nullable=False)
    leverage: Mapped[int] = mapped_column(Integer, default=100)
    commission: Mapped[float] = mapped_column(Float, default=0.0001)

    # Parameter overrides for this backtest
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=BacktestStatus.PENDING.value,
        index=True,
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Results (populated after completion)
    final_balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    equity_curve: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="backtests")
    strategy: Mapped["Strategy"] = relationship("Strategy", back_populates="backtests")
    trades: Mapped[list["BacktestTrade"]] = relationship(
        "BacktestTrade",
        back_populates="backtest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Backtest {self.id} - {self.symbol}>"


class BacktestTrade(Base):
    """Individual trade from a backtest."""

    __tablename__ = "backtest_trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    backtest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("backtests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Trade details
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # buy, sell
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Results
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    commission: Mapped[float] = mapped_column(Float, default=0.0)

    # Stop loss / Take profit
    stop_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    take_profit: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationship
    backtest: Mapped["Backtest"] = relationship("Backtest", back_populates="trades")

    def __repr__(self) -> str:
        return f"<BacktestTrade {self.side} {self.quantity} @ {self.entry_price}>"
