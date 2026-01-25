"""
Analytics API endpoints.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case, cast, Integer
from pydantic import BaseModel

from database import get_db
from dependencies import get_current_db_user
from models.user import User
from models.product import Product
from models.order import Order

router = APIRouter()


# Pydantic schemas
class DatePoint(BaseModel):
    date: str
    revenue: float
    sales: int


class AnalyticsStats(BaseModel):
    totalRevenue: float
    revenueChange: float
    totalSales: int
    salesChange: float
    totalViews: int
    viewsChange: float
    conversionRate: float
    conversionChange: float
    avgOrderValue: float
    avgOrderChange: float


class ProductPerformance(BaseModel):
    id: str
    name: str
    sales: int
    revenue: float
    views: int
    conversionRate: float


class AnalyticsResponse(BaseModel):
    stats: AnalyticsStats
    chartData: List[DatePoint]
    topProducts: List[ProductPerformance]


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get analytics data for the current seller.

    Returns:
    - Key metrics (revenue, sales, views, conversion rate)
    - Historical data for charts
    - Top performing products
    """
    user_id = current_user.id
    if not current_user.is_seller:
        raise HTTPException(status_code=403, detail="Seller account required")

    # Calculate date ranges
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    previous_start_date = start_date - timedelta(days=days)

    # Get seller's products
    products_query = select(Product).where(
        and_(
            Product.seller_id == user_id,
            Product.status == "active"
        )
    )
    products_result = await db.execute(products_query)
    products = products_result.scalars().all()

    if not products:
        return AnalyticsResponse(
            stats=AnalyticsStats(
                totalRevenue=0,
                revenueChange=0,
                totalSales=0,
                salesChange=0,
                totalViews=0,
                viewsChange=0,
                conversionRate=0,
                conversionChange=0,
                avgOrderValue=0,
                avgOrderChange=0
            ),
            chartData=[],
            topProducts=[]
        )

    product_ids = [p.id for p in products]

    # Current period orders (completed)
    current_orders_query = select(Order).where(
        and_(
            Order.seller_id == user_id,
            Order.status == "completed",
            Order.payment_status == "completed",
            Order.created_at >= start_date,
            Order.created_at <= end_date
        )
    )
    current_orders_result = await db.execute(current_orders_query)
    current_orders = current_orders_result.scalars().all()

    # Previous period orders (for comparison)
    previous_orders_query = select(Order).where(
        and_(
            Order.seller_id == user_id,
            Order.status == "completed",
            Order.payment_status == "completed",
            Order.created_at >= previous_start_date,
            Order.created_at < start_date
        )
    )
    previous_orders_result = await db.execute(previous_orders_query)
    previous_orders = previous_orders_result.scalars().all()

    # Calculate metrics
    current_revenue = sum(float(o.amount) for o in current_orders)
    previous_revenue = sum(float(o.amount) for o in previous_orders)
    current_sales = len(current_orders)
    previous_sales = len(previous_orders)

    # Calculate views (placeholder - would need product_views table)
    current_views = sum(p.views or 0 for p in products)
    previous_views = current_views  # Placeholder

    # Calculate conversion rate
    conversion_rate = (current_sales / current_views * 100) if current_views > 0 else 0
    previous_conversion_rate = (previous_sales / previous_views * 100) if previous_views > 0 else 0

    # Calculate average order value
    avg_order_value = (current_revenue / current_sales) if current_sales > 0 else 0
    previous_avg_order_value = (previous_revenue / previous_sales) if previous_sales > 0 else 0

    # Calculate changes
    revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    sales_change = ((current_sales - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0
    views_change = ((current_views - previous_views) / previous_views * 100) if previous_views > 0 else 0
    conversion_change = conversion_rate - previous_conversion_rate
    avg_order_change = ((avg_order_value - previous_avg_order_value) / previous_avg_order_value * 100) if previous_avg_order_value > 0 else 0

    stats = AnalyticsStats(
        totalRevenue=round(current_revenue, 2),
        revenueChange=round(revenue_change, 1),
        totalSales=current_sales,
        salesChange=round(sales_change, 1),
        totalViews=current_views,
        viewsChange=round(views_change, 1),
        conversionRate=round(conversion_rate, 2),
        conversionChange=round(conversion_change, 2),
        avgOrderValue=round(avg_order_value, 2),
        avgOrderChange=round(avg_order_change, 1)
    )

    # Generate chart data (grouped by day)
    chart_data = []
    delta = timedelta(days=1)

    # Determine appropriate bucket size based on days parameter
    if days <= 7:
        # Daily data for 7 days
        bucket_days = 1
    elif days <= 30:
        # Every 3 days for 30 days
        bucket_days = 3
    else:
        # Weekly for 90 days
        bucket_days = 7

    current_bucket_start = start_date
    while current_bucket_start < end_date:
        current_bucket_end = min(current_bucket_start + timedelta(days=bucket_days), end_date)

        # Get orders in this bucket
        bucket_orders_query = select(Order).where(
        and_(
            Order.seller_id == user_id,
            Order.status == "completed",
            Order.payment_status == "completed",
            Order.created_at >= current_bucket_start,
            Order.created_at < current_bucket_end
        )
        )
        bucket_orders_result = await db.execute(bucket_orders_query)
        bucket_orders = bucket_orders_result.scalars().all()

        bucket_revenue = sum(float(o.amount) for o in bucket_orders)
        bucket_sales = len(bucket_orders)

        # Format date label
        if bucket_days == 1:
            date_label = current_bucket_start.strftime("%b %d")
        elif bucket_days <= 3:
            date_label = current_bucket_start.strftime("%b %d")
        else:
            date_label = current_bucket_start.strftime("%b %d")

        chart_data.append(DatePoint(
            date=date_label,
            revenue=round(bucket_revenue, 2),
            sales=bucket_sales
        ))

        current_bucket_start = current_bucket_end

    # Calculate product performance
    product_performance = []

    for product in products:
        # Get orders for this product
        product_orders_query = select(Order).where(
        and_(
            Order.product_id == product.id,
            Order.status == "completed",
            Order.payment_status == "completed",
            Order.created_at >= start_date
        )
        )
        product_orders_result = await db.execute(product_orders_query)
        product_orders = product_orders_result.scalars().all()

        sales_count = len(product_orders)
        revenue = sum(float(o.amount) for o in product_orders)
        views = product.views or 0
        conversion = (sales_count / views * 100) if views > 0 else 0

        product_performance.append(ProductPerformance(
            id=product.id,
            name=product.title,
            sales=sales_count,
            revenue=round(revenue, 2),
            views=views,
            conversionRate=round(conversion, 2)
        ))

    # Sort by revenue and take top 10
    product_performance.sort(key=lambda x: x.revenue, reverse=True)
    top_products = product_performance[:10]

    return AnalyticsResponse(
        stats=stats,
        chartData=chart_data,
        topProducts=top_products
    )


@router.get("/traffic-sources")
async def get_traffic_sources(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get traffic sources data.

    Note: This is a placeholder implementation.
    Real implementation would require tracking referral sources.
    """
    if not current_user.is_seller:
        raise HTTPException(status_code=403, detail="Seller account required")

    # Placeholder data - in real implementation, this would come from analytics tracking
    traffic_sources = [
        {"source": "Direct", "visits": 3421, "percentage": 38.3, "color": "bg-blue-500"},
        {"source": "Google", "visits": 2890, "percentage": 32.3, "color": "bg-green-500"},
        {"source": "Twitter", "visits": 1234, "percentage": 13.8, "color": "bg-sky-500"},
        {"source": "GitHub", "visits": 876, "percentage": 9.8, "color": "bg-gray-600"},
        {"source": "Other", "visits": 513, "percentage": 5.8, "color": "bg-gray-400"},
    ]

    return traffic_sources
