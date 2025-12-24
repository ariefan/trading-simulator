"""Authentication endpoints with JWT tokens and Google OAuth support."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets

from fastapi import APIRouter, HTTPException, status, Header
from jose import JWTError, jwt
from pydantic import BaseModel

from src.config import settings

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth callback."""
    credential: str


class DemoAuthRequest(BaseModel):
    """Request body for demo authentication."""
    name: str = "Demo Trader"


class UserResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None


class TokenResponse(BaseModel):
    """Response containing access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# ============================================================================
# In-memory user store (for demo purposes)
# ============================================================================

# Store users by ID
_users: dict[str, dict] = {}


def create_user(user_id: str, email: str, name: str, picture: Optional[str] = None) -> dict:
    """Create or update a user in the store."""
    user = {
        "id": user_id,
        "email": email,
        "name": name,
        "picture": picture,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "settings": {
            "default_leverage": settings.default_leverage,
            "default_lot_size": 0.1,
            "theme": "dark",
            "notifications_enabled": True,
        },
    }
    _users[user_id] = user
    return user


def get_user(user_id: str) -> Optional[dict]:
    """Get a user by ID."""
    return _users.get(user_id)


# ============================================================================
# JWT Token Functions
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Extract and verify user ID from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google OAuth.

    In production, this would verify the Google credential token.
    For demo purposes, we accept the credential and create a user.
    """
    # In production, you would:
    # 1. Verify the Google credential using google-auth library
    # 2. Extract user info from the verified token
    # 3. Create or update the user in the database

    # For demo, we create a mock user based on the credential
    credential_hash = secrets.token_hex(8)
    user_id = f"google_{credential_hash}"
    email = f"user_{credential_hash[:6]}@demo.trading"
    name = f"Trader {credential_hash[:6].upper()}"

    user = create_user(user_id, email, name, None)

    access_token = create_access_token(
        data={"sub": user_id, "email": email, "name": name}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
        ),
    )


@router.post("/demo", response_model=TokenResponse)
async def demo_auth(request: DemoAuthRequest):
    """
    Create a demo account for testing without Google OAuth.

    This endpoint allows quick access for development and testing.
    """
    demo_id = secrets.token_hex(8)
    user_id = f"demo_{demo_id}"
    email = f"demo_{demo_id[:6]}@trading.local"
    name = request.name or "Demo Trader"

    user = create_user(user_id, email, name, None)

    access_token = create_access_token(
        data={"sub": user_id, "email": email, "name": name}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(authorization: Optional[str] = Header(None)):
    """Refresh an expired access token."""
    user_id = get_current_user_id(authorization)
    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"], "name": user["name"]}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
        ),
    )


@router.post("/logout")
async def logout():
    """Logout the current user."""
    return {"message": "Logged out successfully"}


@router.get("/verify")
async def verify_auth(authorization: Optional[str] = Header(None)):
    """Verify the current authentication status."""
    try:
        user_id = get_current_user_id(authorization)
        user = get_user(user_id)
        if user:
            return {
                "authenticated": True,
                "user": UserResponse(
                    id=user["id"],
                    email=user["email"],
                    name=user["name"],
                    picture=user.get("picture"),
                ),
            }
    except HTTPException:
        pass

    return {"authenticated": False, "user": None}
