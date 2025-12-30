"""AI Chat endpoint with trading assistant tools."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


# ============================================================================
# Trading State Access (avoid circular imports)
# ============================================================================

def _get_trading_state():
    """Get trading state using function-level import to avoid circular dependency."""
    from src.api.v1.endpoints.trading import _trading_state
    return _trading_state


def _get_portfolio_summary() -> dict[str, Any]:
    """Get portfolio summary data."""
    state = _get_trading_state()

    # Calculate unrealized P&L from open positions
    unrealized_pnl = 0.0
    for pos in state.positions.values():
        current_price = state.prices.get(pos["symbol"], pos["entry_price"])
        if pos["side"] == "long":
            pnl = (current_price - pos["entry_price"]) * pos["size"] * 100000
        else:
            pnl = (pos["entry_price"] - current_price) * pos["size"] * 100000
        unrealized_pnl += pnl

    # Calculate margin used
    margin_used = sum(pos.get("margin_used", 0) for pos in state.positions.values())

    equity = state.balance + unrealized_pnl
    initial_balance = 100000.0
    total_pnl = equity - initial_balance

    return {
        "balance": round(state.balance, 2),
        "equity": round(equity, 2),
        "margin": round(margin_used, 2),
        "free_margin": round(equity - margin_used, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_percent": round((total_pnl / initial_balance) * 100, 2),
    }


def _get_performance_metrics() -> dict[str, Any]:
    """Get trading performance metrics."""
    state = _get_trading_state()
    trades = state.closed_trades

    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "max_drawdown": 0.0,
        }

    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] < 0]

    total_wins = sum(t["pnl"] for t in wins) if wins else 0
    total_losses = abs(sum(t["pnl"] for t in losses)) if losses else 0

    return {
        "total_trades": len(trades),
        "win_rate": (len(wins) / len(trades)) * 100 if trades else 0,
        "profit_factor": total_wins / total_losses if total_losses > 0 else float('inf') if total_wins > 0 else 0,
        "average_win": total_wins / len(wins) if wins else 0,
        "average_loss": total_losses / len(losses) if losses else 0,
        "largest_win": max(t["pnl"] for t in wins) if wins else 0,
        "largest_loss": min(t["pnl"] for t in losses) if losses else 0,
        "max_drawdown": 0.0,  # Would need equity curve tracking for real calculation
    }


# ============================================================================
# Models
# ============================================================================

class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request with message history."""
    messages: list[ChatMessage] = Field(..., description="Chat message history")
    model: str = Field(default="anthropic/claude-3-haiku", description="Model to use via OpenRouter")


class ChatResponse(BaseModel):
    """Chat response from the assistant."""
    message: ChatMessage
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class ToolResult(BaseModel):
    """Result from a tool execution."""
    tool: str
    result: Any
    success: bool = True
    error: str | None = None


# ============================================================================
# Trading Tools (can be called by the AI)
# ============================================================================

def tool_get_portfolio() -> dict[str, Any]:
    """Get the current portfolio summary."""
    return _get_portfolio_summary()


def tool_get_positions() -> list[dict[str, Any]]:
    """Get all open positions."""
    state = _get_trading_state()
    positions = []
    for pos_id, pos in state.positions.items():
        current_price = state.prices.get(pos["symbol"], pos["entry_price"])

        # Calculate P&L
        if pos["side"] == "long":
            pnl = (current_price - pos["entry_price"]) * pos["size"] * 100000
        else:
            pnl = (pos["entry_price"] - current_price) * pos["size"] * 100000

        positions.append({
            "id": pos_id,
            "symbol": pos["symbol"],
            "side": pos["side"],
            "size": pos["size"],
            "entry_price": pos["entry_price"],
            "current_price": current_price,
            "unrealized_pnl": round(pnl, 2),
            "stop_loss": pos.get("stop_loss"),
            "take_profit": pos.get("take_profit"),
        })
    return positions


def tool_get_trade_history() -> list[dict[str, Any]]:
    """Get closed trade history."""
    state = _get_trading_state()
    return state.closed_trades[-20:]  # Last 20 trades


def tool_get_market_prices() -> dict[str, dict[str, float]]:
    """Get current market prices for all pairs."""
    state = _get_trading_state()
    result = {}
    for symbol, price in state.prices.items():
        spread = price * 0.0001
        result[symbol] = {
            "bid": round(price - spread / 2, 5),
            "ask": round(price + spread / 2, 5),
            "mid": round(price, 5),
        }
    return result


