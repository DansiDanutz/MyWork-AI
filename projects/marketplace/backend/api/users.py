"""
Users API endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from database import get_db
from dependencies import get_current_db_user
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
    current_user: User = Depends(get_current_db_user),
):
    """Get current user profile."""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        subscription_tier=current_user.subscription_tier,
        is_seller=current_user.is_seller
    )


@router.put("/me", response_model=UserProfile)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return UserProfile.model_validate(current_user)


@router.get("/me/seller", response_model=SellerProfileResponse)
async def get_seller_profile(
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's seller profile."""
    query = select(SellerProfile).where(SellerProfile.user_id == current_user.id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")

    return SellerProfileResponse.model_validate(profile)


@router.post("/become-seller", response_model=SellerProfileResponse, status_code=201)
async def become_seller(
    request: BecomeSellerRequest,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade to seller account."""
    # Check if already a seller
    if current_user.is_seller:
        raise HTTPException(status_code=400, detail="Already a seller")

    # Check subscription (must be Pro or higher)
    if current_user.subscription_tier == "free":
        raise HTTPException(
            status_code=403,
            detail="Pro subscription required to become a seller"
        )

    # Create seller profile
    seller_profile = SellerProfile(
        user_id=current_user.id,
        bio=request.bio,
        website=request.website,
        github_username=request.github_username,
        twitter_handle=request.twitter_handle
    )

    # Update user role
    current_user.role = "seller"

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
