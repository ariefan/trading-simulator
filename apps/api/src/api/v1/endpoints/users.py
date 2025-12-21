from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter()


class UserProfile(BaseModel):
    """User profile information."""

    id: str
    email: str
    name: str
    picture: str | None = None
    initial_balance: float = 100000.0
    created_at: str


class UserSettings(BaseModel):
    """User settings."""

    default_leverage: int = 100
    default_lot_size: float = 0.1
    theme: str = "dark"
    notifications_enabled: bool = True


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's profile."""
    # TODO: Implement with actual auth
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.patch("/me", response_model=UserProfile)
async def update_current_user(
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.get("/me/settings", response_model=UserSettings)
async def get_user_settings(
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's settings."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.patch("/me/settings", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettings,
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's settings."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
