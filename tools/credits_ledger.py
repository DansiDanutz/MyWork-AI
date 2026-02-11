#!/usr/bin/env python3
"""
Credits Ledger — Phase 8: Payments, Credits, Escrow
Single source of truth for all financial transactions in MyWork-AI marketplace.

Supports:
- Credit purchases (Stripe or direct)
- Credit spending (marketplace purchases)
- Escrow holds and releases
- Refunds and reversals
- Full audit trail
"""

import json
import os
import time
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from typing import Optional

# ─── Configuration ───────────────────────────────────────────────
LEDGER_DIR = Path(os.environ.get("MYWORK_LEDGER_DIR", Path.home() / ".mywork" / "ledger"))
ESCROW_DAYS = int(os.environ.get("MYWORK_ESCROW_DAYS", "7"))


class TxType(str, Enum):
    CREDIT_PURCHASE = "credit_purchase"      # User buys credits (Stripe/other)
    CREDIT_SPEND = "credit_spend"            # User spends credits on marketplace
    ESCROW_HOLD = "escrow_hold"              # Credits held in escrow for seller
    ESCROW_RELEASE = "escrow_release"        # Escrow released to seller
    REFUND = "refund"                        # Refund to buyer
    REVERSAL = "reversal"                    # Admin reversal
    BONUS = "bonus"                          # Promotional credits
    PAYOUT = "payout"                        # Seller withdraws credits