def tool_place_order(
    symbol: str,
    side: str,
    size: float,
    order_type: str = "market",
    stop_loss: float | None = None,
    take_profit: float | None = None,
) -> dict[str, Any]:
    """Place a trading order."""
    import uuid

    state = _get_trading_state()

    if symbol not in state.prices:
        return {"success": False, "error": f"Unknown symbol: {symbol}"}

    if side not in ["buy", "sell"]:
        return {"success": False, "error": "Side must be 'buy' or 'sell'"}

    if size <= 0 or size > 10:
        return {"success": False, "error": "Size must be between 0.01 and 10 lots"}

    price = state.prices[symbol]
    spread = price * 0.0001

    # Adjust price for spread
    if side == "buy":
        entry_price = price + spread / 2  # Buy at ask
        position_side = "long"
    else:
        entry_price = price - spread / 2  # Sell at bid
        position_side = "short"

    # Calculate margin
    position_value = size * 100000 * entry_price
    margin_required = position_value / state.leverage

    if margin_required > state.balance:
        return {"success": False, "error": "Insufficient margin"}

    # Create position
    position_id = str(uuid.uuid4())[:8]
    state.positions[position_id] = {
        "symbol": symbol,
        "side": position_side,
        "size": size,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "margin_used": margin_required,
        "opened_at": datetime.utcnow().isoformat(),
    }

    return {
        "success": True,
        "position_id": position_id,
        "symbol": symbol,
        "side": position_side,
        "size": size,
        "entry_price": entry_price,
        "margin_used": round(margin_required, 2),
    }


def tool_close_position(position_id: str) -> dict[str, Any]:
    """Close an open position."""
    state = _get_trading_state()

    if position_id not in state.positions:
        return {"success": False, "error": f"Position {position_id} not found"}

    pos = state.positions[position_id]
    current_price = state.prices.get(pos["symbol"], pos["entry_price"])

    # Calculate P&L
    if pos["side"] == "long":
        pnl = (current_price - pos["entry_price"]) * pos["size"] * 100000
    else:
        pnl = (pos["entry_price"] - current_price) * pos["size"] * 100000

    # Update balance
    state.balance += pnl

    # Record closed trade
    state.closed_trades.append({
        "id": position_id,
        "symbol": pos["symbol"],
        "side": pos["side"],
        "size": pos["size"],
        "entry_price": pos["entry_price"],
        "exit_price": current_price,
        "pnl": round(pnl, 2),
        "closed_at": datetime.utcnow().isoformat(),
    })

    # Remove position
    del state.positions[position_id]

    return {
        "success": True,
        "position_id": position_id,
        "pnl": round(pnl, 2),
        "new_balance": round(state.balance, 2),
    }


def tool_get_performance_metrics() -> dict[str, Any]:
    """Get trading performance metrics."""
    return _get_performance_metrics()


def tool_calculate_position_size(
    account_balance: float,
    risk_percent: float,
    stop_loss_pips: float,
    symbol: str = "EURUSD",
) -> dict[str, Any]:
    """Calculate optimal position size based on risk management."""
    if risk_percent <= 0 or risk_percent > 10:
        return {"error": "Risk percent must be between 0.1 and 10"}

    if stop_loss_pips <= 0:
        return {"error": "Stop loss pips must be positive"}

    # Calculate risk amount
    risk_amount = account_balance * (risk_percent / 100)

    # Pip value for standard lot (100,000 units)
    state = _get_trading_state()
    pip_value = 10 if "JPY" not in symbol else 1000 / state.prices.get(symbol, 100)

    # Position size in lots
    position_size = risk_amount / (stop_loss_pips * pip_value)

    return {
        "account_balance": account_balance,
        "risk_percent": risk_percent,
        "risk_amount": round(risk_amount, 2),
        "stop_loss_pips": stop_loss_pips,
        "recommended_lots": round(position_size, 2),
        "pip_value_per_lot": pip_value,
    }


def tool_analyze_trade(
    symbol: str,
    side: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
) -> dict[str, Any]:
    """Analyze a potential trade setup."""
    if side not in ["buy", "sell"]:
        return {"error": "Side must be 'buy' or 'sell'"}

    pip_multiplier = 10000 if "JPY" not in symbol else 100

    if side == "buy":
        sl_pips = (entry_price - stop_loss) * pip_multiplier
        tp_pips = (take_profit - entry_price) * pip_multiplier
    else:
        sl_pips = (stop_loss - entry_price) * pip_multiplier
        tp_pips = (entry_price - take_profit) * pip_multiplier

    risk_reward = tp_pips / sl_pips if sl_pips > 0 else 0

    # Simple analysis
    analysis = []
    if risk_reward >= 2:
        analysis.append("Good risk/reward ratio (2:1 or better)")
    elif risk_reward >= 1:
        analysis.append("Acceptable risk/reward ratio")
    else:
        analysis.append("Poor risk/reward ratio - consider adjusting levels")

    if sl_pips > 50:
        analysis.append("Wide stop loss - consider tighter risk management")
    elif sl_pips < 10:
        analysis.append("Tight stop loss - may get stopped out by noise")

    return {
        "symbol": symbol,
        "side": side,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "stop_loss_pips": round(sl_pips, 1),
        "take_profit_pips": round(tp_pips, 1),
        "risk_reward_ratio": round(risk_reward, 2),
        "analysis": analysis,
    }


