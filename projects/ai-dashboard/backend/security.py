"""Fail-closed authentication for the personal dashboard control plane."""

import os
from hmac import compare_digest
from typing import Annotated

from fastapi import Header, HTTPException

MINIMUM_ADMIN_TOKEN_LENGTH = 32


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
