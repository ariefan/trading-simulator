from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth callback."""

    credential: str


class TokenResponse(BaseModel):
    """Response containing access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User information response."""

    id: str
    email: str
    name: str
    picture: str | None = None


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate with Google OAuth.

    Verifies the Google credential and creates/updates the user.
    Returns a JWT access token.
    """
    # TODO: Implement Google OAuth verification
    # 1. Verify the Google credential token
    # 2. Extract user info (email, name, picture)
    # 3. Create or update user in database
    # 4. Generate and return JWT token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth not yet implemented",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token():
    """Refresh an expired access token."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented",
    )


@router.post("/logout")
async def logout():
    """Logout the current user."""
    return {"message": "Logged out successfully"}
