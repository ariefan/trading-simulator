"""Paper trading API endpoints."""
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"


# Request/Response Models
class PlaceOrderRequest(BaseModel):
    """Request to place a new order."""
    symbol: str = Field(..., pattern="^[A-Z]{6}$")
    side: OrderSide
    type: OrderType
    size: float = Field(..., gt=0, le=100)
    price: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = Field(None, gt=0)
    take_profit: Optional[float] = Field(None, gt=0)


class OrderResponse(BaseModel):
    """Order response model."""
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    size: float
    price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    status: OrderStatus
    filled_price: Optional[float] = None
    created_at: str
    filled_at: Optional[str] = None


class PositionResponse(BaseModel):
    """Position response model."""
    id: str
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    margin_used: float
    opened_at: str


class ClosePositionRequest(BaseModel):
    """Request to close a position."""
    size: Optional[float] = None  # None = close entire position


# In-memory trading state (demo purposes)
class TradingState:
    def __init__(self):
        self.balance: float = 100000.0
        self.initial_balance: float = 100000.0
        self.leverage: int = 100
        self.positions: dict[str, dict] = {}
        self.orders: dict[str, dict] = {}
        self.closed_trades: list[dict] = []
        self.equity_history: list[dict] = []

        # Simulated prices (would come from market data in production)
        self.prices: dict[str, float] = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 149.50,
            "USDCHF": 0.8750,
            "AUDUSD": 0.6550,
            "USDCAD": 1.3550,
            "NZDUSD": 0.6150,
        }

    def get_price(self, symbol: str) -> float:
        """Get current price for symbol (with small random variation)."""
        import random
        base_price = self.prices.get(symbol, 1.0)
        # Add small random spread simulation
        variation = base_price * random.uniform(-0.0005, 0.0005)
        return round(base_price + variation, 5)

    def calculate_margin(self, symbol: str, size: float) -> float:
        """Calculate required margin for a position."""
        price = self.get_price(symbol)
        # Standard lot = 100,000 units
        notional_value = size * 100000 * price
        return notional_value / self.leverage

    def calculate_equity(self) -> float:
        """Calculate total equity (balance + unrealized P&L)."""
        unrealized_pnl = sum(
            self._calculate_position_pnl(pos)
            for pos in self.positions.values()
        )
        return self.balance + unrealized_pnl

    def calculate_margin_used(self) -> float:
        """Calculate total margin used by open positions."""
        return sum(
            self.calculate_margin(pos["symbol"], pos["size"])
            for pos in self.positions.values()
        )

    def calculate_free_margin(self) -> float:
        """Calculate available margin for new positions."""
        return self.calculate_equity() - self.calculate_margin_used()

    def _calculate_position_pnl(self, position: dict) -> float:
        """Calculate unrealized P&L for a position."""
        current_price = self.get_price(position["symbol"])
        entry_price = position["entry_price"]
        size = position["size"]

        # Calculate pip difference
        if position["side"] == "long":
            pnl = (current_price - entry_price) * size * 100000
        else:
            pnl = (entry_price - current_price) * size * 100000

        return round(pnl, 2)


# Global trading state
_trading_state = TradingState()


@router.get("/positions", response_model=list[PositionResponse])
async def get_positions():
    """Get all open positions."""
    positions = []
    for pos_id, pos in _trading_state.positions.items():
        current_price = _trading_state.get_price(pos["symbol"])
        pnl = _trading_state._calculate_position_pnl(pos)
        pnl_percent = (pnl / (pos["entry_price"] * pos["size"] * 100000)) * 100

        positions.append(PositionResponse(
            id=pos_id,
            symbol=pos["symbol"],
            side=PositionSide(pos["side"]),
            size=pos["size"],
            entry_price=pos["entry_price"],
            current_price=current_price,
            unrealized_pnl=pnl,
            unrealized_pnl_percent=round(pnl_percent, 2),
            stop_loss=pos.get("stop_loss"),
            take_profit=pos.get("take_profit"),
            margin_used=_trading_state.calculate_margin(pos["symbol"], pos["size"]),
            opened_at=pos["opened_at"],
        ))

    return positions


