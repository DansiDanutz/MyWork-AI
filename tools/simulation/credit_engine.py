#!/usr/bin/env python3
"""
Virtual Credit System for MyWork-AI
Manages virtual balances, transactions, and reporting
"""
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

class TransactionType(Enum):
    TOP_UP = "top_up"
    SPEND = "spend"
    TRANSFER = "transfer"
    COMMISSION = "commission"
    REFUND = "refund"
    WITHDRAWAL = "withdrawal"
    BONUS = "bonus"
    PENALTY = "penalty"

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Transaction:
    """Individual transaction record"""
    transaction_id: str
    timestamp: str
    user_id: str
    transaction_type: TransactionType
    amount: float
    balance_before: float
    balance_after: float
    status: TransactionStatus
    description: str
    metadata: Dict[str, Any]
    related_user_id: Optional[str] = None  # For transfers, commissions
    reference_id: Optional[str] = None     # Order ID, product ID, etc.

@dataclass 
class UserBalance:
    """User balance and credit information"""
    user_id: str
    balance: float
    total_earned: float
    total_spent: float
    total_transferred_in: float
    total_transferred_out: float
    total_commissions: float
    total_refunds: float
    created_at: str
    last_updated: str
    is_frozen: bool = False
    credit_limit: float = 0.0

