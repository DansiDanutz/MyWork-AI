"""
Authentication middleware and utilities using Clerk.
"""

from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
import httpx

from config import settings

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)

# Clerk JWKS URL for verifying tokens
CLERK_JWKS_URL = f"https://{settings.CLERK_FRONTEND_API}/.well-known/jwks.json"

# Cache for JWKS client
_jwks_client: Optional[PyJWKClient] = None


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client for Clerk token verification."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(CLERK_JWKS_URL)
    return _jwks_client


async def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT token and return the claims.

    Args:
        token: The JWT token from Clerk

    Returns:
        dict: The decoded token claims including user_id (sub)

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get the signing key from Clerk's JWKS
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify the token
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_exp": True,
                "verify_aud": False,  # Clerk doesn't use audience
            }
        )

        return claims

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )


class CurrentUser:
    """Represents the current authenticated user."""

    def __init__(self, user_id: str, email: Optional[str] = None, claims: dict = None):
        self.user_id = user_id
        self.email = email
        self.claims = claims or {}

    @property
    def session_id(self) -> Optional[str]:
        return self.claims.get("sid")

    @property
    def organization_id(self) -> Optional[str]:
        return self.claims.get("org_id")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user.

    Usage:
        @router.get("/me")
        async def get_me(user: CurrentUser = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    token = credentials.credentials
    claims = await verify_clerk_token(token)

    return CurrentUser(
        user_id=claims.get("sub"),
        email=claims.get("email"),
        claims=claims
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Dependency to optionally get the current user.
    Returns None if not authenticated instead of raising an error.

    Usage:
        @router.get("/products")
        async def list_products(user: Optional[CurrentUser] = Depends(get_optional_user)):
            if user:
                # Show personalized results
            else:
                # Show public results
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        claims = await verify_clerk_token(token)
        return CurrentUser(
            user_id=claims.get("sub"),
            email=claims.get("email"),
            claims=claims
        )
    except HTTPException:
        return None


async def require_seller(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency that requires the user to be a seller.

    Usage:
        @router.post("/products")
        async def create_product(user: CurrentUser = Depends(require_seller)):
            # Only sellers can reach here
    """
    # TODO: Check if user has seller profile in database
    # For now, this just ensures authentication
    # The actual seller check should be done in the endpoint
    return user


async def require_admin(
    user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency that requires the user to be an admin.

    Usage:
        @router.delete("/users/{user_id}")
        async def delete_user(user: CurrentUser = Depends(require_admin)):
            # Only admins can reach here
    """
    # Check if user has admin role in claims
    metadata = user.claims.get("public_metadata", {})
    if metadata.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


# Utility functions for Clerk Backend API
async def get_clerk_user(user_id: str) -> dict:
    """
    Fetch user details from Clerk Backend API.

    Args:
        user_id: The Clerk user ID

    Returns:
        dict: User data from Clerk
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.clerk.com/v1/users/{user_id}",
            headers={
                "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch user from Clerk"
            )

        return response.json()


async def update_clerk_user_metadata(user_id: str, metadata: dict) -> dict:
    """
    Update user's public metadata in Clerk.

    Args:
        user_id: The Clerk user ID
        metadata: The metadata to set

    Returns:
        dict: Updated user data
    """
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"https://api.clerk.com/v1/users/{user_id}",
            headers={
                "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "public_metadata": metadata
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to update user metadata"
            )

        return response.json()
