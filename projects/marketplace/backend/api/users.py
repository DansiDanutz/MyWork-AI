"""
Users API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from database import get_db
from models.user import User, SellerProfile

router = APIRouter()


# Pydantic schemas
class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    subscription_tier: str
    is_seller: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class SellerProfileResponse(BaseModel):
    id: str
    user_id: str
    bio: Optional[str]
    website: Optional[str]
    github_username: Optional[str]
    twitter_handle: Optional[str]
    total_sales: int
    total_revenue: float
    average_rating: float
    verification_level: str
    payouts_enabled: bool

    class Config:
        from_attributes = True


class BecomeSellerRequest(BaseModel):
    bio: Optional[str] = None
    website: Optional[str] = None
    github_username: Optional[str] = None
    twitter_handle: Optional[str] = None


# Endpoints
@router.get("/me", response_model=UserProfile)
async def get_current_user(
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Get current user profile."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        subscription_tier=user.subscription_tier,
        is_seller=user.is_seller
    )


@router.put("/me", response_model=UserProfile)
async def update_current_user(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Update current user profile."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserProfile.model_validate(user)


@router.get("/me/seller", response_model=SellerProfileResponse)
async def get_seller_profile(
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Get current user's seller profile."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(SellerProfile).where(SellerProfile.user_id == user_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")

    return SellerProfileResponse.model_validate(profile)


@router.post("/become-seller", response_model=SellerProfileResponse, status_code=201)
async def become_seller(
    request: BecomeSellerRequest,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Upgrade to seller account."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a seller
    if user.is_seller:
        raise HTTPException(status_code=400, detail="Already a seller")

    # Check subscription (must be Pro or higher)
    if user.subscription_tier == "free":
        raise HTTPException(
            status_code=403,
            detail="Pro subscription required to become a seller"
        )

    # Create seller profile
    seller_profile = SellerProfile(
        user_id=user.id,
        bio=request.bio,
        website=request.website,
        github_username=request.github_username,
        twitter_handle=request.twitter_handle
    )

    # Update user role
    user.role = "seller"

    db.add(seller_profile)
    await db.commit()
    await db.refresh(seller_profile)

    return SellerProfileResponse.model_validate(seller_profile)


@router.get("/{username}", response_model=UserProfile)
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public user profile by username."""
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        id=user.id,
        email="",  # Don't expose email
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        subscription_tier="",  # Don't expose tier
        is_seller=user.is_seller
    )


@router.get("/{username}/seller", response_model=SellerProfileResponse)
async def get_public_seller_profile(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public seller profile by username."""
    # Get user first
    user_query = select(User).where(User.username == username)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get seller profile
    query = select(SellerProfile).where(SellerProfile.user_id == user.id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")

    return SellerProfileResponse.model_validate(profile)
