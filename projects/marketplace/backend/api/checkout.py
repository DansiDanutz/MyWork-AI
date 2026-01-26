"""
Checkout API endpoints for Stripe payment processing.
"""

from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

import stripe

from database import get_db
from dependencies import get_current_db_user
from models.user import User
from models.product import Product
from models.order import Order
from config import settings
from services.delivery import ensure_delivery_artifact

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY or "sk_test_placeholder"


# Pydantic schemas
class CreateCheckoutSessionRequest(BaseModel):
    product_id: str
    license_type: str = "standard"  # standard, extended


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


def _require_stripe_secret() -> None:
    if not settings.STRIPE_SECRET_KEY and settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=500, detail="Stripe secret key not configured")


def _normalize_license_type(license_type: str) -> str:
    if license_type == "unlimited":
        return "enterprise"
    return license_type


# Endpoints
@router.post("/create-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    checkout_data: CreateCheckoutSessionRequest,
    request: Request,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe checkout session for a product purchase.

    This creates a Stripe Checkout session and returns the URL for the frontend to redirect to.
    """
    _require_stripe_secret()
    user_id = current_user.id

    # Get product
    product_query = select(Product).where(Product.id == checkout_data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.status != "active":
        raise HTTPException(status_code=400, detail="Product is not available for purchase")

    # Can't buy your own product
    if product.seller_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot purchase your own product")

    # Check if already purchased or in progress
    existing_query = select(Order).where(
        Order.buyer_id == user_id,
        Order.product_id == product.id,
        Order.status.in_(["completed", "pending"]),
    )
    existing_result = await db.execute(existing_query)
    existing_order = existing_result.scalar_one_or_none()
    if existing_order:
        if existing_order.status == "completed":
            raise HTTPException(status_code=400, detail="You have already purchased this product")
        cutoff = datetime.utcnow() - timedelta(hours=24)
        if existing_order.created_at and existing_order.created_at < cutoff:
            existing_order.status = "failed"
            existing_order.payment_status = "failed"
            await db.commit()
        else:
            raise HTTPException(status_code=400, detail="Checkout already in progress")

    # Calculate price based on license type
    if checkout_data.license_type == "extended":
        price = Decimal(str(product.price)) * Decimal("2.5")
    elif checkout_data.license_type in ("enterprise", "unlimited"):
        price = Decimal(str(product.price)) * Decimal("5")
    else:
        price = Decimal(str(product.price))

    # Convert to cents (Stripe uses smallest currency unit)
    price_cents = int(price * Decimal('100'))

    # Create pending order first so we can reference it in Stripe metadata.
    platform_fee = price * (Decimal(str(settings.PLATFORM_FEE_PERCENT)) / Decimal("100"))
    seller_amount = price - platform_fee
    normalized_license = _normalize_license_type(checkout_data.license_type)
    order = Order(
        buyer_id=user_id,
        seller_id=product.seller_id,
        product_id=product.id,
        amount=price,
        platform_fee=platform_fee,
        stripe_fee=Decimal("0"),
        seller_amount=seller_amount,
        license_type=normalized_license,
        status="pending",
        payment_status="pending",
        download_count=0,
    )
    db.add(order)
    await db.flush()

    metadata = {
        "order_id": order.id,
        "product_id": product.id,
        "buyer_id": user_id,
        "seller_id": product.seller_id,
        "license_type": checkout_data.license_type,
        "price": str(price),
    }

    # Create Stripe Checkout Session
    try:
        # Prefer configured frontend URL if available.
        base_url = settings.APP_URL.rstrip("/") if settings.APP_URL else f"{request.url.scheme}://{request.url.netloc}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": product.title,
                            "description": product.description[:500] if product.description else "",
                            "metadata": {
                                "product_id": product.id,
                                "seller_id": product.seller_id,
                            }
                        },
                        "unit_amount": price_cents,
                    },
                    "quantity": 1,
                }
            ],
            metadata=metadata,
            payment_intent_data={
                "metadata": metadata,
            },
            mode="payment",
            success_url=f"{base_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/products/{product.slug}",
            client_reference_id=order.id,
            idempotency_key=f"checkout_session_{order.id}",
        )

        await db.commit()
        return CheckoutSessionResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )

    except stripe.error.StripeError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


@router.get("/session/{session_id}")
async def get_checkout_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details of a checkout session.

    Useful for checking the status of a session before/after payment.
    """
    _require_stripe_secret()
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        return {
            "id": session.id,
            "status": session.status,
            "payment_status": session.payment_status,
            "metadata": session.metadata,
            "amount_total": session.amount_total,  # In cents
            "currency": session.currency,
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


@router.post("/verify-and-create-order")
async def verify_and_create_order(
    session_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a successful checkout session and create the order in our database.

    Called by the frontend after successful checkout.
    This endpoint verifies the session with Stripe and creates the order record.
    """
    _require_stripe_secret()
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        # Verify payment was successful
        if session.payment_status != "paid":
            raise HTTPException(
                status_code=400,
                detail="Payment not completed"
            )

        # Extract metadata
        metadata = session.metadata or {}
        product_id = metadata.get("product_id")
        buyer_id = metadata.get("buyer_id")
        seller_id = metadata.get("seller_id")
        license_type = metadata.get("license_type", "standard")
        order_id = metadata.get("order_id") or session.get("client_reference_id")
        license_type = _normalize_license_type(license_type)
        amount_total = session.get("amount_total")
        price = Decimal(str(amount_total / 100)) if amount_total else Decimal(str(metadata.get("price", "0")))

        if buyer_id and buyer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        order = None
        if order_id:
            order_result = await db.execute(select(Order).where(Order.id == order_id))
            order = order_result.scalar_one_or_none()
        if not order and session.payment_intent:
            existing_query = select(Order).where(
                Order.stripe_payment_intent_id == session.payment_intent
            )
            existing_result = await db.execute(existing_query)
            order = existing_result.scalar_one_or_none()

        if order:
            if order.status == "completed" and order.payment_status == "completed":
                return {
                    "order_id": order.id,
                    "status": order.status,
                    "message": "Order already completed"
                }
            if order.buyer_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
            order.status = "completed"
            order.payment_status = "completed"
            order.stripe_payment_intent_id = session.payment_intent
            order.amount = price
            order.currency = (session.currency or order.currency or "USD").upper()
            platform_fee = price * (Decimal(str(settings.PLATFORM_FEE_PERCENT)) / Decimal("100"))
            order.platform_fee = platform_fee
            order.seller_amount = price - platform_fee
            order.license_type = license_type
            order.escrow_release_at = datetime.utcnow() + timedelta(days=settings.ESCROW_DAYS)
            await ensure_delivery_artifact(db, order)
            await db.commit()
            product_title = "Unknown"
            if order.product_id:
                product_result = await db.execute(
                    select(Product).where(Product.id == order.product_id)
                )
                product = product_result.scalar_one_or_none()
                if product:
                    product_title = product.title
            return {
                "order_id": order.id,
                "status": order.status,
                "product_name": product_title,
                "amount": float(order.amount),
                "license_type": order.license_type,
                "download_url": f"/api/orders/{order.id}/download",
            }

        # Get product details
        product_query = select(Product).where(Product.id == product_id)
        product_result = await db.execute(product_query)
        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Calculate fees
        platform_fee = price * (Decimal(str(settings.PLATFORM_FEE_PERCENT)) / Decimal("100"))
        seller_amount = price - platform_fee

        # Create the order
        order = Order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            product_id=product_id,
            amount=price,
            platform_fee=platform_fee,
            stripe_fee=Decimal("0"),
            seller_amount=seller_amount,
            license_type=license_type,
            status="completed",
            payment_status="completed",
            stripe_payment_intent_id=session.payment_intent,
            download_count=0,
            escrow_release_at=datetime.utcnow() + timedelta(days=settings.ESCROW_DAYS),
        )

        db.add(order)
        await ensure_delivery_artifact(db, order)
        await db.commit()
        await db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "product_name": product.title,
            "amount": float(order.amount),
            "license_type": order.license_type,
            "download_url": f"/api/orders/{order.id}/download",
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


@router.get("/prices/{product_id}")
async def get_product_prices(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get available pricing options for a product (standard vs extended license).

    Useful for displaying prices on the checkout page.
    """
    product_query = select(Product).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    standard_price = product.price
    extended_price = product.price * Decimal('2.5')

    return {
        "product_id": product.id,
        "product_name": product.title,
        "standard_license": {
            "price": standard_price,
            "description": "Standard License - Single project use"
        },
        "extended_license": {
            "price": extended_price,
            "description": "Extended License - Unlimited projects, resell rights"
        },
        "currency": "USD"
    }
