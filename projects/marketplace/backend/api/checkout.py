"""
Checkout API endpoints for Stripe payment processing.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

import stripe

from database import get_db
from models.user import User
from models.product import Product
from models.order import Order
from config import settings

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


# Endpoints
@router.post("/create-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    checkout_data: CreateCheckoutSessionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe checkout session for a product purchase.

    This creates a Stripe Checkout session and returns the URL for the frontend to redirect to.
    """
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    # Get product
    product_query = select(Product).where(Product.id == checkout_data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.status != "published":
        raise HTTPException(status_code=400, detail="Product is not available for purchase")

    # Can't buy your own product
    if product.seller_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot purchase your own product")

    # Check if already purchased
    existing_query = select(Order).where(
        Order.buyer_id == user_id,
        Order.product_id == product.id,
        Order.status.in_(["completed", "pending"])
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already purchased this product")

    # Calculate price based on license type
    if checkout_data.license_type == "extended":
        price = product.extended_license_price or product.price * 2.5
        license_name = "Extended License"
    else:
        price = product.price
        license_name = "Standard License"

    # Convert to cents (Stripe uses smallest currency unit)
    price_cents = int(price * 100)

    # Create Stripe Checkout Session
    try:
        # Get the base URL from the request
        base_url = f"{request.url.scheme}://{request.url.netloc}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": product.name,
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
            metadata={
                "product_id": product.id,
                "buyer_id": user_id,
                "seller_id": product.seller_id,
                "license_type": checkout_data.license_type,
                "price": str(price),
            },
            mode="payment",
            success_url=f"{base_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/products/{product.slug}",
        )

        return CheckoutSessionResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id
        )

    except stripe.error.StripeError as e:
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
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a successful checkout session and create the order in our database.

    Called by the frontend after successful checkout.
    This endpoint verifies the session with Stripe and creates the order record.
    """
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
        metadata = session.metadata
        product_id = metadata.get("product_id")
        buyer_id = metadata.get("buyer_id")
        seller_id = metadata.get("seller_id")
        license_type = metadata.get("license_type", "standard")
        price = float(metadata.get("price", "0"))

        # Check if order already exists
        existing_query = select(Order).where(Order.payment_intent_id == session.payment_intent)
        existing_result = await db.execute(existing_query)
        existing_order = existing_result.scalar_one_or_none()

        if existing_order:
            return {
                "order_id": existing_order.id,
                "status": existing_order.status,
                "message": "Order already created"
            }

        # Get product details
        product_query = select(Product).where(Product.id == product_id)
        product_result = await db.execute(product_query)
        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Calculate fees
        platform_fee = price * (settings.PLATFORM_FEE_PERCENT / 100)
        seller_amount = price - platform_fee

        # Create the order
        order = Order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            product_id=product_id,
            product_name=product.name,
            amount=price,
            platform_fee=platform_fee,
            seller_amount=seller_amount,
            license_type=license_type,
            status="completed",
            payment_intent_id=session.payment_intent,
            paid_at=datetime.utcnow(),
            download_count=0,
            max_downloads=10,
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "product_name": order.product_name,
            "amount": order.amount,
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
    extended_price = product.extended_license_price or product.price * 2.5

    return {
        "product_id": product.id,
        "product_name": product.name,
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
