#!/usr/bin/env python3
"""
Virtual User Simulator for MyWork-AI
Generates realistic test users and simulates their actions
"""
import json
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum

class UserRole(Enum):
    BUYER = "buyer"
    SELLER = "seller"
    AFFILIATE = "affiliate"

@dataclass
class UserProfile:
    """User profile with all necessary attributes"""
    user_id: str
    name: str
    email: str
    role: UserRole
    credits_balance: float
    referral_code: str
    referred_by: Optional[str] = None
    created_at: str = ""
    last_activity: str = ""
    total_purchases: float = 0.0
    total_sales: float = 0.0
    total_commissions: float = 0.0
    products_listed: int = 0
    referrals_made: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_activity:
            self.last_activity = datetime.now().isoformat()

class UserAction:
    """User action types for simulation"""
    BROWSE = "browse"
    PURCHASE = "purchase"
    LIST_PRODUCT = "list_product"
    REFER_FRIEND = "refer_friend"
    EARN_COMMISSION = "earn_commission"
    TOP_UP_CREDITS = "top_up_credits"
    WITHDRAW_CREDITS = "withdraw_credits"

class VirtualUserSimulator:
    """Main simulator for creating and managing virtual users"""
    
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self.action_log: List[Dict[str, Any]] = []
        self._load_realistic_data()
    
    def _load_realistic_data(self):
        """Load realistic names and email domains for user generation"""
        self.first_names = [
            "Alex", "Jamie", "Taylor", "Jordan", "Casey", "Morgan", "Riley", "Avery",
            "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "James",
            "Isabella", "Benjamin", "Charlotte", "Lucas", "Amelia", "Henry", "Mia", "Alexander",
            "Harper", "Michael", "Evelyn", "Ethan", "Abigail", "Daniel", "Emily", "Jacob",
            "Elizabeth", "Logan", "Sofia", "Jackson", "Avery", "Sebastian", "Ella", "Jack",
            "Scarlett", "Owen", "Grace", "Luke", "Chloe", "Wyatt", "Victoria", "Grayson",
            "Riley", "Leo", "Aria", "Lincoln", "Zoe", "Jaxon", "Lily", "Joshua"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
            "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
            "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner"
        ]
        
        self.email_domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com",
            "icloud.com", "aol.com", "zoho.com", "fastmail.com", "duck.com"
        ]
    
    def generate_referral_code(self, name: str) -> str:
        """Generate a referral code based on user name"""
        return f"{name.upper()[:3]}{random.randint(1000, 9999)}"
    
    def generate_user(self, role: UserRole = None, referred_by: str = None) -> UserProfile:
        """Generate a single realistic user profile"""
        if role is None:
            role = random.choice(list(UserRole))
        
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        
        # Generate email
        email_local = f"{first_name.lower()}.{last_name.lower()}"
        if random.random() < 0.3:  # 30% chance of having numbers
            email_local += str(random.randint(1, 999))
        email_domain = random.choice(self.email_domains)
        email = f"{email_local}@{email_domain}"
        
        # Generate user ID
        user_id = f"user_{len(self.users) + 1:04d}"
        
        # Generate realistic starting balance based on role
        if role == UserRole.BUYER:
            credits_balance = round(random.uniform(10, 500), 2)
        elif role == UserRole.SELLER:
            credits_balance = round(random.uniform(50, 1000), 2)
        else:  # AFFILIATE
            credits_balance = round(random.uniform(20, 300), 2)
        
        user = UserProfile(
            user_id=user_id,
            name=name,
            email=email,
            role=role,
            credits_balance=credits_balance,
            referral_code=self.generate_referral_code(first_name),
            referred_by=referred_by
        )
        
        self.users[user_id] = user
        self._log_action(user_id, "user_registration", {"role": role.value, "referred_by": referred_by})
        
        return user
    
    def generate_test_users(self, count: int = 20) -> List[UserProfile]:
        """Generate multiple test users with some referral relationships"""
        users = []
        
        # Generate initial users without referrals (about 60%)
        initial_count = int(count * 0.6)
        for _ in range(initial_count):
            user = self.generate_user()
            users.append(user)
        
        # Generate users with referrals (40%)
        referral_count = count - initial_count
        for _ in range(referral_count):
            if users:  # Make sure we have users to refer from
                referring_user = random.choice(users)
                user = self.generate_user(referred_by=referring_user.referral_code)
                users.append(user)
                # Update referring user's referral count
                referring_user.referrals_made += 1
        
        return users
    
    def _log_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log a user action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details or {}
        }
        self.action_log.append(log_entry)
        
        # Update user's last activity
        if user_id in self.users:
            self.users[user_id].last_activity = log_entry["timestamp"]
    
    def simulate_browse_action(self, user_id: str, product_category: str = None) -> bool:
        """Simulate user browsing products"""
        if user_id not in self.users:
            return False
        
        categories = ["electronics", "books", "clothing", "software", "courses", "services"]
        category = product_category or random.choice(categories)
        
        # Simulate browsing time
        browse_time = random.randint(30, 600)  # 30 seconds to 10 minutes
        
        self._log_action(user_id, UserAction.BROWSE, {
            "category": category,
            "browse_time_seconds": browse_time
        })
        
        return True
    
    def simulate_purchase_action(self, user_id: str, product_id: str, amount: float) -> bool:
        """Simulate user making a purchase"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Check if user has enough credits
        if user.credits_balance < amount:
            self._log_action(user_id, "purchase_failed", {
                "product_id": product_id,
                "amount": amount,
                "reason": "insufficient_credits",
                "balance": user.credits_balance
            })
            return False
        
        # Deduct credits and update stats
        user.credits_balance = round(user.credits_balance - amount, 2)
        user.total_purchases = round(user.total_purchases + amount, 2)
        
        self._log_action(user_id, UserAction.PURCHASE, {
            "product_id": product_id,
            "amount": amount,
            "remaining_balance": user.credits_balance
        })
        
        return True
    
    def simulate_list_product_action(self, user_id: str, product_name: str, price: float) -> bool:
        """Simulate user listing a product for sale"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Only sellers and affiliates can list products
        if user.role not in [UserRole.SELLER, UserRole.AFFILIATE]:
            return False
        
        product_id = f"prod_{random.randint(10000, 99999)}"
        user.products_listed += 1
        
        self._log_action(user_id, UserAction.LIST_PRODUCT, {
            "product_id": product_id,
            "product_name": product_name,
            "price": price
        })
        
        return True
    
    def simulate_refer_friend_action(self, user_id: str, friend_role: UserRole = None) -> Optional[str]:
        """Simulate user referring a friend"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        
        # Generate a new user as the referred friend
        friend = self.generate_user(role=friend_role, referred_by=user.referral_code)
        user.referrals_made += 1
        
        self._log_action(user_id, UserAction.REFER_FRIEND, {
            "referred_user_id": friend.user_id,
            "referral_code": user.referral_code
        })
        
        return friend.user_id
    
    def simulate_earn_commission_action(self, user_id: str, amount: float, source: str) -> bool:
        """Simulate user earning commission"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.credits_balance = round(user.credits_balance + amount, 2)
        user.total_commissions = round(user.total_commissions + amount, 2)
        
        self._log_action(user_id, UserAction.EARN_COMMISSION, {
            "amount": amount,
            "source": source,
            "new_balance": user.credits_balance
        })
        
        return True
    
    def simulate_random_activity(self, user_id: str) -> List[str]:
        """Simulate random user activity"""
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        actions_performed = []
        
        # Simulate 1-5 random actions
        action_count = random.randint(1, 5)
        
        for _ in range(action_count):
            # Choose action based on user role and randomness
            possible_actions = []
            
            # All users can browse
            possible_actions.append("browse")
            
            # Buyers focus on purchasing
            if user.role == UserRole.BUYER:
                possible_actions.extend(["purchase"] * 3)  # Higher chance
            
            # Sellers focus on listing products
            elif user.role == UserRole.SELLER:
                possible_actions.extend(["list_product"] * 3)
                possible_actions.append("purchase")
            
            # Affiliates focus on referrals and commissions
            elif user.role == UserRole.AFFILIATE:
                possible_actions.extend(["refer_friend"] * 2)
                possible_actions.append("purchase")
            
            # All users can refer friends occasionally
            possible_actions.append("refer_friend")
            
            chosen_action = random.choice(possible_actions)
            
            if chosen_action == "browse":
                if self.simulate_browse_action(user_id):
                    actions_performed.append("browse")
            
            elif chosen_action == "purchase":
                # Simulate realistic purchase amounts
                amount = round(random.uniform(5, min(user.credits_balance, 200)), 2)
                if amount > 0:
                    product_id = f"prod_{random.randint(1000, 9999)}"
                    if self.simulate_purchase_action(user_id, product_id, amount):
                        actions_performed.append(f"purchase ${amount}")
            
            elif chosen_action == "list_product":
                product_names = ["Digital Course", "E-book", "Software Tool", "Consultation", "Template"]
                product_name = random.choice(product_names)
                price = round(random.uniform(10, 500), 2)
                if self.simulate_list_product_action(user_id, product_name, price):
                    actions_performed.append(f"list_product {product_name}")
            
            elif chosen_action == "refer_friend":
                friend_id = self.simulate_refer_friend_action(user_id)
                if friend_id:
                    actions_performed.append(f"refer_friend {friend_id}")
        
        return actions_performed
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        total_users = len(self.users)
        if total_users == 0:
            return {"error": "No users generated"}
        
        role_counts = {role.value: 0 for role in UserRole}
        total_credits = 0
        total_purchases = 0
        total_sales = 0
        total_commissions = 0
        total_referrals = 0
        
        for user in self.users.values():
            role_counts[user.role.value] += 1
            total_credits += user.credits_balance
            total_purchases += user.total_purchases
            total_sales += user.total_sales
            total_commissions += user.total_commissions
            total_referrals += user.referrals_made
        
        return {
            "total_users": total_users,
            "user_roles": role_counts,
            "total_credits_in_circulation": round(total_credits, 2),
            "total_purchase_volume": round(total_purchases, 2),
            "total_sales_volume": round(total_sales, 2),
            "total_commissions_paid": round(total_commissions, 2),
            "total_referrals_made": total_referrals,
            "average_credits_per_user": round(total_credits / total_users, 2),
            "total_actions_logged": len(self.action_log)
        }
    
    def export_users(self, filename: str = None) -> str:
        """Export users to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"users_export_{timestamp}.json"
        
        export_data = {
            "users": {uid: asdict(user) for uid, user in self.users.items()},
            "action_log": self.action_log,
            "stats": self.get_user_stats(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename
    
    def display_users_summary(self) -> str:
        """Display a summary of all users"""
        if not self.users:
            return "No users generated yet."
        
        summary = []
        summary.append("=" * 60)
        summary.append("VIRTUAL USERS SUMMARY")
        summary.append("=" * 60)
        
        for user in self.users.values():
            summary.append(f"ID: {user.user_id} | {user.name} ({user.role.value})")
            summary.append(f"   Email: {user.email}")
            summary.append(f"   Credits: ${user.credits_balance:.2f}")
            summary.append(f"   Referral Code: {user.referral_code}")
            if user.referred_by:
                summary.append(f"   Referred By: {user.referred_by}")
            summary.append(f"   Purchases: ${user.total_purchases:.2f} | Sales: ${user.total_sales:.2f}")
            summary.append(f"   Commissions: ${user.total_commissions:.2f} | Referrals: {user.referrals_made}")
            summary.append("-" * 60)
        
        stats = self.get_user_stats()
        summary.append("\nSTATISTICS:")
        for key, value in stats.items():
            summary.append(f"   {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(summary)

def main():
    """Main function for testing the user simulator"""
    print("🚀 Virtual User Simulator - MyWork-AI")
    print("=" * 50)
    
    # Initialize simulator
    simulator = VirtualUserSimulator()
    
    # Generate test users
    print("Generating 25 test users...")
    users = simulator.generate_test_users(25)
    print(f"✅ Generated {len(users)} users")
    
    # Simulate random activities for all users
    print("\nSimulating user activities...")
    for user in users:
        actions = simulator.simulate_random_activity(user.user_id)
        if actions:
            print(f"   {user.name}: {', '.join(actions)}")
    
    # Display summary
    print("\n" + simulator.display_users_summary())
    
    # Export data
    filename = simulator.export_users()
    print(f"\n📄 Data exported to: {filename}")
    
    print("\n✅ User simulation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)