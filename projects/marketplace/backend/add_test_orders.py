"""
Add test orders for development and testing.
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from database import get_db
from models.product import Product
from models.order import Order

async def add_test_orders():
    """Create sample orders for testing the Orders page."""
    async for session in get_db():
        # Get products
        result = await session.execute(select(Product))
        products = result.scalars().all()

        if not products:
            print("No products found. Please add products first.")
            return

        # Create test orders with different statuses
        test_orders = [
            {
                "status": "completed",
                "days_ago": 1,
                "license": "standard",
            },
            {
                "status": "completed",
                "days_ago": 3,
                "license": "extended",
            },
            {
                "status": "completed",
                "days_ago": 5,
                "license": "standard",
            },
            {
                "status": "completed",
                "days_ago": 7,
                "license": "unlimited",
            },
            {
                "status": "pending",
                "days_ago": 0,
                "license": "standard",
            },
            {
                "status": "pending",
                "days_ago": 1,
                "license": "extended",
            },
            {
                "status": "refunded",
                "days_ago": 10,
                "license": "standard",
            },
            {
                "status": "refund_requested",
                "days_ago": 2,
                "license": "standard",
            },
        ]

        for i, order_data in enumerate(test_orders):
            product = products[i % len(products)]

            # Calculate price based on license
            price = float(product.price)
            if order_data["license"] == "extended":
                amount = price * 2.5
            elif order_data["license"] == "unlimited":
                amount = price * 5
            else:
                amount = price

            platform_fee = amount * 0.10  # 10% platform fee
            seller_amount = amount - platform_fee

            order = Order(
                id=str(uuid.uuid4()),
                order_number=f"ORD-{1000 + i}",
                buyer_id=f"test_buyer_{i + 1}",
                seller_id=product.seller_id,
                product_id=product.id,
                amount=amount,
                currency="USD",
                license_type=order_data["license"],
                platform_fee=platform_fee,
                stripe_fee=amount * 0.029 + 0.30,  # Stripe fee
                seller_amount=seller_amount,
                payment_status="completed" if order_data["status"] == "completed" else "pending",
                download_count=2 if order_data["status"] == "completed" else 0,
                status=order_data["status"],
                escrow_release_at=datetime.utcnow() + timedelta(days=7) if order_data["status"] == "completed" else None,
                escrow_released=False,
                created_at=datetime.utcnow() - timedelta(days=order_data["days_ago"]),
                updated_at=datetime.utcnow() - timedelta(days=order_data["days_ago"]),
            )

            session.add(order)

        await session.commit()
        print(f"✅ Created {len(test_orders)} test orders")

        # Show summary
        result = await session.execute(select(Order))
        all_orders = result.scalars().all()
        print(f"\n📊 Total orders in database: {len(all_orders)}")

        # Count by status
        from collections import Counter
        status_counts = Counter(o.status for o in all_orders)
        print("\nOrders by status:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")

        break

if __name__ == "__main__":
    asyncio.run(add_test_orders())
