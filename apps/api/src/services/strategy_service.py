"""Strategy service - handles custom strategy storage and management."""
import uuid
from datetime import datetime
from typing import Any, Optional

class StrategyService:
    """Service for managing custom and built-in strategies."""

    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self._strategies_store: dict[str, dict] = {}

    def list_strategies(self, skip: int = 0, limit: int = 20) -> tuple[list[dict], int]:
        """List custom strategies."""
        strategies = list(self._strategies_store.values())
        strategies.sort(key=lambda x: x["created_at"], reverse=True)
        return strategies[skip:skip + limit], len(strategies)

    def get_strategy(self, strategy_id: str) -> Optional[dict]:
        """Get a specific custom strategy."""
        return self._strategies_store.get(strategy_id)

    def create_strategy(self, name: str, code: str, description: str = "", parameters: list = None) -> dict:
        """Create a new custom strategy."""
        now = datetime.now().isoformat()
        strategy_id = str(uuid.uuid4())

        strategy_data = {
            "id": strategy_id,
            "name": name,
            "description": description,
            "code": code,
            "parameters": parameters or [],
            "created_at": now,
            "updated_at": now,
        }

        self._strategies_store[strategy_id] = strategy_data
        return strategy_data

    def update_strategy(self, strategy_id: str, updates: dict) -> Optional[dict]:
        """Update an existing custom strategy."""
        if strategy_id not in self._strategies_store:
            return None

        strategy = self._strategies_store[strategy_id]
        
        if "name" in updates:
            strategy["name"] = updates["name"]
        if "description" in updates:
            strategy["description"] = updates["description"]
        if "code" in updates:
            strategy["code"] = updates["code"]
        if "parameters" in updates:
            strategy["parameters"] = updates["parameters"]
            
        strategy["updated_at"] = datetime.now().isoformat()
        return strategy

    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete a custom strategy."""
        if strategy_id in self._strategies_store:
            del self._strategies_store[strategy_id]
            return True
        return False

# Singleton instance
strategy_service = StrategyService()
