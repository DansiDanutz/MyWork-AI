import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from security import require_admin, require_billing_identity, require_stripe_customer_id
from services.billing_service import (
    STRIPE_ENABLED,
    create_checkout_session,
    create_customer_portal_session,
    get_plans,
    handle_webhook,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan: str


@router.get("/plans")
async def list_plans():
    return {"plans": get_plans(), "stripe_enabled": STRIPE_ENABLED}


@router.post("/checkout")
async def checkout(req: CheckoutRequest, _admin: None = Depends(require_admin)):
    if not STRIPE_ENABLED:
        raise HTTPException(status_code=503, detail="Billing not configured. Set STRIPE_SECRET_KEY.")
    email, frontend_origin = require_billing_identity()
    customer_id = require_stripe_customer_id()
    try:
        return create_checkout_session(
            email,
            customer_id,
            req.plan,
            f"{frontend_origin}/pricing?success=true",
            f"{frontend_origin}/pricing?canceled=true",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("/portal")
async def customer_portal(_admin: None = Depends(require_admin)):
    if not STRIPE_ENABLED:
        raise HTTPException(status_code=503, detail="Billing not configured.")
    email, frontend_origin = require_billing_identity()
    customer_id = require_stripe_customer_id()
    try:
        return create_customer_portal_session(customer_id, email, frontend_origin)
    except RuntimeError as e:
        logger.warning("Billing portal identity resolution failed: %s", e)
        raise HTTPException(status_code=503, detail="Billing portal unavailable.") from e


@router.post("/webhook")
async def stripe_webhook(request: Request):
    sig = request.headers.get("stripe-signature", "")
    body = await request.body()
    try:
        result = handle_webhook(body, sig)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signature") from None
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
