"""
Test script to verify the Analytics page loads and displays correctly.
This uses Playwright to navigate and take screenshots.
"""

import asyncio
from playwright.async_api import async_playwright
import os

async def test_analytics_page():
    """Test the analytics page functionality"""

    print("🧪 Starting Analytics Page Test...")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate to the dashboard analytics page
            print("📍 Navigating to http://localhost:3000/dashboard/analytics")
            await page.goto("http://localhost:3000/dashboard/analytics", wait_until="networkidle")

            # Wait for page to load
            await asyncio.sleep(2)

            # Take a screenshot
            screenshot_path = "verification/analytics_page.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")

            # Check for redirects (might be redirected to sign-in if not authenticated)
            current_url = page.url
            print(f"🔗 Current URL: {current_url}")

            if "/sign-in" in current_url:
                print("⚠️  Redirected to sign-in page (authentication required)")

                # Check if the analytics link exists in the dashboard
                print("📍 Checking if analytics link exists in layout...")

                # Try to access the main page to see the navigation
                await page.goto("http://localhost:3000", wait_until="networkidle")
                await asyncio.sleep(1)

                # Check for Analytics link in the page
                analytics_link = await page.query_selector("a[href='/dashboard/analytics']")
                if analytics_link:
                    print("✅ Analytics link found in navigation")
                    analytics_text = await analytics_link.inner_text()
                    print(f"   Link text: '{analytics_text}'")
                else:
                    print("❌ Analytics link NOT found in navigation")

                # Check the sidebar
                sidebar_analytics = await page.query_selector("aside a[href='/analytics']")
                if sidebar_analytics:
                    print("✅ Analytics link found in sidebar")
                else:
                    print("⚠️  Analytics link not in sidebar (might need authentication)")

            else:
                print("✅ Analytics page loaded successfully!")

                # Check for key elements on the analytics page
                title = await page.title()
                print(f"📄 Page title: {title}")

                # Check for analytics heading
                heading = await page.query_selector("h1")
                if heading:
                    heading_text = await heading.inner_text()
                    print(f"📌 Heading: {heading_text}")
                    if "Analytics" in heading_text:
                        print("✅ Analytics heading found")
                    else:
                        print("⚠️  Different heading found")

                # Check for key metrics cards
                metric_cards = await page.query_selector_all(".grid .grid-cols-4 > div, .grid .lg\\:grid-cols-4 > div")
                print(f"📊 Metric cards found: {len(metric_cards)}")

                # Check for time range buttons
                time_range_buttons = await page.query_selector_all("button")
                print(f"🔘 Buttons found: {len(time_range_buttons)}")

                # Check for chart section
                chart_section = await page.query_selector("text=Revenue Over Time")
                if chart_section:
                    print("✅ Chart section found")
                else:
                    print("⚠️  Chart section not found")

                # Check for traffic sources
                traffic_sources = await page.query_selector("text=Traffic Sources")
                if traffic_sources:
                    print("✅ Traffic Sources section found")
                else:
                    print("⚠️  Traffic Sources section not found")

                # Check for top products table
                products_table = await page.query_selector("text=Top Performing Products")
                if products_table:
                    print("✅ Top Products section found")
                else:
                    print("⚠️  Top Products section not found")

            print("\n✅ Analytics page test completed!")

        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_analytics_page())
