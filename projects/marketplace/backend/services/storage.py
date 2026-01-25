"""
Storage utilities for Cloudflare R2 (S3-compatible).
"""

from __future__ import annotations

import mimetypes
import os
import re
import uuid
from functools import lru_cache
from typing import Optional

import boto3
from botocore.config import Config

from config import settings

# Upload validation
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_PACKAGE_BYTES = 500 * 1024 * 1024  # 500 MB

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_PACKAGE_TYPES = {
    "application/zip",
    "application/x-zip-compressed",
    "application/x-tar",
    "application/gzip",
    "application/x-gzip",
    "application/octet-stream",
}


def _sanitize_filename(filename: str) -> str:
    """Return a safe filename (no path separators, limited characters)."""
    name = os.path.basename(filename).strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:120] if name else "upload"


def _guess_extension(filename: str, content_type: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext:
        return ext
    guessed = mimetypes.guess_extension(content_type or "")
    return guessed or ""


def _object_prefix(kind: str) -> str:
    if kind == "preview_image":
        return "images"
    if kind == "package":
        return "packages"
    return "uploads"


def build_object_key(kind: str, filename: str, owner_id: str) -> str:
    """Generate a unique object key for uploads."""
    safe_name = _sanitize_filename(filename)
    ext = _guess_extension(safe_name, "")
    if ext and not safe_name.endswith(ext):
        safe_name = f"{safe_name}{ext}"
    token = uuid.uuid4().hex
    prefix = _object_prefix(kind)
    owner_segment = owner_id or "anonymous"
    return f"{prefix}/{owner_segment}/{token}-{safe_name}"


def validate_upload(kind: str, content_type: str, size_bytes: int) -> None:
    """Validate file type and size for the given upload kind."""
    if size_bytes <= 0:
        raise ValueError("File size must be greater than 0 bytes")

    if kind == "preview_image":
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError("Unsupported image type")
        if size_bytes > MAX_IMAGE_BYTES:
            raise ValueError("Image exceeds maximum size (5MB)")
        return

    if kind == "package":
        if content_type and content_type not in ALLOWED_PACKAGE_TYPES:
            raise ValueError("Unsupported package type")
        if size_bytes > MAX_PACKAGE_BYTES:
            raise ValueError("Package exceeds maximum size (500MB)")
        return

    raise ValueError("Unsupported upload kind")


def resolve_public_base_url() -> Optional[str]:
    """Resolve the public base URL for R2 objects."""
    if settings.R2_PUBLIC_URL:
        return settings.R2_PUBLIC_URL.rstrip("/")

    if not settings.R2_ENDPOINT or not settings.R2_BUCKET:
        return None

    endpoint = settings.R2_ENDPOINT.rstrip("/")
    if "r2.cloudflarestorage.com" in endpoint:
        scheme, rest = endpoint.split("://", 1)
        return f"{scheme}://{settings.R2_BUCKET}.{rest}"

    return None


def build_public_url(key: str) -> Optional[str]:
    base_url = resolve_public_base_url()
    if not base_url:
        return None
    return f"{base_url}/{key}"


def _ensure_r2_config() -> None:
    missing = []
    if not settings.R2_ACCESS_KEY_ID:
        missing.append("R2_ACCESS_KEY_ID")
    if not settings.R2_SECRET_ACCESS_KEY:
        missing.append("R2_SECRET_ACCESS_KEY")
    if not settings.R2_BUCKET:
        missing.append("R2_BUCKET")
    if not settings.R2_ENDPOINT:
        missing.append("R2_ENDPOINT")
    if missing:
        raise ValueError(f"Missing R2 configuration: {', '.join(missing)}")


@lru_cache()
def get_s3_client():
    """Get cached S3 client for R2."""
    _ensure_r2_config()
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def generate_presigned_put(key: str, content_type: str, expires_in: int = 600) -> str:
    """Generate presigned URL for PUT uploads."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.R2_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )


def generate_presigned_get(
    key: str,
    expires_in: int = 600,
    filename: Optional[str] = None,
) -> str:
    """Generate presigned URL for downloads."""
    client = get_s3_client()
    params = {
        "Bucket": settings.R2_BUCKET,
        "Key": key,
    }
    if filename:
        params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'
    return client.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=expires_in,
    )
