"""
Reviews API endpoints.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel, Field

from database import get_db
from dependencies import get_current_db_user
from models.user import User
from models.product import Product
from models.order import Order
from models.review import Review

router = APIRouter()


# Pydantic schemas
class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str
    content: str


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None


class SellerResponseCreate(BaseModel):
    response: str


class ReviewResponse(BaseModel):
    id: str
    product_id: str
    buyer_id: str
    buyer_username: str
    buyer_avatar: Optional[str]
    rating: int
    title: str
    content: str
    is_verified_purchase: bool
    helpful_count: int
    seller_response: Optional[str]
    seller_response_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    average_rating: float
    rating_distribution: dict
    page: int
    page_size: int


# Endpoints
@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a review for a purchased product."""
    user_id = current_user.id

    # Check if product exists
    product_query = select(Product).where(Product.id == review_data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if user purchased the product
    order_query = select(Order).where(
        and_(
            Order.buyer_id == user_id,
            Order.product_id == review_data.product_id,
            Order.status == "completed",
            Order.payment_status == "completed",
        )
    )
    order_result = await db.execute(order_query)
    order = order_result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=403, detail="Purchase required to review")

    # Check if already reviewed
    existing_query = select(Review).where(
        and_(
            Review.buyer_id == user_id,
            Review.product_id == review_data.product_id
        )
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already reviewed this product")

    # Create review
    review = Review(
        product_id=review_data.product_id,
        buyer_id=user_id,
        order_id=order.id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)

    # Update product average rating
    await update_product_rating(review_data.product_id, db)

    # Get buyer info
    buyer_query = select(User).where(User.id == user_id)
    buyer_result = await db.execute(buyer_query)
    buyer = buyer_result.scalar_one_or_none()

    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        buyer_id=review.buyer_id,
        buyer_username=buyer.username if buyer else "Unknown",
        buyer_avatar=buyer.avatar_url if buyer else None,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_verified_purchase=True,
        helpful_count=review.helpful_count,
        seller_response=review.seller_response,
        seller_response_at=review.seller_response_at,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.get("/product/{product_id}", response_model=ReviewListResponse)
async def get_product_reviews(
    product_id: str,
    rating: Optional[int] = Query(None, ge=1, le=5),
    verified_only: bool = False,
    sort: str = Query("newest", pattern="^(newest|oldest|highest|lowest|helpful)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a product."""
    # Check product exists
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build query
    query = select(Review).where(Review.product_id == product_id)

    if rating:
        query = query.where(Review.rating == rating)

    if verified_only:
        query = query.where(Review.order_id.isnot(None))

    # Get total and stats
    all_reviews_query = select(Review).where(Review.product_id == product_id)
    all_reviews_result = await db.execute(all_reviews_query)
    all_reviews = all_reviews_result.scalars().all()

    total = len([
        r for r in all_reviews
        if (not rating or r.rating == rating)
        and (not verified_only or r.order_id is not None)
    ])

    # Calculate rating distribution
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_rating = 0
    for r in all_reviews:
        rating_distribution[r.rating] = rating_distribution.get(r.rating, 0) + 1
        total_rating += r.rating

    average_rating = total_rating / len(all_reviews) if all_reviews else 0

    # Sort
    if sort == "oldest":
        query = query.order_by(Review.created_at.asc())
    elif sort == "highest":
        query = query.order_by(Review.rating.desc())
    elif sort == "lowest":
        query = query.order_by(Review.rating.asc())
    elif sort == "helpful":
        query = query.order_by(Review.helpful_count.desc())
    else:  # newest
        query = query.order_by(Review.created_at.desc())

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reviews = result.scalars().all()

    # Build response
    review_responses = []
    for review in reviews:
        buyer_query = select(User).where(User.id == review.buyer_id)
        buyer_result = await db.execute(buyer_query)
        buyer = buyer_result.scalar_one_or_none()

        review_responses.append(ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            buyer_id=review.buyer_id,
            buyer_username=buyer.username if buyer else "Unknown",
            buyer_avatar=buyer.avatar_url if buyer else None,
            rating=review.rating,
            title=review.title,
            content=review.content,
            is_verified_purchase=review.order_id is not None,
            helpful_count=review.helpful_count,
            seller_response=review.seller_response,
            seller_response_at=review.seller_response_at,
            created_at=review.created_at,
            updated_at=review.updated_at
        ))

    return ReviewListResponse(
        reviews=review_responses,
        total=total,
        average_rating=round(average_rating, 2),
        rating_distribution=rating_distribution,
        page=page,
        page_size=page_size
    )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Update own review."""
    user_id = current_user.id

    query = select(Review).where(Review.id == review_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(review, field, value)

    review.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    # Update product rating if rating changed
    if "rating" in update_dict:
        await update_product_rating(review.product_id, db)

    # Get buyer info
    buyer_query = select(User).where(User.id == review.buyer_id)
    buyer_result = await db.execute(buyer_query)
    buyer = buyer_result.scalar_one_or_none()

    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        buyer_id=review.buyer_id,
        buyer_username=buyer.username if buyer else "Unknown",
        buyer_avatar=buyer.avatar_url if buyer else None,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_verified_purchase=True,
        helpful_count=review.helpful_count,
        seller_response=review.seller_response,
        seller_response_at=review.seller_response_at,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete own review."""
    user_id = current_user.id

    query = select(Review).where(Review.id == review_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    product_id = review.product_id

    await db.delete(review)
    await db.commit()

    # Update product rating
    await update_product_rating(product_id, db)

    return None


@router.post("/{review_id}/helpful")
async def mark_helpful(
    review_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a review as helpful."""
    _ = current_user.id

    query = select(Review).where(Review.id == review_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.helpful_count += 1
    await db.commit()

    return {"helpful_count": review.helpful_count}


@router.post("/{review_id}/respond", response_model=ReviewResponse)
async def seller_respond(
    review_id: str,
    response_data: SellerResponseCreate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Seller responds to a review."""
    user_id = current_user.id

    query = select(Review).where(Review.id == review_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Check if user is the product seller
    product_query = select(Product).where(Product.id == review.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product or product.seller_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    review.seller_response = response_data.response
    review.seller_response_at = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    # Get buyer info
    buyer_query = select(User).where(User.id == review.buyer_id)
    buyer_result = await db.execute(buyer_query)
    buyer = buyer_result.scalar_one_or_none()

    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        buyer_id=review.buyer_id,
        buyer_username=buyer.username if buyer else "Unknown",
        buyer_avatar=buyer.avatar_url if buyer else None,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_verified_purchase=True,
        helpful_count=review.helpful_count,
        seller_response=review.seller_response,
        seller_response_at=review.seller_response_at,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


async def update_product_rating(product_id: str, db: AsyncSession):
    """Recalculate and update product's average rating."""
    # Get all reviews for product
    query = select(Review).where(Review.product_id == product_id)
    result = await db.execute(query)
    reviews = result.scalars().all()

    if not reviews:
        return

    # Calculate average
    total = sum(r.rating for r in reviews)
    average = total / len(reviews)

    # Update product
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if product:
        product.rating_average = round(average, 2)
        product.rating_count = len(reviews)
        await db.commit()
