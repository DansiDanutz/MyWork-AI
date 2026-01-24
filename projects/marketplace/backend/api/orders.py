"""
Orders API endpoints.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from database import get_db
from models.user import User
from models.product import Product
from models.order import Order
from config import settings

router = APIRouter()


# Pydantic schemas
class OrderCreate(BaseModel):
    product_id: str
    license_type: str = "standard"  # standard, extended, unlimited


class OrderResponse(BaseModel):
    id: str
    buyer_id: str
    seller_id: str
    product_id: str
    product_name: str
    amount: float
    platform_fee: float
    seller_amount: float
    license_type: str
    status: str
    payment_intent_id: Optional[str]
    download_count: int
    max_downloads: int
    escrow_release_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int


class RefundRequest(BaseModel):
    reason: str


# Endpoints
@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Create a new order (initiate purchase)."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    # Get product
    product_query = select(Product).where(Product.id == order_data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.status != "published":
        raise HTTPException(status_code=400, detail="Product is not available")

    # Can't buy your own product
    if product.seller_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot purchase your own product")

    # Check if already purchased
    existing_query = select(Order).where(
        and_(
            Order.buyer_id == user_id,
            Order.product_id == product.id,
            Order.status.in_(["completed", "pending"])
        )
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already purchased this product")

    # Get price based on license type
    if order_data.license_type == "extended":
        amount = product.extended_license_price or product.price * 2.5
    elif order_data.license_type == "unlimited":
        amount = product.unlimited_license_price or product.price * 5
    else:
        amount = product.price

    # Calculate fees
    platform_fee = amount * (settings.PLATFORM_FEE_PERCENT / 100)
    seller_amount = amount - platform_fee

    # Create order
    order = Order(
        buyer_id=user_id,
        seller_id=product.seller_id,
        product_id=product.id,
        amount=amount,
        platform_fee=platform_fee,
        seller_amount=seller_amount,
        license_type=order_data.license_type,
        status="pending",
        escrow_release_date=datetime.utcnow() + timedelta(days=settings.ESCROW_DAYS),
        max_downloads=5 if order_data.license_type == "standard" else 10
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)

    # TODO: Create Stripe payment intent
    # TODO: Return client_secret for frontend

    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        product_id=order.product_id,
        product_name=product.name,
        amount=order.amount,
        platform_fee=order.platform_fee,
        seller_amount=order.seller_amount,
        license_type=order.license_type,
        status=order.status,
        payment_intent_id=order.payment_intent_id,
        download_count=order.download_count,
        max_downloads=order.max_downloads,
        escrow_release_date=order.escrow_release_date,
        created_at=order.created_at
    )


@router.get("", response_model=OrderListResponse)
async def list_my_orders(
    role: str = Query("buyer", pattern="^(buyer|seller)$"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """List orders (as buyer or seller)."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    # Build query
    if role == "buyer":
        query = select(Order).where(Order.buyer_id == user_id)
    else:
        query = select(Order).where(Order.seller_id == user_id)

    if status:
        query = query.where(Order.status == status)

    # Count total
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Paginate
    query = query.order_by(Order.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    # Get product names
    order_responses = []
    for order in orders:
        product_query = select(Product).where(Product.id == order.product_id)
        product_result = await db.execute(product_query)
        product = product_result.scalar_one_or_none()

        # Calculate max_downloads based on license type
        if order.license_type == "extended":
            max_downloads = 10
        elif order.license_type == "unlimited":
            max_downloads = 999
        else:
            max_downloads = 5

        order_responses.append(OrderResponse(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            product_id=order.product_id,
            product_name=product.title if product else "Unknown",
            amount=float(order.amount),
            platform_fee=float(order.platform_fee),
            seller_amount=float(order.seller_amount),
            license_type=order.license_type,
            status=order.status,
            payment_intent_id=order.stripe_payment_intent_id,
            download_count=order.download_count,
            max_downloads=max_downloads,
            escrow_release_date=order.escrow_release_at,
            created_at=order.created_at
        ))

    return OrderListResponse(
        orders=order_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Get order details."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Must be buyer or seller
    if order.buyer_id != user_id and order.seller_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get product name
    product_query = select(Product).where(Product.id == order.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    # Calculate max_downloads based on license type
    if order.license_type == "extended":
        max_downloads = 10
    elif order.license_type == "unlimited":
        max_downloads = 999
    else:
        max_downloads = 5

    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        product_id=order.product_id,
        product_name=product.title if product else "Unknown",
        amount=float(order.amount),
        platform_fee=float(order.platform_fee),
        seller_amount=float(order.seller_amount),
        license_type=order.license_type,
        status=order.status,
        payment_intent_id=order.stripe_payment_intent_id,
        download_count=order.download_count,
        max_downloads=max_downloads,
        escrow_release_date=order.escrow_release_at,
        created_at=order.created_at
    )


@router.post("/{order_id}/download")
async def download_product(
    order_id: str,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Get download URL for purchased product."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status != "completed":
        raise HTTPException(status_code=400, detail="Order not completed")

    if order.download_count >= order.max_downloads:
        raise HTTPException(status_code=400, detail="Download limit reached")

    # Increment download count
    order.download_count += 1
    await db.commit()

    # Get product
    product_query = select(Product).where(Product.id == order.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    # TODO: Generate signed download URL from R2
    download_url = f"https://files.mywork.dev/{product.file_url}"

    return {
        "download_url": download_url,
        "downloads_remaining": order.max_downloads - order.download_count
    }


@router.post("/{order_id}/refund", response_model=OrderResponse)
async def request_refund(
    order_id: str,
    refund_data: RefundRequest,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Request a refund for an order."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status != "completed":
        raise HTTPException(status_code=400, detail="Can only refund completed orders")

    # Check if within refund window (7 days)
    if datetime.utcnow() > order.created_at + timedelta(days=7):
        raise HTTPException(status_code=400, detail="Refund window expired")

    # Can't refund if already downloaded multiple times
    if order.download_count > 2:
        raise HTTPException(
            status_code=400,
            detail="Cannot refund after multiple downloads"
        )

    # Update order status
    order.status = "refund_requested"
    order.refund_reason = refund_data.reason
    order.refund_requested_at = datetime.utcnow()

    await db.commit()
    await db.refresh(order)

    # Get product name
    product_query = select(Product).where(Product.id == order.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    # Calculate max_downloads based on license type
    if order.license_type == "extended":
        max_downloads = 10
    elif order.license_type == "unlimited":
        max_downloads = 999
    else:
        max_downloads = 5

    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        product_id=order.product_id,
        product_name=product.title if product else "Unknown",
        amount=float(order.amount),
        platform_fee=float(order.platform_fee),
        seller_amount=float(order.seller_amount),
        license_type=order.license_type,
        status=order.status,
        payment_intent_id=order.stripe_payment_intent_id,
        download_count=order.download_count,
        max_downloads=max_downloads,
        escrow_release_date=order.escrow_release_at,
        created_at=order.created_at
    )
