"""
Webhook handlers for external services.
"""

import json
import stripe
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.order import Order
from models.user import User, SellerProfile
from models.subscription import Subscription
from models.payout import Payout
from config import settings

router = APIRouter()


# Stripe webhook handler
@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    payload = await request.body()

    # Verify webhook signature in production to prevent spoofing
    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        if settings.ENVIRONMENT != "development":
            raise HTTPException(
                status_code=500,
                detail="Stripe webhook secret not configured"
            )
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    # Handle different event types
    if event_type == "payment_intent.succeeded":
        await handle_payment_success(data, db)

    elif event_type == "payment_intent.payment_failed":
        await handle_payment_failed(data, db)

    elif event_type == "customer.subscription.created":
        await handle_subscription_created(data, db)

    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data, db)

    elif event_type == "customer.subscription.deleted":
        await handle_subscription_cancelled(data, db)

    elif event_type == "invoice.payment_succeeded":
        await handle_invoice_paid(data, db)

    elif event_type == "invoice.payment_failed":
        await handle_invoice_failed(data, db)

    elif event_type == "account.updated":
        await handle_connect_account_updated(data, db)

    elif event_type == "transfer.created":
        await handle_transfer_created(data, db)

    elif event_type == "payout.paid":
        await handle_payout_completed(data, db)

    elif event_type == "payout.failed":
        await handle_payout_failed(data, db)

    return {"status": "ok"}


async def handle_payment_success(data: dict, db: AsyncSession):
    """Handle successful payment for an order."""
    payment_intent_id = data.get("id")
    metadata = data.get("metadata", {})
    order_id = metadata.get("order_id")

    if not order_id:
        return  # Not our order

    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        return

    # Update order status
    order.status = "completed"
    order.payment_intent_id = payment_intent_id
    order.paid_at = datetime.utcnow()

    # Set escrow release date
    order.escrow_release_date = datetime.utcnow() + timedelta(days=settings.ESCROW_DAYS)

    await db.commit()

    # TODO: Send purchase confirmation email to buyer
    # TODO: Send sale notification to seller
    # TODO: Update product sales count


