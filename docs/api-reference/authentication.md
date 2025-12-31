# Authentication API

Endpoints for user authentication and token management.

## Demo Authentication

### POST `/auth/demo`

Create a demo account and get an access token.

**Request:**
```json
{
  "name": "Demo Trader"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "demo_abc123",
    "email": "demo_abc@trading.local",
    "name": "Demo Trader",
    "picture": null
  }
}
```

---

## Google OAuth

### POST `/auth/google`

Authenticate with Google OAuth credential.

**Request:**
```json
{
  "credential": "google-oauth-token"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user_123",
    "email": "user@gmail.com",
    "name": "John Doe",
    "picture": "https://..."
  }
}
```

---

## Token Verification

### GET `/auth/verify`

Verify the current token and get user info.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (authenticated):**
```json
{
  "authenticated": true,
  "user": {
    "id": "demo_abc123",
    "email": "demo_abc@trading.local",
    "name": "Demo Trader",
    "picture": null
  }
}
```

**Response (not authenticated):**
```json
{
  "authenticated": false,
  "user": null
}
```

---

## Token Refresh

### POST `/auth/refresh`

Refresh an expiring token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## User Profile

### GET `/users/me`

Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "demo_abc123",
  "email": "demo_abc@trading.local",
  "name": "Demo Trader",
  "picture": null,
  "initial_balance": 100000,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### PATCH `/users/me`

Update user profile.

**Request:**
```json
{
  "name": "New Name"
}
```

---

## User Settings

### GET `/users/me/settings`

Get user trading settings.

**Response:**
```json
{
  "default_leverage": 100,
  "default_lot_size": 0.1,
  "theme": "dark",
  "notifications_enabled": true
}
```

### PATCH `/users/me/settings`

Update user settings.

**Request:**
```json
{
  "default_leverage": 50,
  "theme": "light"
}
```

---

## Using Tokens

Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  http://localhost:8000/api/v1/users/me
```

In JavaScript:

```javascript
const response = await fetch('/api/v1/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```
