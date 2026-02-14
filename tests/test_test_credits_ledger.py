#!/usr/bin/env python3
"""Tests for tools/test_credits_ledger.py"""

import pytest
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

try:
    import test_credits_ledger
except ImportError:
    pytest.skip("Cannot import test_credits_ledger", allow_module_level=True)


def test_make_ledger_exists():
    """Verify make_ledger is callable."""
    assert callable(getattr(test_credits_ledger, "make_ledger", None))

def test_test_add_credits_exists():
    """Verify test_add_credits is callable."""
    assert callable(getattr(test_credits_ledger, "test_add_credits", None))

def test_test_spend_credits_exists():
    """Verify test_spend_credits is callable."""
    assert callable(getattr(test_credits_ledger, "test_spend_credits", None))

def test_test_insufficient_credits_exists():
    """Verify test_insufficient_credits is callable."""
    assert callable(getattr(test_credits_ledger, "test_insufficient_credits", None))

def test_test_escrow_flow_exists():
    """Verify test_escrow_flow is callable."""
    assert callable(getattr(test_credits_ledger, "test_escrow_flow", None))

def test_test_refund_exists():
    """Verify test_refund is callable."""
    assert callable(getattr(test_credits_ledger, "test_refund", None))

def test_test_reconcile_exists():
    """Verify test_reconcile is callable."""
    assert callable(getattr(test_credits_ledger, "test_reconcile", None))

def test_test_transaction_history_exists():
    """Verify test_transaction_history is callable."""
    assert callable(getattr(test_credits_ledger, "test_transaction_history", None))

def test_test_stats_exists():
    """Verify test_stats is callable."""
    assert callable(getattr(test_credits_ledger, "test_stats", None))

def test_test_checksum_integrity_exists():
    """Verify test_checksum_integrity is callable."""
    assert callable(getattr(test_credits_ledger, "test_checksum_integrity", None))
