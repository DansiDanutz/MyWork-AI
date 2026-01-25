"""
API routers for MyWork Marketplace.
"""

from fastapi import APIRouter

from api.products import router as products_router
from api.users import router as users_router
from api.orders import router as orders_router
from api.reviews import router as reviews_router
from api.brain import router as brain_router
from api.webhooks import router as webhooks_router
from api.submissions import router as submissions_router

# Create main API router
api_router = APIRouter()

# Include all routers with prefixes
api_router.include_router(products_router, prefix="/products", tags=["Products"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(brain_router, prefix="/brain", tags=["Brain"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(submissions_router, prefix="/submissions", tags=["Submissions"])

__all__ = [
    "api_router",
    "products_router",
    "users_router",
    "orders_router",
    "reviews_router",
    "brain_router",
    "webhooks_router",
    "submissions_router",
]
