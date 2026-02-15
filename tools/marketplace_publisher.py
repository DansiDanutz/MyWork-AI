#!/usr/bin/env python3
"""
MyWork-AI Marketplace Publisher
================================
Publishes products to multiple platforms:
- LemonSqueezy (API-based, primary)
- Our own marketplace (mywork-ai-production.up.railway.app)
- Gumroad (manual — generates listing text)

Usage:
    python3 marketplace_publisher.py list          # List all products
    python3 marketplace_publisher.py publish <dir>  # Publish a product
    python3 marketplace_publisher.py publish-all    # Publish all products
    python3 marketplace_publisher.py landing <dir>  # Generate landing page
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

PRODUCTS_DIR = Path("/home/Memo1981/n8n-automations")
ZIPS_DIR = PRODUCTS_DIR / "zips"

# Product catalog with pricing and metadata
CATALOG = {
    "ai-customer-support-bot": {
        "name": "AI Customer Support Bot",
        "price": 4999,  # cents
        "description": "Production-ready AI customer support chatbot with knowledge base, conversation history, and feedback system. Built with FastAPI + OpenAI.",
        "tagline": "Automate 80% of your customer support with AI",
        "features": ["AI-powered responses from your knowledge base", "Conversation history & context", "Customer feedback system", "REST API for easy integration", "Docker-ready deployment"],
        "tech": "Python, FastAPI, OpenAI, SQLite",
        "category": "AI / Customer Support",
    },
    "ai-email-assistant": {
        "name": "AI Email Assistant",
        "price": 3499,
        "description": "Smart email automation that drafts replies, categorizes emails, and manages follow-ups using AI. Complete backend with database and services layer.",
        "tagline": "Never write a routine email again",
        "features": ["AI email drafting & replies", "Smart email categorization", "Follow-up scheduling", "Template management", "Multi-provider support"],
        "tech": "Python, FastAPI, OpenAI, SQLite",
        "category": "AI / Productivity",
    },
    "ai-seo-content-generator": {
        "name": "AI SEO Content Generator",
        "price": 4499,
        "description": "Generate SEO-optimized blog posts, meta descriptions, and content briefs. Includes keyword research, competitor analysis, and content scoring.",
        "tagline": "Rank higher with AI-generated content that actually works",
        "features": ["SEO-optimized article generation", "Keyword research & density analysis", "Meta description generator", "Content scoring & readability", "Bulk content generation"],
        "tech": "Python, FastAPI, OpenAI",
        "category": "AI / Marketing",
    },
    "invoice-generator-api": {
        "name": "Invoice Generator API",
        "price": 3999,
        "description": "Professional invoice generation API with PDF export, multi-currency support, and tax calculation. Perfect for SaaS billing integration.",
        "tagline": "Professional invoices via API in seconds",
        "features": ["PDF invoice generation", "Multi-currency support", "Tax calculation", "Company branding", "REST API for integration"],
        "tech": "Python, FastAPI, ReportLab, SQLite",
        "category": "Business / Finance",
    },
    "webhook-relay-logger": {
        "name": "Webhook Relay & Logger",
        "price": 1499,
        "description": "Capture, inspect, replay, and forward webhooks. Essential debugging tool for any API integration. Full logging with search and filters.",
        "tagline": "Debug webhooks like a pro",
        "features": ["Capture & log all webhooks", "Replay failed webhooks", "Forward to multiple endpoints", "Search & filter logs", "Real-time dashboard"],
        "tech": "Python, FastAPI, SQLite, WebSocket",
        "category": "Developer Tools",
    },
    "appointment-booking-system": {
        "name": "Appointment Booking System",
        "price": 2999,
        "description": "Complete booking system with availability management, email notifications, and calendar sync. Ready to embed in any website.",
        "tagline": "Let customers book themselves — you focus on delivery",
        "features": ["Availability management", "Email notifications", "Calendar integration", "Customer self-booking", "Admin dashboard API"],
        "tech": "Python, FastAPI, SQLite, APScheduler",
        "category": "Business / Scheduling",
    },
    "social-media-auto-poster": {
        "name": "Social Media Auto-Poster",
        "price": 1999,
        "description": "Schedule and auto-publish content across Twitter/X, LinkedIn, and more. Includes AI caption generation and basic analytics.",
        "tagline": "Post once, publish everywhere",
        "features": ["Multi-platform posting", "AI caption generation", "Post scheduling", "Basic analytics", "Content calendar API"],
        "tech": "Python, FastAPI, APScheduler, SQLite",
        "category": "Marketing / Social",
    },
    "ai-data-scraper": {
        "name": "AI Data Scraper & Analyzer",
        "price": 3999,
        "description": "Intelligent web scraper with AI-powered data extraction, cleaning, and analysis. Export to CSV, JSON, or database.",
        "tagline": "Extract structured data from any website with AI",
        "features": ["AI-powered data extraction", "Automatic data cleaning", "Multiple export formats", "Scheduled scraping", "Rate limiting & proxy support"],
        "tech": "Python, FastAPI, BeautifulSoup, OpenAI",
        "category": "Data / Scraping",
    },
    "smart-lead-nurture": {
        "name": "Smart Lead Nurture System",
        "price": 2999,
        "description": "Automated lead nurturing with AI-personalized email sequences, lead scoring, and conversion tracking. n8n workflow included.",
        "tagline": "Turn leads into customers on autopilot",
        "features": ["AI-personalized email sequences", "Lead scoring", "Conversion tracking", "n8n workflow integration", "CRM-ready API"],
        "tech": "Python, n8n, SQLite",
        "category": "Sales / Marketing",
    },
}

BUNDLE_PRICE = 4900  # $49 for all 9 products ($350+ value)


def list_products():
    """List all products with status."""
    print("\n🛍️  MyWork-AI Product Catalog\n")
    print(f"{'Product':<35} {'Price':>8} {'Files':>6} {'Ready':>6}")
    print("─" * 60)
    
    total_value = 0
    ready = 0
    for slug, info in CATALOG.items():
        product_dir = PRODUCTS_DIR / slug
        exists = product_dir.exists()
        has_main = (product_dir / "main.py").exists() if exists else False
        file_count = len(list(product_dir.rglob("*"))) if exists else 0
        status = "✅" if (exists and has_main) else "⚠️" if exists else "❌"
        price_str = f"${info['price']/100:.2f}"
        total_value += info['price']
        if exists and has_main:
            ready += 1
        print(f"{info['name']:<35} {price_str:>8} {file_count:>6} {status:>6}")
    
    print("─" * 60)
    print(f"{'Total (individual)':<35} ${total_value/100:.2f}")
    print(f"{'Bundle price':<35} ${BUNDLE_PRICE/100:.2f}")
    print(f"\n📊 {ready}/{len(CATALOG)} products ready to sell")
    
    zip_dir = PRODUCTS_DIR / "zips"
    if zip_dir.exists():
        zips = list(zip_dir.glob("*.zip"))
        print(f"📦 {len(zips)} ZIP files ready for upload")


def generate_landing_page(slug: str):
    """Generate a product landing page in HTML."""
    if slug not in CATALOG:
        print(f"❌ Unknown product: {slug}")
        return
    
    info = CATALOG[slug]
    price = info['price'] / 100
    features_html = "\n".join(f'<li>✅ {f}</li>' for f in info['features'])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{info['name']} - MyWork-AI</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #e0e0e0; }}
        .hero {{ text-align: center; padding: 80px 20px 40px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }}
        .hero h1 {{ font-size: 2.8rem; margin-bottom: 16px; background: linear-gradient(90deg, #00d2ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .hero p {{ font-size: 1.3rem; color: #aaa; max-width: 600px; margin: 0 auto; }}
        .badge {{ display: inline-block; background: #7b2ff7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .features {{ list-style: none; padding: 0; }}
        .features li {{ padding: 12px 0; font-size: 1.1rem; border-bottom: 1px solid #222; }}
        .price-box {{ text-align: center; padding: 40px; background: #111; border-radius: 16px; margin: 40px 0; border: 1px solid #333; }}
        .price {{ font-size: 3rem; font-weight: bold; color: #00d2ff; }}
        .price-note {{ color: #666; margin-top: 8px; }}
        .cta {{ display: inline-block; background: linear-gradient(90deg, #7b2ff7, #00d2ff); color: white; padding: 16px 48px; border-radius: 8px; font-size: 1.2rem; text-decoration: none; margin-top: 20px; font-weight: bold; }}
        .cta:hover {{ opacity: 0.9; transform: translateY(-2px); transition: all 0.2s; }}
        .tech {{ color: #888; font-size: 0.95rem; margin-top: 20px; }}
        .guarantee {{ text-align: center; padding: 20px; color: #888; font-size: 0.9rem; }}
        .section-title {{ font-size: 1.5rem; margin: 40px 0 20px; color: #fff; }}
    </style>
</head>
<body>
    <div class="hero">
        <span class="badge">{info['category']}</span>
        <h1>{info['name']}</h1>
        <p>{info['tagline']}</p>
    </div>
    <div class="container">
        <h2 class="section-title">What You Get</h2>
        <p style="color: #aaa; margin-bottom: 20px;">{info['description']}</p>
        <ul class="features">{features_html}</ul>
        <p class="tech">🛠️ Built with: {info['tech']}</p>
        
        <div class="price-box">
            <div class="price">${price:.2f}</div>
            <div class="price-note">One-time payment · Lifetime access · Free updates</div>
            <a href="#" class="cta">Get Instant Access →</a>
        </div>
        
        <h2 class="section-title">Quick Start</h2>
        <ol style="color: #aaa; line-height: 2;">
            <li>Download & unzip the product</li>
            <li>Copy <code>.env.example</code> → <code>.env</code> and add your API keys</li>
            <li>Run <code>./setup.sh</code></li>
            <li>Your API is live at <code>http://localhost:8000</code> 🚀</li>
        </ol>
        
        <div class="guarantee">
            🔒 30-day money-back guarantee · Built by <a href="https://mywork-ai.dev" style="color: #7b2ff7;">MyWork-AI</a>
        </div>
    </div>
</body>
</html>"""
    
    out_dir = PRODUCTS_DIR / "landing-pages"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{slug}.html"
    out_path.write_text(html)
    print(f"✅ Landing page: {out_path}")
    return out_path