class TxStatus(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    REVERSED = "reversed"


class LedgerEntry:
    """Single ledger transaction."""
    
    def __init__(self, user_id: str, tx_type: TxType, amount: float,
                 description: str = "", order_id: str = "",
                 related_tx: str = "", metadata: Optional[dict] = None):
        self.tx_id = str(uuid.uuid4())
        self.user_id = user_id
        self.tx_type = tx_type
        self.amount = amount  # positive = credit, negative = debit
        self.description = description
        self.order_id = order_id
        self.related_tx = related_tx
        self.status = TxStatus.COMPLETED
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Integrity checksum for tamper detection."""
        data = f"{self.tx_id}:{self.user_id}:{self.amount}:{self.tx_type}:{self.created_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "user_id": self.user_id,
            "tx_type": self.tx_type.value,
            "amount": self.amount,
            "description": self.description,
            "order_id": self.order_id,
            "related_tx": self.related_tx,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LedgerEntry":
        entry = cls.__new__(cls)
        entry.tx_id = d["tx_id"]
        entry.user_id = d["user_id"]
        entry.tx_type = TxType(d["tx_type"])
        entry.amount = d["amount"]
        entry.description = d.get("description", "")
        entry.order_id = d.get("order_id", "")
        entry.related_tx = d.get("related_tx", "")
        entry.status = TxStatus(d["status"])
        entry.metadata = d.get("metadata", {})
        entry.created_at = d["created_at"]
        entry.checksum = d["checksum"]
        return entry


class CreditsLedger:
    """
    File-backed credits ledger with full audit trail.
    
    Every transaction is append-only with checksums for integrity.
    Supports escrow, refunds, and reconciliation.
    """
    
    def __init__(self, ledger_dir: Optional[Path] = None):
        self.ledger_dir = ledger_dir or LEDGER_DIR
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.ledger_dir / "transactions.jsonl"
        self.balances_file = self.ledger_dir / "balances.json"
        self.escrow_file = self.ledger_dir / "escrow.json"
    
    # ─── Core Operations ─────────────────────────────────────────
    
    def add_credits(self, user_id: str, amount: float, source: str = "stripe",
                    stripe_id: str = "", description: str = "") -> LedgerEntry:
        """Add credits to user account (purchase or bonus)."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        
        tx_type = TxType.CREDIT_PURCHASE if source != "bonus" else TxType.BONUS
        entry = LedgerEntry(
            user_id=user_id,
            tx_type=tx_type,
            amount=amount,
            description=description or f"Credit purchase via {source}",
            metadata={"source": source, "stripe_id": stripe_id} if stripe_id else {"source": source},
        )
        self._append_tx(entry)
        self._update_balance(user_id, amount)
        return entry
    
    def spend_credits(self, user_id: str, amount: float, order_id: str,
                      seller_id: str = "", item_name: str = "") -> LedgerEntry:
        """Spend credits on a marketplace purchase. Creates escrow hold for seller."""
        if amount <= 0:
            raise ValueError("Spend amount must be positive")
        
        balance = self.get_balance(user_id)
        if balance < amount:
            raise ValueError(f"Insufficient credits: have {balance}, need {amount}")
        
        # Debit buyer
        spend_entry = LedgerEntry(
            user_id=user_id,
            tx_type=TxType.CREDIT_SPEND,
            amount=-amount,
            description=f"Purchase: {item_name}" if item_name else "Marketplace purchase",
            order_id=order_id,
            metadata={"seller_id": seller_id, "item_name": item_name},
        )
        self._append_tx(spend_entry)
        self._update_balance(user_id, -amount)
        
        # Create escrow hold for seller
        if seller_id:
            escrow_entry = LedgerEntry(
                user_id=seller_id,
                tx_type=TxType.ESCROW_HOLD,
                amount=amount,
                description=f"Escrow hold for order {order_id}",
                order_id=order_id,
                related_tx=spend_entry.tx_id,
                metadata={"buyer_id": user_id, "release_after_days": ESCROW_DAYS},
            )
            escrow_entry.status = TxStatus.PENDING
            self._append_tx(escrow_entry)
            self._add_escrow(escrow_entry)
        
        return spend_entry
    
    def release_escrow(self, order_id: str) -> Optional[LedgerEntry]:
        """Release escrow funds to seller after escrow period."""
        escrow = self._get_escrow(order_id)
        if not escrow:
            return None
        if escrow.get("released"):
            return None  # Idempotent: already released
        
        seller_id = escrow["seller_id"]
        amount = escrow["amount"]
        
        release_entry = LedgerEntry(
            user_id=seller_id,
            tx_type=TxType.ESCROW_RELEASE,
            amount=amount,
            description=f"Escrow released for order {order_id}",
            order_id=order_id,
            related_tx=escrow["escrow_tx_id"],
        )
        self._append_tx(release_entry)
        self._update_balance(seller_id, amount)
        self._mark_escrow_released(order_id)
        return release_entry
    
    def refund(self, user_id: str, amount: float, order_id: str,
               reason: str = "") -> LedgerEntry:
        """Refund credits to buyer. Cancels escrow if pending."""
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        # Cancel escrow if exists
        escrow = self._get_escrow(order_id)
        if escrow and not escrow.get("released"):
            self._mark_escrow_released(order_id, cancelled=True)
        
        refund_entry = LedgerEntry(
            user_id=user_id,
            tx_type=TxType.REFUND,
            amount=amount,
            description=reason or f"Refund for order {order_id}",
            order_id=order_id,
        )
        self._append_tx(refund_entry)
        self._update_balance(user_id, amount)
        return refund_entry
    
    # ─── Queries ─────────────────────────────────────────────────
    
    def get_balance(self, user_id: str) -> float:
        """Get current credit balance for user."""
        balances = self._load_balances()
        return balances.get(user_id, 0.0)
    
    def get_transactions(self, user_id: str, limit: int = 50) -> list[dict]:
        """Get transaction history for user."""
        txs = []
        if not self.ledger_file.exists():
            return txs
        with open(self.ledger_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                tx = json.loads(line)
                if tx["user_id"] == user_id:
                    txs.append(tx)
        return txs[-limit:]
    
    def get_pending_escrows(self) -> list[dict]:
        """Get all pending escrow holds (for scheduled release job)."""
        escrows = self._load_escrows()
        return [e for e in escrows.values() if not e.get("released") and not e.get("cancelled")]
    
    def get_releasable_escrows(self) -> list[dict]:
        """Get escrows ready for release (past escrow period)."""
        now = time.time()
        pending = self.get_pending_escrows()
        releasable = []
        for e in pending:
            created = datetime.fromisoformat(e["created_at"]).timestamp()
            if now - created >= ESCROW_DAYS * 86400:
                releasable.append(e)
        return releasable
    
    def reconcile(self) -> dict:
        """Verify ledger integrity: recompute all balances from transactions."""
        if not self.ledger_file.exists():
            return {"status": "ok", "users": 0, "transactions": 0, "mismatches": []}
        
        computed = {}
        tx_count = 0
        integrity_errors = []
        
        with open(self.ledger_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                tx = json.loads(line)
                tx_count += 1
                uid = tx["user_id"]
                
                # Only count completed transactions toward balance
                if tx["status"] in ("completed",):
                    computed[uid] = computed.get(uid, 0.0) + tx["amount"]
                
                # Verify checksum
                entry = LedgerEntry.from_dict(tx)
                expected = entry._compute_checksum()
                if tx["checksum"] != expected:
                    integrity_errors.append({"tx_id": tx["tx_id"], "error": "checksum_mismatch"})
        
        # Compare with stored balances
        stored = self._load_balances()
        mismatches = []
        all_users = set(list(computed.keys()) + list(stored.keys()))
        for uid in all_users:
            c = round(computed.get(uid, 0.0), 2)
            s = round(stored.get(uid, 0.0), 2)
            if c != s:
                mismatches.append({"user_id": uid, "computed": c, "stored": s})
        
        return {
            "status": "ok" if not mismatches and not integrity_errors else "mismatch",
            "users": len(all_users),
            "transactions": tx_count,
            "mismatches": mismatches,
            "integrity_errors": integrity_errors,
        }
    
    def stats(self) -> dict:
        """Get ledger statistics."""
        if not self.ledger_file.exists():
            return {"transactions": 0, "users": 0, "total_credits_sold": 0, "total_spent": 0}
        
        users = set()
        total_sold = 0.0
        total_spent = 0.0
        tx_count = 0
        
        with open(self.ledger_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                tx = json.loads(line)
                tx_count += 1
                users.add(tx["user_id"])
                if tx["tx_type"] == "credit_purchase":
                    total_sold += tx["amount"]
                elif tx["tx_type"] == "credit_spend":
                    total_spent += abs(tx["amount"])
        
        return {
            "transactions": tx_count,
            "users": len(users),
            "total_credits_sold": round(total_sold, 2),
            "total_spent": round(total_spent, 2),
        }
    
    # ─── Internal ────────────────────────────────────────────────
    
    def _append_tx(self, entry: LedgerEntry):
        with open(self.ledger_file, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")
    
    def _load_balances(self) -> dict:
        if not self.balances_file.exists():
            return {}
        return json.loads(self.balances_file.read_text())
    
    def _update_balance(self, user_id: str, delta: float):
        balances = self._load_balances()
        balances[user_id] = round(balances.get(user_id, 0.0) + delta, 2)
        self.balances_file.write_text(json.dumps(balances, indent=2))
    
    def _load_escrows(self) -> dict:
        if not self.escrow_file.exists():
            return {}
        return json.loads(self.escrow_file.read_text())
    
    def _add_escrow(self, entry: LedgerEntry):
        escrows = self._load_escrows()
        escrows[entry.order_id] = {
            "order_id": entry.order_id,
            "seller_id": entry.user_id,
            "buyer_id": entry.metadata.get("buyer_id", ""),
            "amount": entry.amount,
            "escrow_tx_id": entry.tx_id,
            "created_at": entry.created_at,
            "released": False,
            "cancelled": False,
        }
        self.escrow_file.write_text(json.dumps(escrows, indent=2))
    
    def _get_escrow(self, order_id: str) -> Optional[dict]:
        escrows = self._load_escrows()
        return escrows.get(order_id)
    
    def _mark_escrow_released(self, order_id: str, cancelled: bool = False):
        escrows = self._load_escrows()
        if order_id in escrows:
            escrows[order_id]["released"] = not cancelled
            escrows[order_id]["cancelled"] = cancelled
            escrows[order_id]["released_at"] = datetime.now(timezone.utc).isoformat()
            self.escrow_file.write_text(json.dumps(escrows, indent=2))


# ─── CLI Interface ───────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MyWork-AI Credits Ledger")
    sub = parser.add_subparsers(dest="command")
    
    # balance
    bal = sub.add_parser("balance", help="Check user balance")
    bal.add_argument("user_id")
    
    # add-credits
    add = sub.add_parser("add-credits", help="Add credits to user")
    add.add_argument("user_id")
    add.add_argument("amount", type=float)
    add.add_argument("--source", default="manual")
    add.add_argument("--description", default="")
    
    # spend
    spend = sub.add_parser("spend", help="Spend credits")
    spend.add_argument("user_id")
    spend.add_argument("amount", type=float)
    spend.add_argument("order_id")
    spend.add_argument("--seller", default="")
    spend.add_argument("--item", default="")
    
    # release-escrow
    rel = sub.add_parser("release-escrow", help="Release escrow")
    rel.add_argument("order_id")
    
    # refund
    ref = sub.add_parser("refund", help="Refund credits")
    ref.add_argument("user_id")
    ref.add_argument("amount", type=float)
    ref.add_argument("order_id")
    ref.add_argument("--reason", default="")
    
    # history
    hist = sub.add_parser("history", help="Transaction history")
    hist.add_argument("user_id")
    hist.add_argument("--limit", type=int, default=20)
    
    # reconcile
    sub.add_parser("reconcile", help="Verify ledger integrity")
    
    # stats
    sub.add_parser("stats", help="Ledger statistics")
    
    # pending-escrows
    sub.add_parser("pending-escrows", help="List pending escrows")
    
    # release-due
    sub.add_parser("release-due", help="Release all due escrows")
    
    args = parser.parse_args()
    ledger = CreditsLedger()
    
    if args.command == "balance":
        bal = ledger.get_balance(args.user_id)
        print(f"Balance for {args.user_id}: {bal} credits")
    
    elif args.command == "add-credits":
        entry = ledger.add_credits(args.user_id, args.amount, args.source, description=args.description)
        print(f"✅ Added {args.amount} credits → {entry.tx_id}")
        print(f"   New balance: {ledger.get_balance(args.user_id)}")
    
    elif args.command == "spend":
        entry = ledger.spend_credits(args.user_id, args.amount, args.order_id, args.seller, args.item)
        print(f"✅ Spent {args.amount} credits → {entry.tx_id}")
        print(f"   New balance: {ledger.get_balance(args.user_id)}")
    
    elif args.command == "release-escrow":
        entry = ledger.release_escrow(args.order_id)
        if entry:
            print(f"✅ Escrow released → {entry.tx_id}")
        else:
            print("⚠️ No pending escrow found for this order")
    
    elif args.command == "refund":
        entry = ledger.refund(args.user_id, args.amount, args.order_id, args.reason)
        print(f"✅ Refunded {args.amount} credits → {entry.tx_id}")
        print(f"   New balance: {ledger.get_balance(args.user_id)}")
    
    elif args.command == "history":
        txs = ledger.get_transactions(args.user_id, args.limit)
        if not txs:
            print("No transactions found")
        for tx in txs:
            sign = "+" if tx["amount"] > 0 else ""
            print(f"  {tx['created_at'][:19]}  {sign}{tx['amount']:>8.2f}  {tx['tx_type']:<20}  {tx['description']}")
    
    elif args.command == "reconcile":
        result = ledger.reconcile()
        print(f"Status: {result['status']}")
        print(f"Users: {result['users']}, Transactions: {result['transactions']}")
        if result["mismatches"]:
            print("⚠️ MISMATCHES:")
            for m in result["mismatches"]:
                print(f"  {m['user_id']}: stored={m['stored']}, computed={m['computed']}")
        if result.get("integrity_errors"):
            print("🚨 INTEGRITY ERRORS:")
            for e in result["integrity_errors"]:
                print(f"  {e['tx_id']}: {e['error']}")
        if not result["mismatches"] and not result.get("integrity_errors"):
            print("✅ All balances reconcile correctly")
    
    elif args.command == "stats":
        s = ledger.stats()
        print(f"📊 Ledger Stats:")
        print(f"   Transactions: {s['transactions']}")
        print(f"   Users: {s['users']}")
        print(f"   Total credits sold: {s['total_credits_sold']}")
        print(f"   Total spent: {s['total_spent']}")
    
    elif args.command == "pending-escrows":
        pending = ledger.get_pending_escrows()
        if not pending:
            print("No pending escrows")
        for e in pending:
            print(f"  Order {e['order_id']}: {e['amount']} credits → seller {e['seller_id']} (since {e['created_at'][:10]})")
    
    elif args.command == "release-due":
        due = ledger.get_releasable_escrows()
        if not due:
            print("No escrows due for release")
        for e in due:
            entry = ledger.release_escrow(e["order_id"])
            if entry:
                print(f"✅ Released {e['amount']} credits to {e['seller_id']} (order {e['order_id']})")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
