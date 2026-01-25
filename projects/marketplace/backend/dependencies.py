"""
Shared FastAPI dependencies.
"""

from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser, get_current_user, get_optional_user
from database import get_db
from models.user import User
from services.users import ensure_user


async def get_current_db_user(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Return the database user for the authenticated Clerk user."""
    try:
        user = await ensure_user(current_user, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    return user


async def get_optional_db_user(
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Return the database user if authenticated, otherwise None."""
    if not current_user:
        return None
    try:
        user = await ensure_user(current_user, db)
    except ValueError:
        return None
    if not user.is_active:
        return None
    return user