# Tool registry
AVAILABLE_TOOLS = {
    "get_portfolio": {
        "function": tool_get_portfolio,
        "description": "Get current portfolio summary including balance, equity, margin, and P&L",
        "parameters": {},
    },
    "get_positions": {
        "function": tool_get_positions,
        "description": "Get all open trading positions with current P&L",
        "parameters": {},
    },
    "get_trade_history": {
        "function": tool_get_trade_history,
        "description": "Get recent closed trade history",
        "parameters": {},
    },
    "get_market_prices": {
        "function": tool_get_market_prices,
        "description": "Get current bid/ask prices for all currency pairs",
        "parameters": {},
    },
    "place_order": {
        "function": tool_place_order,
        "description": "Place a new trading order (market or limit)",
        "parameters": {
            "symbol": "Currency pair (e.g., EURUSD, GBPUSD)",
            "side": "Order side: 'buy' or 'sell'",
            "size": "Position size in lots (0.01 to 10)",
            "order_type": "Order type: 'market' or 'limit' (default: market)",
            "stop_loss": "Stop loss price (optional)",
            "take_profit": "Take profit price (optional)",
        },
    },
    "close_position": {
        "function": tool_close_position,
        "description": "Close an open position by its ID",
        "parameters": {
            "position_id": "The ID of the position to close",
        },
    },
    "get_performance_metrics": {
        "function": tool_get_performance_metrics,
        "description": "Get trading performance metrics (win rate, profit factor, Sharpe ratio, etc.)",
        "parameters": {},
    },
    "calculate_position_size": {
        "function": tool_calculate_position_size,
        "description": "Calculate optimal position size based on risk management rules",
        "parameters": {
            "account_balance": "Current account balance",
            "risk_percent": "Percentage of account to risk (e.g., 1 for 1%)",
            "stop_loss_pips": "Distance to stop loss in pips",
            "symbol": "Currency pair (default: EURUSD)",
        },
    },
    "analyze_trade": {
        "function": tool_analyze_trade,
        "description": "Analyze a potential trade setup for risk/reward",
        "parameters": {
            "symbol": "Currency pair",
            "side": "Trade direction: 'buy' or 'sell'",
            "entry_price": "Planned entry price",
            "stop_loss": "Planned stop loss price",
            "take_profit": "Planned take profit price",
        },
    },
}


# ============================================================================
# Simple AI Response (without external API dependency)
# ============================================================================

