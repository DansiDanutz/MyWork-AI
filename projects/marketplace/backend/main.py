"""
MyWork Marketplace - Backend API
================================
FastAPI application for the marketplace platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from uuid import uuid4
import time
import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from config import settings
from database import init_db

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Sentry (optional)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
            SqlalchemyIntegration(),
        ],
        send_default_pii=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info("marketplace_starting", version=settings.APP_VERSION)

    # Initialize database
    if settings.ENVIRONMENT == "development":
        logger.info("initializing_database")
        await init_db()
        logger.info("database_initialized")

    yield

    # Shutdown
    logger.info("marketplace_stopping")


# Initialize FastAPI app
app = FastAPI(
    title="MyWork Marketplace API",
    description="API for the MyWork AI development marketplace",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if not settings.LOG_HTTP_REQUESTS:
        return await call_next(request)

    request_id = request.headers.get("x-request-id", str(uuid4()))
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
            request_id=request_id,
        )
        raise

    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )
    response.headers["X-Request-ID"] = request_id
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://marketplace.mywork.ai",
        "https://frontend-hazel-ten-17.vercel.app",
        "https://mywork-ai-production.up.railway.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": "marketplace-api",
        "environment": settings.ENVIRONMENT
    }


# API Info
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": {
            "products": "/api/products",
            "users": "/api/users",
            "orders": "/api/orders",
            "brain": "/api/brain",
            "checkout": "/api/checkout",
        }
    }


# Import and include routers
from api.products import router as products_router
from api.users import router as users_router
from api.orders import router as orders_router
from api.reviews import router as reviews_router
from api.brain import router as brain_router
from api.webhooks import router as webhooks_router
from api.payouts import router as payouts_router
from api.analytics import router as analytics_router
from api.checkout import router as checkout_router
from api.uploads import router as uploads_router

app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(brain_router, prefix="/api/brain", tags=["Brain"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(payouts_router, tags=["Payouts"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(checkout_router, prefix="/api/checkout", tags=["Checkout"])
app.include_router(uploads_router, prefix="/api/uploads", tags=["Uploads"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
