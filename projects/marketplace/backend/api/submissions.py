"""
Project submission API endpoints.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_db_user
from models.product import Product, ProductVersion, PRODUCT_CATEGORIES
from models.submission import ProjectSubmission, SUBMISSION_STATUSES
from models.user import User, SellerProfile
from models.subscription import SUBSCRIPTION_TIERS
from services.storage import extract_key_from_url
from services.submission_audit import queue_submission_audit

router = APIRouter()


class SubmissionBase(BaseModel):
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
    repo_url: Optional[str] = None
    repo_ref: Optional[str] = None
    repo_provider: Optional[str] = None
    audit_profile: Optional[str] = None
    audit_plan_version: Optional[str] = None
    ip_consent: Optional[bool] = None


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionResponse(SubmissionBase):
    id: str
    seller_id: str
    status: str
    audit_report: Optional[dict] = None
    audit_score: Optional[float] = None
    failure_reason: Optional[str] = None
    product_id: Optional[str] = None
    repo_commit_sha: Optional[str] = None
    brain_opt_in: Optional[bool] = None
    brain_ingest_status: Optional[str] = None
    brain_ingested_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    submissions: List[SubmissionResponse]
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


async def _require_seller_profile(user: User, db: AsyncSession) -> SellerProfile:
    if not user.is_seller:
        raise HTTPException(status_code=403, detail="Seller account required")
    profile = await db.scalar(select(SellerProfile).where(SellerProfile.user_id == user.id))
    if not profile:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    return profile


@router.post("", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a project for audit and approval."""
    await _require_seller_profile(current_user, db)

    tier = current_user.subscription_tier or "free"
    tier_limits = SUBSCRIPTION_TIERS.get(tier, {}).get("limits", {})
    if not tier_limits.get("can_sell", False):
        raise HTTPException(status_code=403, detail="Active subscription required to list projects")

    if submission_data.category not in PRODUCT_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    if not submission_data.repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required for audit")

    if submission_data.ip_consent is not True:
        raise HTTPException(status_code=400, detail="IP consent is required for audit and Brain training")

    preview_images, package_url = _normalize_media_fields(
        submission_data.preview_images,
        submission_data.package_url,
    )

    data = submission_data.model_dump()
    data["preview_images"] = preview_images
    if package_url:
        data["package_url"] = package_url
    data["brain_opt_in"] = True

    submission = ProjectSubmission(
        seller_id=current_user.id,
        status="submitted",
        **data,
    )

    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    queue_submission_audit(submission.id)

    return SubmissionResponse.model_validate(submission)


@router.get("/me", response_model=SubmissionListResponse)
async def list_my_submissions(
    status: Optional[str] = Query(None, pattern="^(submitted|auditing|approved|rejected|published)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's submissions."""
    query = select(ProjectSubmission).where(ProjectSubmission.seller_id == current_user.id)
    if status:
        query = query.where(ProjectSubmission.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    offset = (page - 1) * page_size
    query = query.order_by(ProjectSubmission.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    submissions = result.scalars().all()

    return SubmissionListResponse(
        submissions=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a submission by id."""
    submission = await db.get(ProjectSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return SubmissionResponse.model_validate(submission)


@router.post("/{submission_id}/retry", response_model=SubmissionResponse)
async def retry_audit(
    submission_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-run audit on a submission."""
    submission = await db.get(ProjectSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if submission.status not in ("rejected", "approved"):
        raise HTTPException(status_code=400, detail="Submission is already auditing")

    submission.status = "submitted"
    submission.audit_report = None
    submission.audit_score = None
    submission.failure_reason = None
    submission.audit_started_at = None
    submission.audit_completed_at = None
    await db.commit()
    await db.refresh(submission)

    queue_submission_audit(submission.id)
    return SubmissionResponse.model_validate(submission)


@router.post("/{submission_id}/publish", response_model=SubmissionResponse)
async def publish_submission(
    submission_id: str,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish an approved submission as a marketplace product."""
    submission = await db.get(ProjectSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if submission.status != "approved":
        raise HTTPException(status_code=400, detail="Submission must be approved before publishing")

    if submission.product_id:
        submission.status = "published"
        await db.commit()
        await db.refresh(submission)
        return SubmissionResponse.model_validate(submission)

    # Create product listing from submission
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", submission.title.lower()).strip("-")
    existing = await db.execute(select(Product).where(Product.slug == slug))
    if existing.scalar_one_or_none():
        import random
        slug = f"{slug}-{random.randint(1000, 9999)}"

    if not submission.package_url:
        raise HTTPException(status_code=400, detail="Submission package is missing")

    product = Product(
        seller_id=current_user.id,
        slug=slug,
        title=submission.title,
        description=submission.description,
        short_description=submission.short_description,
        category=submission.category,
        subcategory=submission.subcategory,
        tags=submission.tags or [],
        price=float(submission.price),
        license_type=submission.license_type,
        tech_stack=submission.tech_stack or [],
        framework=submission.framework,
        requirements=submission.requirements,
        demo_url=submission.demo_url,
        documentation_url=submission.documentation_url,
        preview_images=submission.preview_images or [],
        package_url=submission.package_url,
        package_size_bytes=submission.package_size_bytes,
        status="active",
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    version = ProductVersion(
        product_id=product.id,
        version=product.version,
        package_url=submission.package_url,
        package_size_bytes=submission.package_size_bytes,
        changelog="Initial submission",
    )
    db.add(version)

    submission.product_id = product.id
    submission.status = "published"

    await db.commit()
    await db.refresh(submission)

    return SubmissionResponse.model_validate(submission)
