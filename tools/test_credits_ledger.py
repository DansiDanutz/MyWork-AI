#!/usr/bin/env python3
"""Tests for credits_ledger.py — Phase 8 Payment System."""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add tools to path
sys.path.insert(0, os.path.dirname(__file__))
from credits_ledger import CreditsLedger, TxType, TxStatus, LedgerEntry


def make_ledger(tmp):
    """Create a ledger in a temp dir."""
    d = Path(tmp) / "ledger"
    return CreditsLedger(ledger_dir=d)


def test_add_credits():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        entry = ledger.add_credits("user1", 100.0, "stripe", stripe_id="ch_123")
        assert entry.amount == 100.0
        assert entry.tx_type == TxType.CREDIT_PURCHASE
        assert ledger.get_balance("user1") == 100.0
        print("✅ test_add_credits")


def test_spend_credits():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("buyer", 500.0)
        entry = ledger.spend_credits("buyer", 200.0, "order-1", seller_id="seller1", item_name="AI Tool")
        assert entry.amount == -200.0
        assert ledger.get_balance("buyer") == 300.0
        print("✅ test_spend_credits")


def test_insufficient_credits():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("user1", 50.0)
        try:
            ledger.spend_credits("user1", 100.0, "order-1")
            assert False, "Should have raised"
        except ValueError as e:
            assert "Insufficient" in str(e)
        print("✅ test_insufficient_credits")


def test_escrow_flow():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("buyer", 1000.0)
        ledger.spend_credits("buyer", 399.0, "order-42", seller_id="seller1", item_name="SportsAI")
        
        # Seller balance should be 0 (escrow pending)
        assert ledger.get_balance("seller1") == 0.0
        
        # Pending escrows should have 1
        pending = ledger.get_pending_escrows()
        assert len(pending) == 1
        assert pending[0]["order_id"] == "order-42"
        
        # Release escrow
        release = ledger.release_escrow("order-42")
        assert release is not None
        assert ledger.get_balance("seller1") == 399.0
        
        # Idempotent: release again should return None
        assert ledger.release_escrow("order-42") is None
        print("✅ test_escrow_flow")


def test_refund():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("buyer", 500.0)
        ledger.spend_credits("buyer", 200.0, "order-5", seller_id="seller1")
        
        assert ledger.get_balance("buyer") == 300.0
        
        # Refund
        refund = ledger.refund("buyer", 200.0, "order-5", reason="Product issue")
        assert refund.amount == 200.0
        assert ledger.get_balance("buyer") == 500.0
        
        # Escrow should be cancelled
        escrow = ledger._get_escrow("order-5")
        assert escrow["cancelled"] == True
        print("✅ test_refund")


def test_reconcile():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("user1", 100.0)
        ledger.add_credits("user2", 200.0)
        ledger.spend_credits("user1", 50.0, "o1", seller_id="user2")
        ledger.release_escrow("o1")
        
        result = ledger.reconcile()
        assert result["status"] == "ok"
        assert len(result["mismatches"]) == 0
        print("✅ test_reconcile")


def test_transaction_history():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("user1", 100.0)
        ledger.add_credits("user1", 200.0)
        
        txs = ledger.get_transactions("user1")
        assert len(txs) == 2
        assert txs[0]["amount"] == 100.0
        assert txs[1]["amount"] == 200.0
        print("✅ test_transaction_history")


def test_stats():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        ledger.add_credits("u1", 100.0)
        ledger.add_credits("u2", 200.0)
        ledger.spend_credits("u1", 50.0, "o1")
        
        s = ledger.stats()
        assert s["transactions"] == 3
        assert s["users"] == 2
        assert s["total_credits_sold"] == 300.0
        assert s["total_spent"] == 50.0
        print("✅ test_stats")


def test_checksum_integrity():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        entry = ledger.add_credits("user1", 100.0)
        
        # Verify checksum validates
        loaded = LedgerEntry.from_dict(entry.to_dict())
        expected = loaded._compute_checksum()
        assert loaded.checksum == expected
        print("✅ test_checksum_integrity")


def test_bonus_credits():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = make_ledger(tmp)
        entry = ledger.add_credits("user1", 50.0, source="bonus", description="Welcome bonus")
        assert entry.tx_type == TxType.BONUS
        assert ledger.get_balance("user1") == 50.0
        print("✅ test_bonus_credits")


if __name__ == "__main__":
    test_add_credits()
    test_spend_credits()
    test_insufficient_credits()
    test_escrow_flow()
    test_refund()
    test_reconcile()
    test_transaction_history()
    test_stats()
    test_checksum_integrity()
    test_bonus_credits()
    print("\n🎉 All 10 credits ledger tests passed!")
