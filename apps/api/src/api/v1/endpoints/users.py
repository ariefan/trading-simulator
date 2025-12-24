"""User profile and settings endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel

from src.api.v1.endpoints.auth import get_current_user_id, get_user, _users
from src.config import settings

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class UserProfile(BaseModel):
    """User profile information."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    initial_balance: float = 100000.0
    created_at: str


class UserProfileUpdate(BaseModel):
    """User profile update request."""
    name: Optional[str] = None
    picture: Optional[str] = None


class UserSettings(BaseModel):
    """User settings."""
    default_leverage: int = 100
    default_lot_size: float = 0.1
    theme: str = "dark"
    notifications_enabled: bool = True


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(authorization: Optional[str] = Header(None)):
    """Get the current user's profile."""
    user_id = get_current_user_id(authorization)
    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserProfile(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        picture=user.get("picture"),
        initial_balance=settings.default_initial_balance,
        created_at=user.get("created_at", ""),
    )


@router.patch("/me", response_model=UserProfile)
async def update_current_user(
    update: UserProfileUpdate,
    authorization: Optional[str] = Header(None),
):
    """Update the current user's profile."""
    user_id = get_current_user_id(authorization)
    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update fields
    if update.name is not None:
        user["name"] = update.name
    if update.picture is not None:
        user["picture"] = update.picture

    # Save back
    _users[user_id] = user

    return UserProfile(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        picture=user.get("picture"),
        initial_balance=settings.default_initial_balance,
        created_at=user.get("created_at", ""),
    )


@router.get("/me/settings", response_model=UserSettings)
async def get_user_settings(authorization: Optional[str] = Header(None)):
    """Get the current user's settings."""
    user_id = get_current_user_id(authorization)
    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_settings = user.get("settings", {})
    return UserSettings(
        default_leverage=user_settings.get("default_leverage", settings.default_leverage),
        default_lot_size=user_settings.get("default_lot_size", 0.1),
        theme=user_settings.get("theme", "dark"),
        notifications_enabled=user_settings.get("notifications_enabled", True),
    )


@router.patch("/me/settings", response_model=UserSettings)
async def update_user_settings(
    new_settings: UserSettings,
    authorization: Optional[str] = Header(None),
):
    """Update the current user's settings."""
    user_id = get_current_user_id(authorization)
    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Validate leverage
    if new_settings.default_leverage < 1 or new_settings.default_leverage > settings.max_leverage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leverage must be between 1 and {settings.max_leverage}",
        )

    # Update settings
    user["settings"] = {
        "default_leverage": new_settings.default_leverage,
        "default_lot_size": new_settings.default_lot_size,
        "theme": new_settings.theme,
        "notifications_enabled": new_settings.notifications_enabled,
    }

    # Save back
    _users[user_id] = user

    return new_settings
