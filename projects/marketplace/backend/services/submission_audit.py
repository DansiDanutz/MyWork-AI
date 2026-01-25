"""
Submission audit utilities.
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from urllib.request import urlopen

from sqlalchemy import select

from database import async_session_maker
from models.submission import ProjectSubmission
from models.user import SellerProfile
from services.storage import generate_presigned_get


SECRET_PATTERNS = [
    r"sk_(live|test)_[0-9a-zA-Z]{16,}",
    r"pk_live_[0-9a-zA-Z]{16,}",
    r"AKIA[0-9A-Z]{16}",
    r"ghp_[0-9a-zA-Z]{16,}",
    r"-----BEGIN PRIVATE KEY-----",
]

MAX_TEXT_SCAN_BYTES = 512 * 1024
MAX_ARCHIVE_BYTES = 500 * 1024 * 1024
REQUIRED_FILES = ["project.yaml", "readme.md", "license", "license.md"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _matches_secret(content: str) -> Optional[str]:
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, content):
            return pattern
    return None


def _is_text_file(name: str) -> bool:
    lowered = name.lower()
    if lowered.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".tar", ".gz")):
        return False
    return True


def _load_archive_names(path: str) -> tuple[List[str], Optional[str]]:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            return zf.namelist(), "zip"
    if tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as tf:
            return tf.getnames(), "tar"
    return [], None


def _scan_archive_for_secrets(path: str, archive_type: str) -> List[str]:
    hits: List[str] = []
    if archive_type == "zip":
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if info.file_size > MAX_TEXT_SCAN_BYTES:
                    continue
                if not _is_text_file(info.filename):
                    continue
                with zf.open(info) as fp:
                    data = fp.read(MAX_TEXT_SCAN_BYTES)
                if b"\x00" in data:
                    continue
                text = data.decode("utf-8", errors="ignore")
                match = _matches_secret(text)
                if match:
                    hits.append(info.filename)
    elif archive_type == "tar":
        with tarfile.open(path, "r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                if member.size > MAX_TEXT_SCAN_BYTES:
                    continue
                if not _is_text_file(member.name):
                    continue
                fileobj = tf.extractfile(member)
                if not fileobj:
                    continue
                data = fileobj.read(MAX_TEXT_SCAN_BYTES)
                if b"\x00" in data:
                    continue
                text = data.decode("utf-8", errors="ignore")
                match = _matches_secret(text)
                if match:
                    hits.append(member.name)
    return hits


def _perform_audit(submission: Dict[str, Any]) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "checked_at": _now().isoformat(),
        "errors": [],
        "warnings": [],
        "checks": [],
    }

    package_url = submission.get("package_url")
    package_size = submission.get("package_size_bytes") or 0

    if not package_url:
        report["errors"].append("Package archive is required.")
        report["checks"].append({"name": "package_present", "status": "fail"})
        report["score"] = 0
        report["status"] = "rejected"
        return report

    if package_size > MAX_ARCHIVE_BYTES:
        report["errors"].append("Package exceeds maximum allowed size.")

    download_url = package_url
    if not package_url.startswith(("http://", "https://")):
        download_url = generate_presigned_get(package_url, expires_in=300)

    temp_dir = tempfile.mkdtemp(prefix="submission_audit_")
    archive_path = os.path.join(temp_dir, "package")

    try:
        with urlopen(download_url, timeout=30) as response, open(archive_path, "wb") as out:
            shutil.copyfileobj(response, out)

        names, archive_type = _load_archive_names(archive_path)
        if not archive_type:
            report["errors"].append("Package must be a .zip or .tar archive.")
            report["checks"].append({"name": "archive_type", "status": "fail"})
        else:
            report["checks"].append({"name": "archive_type", "status": "pass", "details": archive_type})

        lowered = [name.lower() for name in names]
        for required in REQUIRED_FILES:
            if not any(item.endswith(required) for item in lowered):
                report["errors"].append(f"Missing required file: {required}")
                report["checks"].append({"name": f"required_{required}", "status": "fail"})
            else:
                report["checks"].append({"name": f"required_{required}", "status": "pass"})

        if any(name.lower().endswith((".env", ".env.local", ".env.production")) for name in lowered):
            report["errors"].append("Environment files (.env) must not be included.")

        if any("/node_modules/" in name.lower() or name.lower().startswith("node_modules/") for name in lowered):
            report["warnings"].append("node_modules found. Please remove dependencies before packaging.")

        if any("/venv/" in name.lower() or name.lower().startswith("venv/") for name in lowered):
            report["warnings"].append("venv found. Please remove virtual environments before packaging.")

        if archive_type:
            secret_hits = _scan_archive_for_secrets(archive_path, archive_type)
            if secret_hits:
                report["errors"].append("Potential secrets detected in package files.")
                report["checks"].append({"name": "secret_scan", "status": "fail", "files": secret_hits[:10]})
            else:
                report["checks"].append({"name": "secret_scan", "status": "pass"})
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    errors = report["errors"]
    warnings = report["warnings"]

    score = max(0, 100 - len(errors) * 30 - len(warnings) * 10)
    report["score"] = score
    report["status"] = "approved" if not errors else "rejected"
    return report


async def run_submission_audit(submission_id: str) -> None:
    async with async_session_maker() as session:
        submission = await session.get(ProjectSubmission, submission_id)
        if not submission:
            return
        if submission.status in ("auditing", "approved", "rejected", "published"):
            return

        submission.status = "auditing"
        submission.audit_started_at = _now()
        await session.commit()

        submission_data = {
            "package_url": submission.package_url,
            "package_size_bytes": submission.package_size_bytes,
        }

    try:
        report = await asyncio.to_thread(_perform_audit, submission_data)
    except Exception as exc:
        report = {
            "checked_at": _now().isoformat(),
            "errors": [f"Audit failed: {exc}"],
            "warnings": [],
            "checks": [{"name": "audit_run", "status": "fail"}],
            "score": 0,
            "status": "rejected",
        }

    async with async_session_maker() as session:
        submission = await session.get(ProjectSubmission, submission_id)
        if not submission:
            return

        submission.audit_report = report
        submission.audit_score = report.get("score")
        submission.audit_completed_at = _now()
        submission.failure_reason = "; ".join(report.get("errors", [])) if report.get("errors") else None
        submission.status = report.get("status", "rejected")

        if submission.status == "approved":
            profile = await session.scalar(
                select(SellerProfile).where(SellerProfile.user_id == submission.seller_id)
            )
            if profile and profile.verification_level == "basic":
                profile.verification_level = "verified"
                profile.verified_at = _now()

        await session.commit()


def queue_submission_audit(submission_id: str) -> None:
    """Fire-and-forget audit run."""
    asyncio.create_task(run_submission_audit(submission_id))
