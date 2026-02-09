#!/usr/bin/env python3
"""
Product Lifecycle Simulator for MyWork-AI
Simulates full product lifecycle and webhook events
"""
import json
import uuid
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

class ProductStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class ProductType(Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    DIGITAL = "digital"
    PHYSICAL = "physical"
    SERVICE = "service"

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"

class WebhookEventType(Enum):
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    CHARGE_REFUNDED = "charge.refunded"
    INVOICE_PAID = "invoice.paid"
    CUSTOMER_SUBSCRIPTION_CREATED = "customer.subscription.created"
    CUSTOMER_SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    PAYMENT_FAILED = "payment_method.payment_failed"

@dataclass
class Product:
    """Product entity"""
    product_id: str
    seller_id: str
    title: str
    description: str
    product_type: ProductType
    price: float
    status: ProductStatus
    created_at: str
    updated_at: str
    category: str
    tags: List[str]
    view_count: int = 0
    purchase_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    total_revenue: float = 0.0
    refund_count: int = 0
    refund_amount: float = 0.0
    is_featured: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class Order:
    """Order entity"""
    order_id: str
    buyer_id: str
    product_id: str
    seller_id: str
    amount: float
    status: OrderStatus
    created_at: str
    updated_at: str
    payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    shipping_address: Optional[str] = None
    delivery_date: Optional[str] = None
    refund_reason: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Review:
    """Product review entity"""
    review_id: str
    product_id: str
    buyer_id: str
    order_id: str
    rating: int
    title: str
    comment: str
    status: ReviewStatus
    created_at: str
    updated_at: str
    helpful_votes: int = 0
    metadata: Dict[str, Any] = None

@dataclass
class WebhookEvent:
    """Webhook event simulation"""
    event_id: str
    event_type: WebhookEventType
    timestamp: str
    data: Dict[str, Any]
    processed: bool = False
    retry_count: int = 0

class ProductLifecycleSimulator:
    """Main product lifecycle simulator"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
        self.reviews: Dict[str, Review] = {}
        self.webhook_events: List[WebhookEvent] = []
        
        self.product_categories = [
            "Electronics", "Books", "Software", "Courses", "Templates",
            "Graphics", "Music", "Videos", "Services", "Consulting"
        ]
        
        self.product_adjectives = [
            "Premium", "Professional", "Ultimate", "Complete", "Advanced",
            "Essential", "Modern", "Creative", "Innovative", "Comprehensive"
        ]
        
        self.product_nouns = [
            "Course", "Template", "Toolkit", "Guide", "Blueprint", "Masterclass",
            "Bundle", "Collection", "System", "Framework", "Solution", "Package"
        ]
    
    def generate_realistic_product(self, seller_id: str, product_type: ProductType = None) -> Product:
        """Generate a realistic product"""
        if product_type is None:
            product_type = random.choice(list(ProductType))
        
        adjective = random.choice(self.product_adjectives)
        noun = random.choice(self.product_nouns)
        category = random.choice(self.product_categories)
        
        title = f"{adjective} {category} {noun}"
        description = f"A comprehensive {noun.lower()} designed for {category.lower()} enthusiasts and professionals."
        
        # Price based on product type
        if product_type == ProductType.FREE:
            price = 0.0
        elif product_type == ProductType.SUBSCRIPTION:
            price = round(random.uniform(9.99, 99.99), 2)
        else:
            price = round(random.uniform(4.99, 499.99), 2)
        
        tags = [
            category.lower(),
            product_type.value,
            random.choice(["beginner", "intermediate", "advanced"]),
            random.choice(["2024", "updated", "latest"])
        ]
        
        product = Product(
            product_id=f"prod_{uuid.uuid4().hex[:12]}",
            seller_id=seller_id,
            title=title,
            description=description,
            product_type=product_type,
            price=price,
            status=ProductStatus.DRAFT,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            category=category,
            tags=tags,
            metadata={"generated": True, "version": "1.0"}
        )
        
        self.products[product.product_id] = product
        return product
    
    def submit_for_review(self, product_id: str) -> Tuple[bool, str]:
        """Submit product for review"""
        if product_id not in self.products:
            return False, f"Product {product_id} not found"
        
        product = self.products[product_id]
        
        if product.status != ProductStatus.DRAFT:
            return False, f"Product must be in draft status to submit for review"
        
        product.status = ProductStatus.PENDING_REVIEW
        product.updated_at = datetime.now().isoformat()
        
        return True, "Product submitted for review"
    
    def review_product(self, product_id: str, approve: bool = None, reason: str = "") -> Tuple[bool, str]:
        """Review a product (admin action)"""
        if product_id not in self.products:
            return False, f"Product {product_id} not found"
        
        product = self.products[product_id]
        
        if product.status != ProductStatus.PENDING_REVIEW:
            return False, f"Product is not pending review"
        
        # Auto-approve for simulation if not specified
        if approve is None:
            approve = random.random() > 0.1  # 90% approval rate
        
        if approve:
            product.status = ProductStatus.APPROVED
            result_msg = "Product approved"
        else:
            product.status = ProductStatus.REJECTED
            result_msg = f"Product rejected: {reason}"
        
        product.updated_at = datetime.now().isoformat()
        return True, result_msg
    
    def activate_product(self, product_id: str) -> Tuple[bool, str]:
        """Activate an approved product"""
        if product_id not in self.products:
            return False, f"Product {product_id} not found"
        
        product = self.products[product_id]
        
        if product.status != ProductStatus.APPROVED:
            return False, f"Product must be approved before activation"
        
        product.status = ProductStatus.ACTIVE
        product.updated_at = datetime.now().isoformat()
        
        return True, "Product activated"
    
    def simulate_product_view(self, product_id: str) -> bool:
        """Simulate someone viewing a product"""
        if product_id not in self.products:
            return False
        
        product = self.products[product_id]
        if product.status == ProductStatus.ACTIVE:
            product.view_count += 1
            return True
        
        return False
    
    def create_order(self, buyer_id: str, product_id: str) -> Tuple[bool, str]:
        """Create an order for a product"""
        if product_id not in self.products:
            return False, f"Product {product_id} not found"
        
        product = self.products[product_id]
        
        if product.status != ProductStatus.ACTIVE:
            return False, f"Product is not available for purchase"
        
        order = Order(
            order_id=f"order_{uuid.uuid4().hex[:12]}",
            buyer_id=buyer_id,
            product_id=product_id,
            seller_id=product.seller_id,
            amount=product.price,
            status=OrderStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            payment_intent_id=f"pi_{uuid.uuid4().hex[:24]}",
            metadata={"product_type": product.product_type.value}
        )
        
        self.orders[order.order_id] = order
        return True, order.order_id
    
    def simulate_payment_success(self, order_id: str) -> Tuple[bool, str]:
        """Simulate successful payment (Stripe webhook)"""
        if order_id not in self.orders:
            return False, f"Order {order_id} not found"
        
        order = self.orders[order_id]
        product = self.products[order.product_id]
        
        # Update order status
        order.status = OrderStatus.CONFIRMED
        order.stripe_charge_id = f"ch_{uuid.uuid4().hex[:24]}"
        order.updated_at = datetime.now().isoformat()
        
        # Update product stats
        product.purchase_count += 1
        product.total_revenue += order.amount
        
        # Create webhook event
        webhook_data = {
            "id": order.payment_intent_id,
            "object": "payment_intent",
            "amount": int(order.amount * 100),  # Stripe uses cents
            "currency": "usd",
            "status": "succeeded",
            "charges": {
                "data": [{
                    "id": order.stripe_charge_id,
                    "amount": int(order.amount * 100),
                    "currency": "usd"
                }]
            },
            "metadata": {
                "order_id": order_id,
                "product_id": order.product_id,
                "buyer_id": order.buyer_id
            }
        }
        
        webhook_event = WebhookEvent(
            event_id=f"evt_{uuid.uuid4().hex[:24]}",
            event_type=WebhookEventType.PAYMENT_INTENT_SUCCEEDED,
            timestamp=datetime.now().isoformat(),
            data=webhook_data
        )
        
        self.webhook_events.append(webhook_event)
        
        return True, webhook_event.event_id
    
    def simulate_delivery(self, order_id: str) -> Tuple[bool, str]:
        """Simulate product delivery"""
        if order_id not in self.orders:
            return False, f"Order {order_id} not found"
        
        order = self.orders[order_id]
        product = self.products[order.product_id]
        
        if order.status != OrderStatus.CONFIRMED:
            return False, f"Order must be confirmed before delivery"
        
        # Update order status based on product type
        if product.product_type in [ProductType.DIGITAL, ProductType.FREE]:
            order.status = OrderStatus.DELIVERED
            order.delivery_date = datetime.now().isoformat()
        else:
            order.status = OrderStatus.SHIPPED
            # Simulate delivery in 1-7 days
            delivery_date = datetime.now() + timedelta(days=random.randint(1, 7))
            order.delivery_date = delivery_date.isoformat()
        
        order.updated_at = datetime.now().isoformat()
        
        return True, "Product delivered" if order.status == OrderStatus.DELIVERED else "Product shipped"
    
    def create_review(self, buyer_id: str, order_id: str, rating: int, 
                     title: str, comment: str) -> Tuple[bool, str]:
        """Create a product review"""
        if order_id not in self.orders:
            return False, f"Order {order_id} not found"
        
        order = self.orders[order_id]
        
        if order.buyer_id != buyer_id:
            return False, f"Only the buyer can review this order"
        
        if order.status not in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
            return False, f"Can only review delivered/shipped orders"
        
        if not 1 <= rating <= 5:
            return False, f"Rating must be between 1 and 5"
        
        review = Review(
            review_id=f"rev_{uuid.uuid4().hex[:12]}",
            product_id=order.product_id,
            buyer_id=buyer_id,
            order_id=order_id,
            rating=rating,
            title=title,
            comment=comment,
            status=ReviewStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata={"order_amount": order.amount}
        )
        
        self.reviews[review.review_id] = review
        return True, review.review_id
    
    def moderate_review(self, review_id: str, approve: bool = None, reason: str = "") -> Tuple[bool, str]:
        """Moderate a review"""
        if review_id not in self.reviews:
            return False, f"Review {review_id} not found"
        
        review = self.reviews[review_id]
        
        if review.status != ReviewStatus.PENDING:
            return False, f"Review is not pending moderation"
        
        # Auto-approve for simulation if not specified
        if approve is None:
            # Approve most reviews, but flag some low ratings
            if review.rating <= 2:
                approve = random.random() > 0.3  # 70% approval for low ratings
            else:
                approve = random.random() > 0.05  # 95% approval for good ratings
        
        if approve:
            review.status = ReviewStatus.APPROVED
            self._update_product_rating(review.product_id, review.rating)
            result_msg = "Review approved"
        else:
            review.status = ReviewStatus.REJECTED
            result_msg = f"Review rejected: {reason}"
        
        review.updated_at = datetime.now().isoformat()
        return True, result_msg
    
    def _update_product_rating(self, product_id: str, new_rating: int):
        """Update product's average rating"""
        if product_id not in self.products:
            return
        
        product = self.products[product_id]
        
        # Calculate new average rating
        total_rating_points = product.rating_average * product.rating_count + new_rating
        product.rating_count += 1
        product.rating_average = round(total_rating_points / product.rating_count, 2)
    
    def process_refund(self, order_id: str, reason: str, amount: float = None) -> Tuple[bool, str]:
        """Process a refund"""
        if order_id not in self.orders:
            return False, f"Order {order_id} not found"
        
        order = self.orders[order_id]
        product = self.products[order.product_id]
        
        if order.status == OrderStatus.REFUNDED:
            return False, f"Order is already refunded"
        
        if order.status not in [OrderStatus.CONFIRMED, OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
            return False, f"Cannot refund order in status: {order.status.value}"
        
        refund_amount = amount if amount is not None else order.amount
        
        if refund_amount > order.amount:
            return False, f"Refund amount cannot exceed order amount"
        
        # Update order
        order.status = OrderStatus.REFUNDED
        order.refund_reason = reason
        order.updated_at = datetime.now().isoformat()
        
        # Update product stats
        product.refund_count += 1
        product.refund_amount += refund_amount
        product.total_revenue -= refund_amount
        
        # Create webhook event
        webhook_data = {
            "id": f"re_{uuid.uuid4().hex[:24]}",
            "object": "refund",
            "amount": int(refund_amount * 100),  # Stripe uses cents
            "currency": "usd",
            "charge": order.stripe_charge_id,
            "reason": "requested_by_customer",
            "status": "succeeded",
            "metadata": {
                "order_id": order_id,
                "product_id": order.product_id,
                "refund_reason": reason
            }
        }
        
        webhook_event = WebhookEvent(
            event_id=f"evt_{uuid.uuid4().hex[:24]}",
            event_type=WebhookEventType.CHARGE_REFUNDED,
            timestamp=datetime.now().isoformat(),
            data=webhook_data
        )
        
        self.webhook_events.append(webhook_event)
        
        return True, webhook_event.event_id
    
    def simulate_subscription_events(self, buyer_id: str, product_id: str) -> List[str]:
        """Simulate subscription lifecycle events"""
        if product_id not in self.products:
            return []
        
        product = self.products[product_id]
        
        if product.product_type != ProductType.SUBSCRIPTION:
            return []
        
        events = []
        
        # Create subscription
        subscription_id = f"sub_{uuid.uuid4().hex[:24]}"
        
        # Subscription created webhook
        webhook_data = {
            "id": subscription_id,
            "object": "subscription",
            "customer": f"cus_{uuid.uuid4().hex[:14]}",
            "status": "active",
            "current_period_start": int(datetime.now().timestamp()),
            "current_period_end": int((datetime.now() + timedelta(days=30)).timestamp()),
            "plan": {
                "id": f"plan_{product_id}",
                "amount": int(product.price * 100),
                "currency": "usd",
                "interval": "month"
            },
            "metadata": {
                "product_id": product_id,
                "buyer_id": buyer_id
            }
        }
        
        webhook_event = WebhookEvent(
            event_id=f"evt_{uuid.uuid4().hex[:24]}",
            event_type=WebhookEventType.CUSTOMER_SUBSCRIPTION_CREATED,
            timestamp=datetime.now().isoformat(),
            data=webhook_data
        )
        
        self.webhook_events.append(webhook_event)
        events.append(webhook_event.event_id)
        
        # Simulate monthly invoice payment
        invoice_webhook_data = {
            "id": f"in_{uuid.uuid4().hex[:24]}",
            "object": "invoice",
            "amount_paid": int(product.price * 100),
            "currency": "usd",
            "customer": webhook_data["customer"],
            "subscription": subscription_id,
            "status": "paid",
            "metadata": webhook_data["metadata"]
        }
        
        invoice_webhook = WebhookEvent(
            event_id=f"evt_{uuid.uuid4().hex[:24]}",
            event_type=WebhookEventType.INVOICE_PAID,
            timestamp=datetime.now().isoformat(),
            data=invoice_webhook_data
        )
        
        self.webhook_events.append(invoice_webhook)
        events.append(invoice_webhook.event_id)
        
        return events
    
    def get_product_metrics(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive metrics for a product"""
        if product_id not in self.products:
            return None
        
        product = self.products[product_id]
        
        # Count orders by status
        product_orders = [order for order in self.orders.values() if order.product_id == product_id]
        order_stats = {}
        for status in OrderStatus:
            order_stats[status.value] = sum(1 for order in product_orders if order.status == status)
        
        # Count reviews by status
        product_reviews = [review for review in self.reviews.values() if review.product_id == product_id]
        review_stats = {}
        for status in ReviewStatus:
            review_stats[status.value] = sum(1 for review in product_reviews if review.status == status)
        
        # Calculate conversion rate
        views = product.view_count
        purchases = product.purchase_count
        conversion_rate = (purchases / views * 100) if views > 0 else 0
        
        return {
            "product_id": product_id,
            "title": product.title,
            "status": product.status.value,
            "type": product.product_type.value,
            "price": product.price,
            "performance": {
                "views": views,
                "purchases": purchases,
                "conversion_rate": round(conversion_rate, 2),
                "total_revenue": round(product.total_revenue, 2),
                "average_rating": product.rating_average,
                "rating_count": product.rating_count,
                "refund_count": product.refund_count,
                "refund_amount": round(product.refund_amount, 2),
                "refund_rate": round((product.refund_count / purchases * 100), 2) if purchases > 0 else 0
            },
            "order_breakdown": order_stats,
            "review_breakdown": review_stats,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }
    
    def get_seller_dashboard(self, seller_id: str) -> Dict[str, Any]:
        """Get seller dashboard data"""
        seller_products = [p for p in self.products.values() if p.seller_id == seller_id]
        
        if not seller_products:
            return {"seller_id": seller_id, "error": "No products found"}
        
        # Aggregate stats
        total_revenue = sum(p.total_revenue for p in seller_products)
        total_views = sum(p.view_count for p in seller_products)
        total_purchases = sum(p.purchase_count for p in seller_products)
        total_refunds = sum(p.refund_count for p in seller_products)
        total_refund_amount = sum(p.refund_amount for p in seller_products)
        
        # Product breakdown by status
        status_breakdown = {}
        for status in ProductStatus:
            status_breakdown[status.value] = sum(1 for p in seller_products if p.status == status)
        
        # Type breakdown
        type_breakdown = {}
        for ptype in ProductType:
            type_breakdown[ptype.value] = sum(1 for p in seller_products if p.product_type == ptype)
        
        return {
            "seller_id": seller_id,
            "summary": {
                "total_products": len(seller_products),
                "active_products": sum(1 for p in seller_products if p.status == ProductStatus.ACTIVE),
                "total_revenue": round(total_revenue, 2),
                "total_views": total_views,
                "total_purchases": total_purchases,
                "total_refunds": total_refunds,
                "total_refund_amount": round(total_refund_amount, 2),
                "overall_conversion_rate": round((total_purchases / total_views * 100), 2) if total_views > 0 else 0
            },
            "product_status_breakdown": status_breakdown,
            "product_type_breakdown": type_breakdown,
            "top_products": [
                {
                    "product_id": p.product_id,
                    "title": p.title,
                    "revenue": round(p.total_revenue, 2),
                    "purchases": p.purchase_count,
                    "rating": p.rating_average
                }
                for p in sorted(seller_products, key=lambda x: x.total_revenue, reverse=True)[:5]
            ]
        }
    
    def simulate_full_lifecycle(self, seller_id: str, buyer_id: str, 
                               product_type: ProductType = None) -> Dict[str, Any]:
        """Simulate a complete product lifecycle"""
        lifecycle_log = {
            "seller_id": seller_id,
            "buyer_id": buyer_id,
            "steps": [],
            "success": True,
            "final_status": None
        }
        
        try:
            # 1. Create product
            product = self.generate_realistic_product(seller_id, product_type)
            lifecycle_log["product_id"] = product.product_id
            lifecycle_log["steps"].append(f"✅ Product created: {product.title}")
            
            # 2. Submit for review
            success, msg = self.submit_for_review(product.product_id)
            lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Submit for review: {msg}")
            
            # 3. Review product
            success, msg = self.review_product(product.product_id)
            lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Review: {msg}")
            
            if not success or product.status != ProductStatus.APPROVED:
                lifecycle_log["final_status"] = product.status.value
                return lifecycle_log
            
            # 4. Activate product
            success, msg = self.activate_product(product.product_id)
            lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Activate: {msg}")
            
            # 5. Simulate views
            view_count = random.randint(10, 100)
            for _ in range(view_count):
                self.simulate_product_view(product.product_id)
            lifecycle_log["steps"].append(f"✅ Product viewed {view_count} times")
            
            # 6. Create order
            success, order_id = self.create_order(buyer_id, product.product_id)
            lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Order created: {order_id if success else 'Failed'}")
            
            if not success:
                lifecycle_log["final_status"] = "order_failed"
                return lifecycle_log
            
            # 7. Process payment
            success, webhook_id = self.simulate_payment_success(order_id)
            lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Payment processed: {webhook_id if success else 'Failed'}")
            
            # 8. Deliver product
            success, msg = self.simulate_delivery(order_id)
            lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Delivery: {msg}")
            
            # 9. Create review (70% chance)
            if random.random() < 0.7:
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 35, 35])[0]
                review_titles = {
                    1: "Disappointed",
                    2: "Below expectations",
                    3: "Average product",
                    4: "Good product",
                    5: "Excellent!"
                }
                
                success, review_id = self.create_review(
                    buyer_id, order_id, rating,
                    review_titles[rating],
                    f"This product was {['terrible', 'poor', 'okay', 'good', 'amazing'][rating-1]}."
                )
                lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Review created: {rating} stars")
                
                if success:
                    # Moderate review
                    success, msg = self.moderate_review(review_id)
                    lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Review moderated: {msg}")
            
            # 10. Potential refund (10% chance)
            if random.random() < 0.1:
                refund_reasons = ["Product defect", "Not as described", "Changed mind", "Technical issues"]
                reason = random.choice(refund_reasons)
                success, webhook_id = self.process_refund(order_id, reason)
                lifecycle_log["steps"].append(f"{'✅' if success else '❌'} Refund processed: {reason}")
                lifecycle_log["final_status"] = "refunded"
            else:
                lifecycle_log["final_status"] = "completed"
            
            # Handle subscription events
            if product.product_type == ProductType.SUBSCRIPTION:
                events = self.simulate_subscription_events(buyer_id, product.product_id)
                lifecycle_log["steps"].append(f"✅ Subscription events created: {len(events)} webhooks")
        
        except Exception as e:
            lifecycle_log["success"] = False
            lifecycle_log["error"] = str(e)
            lifecycle_log["steps"].append(f"❌ Error: {str(e)}")
        
        return lifecycle_log
    
    def export_data(self, filename: str = None) -> str:
        """Export all product system data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"product_system_export_{timestamp}.json"
        
        export_data = {
            "products": {pid: asdict(product) for pid, product in self.products.items()},
            "orders": {oid: asdict(order) for oid, order in self.orders.items()},
            "reviews": {rid: asdict(review) for rid, review in self.reviews.items()},
            "webhook_events": [asdict(event) for event in self.webhook_events],
            "system_stats": self.get_system_stats(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Convert enum values to strings for JSON serialization
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif hasattr(obj, 'value'):
                return obj.value
            else:
                return obj
        
        export_data = convert_enums(export_data)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filename
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        total_revenue = sum(p.total_revenue for p in self.products.values())
        total_refunds = sum(p.refund_amount for p in self.products.values())
        
        return {
            "products": {
                "total": len(self.products),
                "by_status": {status.value: sum(1 for p in self.products.values() if p.status == status) for status in ProductStatus},
                "by_type": {ptype.value: sum(1 for p in self.products.values() if p.product_type == ptype) for ptype in ProductType}
            },
            "orders": {
                "total": len(self.orders),
                "by_status": {status.value: sum(1 for o in self.orders.values() if o.status == status) for status in OrderStatus}
            },
            "reviews": {
                "total": len(self.reviews),
                "by_status": {status.value: sum(1 for r in self.reviews.values() if r.status == status) for status in ReviewStatus},
                "average_rating": round(sum(r.rating for r in self.reviews.values() if r.status == ReviewStatus.APPROVED) / max(1, sum(1 for r in self.reviews.values() if r.status == ReviewStatus.APPROVED)), 2)
            },
            "financial": {
                "total_revenue": round(total_revenue, 2),
                "total_refunds": round(total_refunds, 2),
                "net_revenue": round(total_revenue - total_refunds, 2)
            },
            "webhooks": {
                "total_events": len(self.webhook_events),
                "by_type": {event_type.value: sum(1 for w in self.webhook_events if w.event_type == event_type) for event_type in WebhookEventType}
            }
        }

def main():
    """Main function for testing the product lifecycle simulator"""
    print("📦 Product Lifecycle Simulator - MyWork-AI")
    print("=" * 50)
    
    # Initialize simulator
    simulator = ProductLifecycleSimulator()
    
    # Test users
    sellers = ["seller_001", "seller_002", "seller_003"]
    buyers = ["buyer_001", "buyer_002", "buyer_003", "buyer_004", "buyer_005"]
    
    print("Simulating complete product lifecycles...")
    
    # Simulate multiple complete lifecycles
    for i in range(8):
        seller = random.choice(sellers)
        buyer = random.choice(buyers)
        product_type = random.choice(list(ProductType))
        
        lifecycle = simulator.simulate_full_lifecycle(seller, buyer, product_type)
        
        print(f"\n--- Lifecycle {i+1}: {seller} → {buyer} ({product_type.value}) ---")
        for step in lifecycle["steps"]:
            print(f"   {step}")
        print(f"   Final Status: {lifecycle['final_status']}")
    
    print("\n" + "=" * 60)
    print("SYSTEM STATISTICS")
    print("=" * 60)
    
    stats = simulator.get_system_stats()
    
    print("PRODUCTS:")
    print(f"   Total: {stats['products']['total']}")
    for status, count in stats['products']['by_status'].items():
        if count > 0:
            print(f"   {status.replace('_', ' ').title()}: {count}")
    
    print("\nORDERS:")
    print(f"   Total: {stats['orders']['total']}")
    for status, count in stats['orders']['by_status'].items():
        if count > 0:
            print(f"   {status.replace('_', ' ').title()}: {count}")
    
    print("\nREVIEWS:")
    print(f"   Total: {stats['reviews']['total']}")
    print(f"   Average Rating: {stats['reviews']['average_rating']}")
    for status, count in stats['reviews']['by_status'].items():
        if count > 0:
            print(f"   {status.replace('_', ' ').title()}: {count}")
    
    print("\nFINANCIALS:")
    print(f"   Total Revenue: ${stats['financial']['total_revenue']}")
    print(f"   Total Refunds: ${stats['financial']['total_refunds']}")
    print(f"   Net Revenue: ${stats['financial']['net_revenue']}")
    
    print("\nWEBHOOK EVENTS:")
    print(f"   Total Events: {stats['webhooks']['total_events']}")
    for event_type, count in stats['webhooks']['by_type'].items():
        if count > 0:
            print(f"   {event_type}: {count}")
    
    # Show sample seller dashboard
    if sellers:
        print(f"\n--- SELLER DASHBOARD: {sellers[0]} ---")
        dashboard = simulator.get_seller_dashboard(sellers[0])
        print(f"Total Products: {dashboard['summary']['total_products']}")
        print(f"Total Revenue: ${dashboard['summary']['total_revenue']}")
        print(f"Conversion Rate: {dashboard['summary']['overall_conversion_rate']}%")
    
    # Export data
    filename = simulator.export_data()
    print(f"\n📄 Product system data exported to: {filename}")
    
    print("\n✅ Product lifecycle simulation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)