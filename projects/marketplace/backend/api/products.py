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
from dependencies import get_current_db_user
from models.product import Product, PRODUCT_CATEGORIES
from models.user import User
from services.storage import extract_key_from_url, generate_presigned_get

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


def _normalize_media_fields(
    preview_images: Optional[List[str]],
    package_url: Optional[str] = None,
) -> tuple[list[str], Optional[str]]:
    normalized_images: list[str] = []
    for image in preview_images or []:
        normalized_images.append(extract_key_from_url(image))

    normalized_package = None
    if package_url:
        normalized_package = extract_key_from_url(package_url)

    return normalized_images, normalized_package


def _resolve_preview_images(images: Optional[List[str]]) -> list[str]:
    resolved: list[str] = []
    for image in images or []:
        if image.startswith("http://") or image.startswith("https://"):
            resolved.append(image)
        else:
            resolved.append(generate_presigned_get(image, expires_in=3600))
    return resolved


def _product_response(product: Product) -> ProductResponse:
    response = ProductResponse.model_validate(product)
    response.preview_images = _resolve_preview_images(product.preview_images)
    response.package_url = product.package_url
    response.package_size_bytes = product.package_size_bytes
    return response


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
        products=[_product_response(p) for p in products],
        total=total or 0,
        page=page,
        page_size=page_size,
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

    return [_product_response(p) for p in products]


@router.get("/{slug}", response_model=ProductResponse)
async def get_product(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get product by slug."""
    import re

    is_uuid = re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", slug)
    if is_uuid:
        query = select(Product).where(Product.id == slug)
    else:
        query = select(Product).where(Product.slug == slug)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Increment view count
    product.views += 1
    await db.commit()

    return _product_response(product)


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product listing."""
    if not current_user.is_seller:
        raise HTTPException(status_code=403, detail="Seller account required")

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

    preview_images, package_url = _normalize_media_fields(
        product_data.preview_images,
        product_data.package_url,
    )
    data = product_data.model_dump()
    data["preview_images"] = preview_images
    if package_url:
        data["package_url"] = package_url

    product = Product(seller_id=current_user.id, slug=slug, **data)

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return _product_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a product listing."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    if "preview_images" in update_data or "package_url" in update_data:
        preview_images, package_url = _normalize_media_fields(
            update_data.get("preview_images"),
            update_data.get("package_url"),
        )
        if "preview_images" in update_data:
            update_data["preview_images"] = preview_images
        if "package_url" in update_data and package_url:
            update_data["package_url"] = package_url
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return _product_response(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (archive) a product listing."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Soft delete - change status to archived
    product.status = "archived"
    await db.commit()

    return None


@router.post("/{product_id}/publish", response_model=ProductResponse)
async def publish_product(
    product_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a draft product."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    # TODO: Validate product is complete (has package, images, etc.)

    if product.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft products can be published"
        )

    # Auto-approve for now; add moderation workflow later.
    product.status = "active"

    await db.commit()
    await db.refresh(product)

    return _product_response(product)


@router.get("/me", response_model=ProductListResponse)
async def get_my_products(
    status: Optional[str] = Query(None, pattern="^(draft|active|archived|pending)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's products."""

    # Base query - user's products only
    query = select(Product).where(Product.seller_id == current_user.id)

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
        products=[_product_response(p) for p in products],
        total=total or 0,
        page=page,
        page_size=page_size,
    )
