#!/usr/bin/env python3
"""
MLM/Referral Simulator for MyWork-AI
Builds referral trees and manages commission cascades
"""
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict, deque

class CommissionLevel(Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5

@dataclass
class ReferralNode:
    """Individual node in the referral tree"""
    user_id: str
    referrer_id: Optional[str]
    referral_code: str
    level: int
    children: List[str]
    total_referrals: int
    direct_referrals: int
    total_commission_earned: float
    created_at: str
    is_active: bool = True

@dataclass
class CommissionEvent:
    """Commission event record"""
    event_id: str
    timestamp: str
    sale_amount: float
    buyer_id: str
    product_id: str
    commission_tree: List[Dict[str, Any]]
    total_commission_paid: float

class MLMSimulator:
    """Multi-Level Marketing / Referral system simulator"""
    
    def __init__(self, max_levels: int = 5):
        self.max_levels = max_levels
        self.commission_rates = {
            1: 0.20,  # Level 1: 20%
            2: 0.10,  # Level 2: 10%
            3: 0.05,  # Level 3: 5%
            4: 0.02,  # Level 4: 2%
            5: 0.01   # Level 5: 1%
        }
        
        self.referral_tree: Dict[str, ReferralNode] = {}
        self.commission_events: List[CommissionEvent] = []
        self.user_referral_codes: Dict[str, str] = {}  # code -> user_id mapping
        
    def generate_referral_code(self, user_id: str) -> str:
        """Generate unique referral code for user"""
        # Create a code based on user_id with some randomness
        base_code = user_id.upper().replace("_", "")[-6:]
        random_suffix = str(uuid.uuid4())[-4:].upper()
        return f"{base_code}{random_suffix}"
    
    def add_user(self, user_id: str, referrer_code: str = None) -> Tuple[bool, str]:
        """Add a new user to the referral tree"""
        # Check if user already exists
        if user_id in self.referral_tree:
            return False, f"User {user_id} already exists in referral tree"
        
        # Generate referral code for this user
        referral_code = self.generate_referral_code(user_id)
        
        # Ensure referral code is unique
        while referral_code in self.user_referral_codes:
            referral_code = self.generate_referral_code(user_id)
        
        self.user_referral_codes[referral_code] = user_id
        
        referrer_id = None
        level = 0
        
        # Handle referrer if provided
        if referrer_code:
            if referrer_code not in self.user_referral_codes:
                return False, f"Referrer code {referrer_code} not found"
            
            referrer_id = self.user_referral_codes[referrer_code]
            
            # Check for circular referrals
            if self._would_create_cycle(user_id, referrer_id):
                return False, f"Referral would create circular reference"
            
            # Check level depth
            referrer_node = self.referral_tree[referrer_id]
            level = referrer_node.level + 1
            
            if level > self.max_levels:
                return False, f"Maximum referral depth ({self.max_levels}) exceeded"
            
            # Update referrer's children list
            referrer_node.children.append(user_id)
            referrer_node.direct_referrals += 1
            self._update_total_referrals(referrer_id)
        
        # Create new node
        node = ReferralNode(
            user_id=user_id,
            referrer_id=referrer_id,
            referral_code=referral_code,
            level=level,
            children=[],
            total_referrals=0,
            direct_referrals=0,
            total_commission_earned=0.0,
            created_at=datetime.now().isoformat()
        )
        
        self.referral_tree[user_id] = node
        return True, referral_code
    
    def _would_create_cycle(self, new_user_id: str, potential_referrer_id: str) -> bool:
        """Check if adding this referral relationship would create a cycle"""
        # Start from potential referrer and walk up the tree
        current_id = potential_referrer_id
        visited = set()
        
        while current_id:
            if current_id == new_user_id:
                return True  # Would create cycle
            
            if current_id in visited:
                # Already visited this node, avoid infinite loop
                break
            
            visited.add(current_id)
            
            if current_id not in self.referral_tree:
                break
            
            current_id = self.referral_tree[current_id].referrer_id
        
        return False
    
    def _update_total_referrals(self, user_id: str):
        """Update total referrals count for user and all ancestors"""
        # Use BFS to count all descendants
        if user_id not in self.referral_tree:
            return
        
        total_count = self._count_all_descendants(user_id)
        self.referral_tree[user_id].total_referrals = total_count
        
        # Update all ancestors
        current_id = self.referral_tree[user_id].referrer_id
        while current_id:
            ancestor_total = self._count_all_descendants(current_id)
            self.referral_tree[current_id].total_referrals = ancestor_total
            current_id = self.referral_tree[current_id].referrer_id
    
    def _count_all_descendants(self, user_id: str) -> int:
        """Count all descendants of a user using BFS"""
        if user_id not in self.referral_tree:
            return 0
        
        count = 0
        queue = deque([user_id])
        visited = set()
        
        while queue:
            current_id = queue.popleft()
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_id in self.referral_tree:
                children = self.referral_tree[current_id].children
                count += len(children)
                queue.extend(children)
        
        return count
    
    def get_upline_chain(self, user_id: str) -> List[ReferralNode]:
        """Get the upline chain for a user (up to max_levels)"""
        upline = []
        current_id = user_id
        
        for level in range(1, self.max_levels + 1):
            if current_id not in self.referral_tree:
                break
            
            node = self.referral_tree[current_id]
            if not node.referrer_id:
                break
            
            referrer = self.referral_tree[node.referrer_id]
            upline.append(referrer)
            current_id = node.referrer_id
        
        return upline
    
    def calculate_commissions(self, buyer_id: str, sale_amount: float, product_id: str) -> List[Dict[str, Any]]:
        """Calculate commissions for a sale and return commission breakdown"""
        if buyer_id not in self.referral_tree:
            return []
        
        upline_chain = self.get_upline_chain(buyer_id)
        commission_breakdown = []
        
        for level, referrer_node in enumerate(upline_chain, 1):
            if level > self.max_levels or level not in self.commission_rates:
                break
            
            if not referrer_node.is_active:
                continue
            
            commission_rate = self.commission_rates[level]
            commission_amount = sale_amount * commission_rate
            
            commission_info = {
                "user_id": referrer_node.user_id,
                "level": level,
                "commission_rate": commission_rate,
                "commission_amount": round(commission_amount, 2),
                "sale_amount": sale_amount,
                "buyer_id": buyer_id
            }
            
            commission_breakdown.append(commission_info)
            
            # Update node's total commission
            referrer_node.total_commission_earned += commission_amount
        
        return commission_breakdown
    
    def process_sale(self, buyer_id: str, sale_amount: float, product_id: str) -> Tuple[bool, str, float]:
        """Process a sale and calculate/distribute commissions"""
        if buyer_id not in self.referral_tree:
            return False, f"Buyer {buyer_id} not found in referral tree", 0.0
        
        commission_breakdown = self.calculate_commissions(buyer_id, sale_amount, product_id)
        total_commission = sum(c["commission_amount"] for c in commission_breakdown)
        
        # Create commission event record
        event = CommissionEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sale_amount=sale_amount,
            buyer_id=buyer_id,
            product_id=product_id,
            commission_tree=commission_breakdown,
            total_commission_paid=total_commission
        )
        
        self.commission_events.append(event)
        
        return True, event.event_id, total_commission
    
    def get_referral_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive referral statistics for a user"""
        if user_id not in self.referral_tree:
            return None
        
        node = self.referral_tree[user_id]
        
        # Calculate level-wise breakdown
        level_breakdown = {}
        for level in range(1, self.max_levels + 1):
            level_breakdown[f"level_{level}"] = self._count_referrals_at_level(user_id, level)
        
        # Get recent commissions
        recent_commissions = []
        for event in reversed(self.commission_events[-10:]):  # Last 10 events
            for commission in event.commission_tree:
                if commission["user_id"] == user_id:
                    recent_commissions.append({
                        "event_id": event.event_id,
                        "timestamp": event.timestamp,
                        "amount": commission["commission_amount"],
                        "level": commission["level"],
                        "buyer_id": event.buyer_id
                    })
        
        return {
            "user_id": user_id,
            "referral_code": node.referral_code,
            "level": node.level,
            "direct_referrals": node.direct_referrals,
            "total_referrals": node.total_referrals,
            "total_commission_earned": round(node.total_commission_earned, 2),
            "level_breakdown": level_breakdown,
            "recent_commissions": recent_commissions,
            "is_active": node.is_active,
            "created_at": node.created_at
        }
    
    def _count_referrals_at_level(self, user_id: str, target_level: int) -> int:
        """Count referrals at a specific level relative to the user"""
        if user_id not in self.referral_tree:
            return 0
        
        count = 0
        queue = deque([(user_id, 0)])  # (user_id, current_relative_level)
        visited = set()
        
        while queue:
            current_id, current_level = queue.popleft()
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            if current_level == target_level and current_id != user_id:
                count += 1
            
            if current_level < target_level and current_id in self.referral_tree:
                children = self.referral_tree[current_id].children
                for child_id in children:
                    queue.append((child_id, current_level + 1))
        
        return count
    
    def visualize_tree(self, root_user_id: str = None, max_depth: int = 3) -> str:
        """Create ASCII visualization of referral tree"""
        if root_user_id and root_user_id not in self.referral_tree:
            return f"User {root_user_id} not found in referral tree"
        
        # If no root specified, find tree roots (users with no referrer)
        roots = [user_id for user_id, node in self.referral_tree.items() 
                if node.referrer_id is None]
        
        if root_user_id:
            roots = [root_user_id]
        
        if not roots:
            return "No referral tree found"
        
        result = ["REFERRAL TREE VISUALIZATION", "=" * 40]
        
        for root in roots:
            result.extend(self._visualize_subtree(root, 0, max_depth))
            result.append("")
        
        return "\n".join(result)
    
    def _visualize_subtree(self, user_id: str, depth: int, max_depth: int) -> List[str]:
        """Recursively visualize a subtree"""
        if depth > max_depth or user_id not in self.referral_tree:
            return []
        
        node = self.referral_tree[user_id]
        indent = "  " * depth
        prefix = "├─ " if depth > 0 else ""
        
        # Create node representation
        commission_info = f"${node.total_commission_earned:.2f}" if node.total_commission_earned > 0 else "$0"
        node_line = f"{indent}{prefix}{user_id} (L{node.level}, {node.direct_referrals}↓, {commission_info})"
        
        result = [node_line]
        
        # Add children
        for child_id in node.children:
            child_lines = self._visualize_subtree(child_id, depth + 1, max_depth)
            result.extend(child_lines)
        
        return result
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect potential issues in the referral tree"""
        anomalies = []
        
        # Check for orphaned nodes
        for user_id, node in self.referral_tree.items():
            if node.referrer_id and node.referrer_id not in self.referral_tree:
                anomalies.append({
                    "type": "orphaned_node",
                    "user_id": user_id,
                    "description": f"References non-existent referrer {node.referrer_id}"
                })
        
        # Check for inconsistent parent-child relationships
        for user_id, node in self.referral_tree.items():
            for child_id in node.children:
                if child_id not in self.referral_tree:
                    anomalies.append({
                        "type": "missing_child",
                        "user_id": user_id,
                        "description": f"References non-existent child {child_id}"
                    })
                elif self.referral_tree[child_id].referrer_id != user_id:
                    anomalies.append({
                        "type": "inconsistent_relationship",
                        "user_id": user_id,
                        "description": f"Child {child_id} doesn't reference {user_id} as parent"
                    })
        
        # Check for potential cycles (shouldn't happen with our validation)
        for user_id in self.referral_tree:
            if self._detect_cycle_from_node(user_id):
                anomalies.append({
                    "type": "cycle_detected",
                    "user_id": user_id,
                    "description": f"Circular reference detected starting from {user_id}"
                })
        
        return anomalies
    
    def _detect_cycle_from_node(self, start_user_id: str) -> bool:
        """Detect cycles starting from a specific node"""
        visited = set()
        current_id = start_user_id
        
        while current_id and current_id in self.referral_tree:
            if current_id in visited:
                return True
            
            visited.add(current_id)
            current_id = self.referral_tree[current_id].referrer_id
        
        return False
    
    def generate_mlm_report(self) -> Dict[str, Any]:
        """Generate comprehensive MLM performance report"""
        total_users = len(self.referral_tree)
        total_commissions_paid = sum(event.total_commission_paid for event in self.commission_events)
        total_sales_volume = sum(event.sale_amount for event in self.commission_events)
        
        # Level distribution
        level_distribution = defaultdict(int)
        for node in self.referral_tree.values():
            level_distribution[node.level] += 1
        
        # Top performers
        top_performers = sorted(
            self.referral_tree.values(),
            key=lambda x: x.total_commission_earned,
            reverse=True
        )[:10]
        
        # Commission by level
        commission_by_level = defaultdict(float)
        for event in self.commission_events:
            for commission in event.commission_tree:
                level = commission["level"]
                commission_by_level[level] += commission["commission_amount"]
        
        # Recent activity (last 30 events)
        recent_activity = []
        for event in self.commission_events[-30:]:
            recent_activity.append({
                "timestamp": event.timestamp,
                "buyer_id": event.buyer_id,
                "sale_amount": event.sale_amount,
                "total_commission": event.total_commission_paid,
                "recipients": len(event.commission_tree)
            })
        
        return {
            "overview": {
                "total_users": total_users,
                "total_commission_events": len(self.commission_events),
                "total_commissions_paid": round(total_commissions_paid, 2),
                "total_sales_volume": round(total_sales_volume, 2),
                "average_commission_rate": round(total_commissions_paid / total_sales_volume * 100, 2) if total_sales_volume > 0 else 0,
                "commission_rates_by_level": self.commission_rates
            },
            "tree_structure": {
                "level_distribution": dict(level_distribution),
                "max_depth": max(node.level for node in self.referral_tree.values()) if self.referral_tree else 0,
                "tree_roots": [user_id for user_id, node in self.referral_tree.items() if node.referrer_id is None]
            },
            "performance": {
                "top_performers": [
                    {
                        "user_id": node.user_id,
                        "total_commission": round(node.total_commission_earned, 2),
                        "direct_referrals": node.direct_referrals,
                        "total_referrals": node.total_referrals
                    }
                    for node in top_performers
                ],
                "commission_by_level": {f"level_{k}": round(v, 2) for k, v in commission_by_level.items()}
            },
            "recent_activity": recent_activity,
            "anomalies": self.detect_anomalies(),
            "report_generated": datetime.now().isoformat()
        }
    
    def export_data(self, filename: str = None) -> str:
        """Export MLM system data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mlm_system_export_{timestamp}.json"
        
        export_data = {
            "referral_tree": {uid: asdict(node) for uid, node in self.referral_tree.items()},
            "commission_events": [asdict(event) for event in self.commission_events],
            "user_referral_codes": self.user_referral_codes,
            "configuration": {
                "max_levels": self.max_levels,
                "commission_rates": self.commission_rates
            },
            "mlm_report": self.generate_mlm_report(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename

def main():
    """Main function for testing the MLM simulator"""
    print("🔗 MLM/Referral Simulator - MyWork-AI")
    print("=" * 50)
    
    # Initialize MLM simulator
    mlm = MLMSimulator()
    
    # Create test users and referral chain
    print("Building referral tree...")
    
    # Create root user
    success, code_a = mlm.add_user("user_a")
    print(f"   Root user_a: {'✅' if success else '❌'} (Code: {code_a if success else 'Failed'})")
    
    # Level 1 referrals
    success, code_b = mlm.add_user("user_b", code_a)
    print(f"   Level 1 user_b: {'✅' if success else '❌'} (Code: {code_b if success else 'Failed'})")
    
    success, code_c = mlm.add_user("user_c", code_a)
    print(f"   Level 1 user_c: {'✅' if success else '❌'} (Code: {code_c if success else 'Failed'})")
    
    # Level 2 referrals
    success, code_d = mlm.add_user("user_d", code_b)
    print(f"   Level 2 user_d: {'✅' if success else '❌'} (Code: {code_d if success else 'Failed'})")
    
    success, code_e = mlm.add_user("user_e", code_c)
    print(f"   Level 2 user_e: {'✅' if success else '❌'} (Code: {code_e if success else 'Failed'})")
    
    # Level 3 referral
    success, code_f = mlm.add_user("user_f", code_d)
    print(f"   Level 3 user_f: {'✅' if success else '❌'} (Code: {code_f if success else 'Failed'})")
    
    print("\nTesting edge cases...")
    
    # Test circular referral (should fail)
    success, msg = mlm.add_user("user_g", code_f)
    if success:
        # Try to make user_a refer to user_g (would create cycle)
        success, msg = mlm.add_user("user_a", mlm.referral_tree["user_g"].referral_code)
    print(f"   Circular referral test: {'❌' if not success else '✅'} (Should fail)")
    
    # Test self-referral (should fail)
    if "user_g" in mlm.referral_tree:
        success, msg = mlm.add_user("user_h", mlm.referral_tree["user_g"].referral_code)
        print(f"   Self-referral prevention: {'❌' if not success else '✅'}")
    
    print("\nSimulating sales and commissions...")
    
    # Simulate sale by user_f (deepest level) - commissions should cascade up
    success, event_id, total_commission = mlm.process_sale("user_f", 100.0, "product_001")
    print(f"   Sale by user_f ($100): {'✅' if success else '❌'} (Commission: ${total_commission:.2f})")
    
    # Another sale by user_d
    success, event_id, total_commission = mlm.process_sale("user_d", 50.0, "product_002")
    print(f"   Sale by user_d ($50): {'✅' if success else '❌'} (Commission: ${total_commission:.2f})")
    
    # Sale by user_b
    success, event_id, total_commission = mlm.process_sale("user_b", 75.0, "product_003")
    print(f"   Sale by user_b ($75): {'✅' if success else '❌'} (Commission: ${total_commission:.2f})")
    
    print("\n" + "=" * 60)
    print("REFERRAL TREE VISUALIZATION")
    print("=" * 60)
    
    # Visualize the tree
    tree_viz = mlm.visualize_tree(max_depth=5)
    print(tree_viz)
    
    print("\n" + "=" * 60)
    print("MLM PERFORMANCE REPORT")
    print("=" * 60)
    
    # Generate report
    report = mlm.generate_mlm_report()
    
    print("OVERVIEW:")
    for key, value in report["overview"].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\nTREE STRUCTURE:")
    for key, value in report["tree_structure"].items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\nTOP PERFORMERS:")
    for i, performer in enumerate(report["performance"]["top_performers"], 1):
        print(f"   {i}. {performer['user_id']}: ${performer['total_commission']} "
              f"({performer['direct_referrals']} direct, {performer['total_referrals']} total)")
    
    print("\nCOMMISSION BY LEVEL:")
    for level, amount in report["performance"]["commission_by_level"].items():
        print(f"   {level.replace('_', ' ').title()}: ${amount}")
    
    if report["anomalies"]:
        print("\nANOMALIES DETECTED:")
        for anomaly in report["anomalies"]:
            print(f"   {anomaly['type']}: {anomaly['description']}")
    else:
        print("\n✅ No anomalies detected in referral tree")
    
    # Export data
    filename = mlm.export_data()
    print(f"\n📄 MLM data exported to: {filename}")
    
    print("\n✅ MLM simulation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)