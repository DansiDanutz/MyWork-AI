"""
Add test products to the database for category filtering tests.
"""
import asyncio
import sys
sys.path.insert(0, '/Users/dansidanutz/Desktop/MyWork/projects/marketplace/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models.product import Product

DATABASE_URL = "sqlite+aiosqlite:///marketplace.db"

async def add_test_products():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Test products with different categories
        products = [
            Product(
                seller_id="test_seller_1",
                title="SaaS Starter Kit - Complete Template",
                slug="saas-starter-kit",
                description="A full-stack SaaS boilerplate with Next.js, Stripe, and PostgreSQL. Includes authentication, subscription management, and admin dashboard.",
                short_description="Complete SaaS starter with auth and payments",
                category="saas",
                tags=["nextjs", "stripe", "postgresql", "saas"],
                price=299.00,
                license_type="standard",
                tech_stack=["Next.js", "TypeScript", "Stripe", "PostgreSQL"],
                status="active",
                featured=True,
                views=100,
                sales=50,
                rating_average=4.8,
                rating_count=25,
                version="1.0.0",
            ),
            Product(
                seller_id="test_seller_2",
                title="AI Chat Interface Component",
                slug="ai-chat-interface",
                description="Beautiful chat UI with streaming responses, markdown support, and code syntax highlighting. Perfect for AI applications.",
                short_description="Chat UI with streaming and markdown",
                category="ui",
                tags=["react", "ai", "chat", "streaming"],
                price=149.00,
                license_type="standard",
                tech_stack=["React", "TypeScript", "Tailwind CSS"],
                status="active",
                featured=False,
                views=200,
                sales=80,
                rating_average=4.9,
                rating_count=40,
                version="1.2.0",
            ),
            Product(
                seller_id="test_seller_3",
                title="n8n Workflow Automation Bundle",
                slug="n8n-workflow-bundle",
                description="50+ production-ready n8n workflows for common automation tasks: email processing, data sync, API integrations, and more.",
                short_description="50+ n8n automation workflows",
                category="automation",
                tags=["n8n", "automation", "workflows", "integration"],
                price=79.00,
                license_type="standard",
                tech_stack=["n8n", "JavaScript", "Node.js"],
                status="active",
                featured=True,
                views=300,
                sales=120,
                rating_average=4.7,
                rating_count=60,
                version="2.0.0",
            ),
            Product(
                seller_id="test_seller_4",
                title="FastAPI REST API Boilerplate",
                slug="fastapi-rest-api",
                description="Production-ready FastAPI template with JWT authentication, OpenAPI docs, Redis caching, PostgreSQL, and comprehensive test suite.",
                short_description="FastAPI boilerplate with auth and tests",
                category="api",
                tags=["fastapi", "python", "api", "rest"],
                price=199.00,
                license_type="standard",
                tech_stack=["FastAPI", "Python", "PostgreSQL", "Redis"],
                status="active",
                featured=False,
                views=150,
                sales=60,
                rating_average=4.6,
                rating_count=30,
                version="1.5.0",
            ),
            Product(
                seller_id="test_seller_5",
                title="E-commerce Platform Full-Stack",
                slug="ecommerce-platform-fullstack",
                description="Complete e-commerce solution with Next.js storefront, Stripe payments, admin panel, inventory management, and order tracking.",
                short_description="Full-stack e-commerce platform",
                category="fullstack",
                tags=["nextjs", "ecommerce", "stripe", "admin"],
                price=499.00,
                license_type="standard",
                tech_stack=["Next.js", "TypeScript", "Stripe", "PostgreSQL", "Prisma"],
                status="active",
                featured=True,
                views=400,
                sales=90,
                rating_average=4.8,
                rating_count=45,
                version="2.1.0",
            ),
            Product(
                seller_id="test_seller_6",
                title="React Native Mobile App Starter",
                slug="react-native-starter",
                description="Cross-platform mobile app template with React Native, Expo, authentication, push notifications, and backend integration.",
                short_description="React Native mobile app template",
                category="mobile",
                tags=["reactnative", "expo", "mobile", "ios", "android"],
                price=249.00,
                license_type="standard",
                tech_stack=["React Native", "Expo", "TypeScript", "Firebase"],
                status="active",
                featured=False,
                views=180,
                sales=45,
                rating_average=4.5,
                rating_count=22,
                version="1.0.0",
            ),
            Product(
                seller_id="test_seller_7",
                title="AI Content Generator API",
                slug="ai-content-generator",
                description="RESTful API for AI-powered content generation. Supports blog posts, social media, product descriptions with GPT-4 integration.",
                short_description="AI content generation API",
                category="ai",
                tags=["openai", "gpt-4", "api", "content"],
                price=179.00,
                license_type="standard",
                tech_stack=["FastAPI", "Python", "OpenAI", "Redis"],
                status="active",
                featured=True,
                views=250,
                sales=70,
                rating_average=4.9,
                rating_count=35,
                version="1.3.0",
            ),
            Product(
                seller_id="test_seller_8",
                title="Developer CLI Tool Framework",
                slug="developer-cli-tool",
                description="Build beautiful CLI tools with this Python framework. Includes colored output, progress bars, config management, and plugin system.",
                short_description="Python CLI tool framework",
                category="devtools",
                tags=["python", "cli", "click", "terminal"],
                price=99.00,
                license_type="standard",
                tech_stack=["Python", "Click", "Rich", "Typer"],
                status="active",
                featured=False,
                views=120,
                sales=55,
                rating_average=4.7,
                rating_count=28,
                version="2.0.0",
            ),
            Product(
                seller_id="test_seller_9",
                title="Blog Template with CMS",
                slug="blog-template-cms",
                description="Modern blog template with headless CMS, markdown support, syntax highlighting, SEO optimization, and newsletter integration.",
                short_description="Blog template with headless CMS",
                category="other",
                tags=["blog", "cms", "markdown", "seo"],
                price=129.00,
                license_type="standard",
                tech_stack=["Next.js", "MDX", "Tailwind CSS", "Contentful"],
                status="active",
                featured=False,
                views=90,
                sales=35,
                rating_average=4.6,
                rating_count=18,
                version="1.1.0",
            ),
        ]

        for product in products:
            session.add(product)

        await session.commit()
        print(f"✅ Added {len(products)} test products to database")

        # Verify
        from sqlalchemy import select, func
        result = await session.execute(select(func.count()).select_from(Product))
        count = result.scalar()
        print(f"📊 Total products in database: {count}")

if __name__ == "__main__":
    asyncio.run(add_test_products())
