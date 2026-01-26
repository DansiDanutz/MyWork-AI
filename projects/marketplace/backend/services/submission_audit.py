"""
Submission audit utilities.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from urllib.request import urlopen

from sqlalchemy import select

from config import settings
from database import async_session_maker
from models.submission import ProjectSubmission
from models.audit import AuditRun, RepoSnapshot, DeliveryArtifact
from models.user import SellerProfile
from services.storage import generate_presigned_get, build_object_key, build_public_url, get_s3_client


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
REPO_REQUIRED_FILES = REQUIRED_FILES


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


def _sha256_file(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _archive_repo(repo_dir: str, output_dir: str) -> str:
    archive_path = os.path.join(output_dir, "repo_snapshot.zip")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(repo_dir):
            if "/.git" in root:
                continue
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, repo_dir)
                if rel_path.startswith(".git"):
                    continue
                zf.write(full_path, rel_path)
    return archive_path


def _clone_repo(repo_url: str, repo_ref: Optional[str], workdir: str) -> tuple[str, Optional[str]]:
    repo_dir = os.path.join(workdir, "repo")
    clone_cmd = ["git", "clone", "--depth", "1", repo_url, repo_dir]
    if repo_ref:
        clone_cmd = ["git", "clone", "--depth", "1", "--branch", repo_ref, repo_url, repo_dir]
    result = subprocess.run(clone_cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to clone repository")

    if repo_ref and repo_ref not in ("main", "master"):
        checkout = subprocess.run(
            ["git", "-C", repo_dir, "checkout", repo_ref],
            capture_output=True,
            text=True,
            check=False,
        )
        if checkout.returncode != 0:
            raise RuntimeError(checkout.stderr.strip() or "Failed to checkout ref")

    rev = subprocess.run(
        ["git", "-C", repo_dir, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    commit_sha = rev.stdout.strip() if rev.returncode == 0 else None
    return repo_dir, commit_sha


def _scan_repo_for_secrets(repo_dir: str) -> List[str]:
    hits: List[str] = []
    for root, _, files in os.walk(repo_dir):
        if "/.git" in root:
            continue
        for filename in files:
            path = os.path.join(root, filename)
            rel = os.path.relpath(path, repo_dir)
            if not _is_text_file(rel):
                continue
            try:
                with open(path, "rb") as handle:
                    data = handle.read(MAX_TEXT_SCAN_BYTES)
            except OSError:
                continue
            if b"\x00" in data:
                continue
            text = data.decode("utf-8", errors="ignore")
            match = _matches_secret(text)
            if match:
                hits.append(rel)
    return hits


def _perform_audit(submission: Dict[str, Any]) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "checked_at": _now().isoformat(),
        "errors": [],
        "warnings": [],
        "checks": [],
    }

    repo_url = submission.get("repo_url")
    repo_ref = submission.get("repo_ref")

    package_url = submission.get("package_url")
    package_size = submission.get("package_size_bytes") or 0

    if not repo_url:
        report["errors"].append("Repository URL is required for audit.")
        report["checks"].append({"name": "repo_present", "status": "fail"})

    if package_size > MAX_ARCHIVE_BYTES:
        report["errors"].append("Package exceeds maximum allowed size.")

    temp_dir = tempfile.mkdtemp(prefix="submission_audit_")
    archive_path = os.path.join(temp_dir, "package")
    repo_dir = None
    repo_commit = None

    try:
        if repo_url:
            try:
                repo_dir, repo_commit = _clone_repo(repo_url, repo_ref, temp_dir)
                report["checks"].append({"name": "repo_clone", "status": "pass"})
            except Exception as exc:
                report["errors"].append(f"Repo clone failed: {exc}")
                report["checks"].append({"name": "repo_clone", "status": "fail"})

        if repo_dir:
            repo_files = []
            for root, _, files in os.walk(repo_dir):
                if "/.git" in root:
                    continue
                for filename in files:
                    repo_files.append(os.path.relpath(os.path.join(root, filename), repo_dir))
            lowered_repo = [name.lower() for name in repo_files]
            for required in REPO_REQUIRED_FILES:
                if not any(item.endswith(required) for item in lowered_repo):
                    report["errors"].append(f"Missing required file: {required}")
                    report["checks"].append({"name": f"required_{required}", "status": "fail"})
                else:
                    report["checks"].append({"name": f"required_{required}", "status": "pass"})

            if any(name.lower().endswith((".env", ".env.local", ".env.production")) for name in lowered_repo):
                report["errors"].append("Environment files (.env) must not be included.")

            if any("/node_modules/" in name.lower() or name.lower().startswith("node_modules/") for name in lowered_repo):
                report["warnings"].append("node_modules found. Please remove dependencies before packaging.")

            if any("/venv/" in name.lower() or name.lower().startswith("venv/") for name in lowered_repo):
                report["warnings"].append("venv found. Please remove virtual environments before packaging.")

            secret_hits = _scan_repo_for_secrets(repo_dir)
            if secret_hits:
                report["errors"].append("Potential secrets detected in repository files.")
                report["checks"].append({"name": "secret_scan", "status": "fail", "files": secret_hits[:10]})
            else:
                report["checks"].append({"name": "secret_scan", "status": "pass"})

            # create archive for delivery
            snapshot_path = _archive_repo(repo_dir, temp_dir)
            snapshot_sha = _sha256_file(snapshot_path)
            snapshot_size = os.path.getsize(snapshot_path)

            archive_key = None
            archive_url = None
            if snapshot_size > MAX_ARCHIVE_BYTES:
                report["errors"].append("Repository snapshot exceeds maximum allowed size.")
                report["checks"].append(
                    {"name": "repo_archive_size", "status": "fail", "bytes": snapshot_size}
                )
            else:
                report["checks"].append(
                    {"name": "repo_archive_size", "status": "pass", "bytes": snapshot_size}
                )
                try:
                    owner_id = submission.get("seller_id") or "audit"
                    filename = f"{submission.get('title', 'repo')}.zip"
                    archive_key = build_object_key("package", filename, owner_id)
                    client = get_s3_client()
                    client.upload_file(
                        snapshot_path,
                        settings.R2_BUCKET,
                        archive_key,
                        ExtraArgs={"ContentType": "application/zip"},
                    )
                    archive_url = build_public_url(archive_key) or archive_key
                    report["checks"].append({"name": "repo_archive_upload", "status": "pass"})
                except Exception as exc:
                    report["errors"].append(f"Repo archive upload failed: {exc}")
                    report["checks"].append({"name": "repo_archive_upload", "status": "fail"})

            report["repo_snapshot"] = {
                "archive_path": snapshot_path,
                "archive_sha256": snapshot_sha,
                "commit_sha": repo_commit,
                "archive_key": archive_key,
                "archive_url": archive_url,
            }

        if package_url:
            download_url = package_url
            if not package_url.startswith(("http://", "https://")):
                download_url = generate_presigned_get(package_url, expires_in=300)

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
    audit_run_id: Optional[str] = None
    async with async_session_maker() as session:
        submission = await session.get(ProjectSubmission, submission_id)
        if not submission:
            return
        if submission.status in ("auditing", "approved", "rejected", "published"):
            return

        audit_run = AuditRun(
            submission_id=submission.id,
            status="running",
            started_at=_now(),
            pipeline_version=submission.audit_plan_version or "gsd-v1",
        )
        session.add(audit_run)

        submission.status = "auditing"
        submission.audit_started_at = _now()
        await session.commit()
        await session.refresh(audit_run)
        audit_run_id = audit_run.id

        submission_data = {
            "package_url": submission.package_url,
            "package_size_bytes": submission.package_size_bytes,
            "repo_url": submission.repo_url,
            "repo_ref": submission.repo_ref,
            "seller_id": submission.seller_id,
            "title": submission.title,
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

        audit_run = await session.get(AuditRun, audit_run_id) if audit_run_id else None

        submission.audit_report = report
        submission.audit_score = report.get("score")
        submission.audit_completed_at = _now()
        submission.failure_reason = "; ".join(report.get("errors", [])) if report.get("errors") else None
        submission.status = report.get("status", "rejected")

        if audit_run:
            audit_run.report = report
            audit_run.score = report.get("score")
            audit_run.completed_at = _now()
            audit_run.status = "passed" if submission.status == "approved" else "failed"

        if submission.status == "approved" and report.get("repo_snapshot"):
            snapshot_meta = report.get("repo_snapshot", {})
            snapshot = RepoSnapshot(
                submission_id=submission.id,
                repo_url=submission.repo_url or "",
                repo_ref=submission.repo_ref,
                commit_sha=snapshot_meta.get("commit_sha"),
                archive_url=snapshot_meta.get("archive_url"),
                archive_sha256=snapshot_meta.get("archive_sha256"),
            )
            session.add(snapshot)
            await session.flush()

            delivery = DeliveryArtifact(
                submission_id=submission.id,
                product_id=submission.product_id,
                snapshot_id=snapshot.id,
                artifact_url=snapshot_meta.get("archive_url"),
                artifact_sha256=snapshot_meta.get("archive_sha256"),
                status="ready",
            )
            session.add(delivery)

            submission.repo_commit_sha = snapshot_meta.get("commit_sha")
            if submission.brain_opt_in:
                submission.brain_ingest_status = "queued"

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
