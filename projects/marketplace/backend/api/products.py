"""
Products API endpoints.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from database import get_db
from models.product import Product, PRODUCT_CATEGORIES
from auth import get_current_user, CurrentUser

router = APIRouter()


# Pydantic schemas
class ProductBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: str = Field(..., min_length=100)
    short_description: Optional[str] = Field(None, max_length=500)
    category: str
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    price: float = Field(..., ge=0, le=10000)
    license_type: str = "standard"
    tech_stack: Optional[List[str]] = None
    framework: Optional[str] = None
    requirements: Optional[str] = None
    demo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    package_url: Optional[str] = None
    package_size_bytes: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, min_length=100)
    short_description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    price: Optional[float] = Field(None, ge=0, le=10000)
    tags: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    subcategory: Optional[str] = None
    license_type: Optional[str] = None
    framework: Optional[str] = None
    requirements: Optional[str] = None
    demo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    package_url: Optional[str] = None
    package_size_bytes: Optional[int] = None


class ProductResponse(ProductBase):
    id: str
    slug: str
    seller_id: str
    status: str
    views: int
    sales: int
    rating_average: float
    rating_count: int
    version: str
    preview_images: Optional[List[str]] = None
    package_url: Optional[str] = None
    package_size_bytes: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int


# Endpoints
@router.get("", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tech_stack: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|popular|price_low|price_high)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List products with filtering and pagination."""

    # Base query - only active products
    query = select(Product).where(Product.status == "active")

    # Apply filters
    if category:
        query = query.where(Product.category == category)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Product.title.ilike(search_term)) |
            (Product.description.ilike(search_term))
        )

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    if tech_stack:
        query = query.where(Product.tech_stack.contains([tech_stack]))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    if sort == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Product.sales.desc())
    elif sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/categories")
async def list_categories():
    """List all product categories."""
    return {"categories": PRODUCT_CATEGORIES}


@router.get("/featured", response_model=List[ProductResponse])
async def list_featured_products(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """List featured products."""
    query = (
        select(Product)
        .where(Product.status == "active")
        .where(Product.featured == True)
        .order_by(Product.sales.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    products = result.scalars().all()

    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{slug}", response_model=ProductResponse)
async def get_product(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get product by slug."""
    query = select(Product).where(Product.slug == slug)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Increment view count
    product.views += 1
    await db.commit()

    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Create a new product listing."""
    # TODO: Get seller_id from auth
    # TODO: Validate seller has Pro subscription

    # Generate slug
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', product_data.title.lower()).strip('-')

    # Check slug uniqueness
    existing = await db.execute(
        select(Product).where(Product.slug == slug)
    )
    if existing.scalar_one_or_none():
        # Add random suffix
        import random
        slug = f"{slug}-{random.randint(1000, 9999)}"

    product = Product(
        seller_id="temp-seller-id",  # TODO: From auth
        slug=slug,
        **product_data.model_dump()
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Update a product listing."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # TODO: Verify ownership

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Delete (archive) a product listing."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # TODO: Verify ownership

    # Soft delete - change status to archived
    product.status = "archived"
    await db.commit()

    return None


@router.post("/{product_id}/publish", response_model=ProductResponse)
async def publish_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Publish a draft product."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # TODO: Verify ownership
    # TODO: Validate product is complete (has package, images, etc.)

    if product.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft products can be published"
        )

    product.status = "pending"  # Goes to review
    # Or set to "active" if auto-approve
    # product.status = "active"

    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.get("/me", response_model=ProductListResponse)
async def get_my_products(
    status: Optional[str] = Query(None, pattern="^(draft|active|archived|pending)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get the current user's products."""

    # Base query - user's products only
    query = select(Product).where(Product.seller_id == current_user.user_id)

    # Optional status filter
    if status:
        query = query.where(Product.status == status)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting (newest first)
    query = query.order_by(Product.created_at.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        total=total or 0,
        page=page,
        page_size=page_size
    )