@router.get("/orders", response_model=list[OrderResponse])
async def get_orders():
    """Get all pending orders."""
    orders = []
    for order_id, order in _trading_state.orders.items():
        orders.append(OrderResponse(
            id=order_id,
            symbol=order["symbol"],
            side=OrderSide(order["side"]),
            type=OrderType(order["type"]),
            size=order["size"],
            price=order.get("price"),
            stop_loss=order.get("stop_loss"),
            take_profit=order.get("take_profit"),
            status=OrderStatus(order["status"]),
            filled_price=order.get("filled_price"),
            created_at=order["created_at"],
            filled_at=order.get("filled_at"),
        ))

    return orders


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(request: PlaceOrderRequest):
    """Place a new order."""
    # Validate symbol
    if request.symbol not in _trading_state.prices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown symbol: {request.symbol}",
        )

    # Check margin for new position
    required_margin = _trading_state.calculate_margin(request.symbol, request.size)
    free_margin = _trading_state.calculate_free_margin()

    if required_margin > free_margin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient margin. Required: ${required_margin:.2f}, Available: ${free_margin:.2f}",
        )

    order_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    current_price = _trading_state.get_price(request.symbol)

    order = {
        "symbol": request.symbol,
        "side": request.side.value,
        "type": request.type.value,
        "size": request.size,
        "price": request.price,
        "stop_loss": request.stop_loss,
        "take_profit": request.take_profit,
        "status": "pending",
        "created_at": now,
    }

    # For market orders, execute immediately
    if request.type == OrderType.MARKET:
        order["status"] = "filled"
        order["filled_price"] = current_price
        order["filled_at"] = now

        # Create or update position
        position_side = "long" if request.side == OrderSide.BUY else "short"

        # Check if there's an existing position in the opposite direction
        for pos_id, pos in list(_trading_state.positions.items()):
            if pos["symbol"] == request.symbol and pos["side"] != position_side:
                # Close opposite position
                pnl = _trading_state._calculate_position_pnl(pos)
                _trading_state.balance += pnl

                _trading_state.closed_trades.append({
                    "id": str(uuid.uuid4()),
                    "symbol": pos["symbol"],
                    "side": pos["side"],
                    "size": pos["size"],
                    "entry_price": pos["entry_price"],
                    "exit_price": current_price,
                    "pnl": pnl,
                    "opened_at": pos["opened_at"],
                    "closed_at": now,
                })

                del _trading_state.positions[pos_id]

        # Create new position
        position_id = str(uuid.uuid4())
        _trading_state.positions[position_id] = {
            "symbol": request.symbol,
            "side": position_side,
            "size": request.size,
            "entry_price": current_price,
            "stop_loss": request.stop_loss,
            "take_profit": request.take_profit,
            "opened_at": now,
        }
    else:
        # Limit/Stop orders are stored as pending
        _trading_state.orders[order_id] = order

    return OrderResponse(
        id=order_id,
        symbol=order["symbol"],
        side=OrderSide(order["side"]),
        type=OrderType(order["type"]),
        size=order["size"],
        price=order.get("price"),
        stop_loss=order.get("stop_loss"),
        take_profit=order.get("take_profit"),
        status=OrderStatus(order["status"]),
        filled_price=order.get("filled_price"),
        created_at=order["created_at"],
        filled_at=order.get("filled_at"),
    )


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: str):
    """Cancel a pending order."""
    if order_id not in _trading_state.orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )

    order = _trading_state.orders[order_id]
    if order["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled",
        )

    order["status"] = "cancelled"
    del _trading_state.orders[order_id]


@router.post("/positions/{position_id}/close", response_model=dict)
async def close_position(position_id: str, request: Optional[ClosePositionRequest] = None):
    """Close an open position."""
    if position_id not in _trading_state.positions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position {position_id} not found",
        )

    position = _trading_state.positions[position_id]
    now = datetime.now().isoformat()
    current_price = _trading_state.get_price(position["symbol"])

    # Calculate P&L
    pnl = _trading_state._calculate_position_pnl(position)

    # Update balance
    _trading_state.balance += pnl

    # Record closed trade
    closed_trade = {
        "id": str(uuid.uuid4()),
        "symbol": position["symbol"],
        "side": position["side"],
        "size": position["size"],
        "entry_price": position["entry_price"],
        "exit_price": current_price,
        "pnl": pnl,
        "pnl_percent": round((pnl / (position["entry_price"] * position["size"] * 100000)) * 100, 2),
        "opened_at": position["opened_at"],
        "closed_at": now,
    }
    _trading_state.closed_trades.append(closed_trade)

    # Remove position
    del _trading_state.positions[position_id]

    return {
        "message": "Position closed",
        "trade": closed_trade,
    }


@router.get("/history", response_model=list[dict])
async def get_trade_history():
    """Get closed trade history."""
    return sorted(
        _trading_state.closed_trades,
        key=lambda x: x["closed_at"],
        reverse=True,
    )


@router.post("/reset", response_model=dict)
async def reset_account():
    """Reset the paper trading account to initial state."""
    global _trading_state
    _trading_state = TradingState()
    return {
        "message": "Account reset to initial state",
        "balance": _trading_state.balance,
    }
