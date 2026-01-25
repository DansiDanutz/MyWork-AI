"""
User provisioning helpers for Clerk-authenticated requests.
"""

from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser, get_clerk_user
from models.user import User

USERNAME_MAX_LENGTH = 50


def _normalize_username(raw: Optional[str], fallback: str) -> str:
    base = (raw or "").strip().lower()
    if not base:
        base = fallback
    base = re.sub(r"[^a-z0-9_]+", "", base)
    base = base.strip("_")
    if not base:
        base = f"user_{fallback[:8]}"
    return base[:USERNAME_MAX_LENGTH]


def _extract_primary_email(data: dict) -> Optional[str]:
    primary_id = data.get("primary_email_address_id")
    emails = data.get("email_addresses") or []
    if primary_id:
        for item in emails:
            if item.get("id") == primary_id and item.get("email_address"):
                return item.get("email_address")
    for item in emails:
        if item.get("email_address"):
            return item.get("email_address")
    return None


def _build_display_name(data: dict, username: str, email: Optional[str]) -> str:
    first = (data.get("first_name") or "").strip()
    last = (data.get("last_name") or "").strip()
    name = f"{first} {last}".strip()
    if name:
        return name
    if data.get("username"):
        return data.get("username")
    if email:
        return email.split("@")[0]
    return username


async def _ensure_unique_username(base: str, db: AsyncSession) -> str:
    candidate = base[:USERNAME_MAX_LENGTH]
    suffix = 1
    while True:
        existing = await db.scalar(select(User.id).where(User.username == candidate))
        if not existing:
            return candidate
        suffix += 1
        suffix_str = f"-{suffix}"
        trimmed = base[: USERNAME_MAX_LENGTH - len(suffix_str)]
        candidate = f"{trimmed}{suffix_str}"


async def build_user_from_clerk(clerk_id: str, clerk_data: dict, db: AsyncSession) -> User:
    """Build a new User model instance from Clerk API payload."""
    email = _extract_primary_email(clerk_data)
    if not email:
        raise ValueError("Clerk user email not available")

    raw_username = clerk_data.get("username") or email.split("@")[0]
    base_username = _normalize_username(raw_username, clerk_id)
    username = await _ensure_unique_username(base_username, db)
    display_name = _build_display_name(clerk_data, username, email)
    avatar_url = clerk_data.get("image_url")

    return User(
        clerk_id=clerk_id,
        email=email,
        username=username,
        display_name=display_name,
        avatar_url=avatar_url,
    )


def normalize_username(raw: Optional[str], fallback: str) -> str:
    return _normalize_username(raw, fallback)


def extract_primary_email(data: dict) -> Optional[str]:
    return _extract_primary_email(data)


def build_display_name(data: dict, username: str, email: Optional[str]) -> str:
    return _build_display_name(data, username, email)


async def ensure_unique_username(base: str, db: AsyncSession) -> str:
    return await _ensure_unique_username(base, db)


async def ensure_user(current_user: CurrentUser, db: AsyncSession) -> User:
    """Fetch or create the database user for the authenticated Clerk user."""
    result = await db.execute(
        select(User).where(User.clerk_id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        return user

    try:
        clerk_data = await get_clerk_user(current_user.user_id)
        user = await build_user_from_clerk(current_user.user_id, clerk_data, db)
    except Exception:
        if not current_user.email:
            raise ValueError("Clerk user email not available")
        base_username = _normalize_username(current_user.email.split("@")[0], current_user.user_id)
        username = await _ensure_unique_username(base_username, db)
        display_name = current_user.email.split("@")[0]
        user = User(
            clerk_id=current_user.user_id,
            email=current_user.email,
            username=username,
            display_name=display_name,
            avatar_url=None,
        )
    db.add(user)
    await db.flush()
    return user