def generate_ai_response(messages: list[ChatMessage], tools_context: str) -> str:
    """Generate a simple rule-based response for demo purposes.

    In production, this would call OpenRouter/LangChain.
    For demo, we provide helpful responses based on keywords.
    """
    last_message = messages[-1].content.lower() if messages else ""

    # Portfolio queries
    if any(word in last_message for word in ["portfolio", "balance", "equity", "account"]):
        portfolio = tool_get_portfolio()
        return f"""Here's your current portfolio status:

**Account Summary:**
- Balance: ${portfolio['balance']:,.2f}
- Equity: ${portfolio['equity']:,.2f}
- Free Margin: ${portfolio['free_margin']:,.2f}
- Margin Used: ${portfolio['margin']:,.2f}
- Total P&L: ${portfolio['total_pnl']:,.2f} ({portfolio['total_pnl_percent']:.2f}%)

{'You have open positions affecting your equity.' if portfolio['unrealized_pnl'] != 0 else 'No open positions currently.'}"""

    # Position queries
    if any(word in last_message for word in ["position", "trade", "open"]):
        positions = tool_get_positions()
        if not positions:
            return "You don't have any open positions currently. Would you like me to help you analyze a potential trade?"

        pos_text = "\n".join([
            f"- **{p['symbol']}** {p['side'].upper()}: {p['size']} lots @ {p['entry_price']:.5f} → P&L: ${p['unrealized_pnl']:,.2f}"
            for p in positions
        ])
        return f"**Your Open Positions:**\n{pos_text}"

    # Price queries
    if any(word in last_message for word in ["price", "quote", "rate", "market"]):
        prices = tool_get_market_prices()
        price_text = "\n".join([
            f"- **{symbol}**: Bid {data['bid']:.5f} / Ask {data['ask']:.5f}"
            for symbol, data in list(prices.items())[:5]
        ])
        return f"**Current Market Prices:**\n{price_text}\n\nPrices update in real-time via WebSocket on the Trading page."

    # Performance queries
    if any(word in last_message for word in ["performance", "metrics", "stats", "win rate"]):
        metrics = tool_get_performance_metrics()
        return f"""**Your Trading Performance:**
- Total Trades: {metrics['total_trades']}
- Win Rate: {metrics['win_rate']:.1f}%
- Profit Factor: {metrics['profit_factor']:.2f}
- Average Win: ${metrics['average_win']:,.2f}
- Average Loss: ${metrics['average_loss']:,.2f}
- Largest Win: ${metrics['largest_win']:,.2f}
- Largest Loss: ${metrics['largest_loss']:,.2f}
- Max Drawdown: {metrics['max_drawdown']:.2f}%

{'Good job maintaining a positive expectancy!' if metrics['profit_factor'] > 1 else 'Consider reviewing your strategy - profit factor is below 1.'}"""

    # Risk management queries
    if any(word in last_message for word in ["risk", "position size", "lot", "calculate"]):
        # Extract numbers from message for calculation
        import re
        numbers = re.findall(r'\d+\.?\d*', last_message)

        if len(numbers) >= 2:
            state = _get_trading_state()
            balance = float(numbers[0]) if float(numbers[0]) > 100 else state.balance
            risk_pct = float(numbers[1]) if float(numbers[1]) <= 10 else 1.0
            sl_pips = float(numbers[2]) if len(numbers) > 2 else 20

            result = tool_calculate_position_size(balance, risk_pct, sl_pips)
            return f"""**Position Size Calculation:**
- Account Balance: ${result['account_balance']:,.2f}
- Risk: {result['risk_percent']}% (${result['risk_amount']:,.2f})
- Stop Loss: {result['stop_loss_pips']} pips
- **Recommended Size: {result['recommended_lots']} lots**

This ensures you only risk {result['risk_percent']}% of your account on this trade."""

        return """To calculate position size, I need:
1. Your account balance
2. Risk percentage (typically 1-2%)
3. Stop loss distance in pips

For example: "Calculate position size for $10,000 account, 1% risk, 20 pip stop loss"

**General Rule:** Never risk more than 1-2% of your account on a single trade."""

    # Trading advice
    if any(word in last_message for word in ["buy", "sell", "should i", "advice", "recommend"]):
        return """I can help you analyze trades, but I don't provide trading recommendations. Here's what I can do:

1. **Analyze your trade setup** - Tell me the symbol, direction, entry, stop loss, and take profit
2. **Calculate position size** - Based on your risk tolerance
3. **Review your performance** - Look at your trading statistics
4. **Show market prices** - Current bid/ask for all pairs

Remember: Most trading strategies don't beat random chance or buy-and-hold over time. Always use proper risk management!"""

    # Help
    if any(word in last_message for word in ["help", "what can you", "how do i"]):
        return """I'm your trading assistant! Here's what I can help with:

**Portfolio & Positions:**
- "Show my portfolio" - Account summary
- "What are my open positions?" - Current trades
- "Show my performance" - Trading statistics

**Market Data:**
- "What's the EUR/USD price?" - Current quotes
- "Show market prices" - All pairs

**Risk Management:**
- "Calculate position size for $10k, 1% risk, 20 pip stop" - Sizing
- "Analyze trade: buy EURUSD at 1.0850, SL 1.0800, TP 1.0950" - Setup analysis

**Trading:**
- Use the Trading page to place actual orders
- I can help you plan, but execution is up to you!

What would you like to know?"""

    # Default response
    return """I'm here to help with your trading! You can ask me about:

- Your portfolio and positions
- Market prices
- Position sizing and risk management
- Trade analysis
- Performance metrics

What would you like to know?"""


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat with the trading assistant.

    The assistant can help with:
    - Portfolio and position queries
    - Market price information
    - Risk management calculations
    - Trade analysis
    - Performance metrics
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    # Build tools context
    tools_context = "Available tools:\n" + "\n".join([
        f"- {name}: {info['description']}"
        for name, info in AVAILABLE_TOOLS.items()
    ])

    # Generate response
    response_text = generate_ai_response(request.messages, tools_context)

    return ChatResponse(
        message=ChatMessage(role="assistant", content=response_text),
        tool_calls=[],
    )


@router.get("/tools")
async def list_tools() -> dict[str, Any]:
    """List available AI tools."""
    return {
        "tools": [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"],
            }
            for name, info in AVAILABLE_TOOLS.items()
        ]
    }


@router.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: dict[str, Any] = {}) -> ToolResult:
    """Execute a specific tool directly."""
    if tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    try:
        tool_func = AVAILABLE_TOOLS[tool_name]["function"]
        result = tool_func(**params)
        return ToolResult(tool=tool_name, result=result)
    except Exception as e:
        return ToolResult(tool=tool_name, result=None, success=False, error=str(e))