async def handle_payment_failed(data: dict, db: AsyncSession):
    """Handle failed payment."""
    metadata = data.get("metadata", {})
    order_id = metadata.get("order_id")

    if not order_id:
        return

    query = select(Order).where(Order.id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        return

    order.status = "failed"
    await db.commit()

    # TODO: Send payment failed email to buyer


async def handle_subscription_created(data: dict, db: AsyncSession):
    """Handle new subscription created."""
    stripe_subscription_id = data.get("id")
    stripe_customer_id = data.get("customer")
    status = data.get("status")
    metadata = data.get("metadata", {})
    user_id = metadata.get("user_id")

    if not user_id:
        return

    # Get plan details from items
    items = data.get("items", {}).get("data", [])
    if not items:
        return

    price_id = items[0].get("price", {}).get("id")

    # Determine tier from price
    tier = "pro"  # Default
    # TODO: Map price_id to tier using settings

    # Get or create subscription
    query = select(Subscription).where(Subscription.user_id == user_id)
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.tier = tier
        subscription.stripe_subscription_id = stripe_subscription_id
        subscription.stripe_price_id = price_id
        subscription.status = status
    else:
        subscription = Subscription(
            user_id=user_id,
            tier=tier,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
            stripe_price_id=price_id,
            status=status
        )
        db.add(subscription)

    # Update user's subscription tier
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if user:
        user.subscription_tier = tier
        user.stripe_customer_id = stripe_customer_id

    await db.commit()

    # TODO: Send welcome email


async def handle_subscription_updated(data: dict, db: AsyncSession):
    """Handle subscription updates (upgrade/downgrade)."""
    stripe_subscription_id = data.get("id")
    status = data.get("status")

    query = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return

    # Update status
    subscription.status = status

    # Check for plan changes
    items = data.get("items", {}).get("data", [])
    if items:
        new_price_id = items[0].get("price", {}).get("id")
        if new_price_id != subscription.stripe_price_id:
            subscription.stripe_price_id = new_price_id
            # TODO: Determine new tier and update

    await db.commit()


async def handle_subscription_cancelled(data: dict, db: AsyncSession):
    """Handle subscription cancellation."""
    stripe_subscription_id = data.get("id")

    query = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return

    subscription.status = "cancelled"
    subscription.cancelled_at = datetime.utcnow()

    # Downgrade user to free
    user_query = select(User).where(User.id == subscription.user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if user:
        user.subscription_tier = "free"

    await db.commit()

    # TODO: Send cancellation email
    # TODO: Disable selling if seller


async def handle_invoice_paid(data: dict, db: AsyncSession):
    """Handle successful invoice payment (subscription renewal)."""
    stripe_subscription_id = data.get("subscription")
    stripe_customer_id = data.get("customer")
    amount_paid = data.get("amount_paid", 0) / 100  # Convert from cents

    if not stripe_subscription_id:
        return

    query = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return

    # Update billing period
    period_end = data.get("lines", {}).get("data", [{}])[0].get("period", {}).get("end")
    if period_end:
        subscription.current_period_end = datetime.fromtimestamp(period_end)

    subscription.status = "active"
    await db.commit()


async def handle_invoice_failed(data: dict, db: AsyncSession):
    """Handle failed invoice payment."""
    stripe_subscription_id = data.get("subscription")

    if not stripe_subscription_id:
        return

    query = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return

    subscription.status = "past_due"
    await db.commit()

    # TODO: Send payment failed email with retry link


async def handle_connect_account_updated(data: dict, db: AsyncSession):
    """Handle Stripe Connect account updates (for sellers)."""
    account_id = data.get("id")
    charges_enabled = data.get("charges_enabled", False)
    payouts_enabled = data.get("payouts_enabled", False)
    details_submitted = data.get("details_submitted", False)

    query = select(SellerProfile).where(
        SellerProfile.stripe_account_id == account_id
    )
    result = await db.execute(query)
    seller = result.scalar_one_or_none()

    if not seller:
        return

    # Update seller verification status
    if charges_enabled and payouts_enabled and details_submitted:
        seller.payouts_enabled = True
        seller.verification_level = "verified"
    else:
        seller.payouts_enabled = False

    await db.commit()

    # TODO: Notify seller of verification status change


async def handle_transfer_created(data: dict, db: AsyncSession):
    """Handle transfer to seller (payout initiated)."""
    transfer_id = data.get("id")
    destination = data.get("destination")  # Connect account ID
    amount = data.get("amount", 0) / 100  # Convert from cents
    metadata = data.get("metadata", {})
    order_id = metadata.get("order_id")

    if not order_id:
        return

    # Create payout record
    payout = Payout(
        seller_id=metadata.get("seller_id"),
        amount=amount,
        status="pending",
        stripe_transfer_id=transfer_id,
        order_ids=[order_id]
    )

    db.add(payout)
    await db.commit()


async def handle_payout_completed(data: dict, db: AsyncSession):
    """Handle completed payout to seller's bank."""
    # This is when funds actually reach seller's bank
    # Note: This comes from the Connect account, not our platform
    pass


async def handle_payout_failed(data: dict, db: AsyncSession):
    """Handle failed payout."""
    # Mark payout as failed and notify seller
    pass


# Clerk webhook handler
@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Clerk webhook events (user management)."""
    # TODO: Verify webhook signature

    payload = await request.json()
    event_type = payload.get("type")
    data = payload.get("data", {})

    if event_type == "user.created":
        await handle_user_created(data, db)

    elif event_type == "user.updated":
        await handle_user_updated(data, db)

    elif event_type == "user.deleted":
        await handle_user_deleted(data, db)

    return {"status": "ok"}


async def handle_user_created(data: dict, db: AsyncSession):
    """Handle new user creation from Clerk."""
    clerk_id = data.get("id")
    email = data.get("email_addresses", [{}])[0].get("email_address")
    username = data.get("username")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    image_url = data.get("image_url")

    # Generate username if not provided
    if not username:
        username = email.split("@")[0] if email else f"user_{clerk_id[:8]}"

    # Create user in our database
    user = User(
        id=clerk_id,  # Use Clerk ID as our user ID
        email=email,
        username=username,
        display_name=f"{first_name} {last_name}".strip() or username,
        avatar_url=image_url
    )

    db.add(user)

    # Create free subscription
    subscription = Subscription(
        user_id=clerk_id,
        tier="free",
        status="active"
    )
    db.add(subscription)

    await db.commit()


async def handle_user_updated(data: dict, db: AsyncSession):
    """Handle user profile updates from Clerk."""
    clerk_id = data.get("id")
    email = data.get("email_addresses", [{}])[0].get("email_address")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    image_url = data.get("image_url")

    query = select(User).where(User.id == clerk_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return

    user.email = email
    user.display_name = f"{first_name} {last_name}".strip() or user.username
    user.avatar_url = image_url

    await db.commit()


async def handle_user_deleted(data: dict, db: AsyncSession):
    """Handle user deletion from Clerk."""
    clerk_id = data.get("id")

    # Soft delete - just mark as inactive
    query = select(User).where(User.id == clerk_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return

    user.is_active = False
    await db.commit()

    # TODO: Handle seller products (unpublish)
    # TODO: Cancel active subscriptions
