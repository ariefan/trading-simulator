from fastapi import APIRouter

from src.api.v1.endpoints import auth, backtests, market, portfolio, strategies, trading, users, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["Backtesting"])
api_router.include_router(trading.router, prefix="/trading", tags=["Paper Trading"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
