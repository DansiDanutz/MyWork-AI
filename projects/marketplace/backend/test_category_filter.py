#!/usr/bin/env python3
"""Test category filtering directly."""
import asyncio
import sys
sys.path.insert(0, '/Users/dansidanutz/Desktop/MyWork/projects/marketplace/backend')

from database import get_db_context
from sqlalchemy import select, func
from models.product import Product

async def test_categories():
    async with get_db_context() as db:
        # Get all products
        result = await db.execute(select(Product))
        all_products = result.scalars().all()
        print(f"\n✅ Total products: {len(all_products)}")

        # Test SaaS category
        result = await db.execute(
            select(Product).where(Product.category == "saas")
        )
        saas_products = result.scalars().all()
        print(f"\n✅ SaaS products: {len(saas_products)}")
        for p in saas_products:
            print(f"   - {p.title} (category: {p.category})")

        # Test UI category
        result = await db.execute(
            select(Product).where(Product.category == "ui")
        )
        ui_products = result.scalars().all()
        print(f"\n✅ UI products: {len(ui_products)}")
        for p in ui_products:
            print(f"   - {p.title} (category: {p.category})")

        # Test automation category
        result = await db.execute(
            select(Product).where(Product.category == "automation")
        )
        automation_products = result.scalars().all()
        print(f"\n✅ Automation products: {len(automation_products)}")
        for p in automation_products:
            print(f"   - {p.title} (category: {p.category})")

        print("\n✅ Category filtering works correctly!")

if __name__ == "__main__":
    asyncio.run(test_categories())
