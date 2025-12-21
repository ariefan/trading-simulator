import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.strategy import Strategy
    from src.models.backtest import Backtest


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    picture: Mapped[str | None] = mapped_column(String(500), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Account settings
    initial_balance: Mapped[float] = mapped_column(Float, default=100000.0)
    default_leverage: Mapped[int] = mapped_column(Integer, default=100)
    theme: Mapped[str] = mapped_column(String(20), default="dark")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    strategies: Mapped[list["Strategy"]] = relationship(
        "Strategy",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    backtests: Mapped[list["Backtest"]] = relationship(
        "Backtest",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
