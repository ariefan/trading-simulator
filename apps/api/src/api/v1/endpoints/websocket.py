"""WebSocket endpoint for real-time price updates."""

import asyncio
import json
import random
from datetime import datetime
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    def subscribe(self, websocket: WebSocket, symbols: list[str]):
        """Subscribe to price updates for symbols."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].update(symbols)

    def unsubscribe(self, websocket: WebSocket, symbols: list[str]):
        """Unsubscribe from price updates for symbols."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].difference_update(symbols)

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict[str, Any]):
        """Broadcast a message to all connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_price(self, symbol: str, price_data: dict[str, Any]):
        """Broadcast price update to subscribers of a symbol."""
        message = {"type": "price", "symbol": symbol, "data": price_data}
        disconnected = []
        for connection in self.active_connections:
            if symbol in self.subscriptions.get(connection, set()):
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

# Simulated base prices for forex pairs
BASE_PRICES: dict[str, float] = {
    "EURUSD": 1.0850,
    "GBPUSD": 1.2650,
    "USDJPY": 149.50,
    "AUDUSD": 0.6550,
    "USDCAD": 1.3600,
    "USDCHF": 0.8750,
    "NZDUSD": 0.6100,
    "EURGBP": 0.8580,
    "EURJPY": 162.20,
    "GBPJPY": 189.10,
}

# Current simulated prices (will fluctuate)
current_prices: dict[str, dict[str, float]] = {}


def initialize_prices():
    """Initialize prices with bid/ask spreads."""
    for symbol, mid_price in BASE_PRICES.items():
        spread = mid_price * 0.0001  # 1 pip spread
        current_prices[symbol] = {
            "bid": mid_price - spread / 2,
            "ask": mid_price + spread / 2,
            "mid": mid_price,
        }


def simulate_price_tick(symbol: str) -> dict[str, Any]:
    """Simulate a price tick with random movement."""
    if symbol not in current_prices:
        if symbol not in BASE_PRICES:
            return {}
        initialize_prices()

    prices = current_prices[symbol]

    # Random price movement (-5 to +5 pips)
    pip_size = 0.0001 if "JPY" not in symbol else 0.01
    movement = random.uniform(-5, 5) * pip_size

    # Update prices
    prices["mid"] += movement
    spread = prices["mid"] * 0.0001
    prices["bid"] = prices["mid"] - spread / 2
    prices["ask"] = prices["mid"] + spread / 2

    # Calculate daily change (simulated)
    base = BASE_PRICES.get(symbol, prices["mid"])
    change = prices["mid"] - base
    change_percent = (change / base) * 100

    return {
        "bid": round(prices["bid"], 5 if "JPY" not in symbol else 3),
        "ask": round(prices["ask"], 5 if "JPY" not in symbol else 3),
        "mid": round(prices["mid"], 5 if "JPY" not in symbol else 3),
        "spread": round((prices["ask"] - prices["bid"]) * (10000 if "JPY" not in symbol else 100), 1),
        "change": round(change, 5 if "JPY" not in symbol else 3),
        "changePercent": round(change_percent, 3),
        "timestamp": datetime.utcnow().isoformat(),
    }


async def price_broadcaster():
    """Background task to broadcast price updates."""
    initialize_prices()

    while True:
        # Broadcast prices for all symbols that have subscribers
        all_subscribed_symbols: set[str] = set()
        for symbols in manager.subscriptions.values():
            all_subscribed_symbols.update(symbols)

        for symbol in all_subscribed_symbols:
            price_data = simulate_price_tick(symbol)
            if price_data:
                await manager.broadcast_price(symbol, price_data)

        # Update every 500ms for realistic tick simulation
        await asyncio.sleep(0.5)


# Global task reference
_broadcaster_task: asyncio.Task | None = None


def start_broadcaster():
    """Start the price broadcaster if not already running."""
    global _broadcaster_task
    if _broadcaster_task is None or _broadcaster_task.done():
        _broadcaster_task = asyncio.create_task(price_broadcaster())


@router.websocket("/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates.

    Send JSON messages to subscribe/unsubscribe:
    - {"action": "subscribe", "symbols": ["EURUSD", "GBPUSD"]}
    - {"action": "unsubscribe", "symbols": ["EURUSD"]}

    Receive price updates:
    - {"type": "price", "symbol": "EURUSD", "data": {...}}
    """
    await manager.connect(websocket)

    # Start broadcaster if not running
    start_broadcaster()

    # Send welcome message with available symbols
    await manager.send_personal_message(
        {
            "type": "connected",
            "message": "Connected to price feed",
            "availableSymbols": list(BASE_PRICES.keys()),
        },
        websocket,
    )

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                symbols = message.get("symbols", [])

                if action == "subscribe":
                    # Validate symbols
                    valid_symbols = [s for s in symbols if s in BASE_PRICES]
                    manager.subscribe(websocket, valid_symbols)

                    # Send initial prices for subscribed symbols
                    for symbol in valid_symbols:
                        price_data = simulate_price_tick(symbol)
                        if price_data:
                            await manager.send_personal_message(
                                {"type": "price", "symbol": symbol, "data": price_data},
                                websocket,
                            )

                    await manager.send_personal_message(
                        {
                            "type": "subscribed",
                            "symbols": valid_symbols,
                        },
                        websocket,
                    )

                elif action == "unsubscribe":
                    manager.unsubscribe(websocket, symbols)
                    await manager.send_personal_message(
                        {
                            "type": "unsubscribed",
                            "symbols": symbols,
                        },
                        websocket,
                    )

                elif action == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON"},
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
