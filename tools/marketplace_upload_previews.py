#!/usr/bin/env python3
"""
Upload SportsAI preview images to Marketplace via presigned URLs and
attach them to the product listing.

Requires:
  - MARKETPLACE_TOKEN (Clerk JWT)
Optional:
  - MARKETPLACE_API_URL (default: https://mywork-ai-production.up.railway.app)
  - MARKETPLACE_PRODUCT_ID (default: SportsAI ID)
  - PREVIEW_DIR (default: assets/screenshots/sportsai)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

DEFAULT_API_URL = "https://mywork-ai-production.up.railway.app"
DEFAULT_PRODUCT_ID = "c54f73f4-b66c-4130-8654-292ad79adf36"
DEFAULT_PREVIEW_DIR = Path("assets/screenshots/sportsai")


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Missing required env: {name}")
        sys.exit(1)
    return value


def _request_json(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "MyWork-PreviewUploader/1.0",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method=method)
    with urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def _upload_file(upload_url: str, content_type: str, file_path: Path) -> None:
    data = file_path.read_bytes()
    req = Request(upload_url, data=data, method="PUT")
    req.add_header("Content-Type", content_type)
    req.add_header("Content-Length", str(len(data)))
    with urlopen(req, timeout=60) as resp:
        if resp.status not in (200, 201, 204):
            raise RuntimeError(f"Upload failed with status {resp.status}")


def main() -> int:
    api_url = os.environ.get("MARKETPLACE_API_URL", DEFAULT_API_URL).rstrip("/")
    token = _require_env("MARKETPLACE_TOKEN")
    product_id = os.environ.get("MARKETPLACE_PRODUCT_ID", DEFAULT_PRODUCT_ID).strip()
    preview_dir = Path(os.environ.get("PREVIEW_DIR", str(DEFAULT_PREVIEW_DIR)))

    if not preview_dir.exists():
        print(f"Preview directory not found: {preview_dir}")
        return 1

    images = sorted([p for p in preview_dir.glob("*.png") if p.is_file()])
    if not images:
        print(f"No PNG files found in {preview_dir}")
        return 1

    file_keys: list[str] = []

    for image in images:
        payload = {
            "kind": "preview_image",
            "filename": image.name,
            "content_type": "image/png",
            "size_bytes": image.stat().st_size,
        }
        try:
            presign = _request_json(
                "POST",
                f"{api_url}/api/uploads/presign",
                token,
                payload,
            )
        except HTTPError as exc:
            detail = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
            print(f"Presign failed for {image.name}: {exc} {detail}")
            return 1

        upload_url = presign.get("upload_url")
        file_key = presign.get("file_key")
        if not upload_url or not file_key:
            print(f"Invalid presign response for {image.name}: {presign}")
            return 1

        _upload_file(upload_url, "image/png", image)
        file_keys.append(file_key)
        print(f"Uploaded {image.name} -> {file_key}")

    update_payload = {"preview_images": file_keys}
    try:
        updated = _request_json(
            "PUT",
            f"{api_url}/api/products/{product_id}",
            token,
            update_payload,
        )
    except HTTPError as exc:
        detail = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
        print(f"Product update failed: {exc} {detail}")
        return 1

    print("Preview images attached to product:")
    for image in updated.get("preview_images", []):
        print(f"- {image}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