def generate_all_landing_pages():
    """Generate landing pages for all products."""
    for slug in CATALOG:
        generate_landing_page(slug)
    
    # Generate bundle page
    products_html = ""
    for slug, info in CATALOG.items():
        products_html += f"""
        <div style="background: #111; border-radius: 12px; padding: 24px; border: 1px solid #222;">
            <h3 style="color: #00d2ff; margin-bottom: 8px;">{info['name']}</h3>
            <p style="color: #aaa; font-size: 0.95rem;">{info['tagline']}</p>
            <p style="color: #666; font-size: 0.85rem; margin-top: 8px;">Individual price: <s>${info['price']/100:.2f}</s></p>
        </div>"""
    
    total = sum(p['price'] for p in CATALOG.values()) / 100
    bundle_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyWork-AI Mega Bundle — 9 Products for $49</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #e0e0e0; }}
        .hero {{ text-align: center; padding: 80px 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 16px; }}
        .hero .gradient {{ background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .savings {{ display: inline-block; background: #ff4444; color: white; padding: 8px 20px; border-radius: 20px; font-size: 1.1rem; margin: 20px 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
        .price-box {{ text-align: center; padding: 40px 20px; max-width: 600px; margin: 40px auto; background: #111; border-radius: 16px; border: 2px solid #7b2ff7; }}
        .old-price {{ font-size: 1.5rem; color: #666; text-decoration: line-through; }}
        .new-price {{ font-size: 3.5rem; font-weight: bold; color: #00d2ff; }}
        .cta {{ display: inline-block; background: linear-gradient(90deg, #7b2ff7, #00d2ff); color: white; padding: 20px 60px; border-radius: 8px; font-size: 1.3rem; text-decoration: none; margin-top: 20px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="hero">
        <h1><span class="gradient">🚀 MyWork-AI Mega Bundle</span></h1>
        <p style="font-size: 1.3rem; color: #aaa;">9 Production-Ready Automation Tools</p>
        <div class="savings">💰 Save ${total - BUNDLE_PRICE/100:.2f} (86% OFF)</div>
    </div>
    <div class="grid">{products_html}</div>
    <div class="price-box">
        <div class="old-price">${total:.2f}</div>
        <div class="new-price">${BUNDLE_PRICE/100:.2f}</div>
        <p style="color: #888; margin: 8px 0 20px;">One-time payment · All 9 products · Lifetime updates</p>
        <a href="#" class="cta">Get The Bundle →</a>
    </div>
    <p style="text-align: center; color: #666; padding: 40px;">🔒 30-day money-back guarantee · Built by MyWork-AI</p>
</body>
</html>"""
    
    out_path = PRODUCTS_DIR / "landing-pages" / "mega-bundle.html"
    out_path.write_text(bundle_html)
    print(f"✅ Bundle landing page: {out_path}")


def generate_gumroad_listing(slug: str):
    """Generate copy-paste ready Gumroad listing text."""
    if slug not in CATALOG:
        print(f"❌ Unknown product: {slug}")
        return
    
    info = CATALOG[slug]
    price = info['price'] / 100
    features = "\n".join(f"✅ {f}" for f in info['features'])
    
    print(f"""
╔══════════════════════════════════════════════════╗
  GUMROAD LISTING — Copy & Paste
╚══════════════════════════════════════════════════╝

📛 Product Name: {info['name']}
💰 Price: ${price:.2f}
🏷️ Tags: {info['category'].lower()}, automation, api, python, fastapi

📝 Description:
{info['tagline']}

{info['description']}

What's included:
{features}

🛠️ Tech Stack: {info['tech']}

Quick Start:
1. Download & unzip
2. Copy .env.example → .env (add your API keys)
3. Run ./setup.sh
4. Your API is live at http://localhost:8000 🚀

Also available as Docker: docker-compose up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: marketplace_publisher.py [list|landing|landing-all|gumroad] [product]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        list_products()
    elif cmd == "landing" and len(sys.argv) > 2:
        generate_landing_page(sys.argv[2])
    elif cmd == "landing-all":
        generate_all_landing_pages()
    elif cmd == "gumroad" and len(sys.argv) > 2:
        generate_gumroad_listing(sys.argv[2])
    else:
        print("Usage: marketplace_publisher.py [list|landing|landing-all|gumroad <slug>]")
