"""Fail-closed authentication for the personal dashboard control plane."""

from __future__ import annotations

import os
import re
from hmac import compare_digest
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Header, HTTPException

MINIMUM_ADMIN_TOKEN_LENGTH = 32
HOSTNAME_PATTERN = re.compile(
    r"(?=.{1,253}\Z)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
)


def require_billing_identity() -> tuple[str, str]:
    """Return a configured checkout identity and trusted frontend origin."""
    email = os.getenv("AI_DASHBOARD_BILLING_EMAIL", "").strip()
    local, separator, domain = email.rpartition("@")
    valid_email = (
        separator == "@"
        and bool(local)
        and "." in domain
        and "@" not in local
        and "@" not in domain
        and not local.startswith(".")
        and not local.endswith(".")
        and ".." not in local
        and not domain.startswith(".")
        and not domain.endswith(".")
        and ".." not in domain
        and len(email) <= 254
        and not any(character.isspace() for character in email)
    )

    configured_origin = os.getenv("AI_DASHBOARD_FRONTEND_ORIGIN", "").strip()
    try:
        origin = urlsplit(configured_origin)
        _ = origin.port
    except ValueError:
        origin = urlsplit("")
    local_http = origin.scheme == "http" and origin.hostname in {"127.0.0.1", "localhost"}
    valid_hostname = bool(HOSTNAME_PATTERN.fullmatch(origin.hostname or ""))
    valid_origin = (
        (origin.scheme == "https" or local_http)
        and valid_hostname
        and bool(origin.netloc)
        and origin.username is None
        and origin.password is None
        and origin.path in {"", "/"}
        and not origin.query
        and not origin.fragment
    )

    if not valid_email or not valid_origin:
        raise HTTPException(status_code=503, detail="Billing identity is not configured")

    return email, configured_origin.rstrip("/")


def require_admin(authorization: Annotated[str | None, Header()] = None) -> None:
    """Require the configured bearer token before privileged dashboard access."""
    expected = os.getenv("AI_DASHBOARD_ADMIN_TOKEN", "").strip()
    if len(expected) < MINIMUM_ADMIN_TOKEN_LENGTH:
        raise HTTPException(status_code=503, detail="Dashboard administration is disabled")

    scheme, separator, credential = (authorization or "").partition(" ")
    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not credential
        or not compare_digest(credential, expected)
    ):
        raise HTTPException(status_code=401, detail="Valid administrator authentication is required")
