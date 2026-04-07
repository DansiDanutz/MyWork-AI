from fastapi import APIRouter, Request, Header, HTTPException
from pydantic import BaseModel
from services.billing_service import get_plans, create_checkout_session, create_customer_portal_session, handle_webhook, STRIPE_ENABLED
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    email: str
    plan: str
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    customer_id: str
    return_url: str


@router.get("/plans")
async def list_plans():
    return {"plans": get_plans(), "stripe_enabled": STRIPE_ENABLED}


@router.post("/checkout")
async def checkout(req: CheckoutRequest):
    if not STRIPE_ENABLED:
        raise HTTPException(status_code=503, detail="Billing not configured. Set STRIPE_SECRET_KEY.")
    try:
        return create_checkout_session(req.email, req.plan, req.success_url, req.cancel_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/portal")
async def customer_portal(req: PortalRequest):
    if not STRIPE_ENABLED:
        raise HTTPException(status_code=503, detail="Billing not configured.")
    try:
        return create_customer_portal_session(req.customer_id, req.return_url)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    sig = request.headers.get("stripe-signature", "")
    body = await request.body()
    try:
        result = handle_webhook(body, sig)
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
