"""
Upload endpoints for generating presigned URLs.
"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import CurrentUser, get_current_user
from services.storage import (
    build_object_key,
    build_public_url,
    generate_presigned_put,
    validate_upload,
)

router = APIRouter()


class PresignRequest(BaseModel):
    kind: Literal["preview_image", "package"]
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=255)
    size_bytes: int = Field(..., gt=0)


class PresignResponse(BaseModel):
    upload_url: str
    file_key: str
    public_url: Optional[str] = None
    expires_in: int


@router.post("/presign", response_model=PresignResponse)
async def create_presigned_upload(
    payload: PresignRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a presigned upload URL for direct-to-R2 uploads."""
    try:
        validate_upload(payload.kind, payload.content_type, payload.size_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        key = build_object_key(payload.kind, payload.filename, current_user.user_id)
        upload_url = generate_presigned_put(
            key=key,
            content_type=payload.content_type,
            expires_in=600,
        )
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    public_url = None
    if payload.kind == "preview_image":
        public_url = build_public_url(key)

    return PresignResponse(
        upload_url=upload_url,
        file_key=key,
        public_url=public_url,
        expires_in=600,
    )
