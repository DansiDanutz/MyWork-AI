#!/usr/bin/env python3
"""
Brain Sync Tool
===============
Sync local Brain entries to the Marketplace Brain API.

Usage:
    python tools/brain_sync.py export
    python tools/brain_sync.py push

Environment:
    MARKETPLACE_BRAIN_URL   (default: https://mywork-ai-production.up.railway.app/api/brain)
    MARKETPLACE_BRAIN_TOKEN (required for push; Clerk JWT bearer token)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from config import BRAIN_DATA_JSON, PLANNING_DIR, print_error, print_info, print_success

SYNC_REGISTRY = PLANNING_DIR / "brain_sync_registry.json"
DEFAULT_BRAIN_URL = "https://mywork-ai-production.up.railway.app/api/brain"

TYPE_MAP = {
    "lesson": "lesson",
    "pattern": "pattern",
    "insight": "tip",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_local_entries() -> List[Dict[str, Any]]:
    if not BRAIN_DATA_JSON.exists():
        print_error(f"Missing local brain data: {BRAIN_DATA_JSON}")
        return []
    data = json.loads(BRAIN_DATA_JSON.read_text())
    return data.get("entries", [])


def _load_sync_registry() -> Dict[str, Any]:
    if SYNC_REGISTRY.exists():
        try:
            return json.loads(SYNC_REGISTRY.read_text())
        except Exception:
            return {"synced_ids": []}
    return {"synced_ids": []}


def _save_sync_registry(registry: Dict[str, Any]) -> None:
    registry["last_synced_at"] = _now_iso()
    PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    SYNC_REGISTRY.write_text(json.dumps(registry, indent=2))


def _title_from_content(content: str) -> str:
    trimmed = content.strip().replace("\n", " ")
    if len(trimmed) <= 80:
        return trimmed
    return trimmed[:77].rsplit(" ", 1)[0] + "..."


def _build_payload(entry: Dict[str, Any]) -> Dict[str, Any]:
    entry_type = TYPE_MAP.get(entry.get("type"), "lesson")
    title = entry.get("title") or _title_from_content(entry.get("content", ""))
    content = entry.get("content", "")
    context = entry.get("context")
    if context:
        content = f"{content}\n\nContext: {context}"
    tags = list(entry.get("tags") or [])
    local_tag = f"local:{entry.get('id', 'unknown')}"
    tags.extend(["source:mywork", local_tag])
    # de-duplicate tags
    tags = sorted({tag for tag in tags if tag})

    return {
        "title": title,
        "content": content,
        "type": entry_type,
        "category": "framework",
        "tags": tags,
        "language": None,
        "framework": None,
    }


def _http_get_json(url: str) -> Dict[str, Any]:
    req = Request(url, headers={"User-Agent": "MyWork-BrainSync/1.0"})
    with urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_post_json(url: str, payload: Dict[str, Any], token: str) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "User-Agent": "MyWork-BrainSync/1.0",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    req = Request(url, data=body, headers=headers, method="POST")
    with urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _remote_exists(base_url: str, local_tag: str) -> bool:
    query = urlencode({"tag": local_tag, "page": 1, "page_size": 1})
    url = f"{base_url}?{query}"
    data = _http_get_json(url)
    return data.get("total", 0) > 0


def export_payload() -> int:
    entries = _load_local_entries()
    if not entries:
        return 1
    payloads = [_build_payload(entry) for entry in entries]
    export_path = PLANNING_DIR / "brain_sync_payload.json"
    export_path.write_text(json.dumps(payloads, indent=2))
    print_success(f"Exported {len(payloads)} entries to {export_path}")
    return 0


def push_entries() -> int:
    token = os.environ.get("MARKETPLACE_BRAIN_TOKEN", "").strip()
    if not token:
        print_error("MARKETPLACE_BRAIN_TOKEN is required to push entries.")
        print_info("Tip: Use a Clerk JWT from an authenticated session.")
        return 1

    base_url = os.environ.get("MARKETPLACE_BRAIN_URL", DEFAULT_BRAIN_URL).strip()

    registry = _load_sync_registry()
    synced_ids = set(registry.get("synced_ids", []))

    entries = _load_local_entries()
    if not entries:
        return 1

    created = 0
    skipped = 0

    for entry in entries:
        entry_id = entry.get("id")
        if entry_id in synced_ids:
            skipped += 1
            continue

        local_tag = f"local:{entry_id}"
        try:
            if _remote_exists(base_url, local_tag):
                skipped += 1
                synced_ids.add(entry_id)
                continue
        except Exception as exc:
            print_error(f"Failed to check remote for {entry_id}: {exc}")
            return 1

        payload = _build_payload(entry)
        try:
            _http_post_json(base_url, payload, token)
            created += 1
            synced_ids.add(entry_id)
        except Exception as exc:
            print_error(f"Failed to push {entry_id}: {exc}")
            return 1

    registry["synced_ids"] = sorted(synced_ids)
    _save_sync_registry(registry)

    print_success(f"Brain sync complete. Created: {created}, Skipped: {skipped}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "export":
        return export_payload()
    if cmd == "push":
        return push_entries()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
