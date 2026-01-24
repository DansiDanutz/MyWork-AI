"""
Brain API endpoints - Collective knowledge system.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel

from database import get_db
from models.brain import BrainEntry
from models.user import User

router = APIRouter()


# Pydantic schemas
class BrainEntryCreate(BaseModel):
    title: str
    content: str
    type: str  # pattern, snippet, tutorial, solution, documentation
    category: str
    tags: List[str] = []
    language: Optional[str] = None
    framework: Optional[str] = None


class BrainEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class BrainEntryResponse(BaseModel):
    id: str
    contributor_id: str
    contributor_username: Optional[str]
    title: str
    content: str
    type: str
    category: str
    tags: List[str]
    language: Optional[str]
    framework: Optional[str]
    quality_score: float
    usage_count: int
    helpful_votes: int
    unhelpful_votes: int
    verified: bool

    class Config:
        from_attributes = True


class BrainSearchResponse(BaseModel):
    entries: List[BrainEntryResponse]
    total: int
    page: int
    page_size: int


class BrainQueryRequest(BaseModel):
    query: str
    category: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    limit: int = 5


class BrainQueryResponse(BaseModel):
    query: str
    results: List[BrainEntryResponse]
    ai_summary: Optional[str] = None


class VoteRequest(BaseModel):
    vote: int  # 1 for upvote, -1 for downvote


# Endpoints
@router.post("", response_model=BrainEntryResponse, status_code=201)
async def contribute_knowledge(
    entry_data: BrainEntryCreate,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Contribute knowledge to the Brain."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    # Validate entry type
    valid_types = ["pattern", "snippet", "tutorial", "solution", "documentation"]
    if entry_data.type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry type. Must be one of: {valid_types}"
        )

    # Create entry
    entry = BrainEntry(
        contributor_id=user_id,
        title=entry_data.title,
        content=entry_data.content,
        type=entry_data.type,
        category=entry_data.category,
        tags=entry_data.tags,
        language=entry_data.language,
        framework=entry_data.framework,
        status="active",  # Default to active status
        quality_score=0.5  # Start with neutral score
    )

    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    # TODO: Generate embedding and store in Pinecone
    # TODO: Trigger quality assessment

    return BrainEntryResponse(
        id=entry.id,
        contributor_id=entry.contributor_id,
        contributor_username=None,  # TODO: Get username
        title=entry.title,
        content=entry.content,
        type=entry.type,
        category=entry.category,
        tags=entry.tags or [],
        language=entry.language,
        framework=entry.framework,
        quality_score=entry.quality_score,
        usage_count=entry.usage_count,
        helpful_votes=entry.helpful_votes,
        unhelpful_votes=entry.unhelpful_votes,
        verified=entry.verified
    )


@router.get("", response_model=BrainSearchResponse)
async def search_brain(
    q: Optional[str] = None,
    category: Optional[str] = None,
    entry_type: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    tag: Optional[str] = None,
    verified_only: bool = False,
    sort: str = Query("relevance", pattern="^(relevance|newest|popular|quality)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Search the Brain knowledge base."""
    # Build query
    query = select(BrainEntry).where(BrainEntry.status == "active")

    if category:
        query = query.where(BrainEntry.category == category)

    if entry_type:
        query = query.where(BrainEntry.type == entry_type)

    if language:
        query = query.where(BrainEntry.language == language)

    if framework:
        query = query.where(BrainEntry.framework == framework)

    if verified_only:
        query = query.where(BrainEntry.verified == True)

    if tag:
        query = query.where(BrainEntry.tags.contains([tag]))

    if q:
        # Simple text search (TODO: Use Pinecone for semantic search)
        search_filter = BrainEntry.title.ilike(f"%{q}%") | BrainEntry.content.ilike(f"%{q}%")
        query = query.where(search_filter)

    # Count total
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Sort
    if sort == "newest":
        query = query.order_by(BrainEntry.created_at.desc())
    elif sort == "popular":
        query = query.order_by(BrainEntry.usage_count.desc())
    elif sort == "quality":
        query = query.order_by(BrainEntry.quality_score.desc())
    else:  # relevance (default to quality + usage)
        query = query.order_by(
            (BrainEntry.quality_score * 0.6 + BrainEntry.usage_count * 0.4).desc()
        )

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    entries = result.scalars().all()

    entry_responses = []
    for entry in entries:
        # Get contributor username
        user_query = select(User).where(User.id == entry.contributor_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        entry_responses.append(BrainEntryResponse(
            id=entry.id,
            contributor_id=entry.contributor_id,
            contributor_username=user.username if user else None,
            title=entry.title,
            content=entry.content,
            type=entry.type,
            category=entry.category,
            tags=entry.tags or [],
            language=entry.language,
            framework=entry.framework,
            quality_score=entry.quality_score,
            usage_count=entry.usage_count,
            helpful_votes=entry.helpful_votes,
            unhelpful_votes=entry.unhelpful_votes,
            verified=entry.verified
        ))

    return BrainSearchResponse(
        entries=entry_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/query", response_model=BrainQueryResponse)
async def query_brain(
    query_data: BrainQueryRequest,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency (rate limit for free tier)
):
    """
    Query the Brain with natural language.
    Uses semantic search + AI to find and summarize relevant knowledge.
    """
    # TODO: Implement semantic search with Pinecone
    # 1. Generate embedding for query
    # 2. Search Pinecone for similar entries
    # 3. Fetch full entries from PostgreSQL
    # 4. Use Claude to generate summary

    # For now, fall back to text search
    query = select(BrainEntry).where(BrainEntry.is_public == True)

    if query_data.category:
        query = query.where(BrainEntry.category == query_data.category)

    if query_data.language:
        query = query.where(BrainEntry.language == query_data.language)

    if query_data.framework:
        query = query.where(BrainEntry.framework == query_data.framework)

    # Text search
    search_filter = (
        BrainEntry.title.ilike(f"%{query_data.query}%") |
        BrainEntry.content.ilike(f"%{query_data.query}%")
    )
    query = query.where(search_filter)

    # Get top results by quality
    query = query.order_by(BrainEntry.quality_score.desc()).limit(query_data.limit)

    result = await db.execute(query)
    entries = result.scalars().all()

    # Increment usage count for returned entries
    for entry in entries:
        entry.usage_count += 1
    await db.commit()

    entry_responses = []
    for entry in entries:
        user_query = select(User).where(User.id == entry.contributor_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        entry_responses.append(BrainEntryResponse(
            id=entry.id,
            contributor_id=entry.contributor_id,
            contributor_username=user.username if user else None,
            title=entry.title,
            content=entry.content,
            type=entry.type,
            category=entry.category,
            tags=entry.tags or [],
            language=entry.language,
            framework=entry.framework,
            quality_score=entry.quality_score,
            usage_count=entry.usage_count,
            helpful_votes=entry.helpful_votes,
            unhelpful_votes=entry.unhelpful_votes,
            verified=entry.verified
        ))

    # TODO: Generate AI summary using Claude
    ai_summary = None

    return BrainQueryResponse(
        query=query_data.query,
        results=entry_responses,
        ai_summary=ai_summary
    )


@router.get("/stats/overview")
async def get_brain_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get Brain statistics."""
    # Total entries
    total_query = select(func.count(BrainEntry.id))
    total_result = await db.execute(total_query)
    total_entries = total_result.scalar()

    # Entries by type
    type_query = select(
        BrainEntry.type,
        func.count(BrainEntry.id)
    ).group_by(BrainEntry.type)
    type_result = await db.execute(type_query)
    entries_by_type = dict(type_result.all())

    # Top categories
    category_query = select(
        BrainEntry.category,
        func.count(BrainEntry.id)
    ).group_by(BrainEntry.category).order_by(func.count(BrainEntry.id).desc()).limit(10)
    category_result = await db.execute(category_query)
    top_categories = dict(category_result.all())

    # Verified entries
    verified_query = select(func.count(BrainEntry.id)).where(BrainEntry.verified == True)
    verified_result = await db.execute(verified_query)
    verified_count = verified_result.scalar()

    # Total usage
    usage_query = select(func.sum(BrainEntry.usage_count))
    usage_result = await db.execute(usage_query)
    total_usage = usage_result.scalar() or 0

    return {
        "total_entries": total_entries,
        "verified_entries": verified_count,
        "total_queries": total_usage,
        "entries_by_type": entries_by_type,
        "top_categories": top_categories
    }


@router.get("/{entry_id}", response_model=BrainEntryResponse)
async def get_brain_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific Brain entry."""
    query = select(BrainEntry).where(BrainEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if not entry.status:
        # TODO: Check if user is contributor or admin
        raise HTTPException(status_code=403, detail="Entry is private")

    # Get contributor username
    user_query = select(User).where(User.id == entry.contributor_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    return BrainEntryResponse(
        id=entry.id,
        contributor_id=entry.contributor_id,
        contributor_username=user.username if user else None,
        title=entry.title,
        content=entry.content,
        type=entry.type,
        category=entry.category,
        tags=entry.tags or [],
        language=entry.language,
        framework=entry.framework,
        quality_score=entry.quality_score,
        usage_count=entry.usage_count,
        helpful_votes=entry.helpful_votes,
        unhelpful_votes=entry.unhelpful_votes,
        verified=entry.verified
    )


@router.put("/{entry_id}", response_model=BrainEntryResponse)
async def update_brain_entry(
    entry_id: str,
    update_data: BrainEntryUpdate,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Update a Brain entry (contributor only)."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(BrainEntry).where(BrainEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if entry.contributor_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)

    # TODO: Re-generate embedding if content changed

    user_query = select(User).where(User.id == entry.contributor_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    return BrainEntryResponse(
        id=entry.id,
        contributor_id=entry.contributor_id,
        contributor_username=user.username if user else None,
        title=entry.title,
        content=entry.content,
        type=entry.type,
        category=entry.category,
        tags=entry.tags or [],
        language=entry.language,
        framework=entry.framework,
        quality_score=entry.quality_score,
        usage_count=entry.usage_count,
        helpful_votes=entry.helpful_votes,
        unhelpful_votes=entry.unhelpful_votes,
        verified=entry.verified
    )


@router.delete("/{entry_id}", status_code=204)
async def delete_brain_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Delete a Brain entry (contributor only)."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    query = select(BrainEntry).where(BrainEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if entry.contributor_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(entry)
    await db.commit()

    # TODO: Remove from Pinecone

    return None


@router.post("/{entry_id}/vote", response_model=BrainEntryResponse)
async def vote_on_entry(
    entry_id: str,
    vote_data: VoteRequest,
    db: AsyncSession = Depends(get_db)
    # TODO: Add auth dependency
):
    """Upvote or downvote a Brain entry."""
    # TODO: Get user_id from auth token
    user_id = "temp-user-id"

    if vote_data.vote not in [1, -1]:
        raise HTTPException(status_code=400, detail="Vote must be 1 or -1")

    query = select(BrainEntry).where(BrainEntry.id == entry_id)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # TODO: Track user votes to prevent double voting

    if vote_data.vote == 1:
        entry.helpful_votes += 1
    else:
        entry.unhelpful_votes += 1

    # Recalculate quality score
    total_votes = entry.helpful_votes + entry.unhelpful_votes
    if total_votes > 0:
        vote_ratio = entry.helpful_votes / total_votes
        # Weight by usage and votes
        entry.quality_score = (
            vote_ratio * 0.5 +
            min(entry.usage_count / 100, 1) * 0.3 +
            0.2  # Base score
        )

    await db.commit()
    await db.refresh(entry)

    user_query = select(User).where(User.id == entry.contributor_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    return BrainEntryResponse(
        id=entry.id,
        contributor_id=entry.contributor_id,
        contributor_username=user.username if user else None,
        title=entry.title,
        content=entry.content,
        type=entry.type,
        category=entry.category,
        tags=entry.tags or [],
        language=entry.language,
        framework=entry.framework,
        quality_score=entry.quality_score,
        usage_count=entry.usage_count,
        helpful_votes=entry.helpful_votes,
        unhelpful_votes=entry.unhelpful_votes,
        verified=entry.verified
    )
