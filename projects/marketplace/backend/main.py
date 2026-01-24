"""
MyWork Marketplace - Backend API
================================
FastAPI application for the marketplace platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    logger.info("marketplace_starting", version="0.1.0")
    yield
    # Shutdown
    logger.info("marketplace_stopping")


# Initialize FastAPI app
app = FastAPI(
    title="MyWork Marketplace API",
    description="API for the MyWork AI development marketplace",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://marketplace.mywork.ai",
    ],
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
        "version": "0.1.0",
        "service": "marketplace-api"
    }


# API Info
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "MyWork Marketplace API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


# TODO: Import and include routers
# from api.products import router as products_router
# from api.orders import router as orders_router
# from api.users import router as users_router
# from api.brain import router as brain_router
# from api.webhooks import router as webhooks_router
#
# app.include_router(products_router, prefix="/api/products", tags=["Products"])
# app.include_router(orders_router, prefix="/api/orders", tags=["Orders"])
# app.include_router(users_router, prefix="/api/users", tags=["Users"])
# app.include_router(brain_router, prefix="/api/brain", tags=["Brain"])
# app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
