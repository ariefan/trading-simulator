"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health/root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data


class TestMarketEndpoints:
    """Tests for market data endpoints."""

    def test_get_currency_pairs(self, client):
        """Test getting list of currency pairs."""
        response = client.get("/api/v1/market/pairs")
        assert response.status_code == 200

        pairs = response.json()
        assert isinstance(pairs, list)
        assert len(pairs) > 0

        # Check structure
        pair = pairs[0]
        assert "symbol" in pair
        assert "base_currency" in pair
        assert "quote_currency" in pair

    def test_get_specific_pair(self, client):
        """Test getting specific currency pair."""
        response = client.get("/api/v1/market/pairs/EURUSD")
        assert response.status_code == 200

        pair = response.json()
        assert pair["symbol"] == "EURUSD"

    def test_get_invalid_pair_returns_404(self, client):
        """Test getting invalid pair returns 404."""
        response = client.get("/api/v1/market/pairs/INVALID")
        assert response.status_code == 404

    def test_get_candles(self, client):
        """Test getting candle data."""
        response = client.get("/api/v1/market/candles/EURUSD?timeframe=1h&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert "candles" in data
        assert len(data["candles"]) <= 10


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_demo_auth(self, client):
        """Test demo authentication."""
        response = client.post(
            "/api/v1/auth/demo",
            json={"name": "Test Trader"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["token_type"] == "bearer"

    def test_verify_with_valid_token(self, client):
        """Test token verification with valid token."""
        # First get a token
        auth_response = client.post(
            "/api/v1/auth/demo",
            json={"name": "Test Trader"}
        )
        token = auth_response.json()["access_token"]

        # Verify it
        response = client.get(
            "/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["authenticated"] == True
        assert data["user"] is not None

    def test_verify_without_token(self, client):
        """Test verification without token returns unauthenticated."""
        response = client.get("/api/v1/auth/verify")
        assert response.status_code == 200

        data = response.json()
        assert data["authenticated"] == False


class TestTradingEndpoints:
    """Tests for trading endpoints."""

    def test_get_positions(self, client):
        """Test getting open positions."""
        response = client.get("/api/v1/trading/positions")
        assert response.status_code == 200

        positions = response.json()
        assert isinstance(positions, list)

    def test_get_orders(self, client):
        """Test getting orders."""
        response = client.get("/api/v1/trading/orders")
        assert response.status_code == 200

        orders = response.json()
        assert isinstance(orders, list)

    def test_place_market_order(self, client):
        """Test placing a market order."""
        response = client.post(
            "/api/v1/trading/orders",
            json={
                "symbol": "EURUSD",
                "side": "buy",
                "type": "market",
                "size": 0.1
            }
        )
        assert response.status_code == 200

        order = response.json()
        assert order["symbol"] == "EURUSD"
        assert order["side"] == "buy"

    def test_get_trade_history(self, client):
        """Test getting trade history."""
        response = client.get("/api/v1/trading/history")
        assert response.status_code == 200

        history = response.json()
        assert isinstance(history, list)


class TestPortfolioEndpoints:
    """Tests for portfolio endpoints."""

    def test_get_portfolio_summary(self, client):
        """Test getting portfolio summary."""
        response = client.get("/api/v1/portfolio/")
        assert response.status_code == 200

        portfolio = response.json()
        assert "balance" in portfolio
        assert "equity" in portfolio
        assert "margin" in portfolio

    def test_get_portfolio_history(self, client):
        """Test getting portfolio history."""
        response = client.get("/api/v1/portfolio/history")
        assert response.status_code == 200

        history = response.json()
        assert isinstance(history, list)

    def test_get_performance_metrics(self, client):
        """Test getting performance metrics."""
        response = client.get("/api/v1/portfolio/metrics")
        assert response.status_code == 200

        metrics = response.json()
        assert "total_trades" in metrics
        assert "win_rate" in metrics


class TestAIEndpoints:
    """Tests for AI assistant endpoints."""

    def test_chat_endpoint(self, client):
        """Test chat with AI assistant."""
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What is my portfolio balance?"}
                ]
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert data["message"]["role"] == "assistant"

    def test_list_tools(self, client):
        """Test listing AI tools."""
        response = client.get("/api/v1/ai/tools")
        assert response.status_code == 200

        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) > 0

    def test_execute_tool(self, client):
        """Test executing a specific tool."""
        response = client.post(
            "/api/v1/ai/tools/get_portfolio",
            json={}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["success"] == True
        assert result["tool"] == "get_portfolio"


class TestSignalsEndpoints:
    """Tests for trading signals endpoints."""

    def test_get_all_signals(self, client):
        """Test getting all trading signals."""
        response = client.get("/api/v1/signals/")
        assert response.status_code == 200

        signals = response.json()
        assert isinstance(signals, list)

    def test_get_signal_for_symbol(self, client):
        """Test getting signal for specific symbol."""
        response = client.get("/api/v1/signals/EURUSD")
        assert response.status_code == 200

        signal = response.json()
        assert "symbol" in signal
        assert "signal" in signal

    def test_get_pattern_analysis(self, client):
        """Test getting pattern analysis."""
        response = client.get("/api/v1/signals/EURUSD/patterns")
        assert response.status_code == 200

        patterns = response.json()
        assert "symbol" in patterns
        assert "patterns" in patterns

    def test_get_risk_assessment(self, client):
        """Test getting risk assessment."""
        response = client.get("/api/v1/signals/EURUSD/risk")
        assert response.status_code == 200

        risk = response.json()
        assert "symbol" in risk

    def test_get_full_analysis(self, client):
        """Test getting full analysis."""
        response = client.get("/api/v1/signals/EURUSD/analysis")
        assert response.status_code == 200

        analysis = response.json()
        assert "symbol" in analysis
        assert "signals" in analysis


class TestBacktestEndpoints:
    """Tests for backtesting endpoints."""

    def test_list_strategies(self, client):
        """Test listing available strategies."""
        response = client.get("/api/v1/backtests/strategies")
        assert response.status_code == 200

        strategies = response.json()
        assert isinstance(strategies, list)
        assert len(strategies) > 0

    def test_run_backtest(self, client):
        """Test running a backtest."""
        response = client.post(
            "/api/v1/backtests/",
            json={
                "strategy_id": "sma_crossover",
                "symbol": "EURUSD",
                "timeframe": "1h",
                "start_date": "2024-01-01",
                "end_date": "2024-03-01",
                "initial_balance": 10000,
                "leverage": 100,
                "parameters": {
                    "fast_period": 10,
                    "slow_period": 20
                }
            }
        )
        assert response.status_code == 200

        result = response.json()
        assert "id" in result or "metrics" in result


class TestUserEndpoints:
    """Tests for user endpoints."""

    def test_get_user_profile_with_token(self, client):
        """Test getting user profile with valid token."""
        # Get token first
        auth_response = client.post(
            "/api/v1/auth/demo",
            json={"name": "Test User"}
        )
        token = auth_response.json()["access_token"]

        # Get profile
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        profile = response.json()
        assert "id" in profile
        assert "name" in profile

    def test_get_user_settings_with_token(self, client):
        """Test getting user settings."""
        # Get token first
        auth_response = client.post(
            "/api/v1/auth/demo",
            json={"name": "Test User"}
        )
        token = auth_response.json()["access_token"]

        # Get settings
        response = client.get(
            "/api/v1/users/me/settings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        settings = response.json()
        assert "default_leverage" in settings
        assert "theme" in settings

    def test_update_user_settings(self, client):
        """Test updating user settings."""
        # Get token first
        auth_response = client.post(
            "/api/v1/auth/demo",
            json={"name": "Test User"}
        )
        token = auth_response.json()["access_token"]

        # Update settings
        response = client.patch(
            "/api/v1/users/me/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={"default_leverage": 50, "theme": "light"}
        )
        assert response.status_code == 200

        settings = response.json()
        assert settings["default_leverage"] == 50
        assert settings["theme"] == "light"
