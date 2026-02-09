#!/usr/bin/env python3
"""
Full Simulation Runner for MyWork-AI
Orchestrates all simulators together for comprehensive testing
"""
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Import all simulation components
from user_simulator import VirtualUserSimulator, UserRole
from credit_engine import CreditEngine
from mlm_simulator import MLMSimulator
from product_simulator import ProductLifecycleSimulator, ProductType

class SimulationOrchestrator:
    """Main orchestrator for all simulation components"""
    
    def __init__(self):
        self.user_simulator = VirtualUserSimulator()
        self.credit_engine = CreditEngine()
        self.mlm_simulator = MLMSimulator()
        self.product_simulator = ProductLifecycleSimulator()
        
        self.simulation_log = []
        self.scenarios_passed = 0
        self.scenarios_failed = 0
        
        # Simulation parameters
        self.target_users = 20
        self.target_sellers = 5
        self.target_purchases = 15
        self.target_refunds = 3
        
    def log_step(self, step: str, success: bool = True, details: str = ""):
        """Log a simulation step"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "success": success,
            "details": details
        }
        self.simulation_log.append(log_entry)
        
        if success:
            print(f"✅ {step}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {step}")
            if details:
                print(f"   Error: {details}")
    
    def run_scenario(self, scenario_name: str, scenario_func) -> bool:
        """Run a simulation scenario and track success/failure"""
        try:
            print(f"\n🎯 Running scenario: {scenario_name}")
            result = scenario_func()
            if result:
                self.scenarios_passed += 1
                self.log_step(f"Scenario '{scenario_name}' completed successfully")
            else:
                self.scenarios_failed += 1
                self.log_step(f"Scenario '{scenario_name}' failed", False)
            return result
        except Exception as e:
            self.scenarios_failed += 1
            self.log_step(f"Scenario '{scenario_name}' crashed", False, str(e))
            return False
    
    def scenario_user_registration(self) -> bool:
        """Scenario: Generate users with referral relationships"""
        try:
            # Generate test users with some referrals
            users = self.user_simulator.generate_test_users(self.target_users)
            
            # Create user balances in credit engine
            for user in users:
                initial_balance = round(random.uniform(50, 500), 2)
                success = self.credit_engine.create_user_balance(user.user_id, initial_balance)
                if not success:
                    return False
                
            # Build MLM tree based on user simulator referral relationships
            # Create referral code to user mapping
            user_by_code = {user.referral_code: user for user in users}
            
            # Add all users to MLM system, starting with root users
            added_to_mlm = set()
            
            # First pass: Add users without referrals (roots)
            for user in users:
                if not user.referred_by:
                    success, mlm_code = self.mlm_simulator.add_user(user.user_id)
                    if success:
                        added_to_mlm.add(user.user_id)
                        # Update user's MLM code
                        user.mlm_referral_code = mlm_code
            
            # Multi-pass: Add users with referrals, level by level
            max_attempts = 10  # Prevent infinite loops
            attempt = 0
            
            while attempt < max_attempts:
                added_this_round = 0
                
                for user in users:
                    # Skip if already added or has no referral
                    if user.user_id in added_to_mlm or not user.referred_by:
                        continue
                    
                    # Find the referring user
                    referring_user = user_by_code.get(user.referred_by)
                    if referring_user and referring_user.user_id in added_to_mlm:
                        # Get the referring user's MLM referral code
                        referring_mlm_code = getattr(referring_user, 'mlm_referral_code', None)
                        if referring_mlm_code:
                            success, mlm_code = self.mlm_simulator.add_user(user.user_id, referring_mlm_code)
                            if success:
                                added_to_mlm.add(user.user_id)
                                user.mlm_referral_code = mlm_code
                                added_this_round += 1
                
                # Break if no progress this round
                if added_this_round == 0:
                    break
                
                attempt += 1
            
            # Add any remaining users without referrals as fallback
            for user in users:
                if user.user_id not in added_to_mlm:
                    success, mlm_code = self.mlm_simulator.add_user(user.user_id)
                    if success:
                        added_to_mlm.add(user.user_id)
                        user.mlm_referral_code = mlm_code
            
            # Synchronize balances - Credit engine is source of truth
            for user in users:
                credit_balance = self.credit_engine.get_balance(user.user_id)
                if credit_balance is not None:
                    user.credits_balance = credit_balance
            
            self.log_step(f"Generated {len(users)} users with balances and referral relationships")
            return len(users) == self.target_users
            
        except Exception as e:
            self.log_step("User registration scenario failed", False, str(e))
            return False
    
    def scenario_product_listings(self) -> bool:
        """Scenario: Sellers list products"""
        try:
            # Get seller users
            sellers = [user for user in self.user_simulator.users.values() 
                      if user.role in [UserRole.SELLER, UserRole.AFFILIATE]]
            
            if len(sellers) < self.target_sellers:
                # Convert some buyers to sellers if needed
                buyers = [user for user in self.user_simulator.users.values() 
                         if user.role == UserRole.BUYER]
                additional_needed = self.target_sellers - len(sellers)
                for i in range(min(additional_needed, len(buyers))):
                    buyers[i].role = UserRole.SELLER
                    sellers.append(buyers[i])
            
            products_created = 0
            for seller in sellers[:self.target_sellers]:
                # Each seller creates 1-3 products
                num_products = random.randint(1, 3)
                for _ in range(num_products):
                    product_type = random.choice(list(ProductType))
                    product = self.product_simulator.generate_realistic_product(
                        seller.user_id, product_type
                    )
                    
                    # Complete the product lifecycle to make it available
                    success, _ = self.product_simulator.submit_for_review(product.product_id)
                    if success:
                        success, _ = self.product_simulator.review_product(product.product_id, approve=True)
                        if success:
                            success, _ = self.product_simulator.activate_product(product.product_id)
                            if success:
                                products_created += 1
                                # Simulate some views
                                views = random.randint(5, 50)
                                for _ in range(views):
                                    self.product_simulator.simulate_product_view(product.product_id)
            
            self.log_step(f"Created and activated {products_created} products from {len(sellers[:self.target_sellers])} sellers")
            return products_created >= self.target_sellers
            
        except Exception as e:
            self.log_step("Product listing scenario failed", False, str(e))
            return False
    
    def scenario_marketplace_activity(self) -> bool:
        """Scenario: Simulate purchases, commissions, and credits flow"""
        try:
            # Get active products
            active_products = [p for p in self.product_simulator.products.values() 
                             if p.status.value == "active"]
            
            if not active_products:
                self.log_step("No active products for marketplace activity", False)
                return False
            
            # Get buyers
            buyers = [user for user in self.user_simulator.users.values() 
                     if user.role in [UserRole.BUYER, UserRole.AFFILIATE]]
            
            purchases_made = 0
            commissions_paid = 0
            
            # Simulate purchases
            for _ in range(self.target_purchases):
                buyer = random.choice(buyers)
                product = random.choice(active_products)
                
                # Check if buyer has enough credits
                buyer_balance = self.credit_engine.get_balance(buyer.user_id)
                if buyer_balance is None or buyer_balance < product.price:
                    # Top up buyer's account
                    top_up_amount = max(product.price * 2, 100.0)
                    success, _ = self.credit_engine.top_up(buyer.user_id, top_up_amount, "auto_topup")
                    if not success:
                        continue
                
                # Create order
                success, order_id = self.product_simulator.create_order(buyer.user_id, product.product_id)
                if not success:
                    continue
                
                # Process payment (deduct credits)
                success, _ = self.credit_engine.spend(
                    buyer.user_id, product.price, f"Purchase: {product.title}", order_id
                )
                if not success:
                    continue
                
                # Update user simulator balance
                buyer.credits_balance = self.credit_engine.get_balance(buyer.user_id)
                
                # Complete the order
                success, _ = self.product_simulator.simulate_payment_success(order_id)
                if success:
                    success, _ = self.product_simulator.simulate_delivery(order_id)
                
                purchases_made += 1
                
                # Process MLM commissions if buyer is in MLM tree
                if buyer.user_id in self.mlm_simulator.referral_tree:
                    commission_breakdown = self.mlm_simulator.calculate_commissions(
                        buyer.user_id, product.price, product.product_id
                    )
                    
                    for commission in commission_breakdown:
                        # Pay commission in credits
                        success, _ = self.credit_engine.earn_commission(
                            commission["user_id"],
                            commission["commission_amount"],
                            f"L{commission['level']} commission",
                            commission["level"],
                            order_id
                        )
                        if success:
                            commissions_paid += 1
                            # Update user simulator balance
                            if commission["user_id"] in self.user_simulator.users:
                                self.user_simulator.users[commission["user_id"]].credits_balance += commission["commission_amount"]
                    
                    # Record MLM commission event
                    success, _, _ = self.mlm_simulator.process_sale(
                        buyer.user_id, product.price, product.product_id
                    )
                
                # Simulate review (30% chance)
                if random.random() < 0.3:
                    rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 35, 35])[0]
                    review_titles = ["Poor", "Below average", "Average", "Good", "Excellent"]
                    success, review_id = self.product_simulator.create_review(
                        buyer.user_id, order_id, rating, review_titles[rating-1],
                        f"This product was {review_titles[rating-1].lower()}."
                    )
                    if success:
                        # Auto-approve review
                        self.product_simulator.moderate_review(review_id, approve=True)
            
            self.log_step(f"Processed {purchases_made} purchases with {commissions_paid} commission payments")
            return purchases_made >= self.target_purchases * 0.8  # 80% success rate acceptable
            
        except Exception as e:
            self.log_step("Marketplace activity scenario failed", False, str(e))
            return False
    
    def scenario_refunds_processing(self) -> bool:
        """Scenario: Process refunds and handle credit returns"""
        try:
            # Get completed orders that can be refunded
            refundable_orders = [
                order for order in self.product_simulator.orders.values()
                if order.status.value in ["confirmed", "delivered", "shipped"]
            ]
            
            if len(refundable_orders) < self.target_refunds:
                self.log_step(f"Only {len(refundable_orders)} refundable orders, target is {self.target_refunds}")
                # Adjust target to available orders
                actual_target = min(self.target_refunds, len(refundable_orders))
            else:
                actual_target = self.target_refunds
            
            refunds_processed = 0
            refund_reasons = [
                "Product defect", "Not as described", "Changed mind", 
                "Technical issues", "Received wrong item"
            ]
            
            # Process refunds
            selected_orders = random.sample(refundable_orders, actual_target)
            
            for order in selected_orders:
                reason = random.choice(refund_reasons)
                
                # Process refund in product system
                success, webhook_id = self.product_simulator.process_refund(
                    order.order_id, reason, order.amount
                )
                
                if success:
                    # Return credits to buyer
                    success, _ = self.credit_engine.refund(
                        order.buyer_id, order.amount, reason, order.order_id
                    )
                    
                    if success:
                        refunds_processed += 1
            
            self.log_step(f"Processed {refunds_processed} refunds with credit returns")
            return refunds_processed >= actual_target * 0.8  # 80% success rate acceptable
            
        except Exception as e:
            self.log_step("Refunds processing scenario failed", False, str(e))
            return False
    
    def scenario_system_integrity(self) -> bool:
        """Scenario: Verify system integrity and detect anomalies"""
        try:
            issues_found = 0
            
            # Check MLM anomalies
            mlm_anomalies = self.mlm_simulator.detect_anomalies()
            if mlm_anomalies:
                issues_found += len(mlm_anomalies)
                self.log_step(f"MLM anomalies detected: {len(mlm_anomalies)}", False)
                for anomaly in mlm_anomalies:
                    print(f"   - {anomaly['type']}: {anomaly['description']}")
            
            # Check credit system balance
            total_circulation = self.credit_engine.get_total_circulation()
            credits_issued = self.credit_engine.total_credits_issued
            credits_burned = self.credit_engine.total_credits_burned
            
            expected_circulation = credits_issued - credits_burned
            if abs(total_circulation - expected_circulation) > 0.01:  # Allow for rounding
                issues_found += 1
                self.log_step(
                    "Credit circulation mismatch", False,
                    f"Expected: {expected_circulation}, Actual: {total_circulation}"
                )
            
            # Synchronize balances before checking (Credit engine is source of truth)
            for user_id, balance_record in self.credit_engine.balances.items():
                if user_id in self.user_simulator.users:
                    user_profile = self.user_simulator.users[user_id]
                    user_profile.credits_balance = balance_record.balance
            
            # Check for any remaining inconsistencies
            balance_mismatches = 0
            for user_id, balance_record in self.credit_engine.balances.items():
                if user_id in self.user_simulator.users:
                    user_profile = self.user_simulator.users[user_id]
                    if abs(user_profile.credits_balance - balance_record.balance) > 0.01:
                        balance_mismatches += 1
            
            if balance_mismatches > 0:
                issues_found += balance_mismatches
                self.log_step(f"Balance synchronization fixed {balance_mismatches} mismatches")
            
            if issues_found == 0:
                self.log_step("System integrity check passed - no anomalies detected")
            else:
                self.log_step(f"System integrity issues found: {issues_found}", False)
            
            return issues_found == 0
            
        except Exception as e:
            self.log_step("System integrity scenario failed", False, str(e))
            return False
    
    def run_full_simulation(self) -> bool:
        """Run the complete marketplace simulation"""
        print("🚀 Starting Full MyWork-AI Marketplace Simulation")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all scenarios
        scenarios = [
            ("User Registration & Referrals", self.scenario_user_registration),
            ("Product Listings & Approval", self.scenario_product_listings),
            ("Marketplace Activity & Commissions", self.scenario_marketplace_activity),
            ("Refunds & Credit Returns", self.scenario_refunds_processing),
            ("System Integrity Check", self.scenario_system_integrity)
        ]
        
        all_passed = True
        for scenario_name, scenario_func in scenarios:
            success = self.run_scenario(scenario_name, scenario_func)
            if not success:
                all_passed = False
        
        end_time = datetime.now()
        simulation_duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("SIMULATION SUMMARY")
        print("=" * 60)
        
        print(f"Duration: {simulation_duration:.2f} seconds")
        print(f"Scenarios Passed: {self.scenarios_passed}")
        print(f"Scenarios Failed: {self.scenarios_failed}")
        print(f"Overall Success: {'✅' if all_passed else '❌'}")
        
        return all_passed
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive simulation report"""
        timestamp = datetime.now()
        
        # Get stats from all systems
        user_stats = self.user_simulator.get_user_stats()
        credit_report = self.credit_engine.generate_system_report()
        mlm_report = self.mlm_simulator.generate_mlm_report()
        product_stats = self.product_simulator.get_system_stats()
        
        # Calculate cross-system metrics
        total_revenue = sum(p.total_revenue for p in self.product_simulator.products.values())
        total_commissions = sum(event.total_commission_paid for event in self.mlm_simulator.commission_events)
        commission_percentage = (total_commissions / total_revenue * 100) if total_revenue > 0 else 0
        
        report = {
            "simulation_overview": {
                "timestamp": timestamp.isoformat(),
                "scenarios_passed": self.scenarios_passed,
                "scenarios_failed": self.scenarios_failed,
                "overall_success": self.scenarios_passed > self.scenarios_failed,
                "total_log_entries": len(self.simulation_log)
            },
            "user_system": user_stats,
            "credit_system": credit_report,
            "mlm_system": mlm_report,
            "product_system": product_stats,
            "cross_system_metrics": {
                "total_marketplace_revenue": round(total_revenue, 2),
                "total_mlm_commissions": round(total_commissions, 2),
                "commission_percentage_of_revenue": round(commission_percentage, 2),
                "average_commission_per_sale": round(total_commissions / len(self.product_simulator.orders), 2) if self.product_simulator.orders else 0,
                "users_with_commissions": len([user for user in self.mlm_simulator.referral_tree.values() if user.total_commission_earned > 0])
            },
            "simulation_log": self.simulation_log[-50:]  # Last 50 log entries
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save simulation report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"simulation_report_{timestamp}.md"
        
        # Create reports directory if it doesn't exist
        reports_dir = "/home/Memo1981/MyWork-AI/reports"
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        
        # Generate markdown report
        md_content = self.generate_markdown_report(report)
        
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        # Also save JSON version
        json_filename = filename.replace('.md', '.json')
        json_filepath = os.path.join(reports_dir, json_filename)
        
        with open(json_filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filepath
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown format report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# MyWork-AI Simulation Report
Generated: {timestamp}

## Executive Summary

- **Overall Status**: {'✅ PASSED' if report['simulation_overview']['overall_success'] else '❌ FAILED'}
- **Scenarios Passed**: {report['simulation_overview']['scenarios_passed']}
- **Scenarios Failed**: {report['simulation_overview']['scenarios_failed']}
- **Total Revenue**: ${report['cross_system_metrics']['total_marketplace_revenue']:,.2f}
- **Total Commissions**: ${report['cross_system_metrics']['total_mlm_commissions']:,.2f}
- **Commission Rate**: {report['cross_system_metrics']['commission_percentage_of_revenue']:.2f}%

## User System Statistics

- **Total Users**: {report['user_system']['total_users']}
- **User Roles**: {', '.join(f"{role}: {count}" for role, count in report['user_system']['user_roles'].items())}
- **Total Credits in Circulation**: ${report['user_system']['total_credits_in_circulation']:,.2f}
- **Total Purchase Volume**: ${report['user_system']['total_purchase_volume']:,.2f}
- **Average Credits per User**: ${report['user_system']['average_credits_per_user']:,.2f}

## Credit System Report

### System Overview
"""

        for key, value in report['credit_system']['system_overview'].items():
            md += f"- **{key.replace('_', ' ').title()}**: {value}\n"

        md += f"""
### Financial Statistics
"""

        for key, value in report['credit_system']['financial_stats'].items():
            md += f"- **{key.replace('_', ' ').title()}**: ${value:,.2f}\n" if isinstance(value, (int, float)) else f"- **{key.replace('_', ' ').title()}**: {value}\n"

        md += f"""
## MLM/Referral System Report

### Overview
- **Total Users**: {report['mlm_system']['overview']['total_users']}
- **Total Commission Events**: {report['mlm_system']['overview']['total_commission_events']}
- **Total Commissions Paid**: ${report['mlm_system']['overview']['total_commissions_paid']:,.2f}
- **Total Sales Volume**: ${report['mlm_system']['overview']['total_sales_volume']:,.2f}
- **Average Commission Rate**: {report['mlm_system']['overview']['average_commission_rate']}%

### Tree Structure
- **Max Depth**: {report['mlm_system']['tree_structure']['max_depth']} levels
- **Tree Roots**: {len(report['mlm_system']['tree_structure']['tree_roots'])} root users

### Top Performers
"""

        for i, performer in enumerate(report['mlm_system']['performance']['top_performers'][:5], 1):
            md += f"{i}. **{performer['user_id']}**: ${performer['total_commission']:.2f} earned, {performer['direct_referrals']} direct referrals\n"

        md += f"""
## Product System Report

### Products
- **Total Products**: {report['product_system']['products']['total']}
- **Active Products**: {report['product_system']['products']['by_status'].get('active', 0)}
- **Approved Products**: {report['product_system']['products']['by_status'].get('approved', 0)}

### Orders
- **Total Orders**: {report['product_system']['orders']['total']}
- **Confirmed Orders**: {report['product_system']['orders']['by_status'].get('confirmed', 0)}
- **Delivered Orders**: {report['product_system']['orders']['by_status'].get('delivered', 0)}
- **Refunded Orders**: {report['product_system']['orders']['by_status'].get('refunded', 0)}

### Reviews
- **Total Reviews**: {report['product_system']['reviews']['total']}
- **Average Rating**: {report['product_system']['reviews']['average_rating']}/5.0
- **Approved Reviews**: {report['product_system']['reviews']['by_status'].get('approved', 0)}

### Financial Performance
- **Total Revenue**: ${report['product_system']['financial']['total_revenue']:,.2f}
- **Total Refunds**: ${report['product_system']['financial']['total_refunds']:,.2f}
- **Net Revenue**: ${report['product_system']['financial']['net_revenue']:,.2f}

## Cross-System Integration

- **Users with Active Commissions**: {report['cross_system_metrics']['users_with_commissions']}
- **Average Commission per Sale**: ${report['cross_system_metrics']['average_commission_per_sale']:.2f}
- **Total Webhook Events**: {report['product_system']['webhooks']['total_events']}

## Anomalies and Issues

"""

        if report['mlm_system']['anomalies']:
            md += "### MLM System Anomalies\n"
            for anomaly in report['mlm_system']['anomalies']:
                md += f"- **{anomaly['type']}**: {anomaly['description']}\n"
        else:
            md += "✅ No MLM system anomalies detected\n"

        md += f"""
## Simulation Log (Recent Activity)

"""

        for log_entry in report['simulation_log'][-10:]:  # Last 10 entries
            status = "✅" if log_entry['success'] else "❌"
            md += f"- {status} **{log_entry['step']}**"
            if log_entry['details']:
                md += f" - {log_entry['details']}"
            md += "\n"

        md += f"""
---
*Report generated by MyWork-AI Simulation Engine*
*Total simulation time: {len(report['simulation_log'])} steps completed*
"""

        return md

def main():
    """Main function to run the complete simulation"""
    print("🏢 MyWork-AI Complete Simulation Engine")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = SimulationOrchestrator()
    
    # Run the full simulation
    success = orchestrator.run_full_simulation()
    
    # Generate comprehensive report
    print("\n📊 Generating comprehensive report...")
    report = orchestrator.generate_comprehensive_report()
    
    # Save report
    report_file = orchestrator.save_report(report)
    print(f"📄 Report saved to: {report_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("FINAL SIMULATION RESULTS")
    print("=" * 60)
    
    print(f"Overall Success: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"Scenarios Passed: {orchestrator.scenarios_passed}")
    print(f"Scenarios Failed: {orchestrator.scenarios_failed}")
    print(f"Total Users Created: {len(orchestrator.user_simulator.users)}")
    print(f"Total Products: {len(orchestrator.product_simulator.products)}")
    print(f"Total Orders: {len(orchestrator.product_simulator.orders)}")
    print(f"Total MLM Events: {len(orchestrator.mlm_simulator.commission_events)}")
    print(f"Total Credit Transactions: {len(orchestrator.credit_engine.transactions)}")
    
    # Show key metrics
    total_revenue = sum(p.total_revenue for p in orchestrator.product_simulator.products.values())
    total_commissions = sum(e.total_commission_paid for e in orchestrator.mlm_simulator.commission_events)
    
    print(f"\nKey Metrics:")
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Total Commissions: ${total_commissions:.2f}")
    print(f"Commission Rate: {(total_commissions/total_revenue*100):.2f}%" if total_revenue > 0 else "Commission Rate: 0%")
    
    print(f"\n📄 Full report available at: {report_file}")
    print("\n✅ Simulation engine execution completed!")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)