class CreditEngine:
    """Main credit management system"""
    
    def __init__(self, max_balance: float = 100000.0, min_transaction: float = 0.01):
        self.balances: Dict[str, UserBalance] = {}
        self.transactions: List[Transaction] = []
        self.max_balance = max_balance
        self.min_transaction = min_transaction
        self.total_credits_issued = 0.0
        self.total_credits_burned = 0.0
        
    def create_user_balance(self, user_id: str, initial_balance: float = 0.0) -> bool:
        """Create a new user balance record"""
        if user_id in self.balances:
            return False  # User already exists
            
        if initial_balance < 0:
            return False  # No negative initial balances
            
        timestamp = datetime.now().isoformat()
        
        self.balances[user_id] = UserBalance(
            user_id=user_id,
            balance=initial_balance,
            total_earned=initial_balance,
            total_spent=0.0,
            total_transferred_in=0.0,
            total_transferred_out=0.0,
            total_commissions=0.0,
            total_refunds=0.0,
            created_at=timestamp,
            last_updated=timestamp
        )
        
        # If initial balance > 0, create an initial transaction
        if initial_balance > 0:
            self.total_credits_issued += initial_balance
            self._create_transaction(
                user_id=user_id,
                transaction_type=TransactionType.TOP_UP,
                amount=initial_balance,
                balance_before=0.0,
                balance_after=initial_balance,
                description="Initial balance",
                metadata={"source": "system_init"}
            )
            
        return True
    
    def _create_transaction(self, user_id: str, transaction_type: TransactionType, 
                          amount: float, balance_before: float, balance_after: float,
                          description: str, metadata: Dict[str, Any] = None,
                          related_user_id: str = None, reference_id: str = None,
                          status: TransactionStatus = TransactionStatus.COMPLETED) -> str:
        """Create a new transaction record"""
        transaction_id = str(uuid.uuid4())
        
        transaction = Transaction(
            transaction_id=transaction_id,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status=status,
            description=description,
            metadata=metadata or {},
            related_user_id=related_user_id,
            reference_id=reference_id
        )
        
        self.transactions.append(transaction)
        return transaction_id
    
    def _validate_transaction(self, user_id: str, amount: float, 
                            transaction_type: TransactionType) -> Tuple[bool, str]:
        """Validate if a transaction can be performed"""
        if user_id not in self.balances:
            return False, f"User {user_id} not found"
            
        if amount < self.min_transaction:
            return False, f"Amount {amount} below minimum {self.min_transaction}"
            
        if amount <= 0:
            return False, "Amount must be positive"
            
        user_balance = self.balances[user_id]
        
        if user_balance.is_frozen:
            return False, f"User {user_id} account is frozen"
        
        # Check for debit operations
        if transaction_type in [TransactionType.SPEND, TransactionType.TRANSFER, TransactionType.WITHDRAWAL]:
            if user_balance.balance < amount:
                return False, f"Insufficient balance. Required: {amount}, Available: {user_balance.balance}"
                
        # Check for credit operations that would exceed max balance
        elif transaction_type in [TransactionType.TOP_UP, TransactionType.COMMISSION, TransactionType.REFUND]:
            if user_balance.balance + amount > self.max_balance:
                return False, f"Transaction would exceed maximum balance {self.max_balance}"
        
        return True, "Valid"
    
    def top_up(self, user_id: str, amount: float, source: str = "manual", 
              reference_id: str = None) -> Tuple[bool, str]:
        """Add credits to user balance"""
        valid, message = self._validate_transaction(user_id, amount, TransactionType.TOP_UP)
        if not valid:
            return False, message
            
        user_balance = self.balances[user_id]
        balance_before = user_balance.balance
        balance_after = balance_before + amount
        
        # Update balance
        user_balance.balance = balance_after
        user_balance.total_earned += amount
        user_balance.last_updated = datetime.now().isoformat()
        
        # Track system totals
        self.total_credits_issued += amount
        
        # Create transaction record
        transaction_id = self._create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.TOP_UP,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"Top up from {source}",
            metadata={"source": source},
            reference_id=reference_id
        )
        
        return True, transaction_id
    
    def spend(self, user_id: str, amount: float, description: str = "Purchase",
             reference_id: str = None) -> Tuple[bool, str]:
        """Deduct credits from user balance"""
        valid, message = self._validate_transaction(user_id, amount, TransactionType.SPEND)
        if not valid:
            return False, message
            
        user_balance = self.balances[user_id]
        balance_before = user_balance.balance
        balance_after = balance_before - amount
        
        # Update balance
        user_balance.balance = balance_after
        user_balance.total_spent += amount
        user_balance.last_updated = datetime.now().isoformat()
        
        # Track system totals
        self.total_credits_burned += amount
        
        # Create transaction record
        transaction_id = self._create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.SPEND,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            metadata={"category": "purchase"},
            reference_id=reference_id
        )
        
        return True, transaction_id
    
    def transfer(self, from_user_id: str, to_user_id: str, amount: float,
                description: str = "Transfer") -> Tuple[bool, str]:
        """Transfer credits between users"""
        if from_user_id == to_user_id:
            return False, "Cannot transfer to yourself"
            
        if to_user_id not in self.balances:
            return False, f"Recipient user {to_user_id} not found"
        
        # Validate sender can make the transfer
        valid, message = self._validate_transaction(from_user_id, amount, TransactionType.TRANSFER)
        if not valid:
            return False, message
            
        # Validate recipient can receive
        to_balance = self.balances[to_user_id]
        if to_balance.balance + amount > self.max_balance:
            return False, f"Transfer would exceed recipient's maximum balance"
        
        if to_balance.is_frozen:
            return False, f"Recipient account {to_user_id} is frozen"
        
        # Perform transfer
        from_balance = self.balances[from_user_id]
        from_before = from_balance.balance
        from_after = from_before - amount
        
        to_before = to_balance.balance
        to_after = to_before + amount
        
        # Update balances
        from_balance.balance = from_after
        from_balance.total_transferred_out += amount
        from_balance.last_updated = datetime.now().isoformat()
        
        to_balance.balance = to_after
        to_balance.total_transferred_in += amount
        to_balance.last_updated = datetime.now().isoformat()
        
        # Create transaction records for both users
        transfer_ref = str(uuid.uuid4())
        
        # Sender transaction
        sender_tx = self._create_transaction(
            user_id=from_user_id,
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            balance_before=from_before,
            balance_after=from_after,
            description=f"Transfer to {to_user_id}: {description}",
            metadata={"transfer_type": "outgoing", "transfer_ref": transfer_ref},
            related_user_id=to_user_id
        )
        
        # Recipient transaction  
        recipient_tx = self._create_transaction(
            user_id=to_user_id,
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            balance_before=to_before,
            balance_after=to_after,
            description=f"Transfer from {from_user_id}: {description}",
            metadata={"transfer_type": "incoming", "transfer_ref": transfer_ref},
            related_user_id=from_user_id
        )
        
        return True, transfer_ref
    
    def earn_commission(self, user_id: str, amount: float, source: str,
                       level: int = 1, reference_id: str = None) -> Tuple[bool, str]:
        """Award commission to user"""
        valid, message = self._validate_transaction(user_id, amount, TransactionType.COMMISSION)
        if not valid:
            return False, message
            
        user_balance = self.balances[user_id]
        balance_before = user_balance.balance
        balance_after = balance_before + amount
        
        # Update balance
        user_balance.balance = balance_after
        user_balance.total_commissions += amount
        user_balance.last_updated = datetime.now().isoformat()
        
        # Track system totals
        self.total_credits_issued += amount
        
        # Create transaction record
        transaction_id = self._create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.COMMISSION,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"Level {level} commission from {source}",
            metadata={"source": source, "level": level, "commission_type": "referral"},
            reference_id=reference_id
        )
        
        return True, transaction_id
    
    def refund(self, user_id: str, amount: float, reason: str,
              reference_id: str = None) -> Tuple[bool, str]:
        """Process a refund to user"""
        valid, message = self._validate_transaction(user_id, amount, TransactionType.REFUND)
        if not valid:
            return False, message
            
        user_balance = self.balances[user_id]
        balance_before = user_balance.balance
        balance_after = balance_before + amount
        
        # Update balance
        user_balance.balance = balance_after
        user_balance.total_refunds += amount
        user_balance.last_updated = datetime.now().isoformat()
        
        # Track system totals (refunds add back to circulation)
        self.total_credits_issued += amount
        
        # Create transaction record
        transaction_id = self._create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.REFUND,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=f"Refund: {reason}",
            metadata={"reason": reason, "refund_type": "purchase"},
            reference_id=reference_id
        )
        
        return True, transaction_id
    
    def get_balance(self, user_id: str) -> Optional[float]:
        """Get current user balance"""
        if user_id not in self.balances:
            return None
        return self.balances[user_id].balance
    
    def get_user_transactions(self, user_id: str, limit: int = None) -> List[Transaction]:
        """Get transaction history for a user"""
        user_transactions = [tx for tx in self.transactions if tx.user_id == user_id]
        user_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            user_transactions = user_transactions[:limit]
            
        return user_transactions
    
    def freeze_account(self, user_id: str, reason: str = "Administrative action") -> bool:
        """Freeze user account"""
        if user_id not in self.balances:
            return False
            
        self.balances[user_id].is_frozen = True
        self.balances[user_id].last_updated = datetime.now().isoformat()
        
        # Log the freeze action
        self._create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.PENALTY,
            amount=0.0,
            balance_before=self.balances[user_id].balance,
            balance_after=self.balances[user_id].balance,
            description=f"Account frozen: {reason}",
            metadata={"action": "freeze", "reason": reason}
        )
        
        return True
    
    def unfreeze_account(self, user_id: str, reason: str = "Administrative action") -> bool:
        """Unfreeze user account"""
        if user_id not in self.balances:
            return False
            
        self.balances[user_id].is_frozen = False
        self.balances[user_id].last_updated = datetime.now().isoformat()
        
        # Log the unfreeze action
        self._create_transaction(
            user_id=user_id,
            transaction_type=TransactionType.BONUS,
            amount=0.0,
            balance_before=self.balances[user_id].balance,
            balance_after=self.balances[user_id].balance,
            description=f"Account unfrozen: {reason}",
            metadata={"action": "unfreeze", "reason": reason}
        )
        
        return True
    
    def get_total_circulation(self) -> float:
        """Get total credits currently in circulation"""
        return sum(balance.balance for balance in self.balances.values())
    
    def get_top_earners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top earners by total earnings"""
        sorted_users = sorted(self.balances.values(), 
                            key=lambda x: x.total_earned, reverse=True)
        
        return [
            {
                "user_id": user.user_id,
                "total_earned": user.total_earned,
                "current_balance": user.balance,
                "total_commissions": user.total_commissions
            }
            for user in sorted_users[:limit]
        ]
    
    def get_transaction_volume(self, days: int = 7) -> Dict[str, Any]:
        """Get transaction volume for specified period"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()
        
        recent_transactions = [tx for tx in self.transactions 
                             if tx.timestamp >= cutoff_iso and tx.status == TransactionStatus.COMPLETED]
        
        volume_by_type = {}
        total_volume = 0.0
        transaction_count = len(recent_transactions)
        
        for tx in recent_transactions:
            tx_type = tx.transaction_type.value
            if tx_type not in volume_by_type:
                volume_by_type[tx_type] = {"count": 0, "volume": 0.0}
            
            volume_by_type[tx_type]["count"] += 1
            volume_by_type[tx_type]["volume"] += tx.amount
            total_volume += tx.amount
        
        return {
            "period_days": days,
            "total_transactions": transaction_count,
            "total_volume": round(total_volume, 2),
            "average_transaction_size": round(total_volume / transaction_count, 2) if transaction_count > 0 else 0,
            "volume_by_type": volume_by_type
        }
    
    def generate_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report"""
        total_users = len(self.balances)
        total_circulation = self.get_total_circulation()
        
        # Calculate various stats
        active_users = sum(1 for b in self.balances.values() if b.balance > 0)
        frozen_accounts = sum(1 for b in self.balances.values() if b.is_frozen)
        
        total_spent = sum(b.total_spent for b in self.balances.values())
        total_transferred = sum(b.total_transferred_out for b in self.balances.values())
        total_commissions = sum(b.total_commissions for b in self.balances.values())
        total_refunds = sum(b.total_refunds for b in self.balances.values())
        
        # Transaction stats
        completed_transactions = [tx for tx in self.transactions 
                                if tx.status == TransactionStatus.COMPLETED]
        
        transaction_types = {}
        for tx in completed_transactions:
            tx_type = tx.transaction_type.value
            if tx_type not in transaction_types:
                transaction_types[tx_type] = 0
            transaction_types[tx_type] += 1
        
        return {
            "system_overview": {
                "total_users": total_users,
                "active_users": active_users,
                "frozen_accounts": frozen_accounts,
                "total_circulation": round(total_circulation, 2),
                "credits_issued": round(self.total_credits_issued, 2),
                "credits_burned": round(self.total_credits_burned, 2)
            },
            "financial_stats": {
                "total_spent": round(total_spent, 2),
                "total_transferred": round(total_transferred, 2),
                "total_commissions_paid": round(total_commissions, 2),
                "total_refunds": round(total_refunds, 2),
                "average_balance": round(total_circulation / total_users, 2) if total_users > 0 else 0
            },
            "transaction_stats": {
                "total_transactions": len(self.transactions),
                "completed_transactions": len(completed_transactions),
                "transactions_by_type": transaction_types
            },
            "top_earners": self.get_top_earners(5),
            "recent_volume": self.get_transaction_volume(7),
            "report_generated": datetime.now().isoformat()
        }
    
    def export_data(self, filename: str = None) -> str:
        """Export all credit system data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"credit_system_export_{timestamp}.json"
        
        export_data = {
            "balances": {uid: asdict(balance) for uid, balance in self.balances.items()},
            "transactions": [asdict(tx) for tx in self.transactions],
            "system_config": {
                "max_balance": self.max_balance,
                "min_transaction": self.min_transaction,
                "total_credits_issued": self.total_credits_issued,
                "total_credits_burned": self.total_credits_burned
            },
            "system_report": self.generate_system_report(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Convert enum values to strings for JSON serialization
        for tx in export_data["transactions"]:
            tx["transaction_type"] = tx["transaction_type"].value if hasattr(tx["transaction_type"], "value") else str(tx["transaction_type"])
            tx["status"] = tx["status"].value if hasattr(tx["status"], "value") else str(tx["status"])
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename

def main():
    """Main function for testing the credit engine"""
    print("🏦 Virtual Credit System - MyWork-AI")
    print("=" * 50)
    
    # Initialize credit engine
    engine = CreditEngine()
    
    # Create test users
    test_users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
    
    print("Creating user accounts...")
    for user_id in test_users:
        initial_balance = round(random.uniform(50, 500), 2)
        success = engine.create_user_balance(user_id, initial_balance)
        print(f"   {user_id}: ${initial_balance:.2f} - {'✅' if success else '❌'}")
    
    print("\nSimulating transactions...")
    
    # Top-up test
    success, tx_id = engine.top_up("user_001", 100.0, "credit_card")
    print(f"   Top-up user_001 $100: {'✅' if success else '❌'} ({tx_id if success else 'Failed'})")
    
    # Purchase test
    success, tx_id = engine.spend("user_001", 25.50, "Digital Course Purchase")
    print(f"   Purchase user_001 $25.50: {'✅' if success else '❌'} ({tx_id if success else 'Failed'})")
    
    # Transfer test
    success, tx_id = engine.transfer("user_002", "user_003", 50.0, "Payment for services")
    print(f"   Transfer user_002→user_003 $50: {'✅' if success else '❌'} ({tx_id if success else 'Failed'})")
    
    # Commission test
    success, tx_id = engine.earn_commission("user_004", 15.0, "Referral sale", level=1)
    print(f"   Commission user_004 $15: {'✅' if success else '❌'} ({tx_id if success else 'Failed'})")
    
    # Refund test
    success, tx_id = engine.refund("user_005", 30.0, "Product defect")
    print(f"   Refund user_005 $30: {'✅' if success else '❌'} ({tx_id if success else 'Failed'})")
    
    # Error handling tests
    print("\nTesting error handling...")
    
    # Insufficient balance
    success, msg = engine.spend("user_001", 10000.0, "Impossible purchase")
    print(f"   Overspend test: {'❌' if not success else '✅'} ({msg})")
    
    # Invalid user
    success, msg = engine.top_up("invalid_user", 100.0)
    print(f"   Invalid user test: {'❌' if not success else '✅'} ({msg})")
    
    # Generate and display report
    print("\n" + "=" * 60)
    print("SYSTEM REPORT")
    print("=" * 60)
    
    report = engine.generate_system_report()
    
    print("SYSTEM OVERVIEW:")
    for key, value in report["system_overview"].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\nFINANCIAL STATS:")
    for key, value in report["financial_stats"].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\nTRANSACTION STATS:")
    for key, value in report["transaction_stats"].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\nTOP EARNERS:")
    for i, user in enumerate(report["top_earners"], 1):
        print(f"   {i}. {user['user_id']}: ${user['total_earned']:.2f} earned, ${user['current_balance']:.2f} balance")
    
    print("\nRECENT VOLUME (7 days):")
    volume = report["recent_volume"]
    print(f"   Total Volume: ${volume['total_volume']}")
    print(f"   Total Transactions: {volume['total_transactions']}")
    print(f"   Average Size: ${volume['average_transaction_size']}")
    
    # Export data
    filename = engine.export_data()
    print(f"\n📄 Data exported to: {filename}")
    
    print("\n✅ Credit system simulation completed successfully!")
    return True

if __name__ == "__main__":
    import random
    success = main()
    exit(0 if success else 1)