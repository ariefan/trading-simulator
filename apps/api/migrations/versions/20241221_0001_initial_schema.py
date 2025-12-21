"""Initial schema with users, strategies, backtests, and market data.

Revision ID: 0001
Revises:
Create Date: 2024-12-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("picture", sa.String(length=500), nullable=True),
        sa.Column("google_id", sa.String(length=255), nullable=True),
        sa.Column("initial_balance", sa.Float(), nullable=True, default=100000.0),
        sa.Column("default_leverage", sa.Integer(), nullable=True, default=100),
        sa.Column("theme", sa.String(length=20), nullable=True, default="dark"),
        sa.Column("notifications_enabled", sa.Boolean(), nullable=True, default=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Create strategies table
    op.create_table(
        "strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True, default=""),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("parameters", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=True, default=False),
        sa.Column("version", sa.Integer(), nullable=True, default=1),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_strategies_user_id"), "strategies", ["user_id"], unique=False)

    # Create backtests table
    op.create_table(
        "backtests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=10), nullable=False),
        sa.Column("timeframe", sa.String(length=5), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("initial_balance", sa.Float(), nullable=False),
        sa.Column("leverage", sa.Integer(), nullable=True, default=100),
        sa.Column("commission", sa.Float(), nullable=True, default=0.0001),
        sa.Column("parameters", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True, default="pending"),
        sa.Column("progress", sa.Float(), nullable=True, default=0.0),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("final_balance", sa.Float(), nullable=True),
        sa.Column("results", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("equity_curve", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["strategy_id"], ["strategies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backtests_status"), "backtests", ["status"], unique=False)
    op.create_index(op.f("ix_backtests_strategy_id"), "backtests", ["strategy_id"], unique=False)
    op.create_index(op.f("ix_backtests_user_id"), "backtests", ["user_id"], unique=False)

    # Create backtest_trades table
    op.create_table(
        "backtest_trades",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("backtest_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("entry_price", sa.Float(), nullable=False),
        sa.Column("exit_price", sa.Float(), nullable=True),
        sa.Column("entry_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exit_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pnl", sa.Float(), nullable=True),
        sa.Column("pnl_percent", sa.Float(), nullable=True),
        sa.Column("commission", sa.Float(), nullable=True, default=0.0),
        sa.Column("stop_loss", sa.Float(), nullable=True),
        sa.Column("take_profit", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["backtest_id"], ["backtests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_backtest_trades_backtest_id"),
        "backtest_trades",
        ["backtest_id"],
        unique=False,
    )

    # Create currency_pairs table
    op.create_table(
        "currency_pairs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("symbol", sa.String(length=10), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("pip_value", sa.Float(), nullable=False),
        sa.Column("min_lot_size", sa.Float(), nullable=True, default=0.01),
        sa.Column("max_lot_size", sa.Float(), nullable=True, default=100.0),
        sa.Column("max_leverage", sa.Integer(), nullable=True, default=100),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_index(op.f("ix_currency_pairs_symbol"), "currency_pairs", ["symbol"], unique=True)

    # Create candles table (will be converted to hypertable)
    op.create_table(
        "candles",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(length=10), nullable=False),
        sa.Column("timeframe", sa.String(length=5), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=True, default=0.0),
        sa.PrimaryKeyConstraint("time", "symbol", "timeframe"),
    )
    op.create_index(
        "idx_candles_symbol_timeframe_time",
        "candles",
        ["symbol", "timeframe", "time"],
        unique=False,
    )

    # Convert candles to TimescaleDB hypertable
    op.execute(
        "SELECT create_hypertable('candles', 'time', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE)"
    )

    # Seed currency pairs
    op.execute("""
        INSERT INTO currency_pairs (id, symbol, base_currency, quote_currency, pip_value, min_lot_size, max_lot_size, max_leverage, is_active)
        VALUES
            (gen_random_uuid(), 'EURUSD', 'EUR', 'USD', 0.0001, 0.01, 100.0, 100, true),
            (gen_random_uuid(), 'GBPUSD', 'GBP', 'USD', 0.0001, 0.01, 100.0, 100, true),
            (gen_random_uuid(), 'USDJPY', 'USD', 'JPY', 0.01, 0.01, 100.0, 100, true),
            (gen_random_uuid(), 'USDCHF', 'USD', 'CHF', 0.0001, 0.01, 100.0, 100, true),
            (gen_random_uuid(), 'AUDUSD', 'AUD', 'USD', 0.0001, 0.01, 100.0, 100, true),
            (gen_random_uuid(), 'USDCAD', 'USD', 'CAD', 0.0001, 0.01, 100.0, 100, true),
            (gen_random_uuid(), 'NZDUSD', 'NZD', 'USD', 0.0001, 0.01, 100.0, 100, true)
        ON CONFLICT (symbol) DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_index("idx_candles_symbol_timeframe_time", table_name="candles")
    op.drop_table("candles")
    op.drop_index(op.f("ix_currency_pairs_symbol"), table_name="currency_pairs")
    op.drop_table("currency_pairs")
    op.drop_index(op.f("ix_backtest_trades_backtest_id"), table_name="backtest_trades")
    op.drop_table("backtest_trades")
    op.drop_index(op.f("ix_backtests_user_id"), table_name="backtests")
    op.drop_index(op.f("ix_backtests_strategy_id"), table_name="backtests")
    op.drop_index(op.f("ix_backtests_status"), table_name="backtests")
    op.drop_table("backtests")
    op.drop_index(op.f("ix_strategies_user_id"), table_name="strategies")
    op.drop_table("strategies")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
