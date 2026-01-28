# MyWork AI - Technical Specification

> Detailed technical architecture for the marketplace platform.

**Version:** 1.0
**Date:** January 2026

---

## 1. System Architecture

### High-Level Overview

```text
text

```text

text

```text
text

```text

text

```text                 +------------------+

                 |   CDN (Cloudflare)|

                 +--------+---------+

                          |

                          v

```text
```text
text

```text

text

```text
text
+------------------------------------------------------------------+

|                         FRONTEND LAYER                            |
|  +------------------+  +------------------+  +------------------+ |
|  |   Marketing      |  |   Marketplace    |  |   Dashboard      | |
|  |   (Next.js)      |  |   (Next.js)      |  |   (Next.js)      | |
|  |   mywork.ai      |  |   market.mywork  |  |   app.mywork     | |
|  +------------------+  +------------------+  +------------------+ |

+------------------------------------------------------------------+

```text

text

```text
text

```text

text

```text                          |

                          v

```text
```text
text

```text

text

```text
text
+------------------------------------------------------------------+

|                         API GATEWAY                               |
|                    (Vercel Edge Functions)                        |
|  - Rate Limiting    - Auth Verification    - Request Routing      |

+------------------------------------------------------------------+

```text

text

```text
text

```text

text

```text                          |

```text  +---------------------------+---------------------------+

  |                           |                           |

  v                           v                           v

```text
text

```text

text

```text
text
+------------------+          +------------------+          +------------------+

|   AUTH SERVICE   |          | MARKETPLACE API  |          |   BRAIN API      |
|   (Clerk)        |          | (FastAPI)        |          |   (FastAPI)      |
|                  |          |                  |          |                  |
| - OAuth          |          | - Products       |          | - Knowledge      |
| - Sessions       |          | - Orders         |          | - Embeddings     |
| - MFA            |          | - Reviews        |          | - Suggestions    |

+------------------+          +------------------+          +------------------+

```text

text

```text
text

```text

text

  |                           |                           |

  v                           v                           v

```text
text

```text

text

```text
text
+------------------------------------------------------------------+

|                         DATA LAYER                                |
|  +------------------+  +------------------+  +------------------+ |
|  |   PostgreSQL     |  |   Redis          |  |   Pinecone       | |
|  |   (Supabase)     |  |   (Upstash)      |  |   (Vectors)      | |
|  |                  |  |                  |  |                  | |
|  | - Users          |  | - Sessions       |  | - Embeddings     | |
|  | - Products       |  | - Cache          |  | - Patterns       | |
|  | - Orders         |  | - Rate limits    |  | - Solutions      | |
|  | - Payouts        |  | - Queue          |  |                  | |
|  +------------------+  +------------------+  +------------------+ |

+------------------------------------------------------------------+

```text

text

```text
text

```text

text

  |                           |                           |

  v                           v                           v

```text
text

```text

text

```text
markdown

+------------------------------------------------------------------+

|                      EXTERNAL SERVICES                            |
|  +------------------+  +------------------+  +------------------+ |
|  |   Stripe         |  |   GitHub         |  |   Anthropic      | |
|  |   Connect        |  |   API            |  |   Claude API     | |
|  +------------------+  +------------------+  +------------------+ |
|  +------------------+  +------------------+  +------------------+ |
|  |   R2/S3          |  |   Resend         |  |   PostHog        | |
|  |   Storage        |  |   Email          |  |   Analytics      | |
|  +------------------+  +------------------+  +------------------+ |

+------------------------------------------------------------------+

```text

text

---

## 2. Database Schema

### Core Tables

```text
sql

-- Users & Authentication
CREATE TABLE users (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
clerk_id VARCHAR(255) UNIQUE NOT NULL,
email VARCHAR(255) UNIQUE NOT NULL,
username VARCHAR(50) UNIQUE NOT NULL,
display_name VARCHAR(100),
avatar_url TEXT,
role VARCHAR(20) DEFAULT 'buyer', -- buyer, seller, admin
stripe_customer_id VARCHAR(255),
stripe_connect_id VARCHAR(255), -- For sellers
subscription_tier VARCHAR(20) DEFAULT 'free', -- free, pro, team, enterprise
subscription_expires_at TIMESTAMP,
verified_seller BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Seller Profiles
CREATE TABLE seller_profiles (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,
bio TEXT,
website VARCHAR(255),
github_username VARCHAR(50),
twitter_handle VARCHAR(50),
total_sales INTEGER DEFAULT 0,
total_revenue DECIMAL(12,2) DEFAULT 0,
average_rating DECIMAL(3,2) DEFAULT 0,
verification_level VARCHAR(20) DEFAULT 'basic', -- basic, verified, premium
payout_schedule VARCHAR(20) DEFAULT 'weekly', -- weekly, monthly
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Products
CREATE TABLE products (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
title VARCHAR(200) NOT NULL,
slug VARCHAR(200) UNIQUE NOT NULL,
description TEXT NOT NULL,
short_description VARCHAR(500),
category VARCHAR(50) NOT NULL,
subcategory VARCHAR(50),
tags TEXT[], -- Array of tags

-- Pricing
price DECIMAL(10,2) NOT NULL,
currency VARCHAR(3) DEFAULT 'USD',
license_type VARCHAR(20) DEFAULT 'standard', -- standard, extended, enterprise

-- Technical Details
tech_stack TEXT[], -- ['Next.js', 'FastAPI', 'PostgreSQL']
framework VARCHAR(50),
requirements TEXT,

-- Files
preview_images TEXT[], -- Array of URLs
demo_url VARCHAR(255),
documentation_url VARCHAR(255),
package_url VARCHAR(255), -- R2/S3 URL to zip
package_size_bytes BIGINT,

-- Stats
views INTEGER DEFAULT 0,
sales INTEGER DEFAULT 0,
rating_average DECIMAL(3,2) DEFAULT 0,
rating_count INTEGER DEFAULT 0,

-- Status
status VARCHAR(20) DEFAULT 'draft', -- draft, pending, active, suspended
featured BOOLEAN DEFAULT FALSE,
featured_until TIMESTAMP,

-- Metadata
version VARCHAR(20) DEFAULT '1.0.0',
last_updated_at TIMESTAMP,
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Product Versions (for updates)
CREATE TABLE product_versions (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
product_id UUID REFERENCES products(id) ON DELETE CASCADE,
version VARCHAR(20) NOT NULL,
changelog TEXT,
package_url VARCHAR(255) NOT NULL,
package_size_bytes BIGINT,
created_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Orders
CREATE TABLE orders (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
order_number VARCHAR(20) UNIQUE NOT NULL, -- MW-2026-00001
buyer_id UUID REFERENCES users(id),
seller_id UUID REFERENCES users(id),
product_id UUID REFERENCES products(id),

-- Pricing
amount DECIMAL(10,2) NOT NULL,
currency VARCHAR(3) DEFAULT 'USD',
platform_fee DECIMAL(10,2) NOT NULL, -- 10%
stripe_fee DECIMAL(10,2) NOT NULL, -- 2.9% + $0.30
seller_amount DECIMAL(10,2) NOT NULL, -- amount - fees

-- Payment
stripe_payment_intent_id VARCHAR(255),
stripe_charge_id VARCHAR(255),
payment_status VARCHAR(20) DEFAULT 'pending', -- pending, completed, refunded,
failed

-- Fulfillment
download_url VARCHAR(255),
download_expires_at TIMESTAMP,
download_count INTEGER DEFAULT 0,

-- Status
status VARCHAR(20) DEFAULT 'pending', -- pending, completed, refunded, disputed
refund_reason TEXT,
refunded_at TIMESTAMP,

created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Payouts
CREATE TABLE payouts (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
seller_id UUID REFERENCES users(id),

-- Amount
amount DECIMAL(10,2) NOT NULL,
currency VARCHAR(3) DEFAULT 'USD',

-- Stripe
stripe_transfer_id VARCHAR(255),
stripe_payout_id VARCHAR(255),

-- Status
status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
failure_reason TEXT,

-- Period
period_start TIMESTAMP NOT NULL,
period_end TIMESTAMP NOT NULL,

processed_at TIMESTAMP,
created_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Reviews
CREATE TABLE reviews (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
buyer_id UUID REFERENCES users(id),
product_id UUID REFERENCES products(id),

rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
title VARCHAR(200),
content TEXT,

-- Helpful votes
helpful_count INTEGER DEFAULT 0,

-- Status
status VARCHAR(20) DEFAULT 'active', -- active, hidden, flagged
seller_response TEXT,
seller_response_at TIMESTAMP,

created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Brain Knowledge
CREATE TABLE brain_entries (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
contributor_id UUID REFERENCES users(id),

-- Content
type VARCHAR(50) NOT NULL, -- pattern, solution, lesson, tip
title VARCHAR(200) NOT NULL,
content TEXT NOT NULL,
context TEXT,
tags TEXT[],

-- Embedding
embedding_id VARCHAR(255), -- Pinecone ID

-- Stats
usage_count INTEGER DEFAULT 0,
helpful_votes INTEGER DEFAULT 0,

-- Status
status VARCHAR(20) DEFAULT 'active', -- active, deprecated, merged

created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
text
);

-- Subscriptions
CREATE TABLE subscriptions (

```text

text

id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
user_id UUID REFERENCES users(id) ON DELETE CASCADE,

tier VARCHAR(20) NOT NULL, -- pro, team, enterprise

stripe_subscription_id VARCHAR(255),
stripe_price_id VARCHAR(255),

status VARCHAR(20) DEFAULT 'active', -- active, canceled, past_due

current_period_start TIMESTAMP,
current_period_end TIMESTAMP,
cancel_at_period_end BOOLEAN DEFAULT FALSE,
canceled_at TIMESTAMP,

created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

```text
markdown

);

-- Indexes
CREATE INDEX idx_products_seller ON products(seller_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_featured ON products(featured) WHERE featured = true;
CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_seller ON orders(seller_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_brain_type ON brain_entries(type);
CREATE INDEX idx_brain_tags ON brain_entries USING GIN(tags);

```text

text

### Row-Level Security (Supabase)

```text
sql

-- Users can only see their own data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON users

```text

text

FOR SELECT USING (auth.uid() = clerk_id);

```text
text
CREATE POLICY "Users can update own profile" ON users

```text

text

FOR UPDATE USING (auth.uid() = clerk_id);

```text
text
-- Products are public to view, but only seller can edit
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Products are viewable by everyone" ON products

```text

text

FOR SELECT USING (status = 'active');

```text
text
CREATE POLICY "Sellers can manage own products" ON products

```text

text

FOR ALL USING (seller_id = auth.uid());

```text
text
-- Orders visible to buyer and seller
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Order visible to buyer" ON orders

```text

text

FOR SELECT USING (buyer_id = auth.uid());

```text
text
CREATE POLICY "Order visible to seller" ON orders

```text

text

FOR SELECT USING (seller_id = auth.uid());

```text
markdown

```text

text

---

## 3. API Specification

### Authentication

All authenticated endpoints require:

```text
text

Authorization: Bearer <clerk_session_token>

```text

text

### Marketplace API Endpoints

```text
yaml

# Products

GET    /api/products                    # List products (public)
GET    /api/products/:slug              # Get product details (public)
POST   /api/products                    # Create product (seller)
PUT    /api/products/:id                # Update product (seller)
DELETE /api/products/:id                # Delete product (seller)
POST   /api/products/:id/publish        # Publish product (seller)

# Search

GET    /api/search?q=<query>&category=<cat>&min_price=<>&max_price=<>

# Orders

POST   /api/orders                      # Create order (buyer)
GET    /api/orders                      # List my orders (buyer)
GET    /api/orders/:id                  # Get order details
GET    /api/orders/:id/download         # Get download URL
POST   /api/orders/:id/refund           # Request refund

# Reviews

GET    /api/products/:id/reviews        # List product reviews
POST   /api/products/:id/reviews        # Create review (verified buyer)
PUT    /api/reviews/:id                 # Update review (author)
DELETE /api/reviews/:id                 # Delete review (author)

# Seller Dashboard

GET    /api/seller/products             # My products
GET    /api/seller/orders               # My sales
GET    /api/seller/analytics            # Sales analytics
GET    /api/seller/payouts              # Payout history
POST   /api/seller/payout               # Request payout

# User

GET    /api/user/profile                # Get my profile
PUT    /api/user/profile                # Update profile
GET    /api/user/purchases              # My purchases
POST   /api/user/become-seller          # Upgrade to seller

# Stripe Webhooks

POST   /api/webhooks/stripe             # Stripe events

```text

text

### Brain API Endpoints

```text
yaml

# Knowledge

POST   /api/brain/learn                 # Contribute knowledge
POST   /api/brain/query                 # Query the brain
GET    /api/brain/suggest?context=<>    # Get suggestions
GET    /api/brain/patterns?type=<>      # List patterns

# Personal Brain (Pro+)

GET    /api/brain/mine                  # My contributions
GET    /api/brain/stats                 # My brain stats

```text

text

### Example API Responses

**GET /api/products/:slug**

```text
json
{
  "id": "uuid",
  "title": "AI Dashboard Starter",
  "slug": "ai-dashboard-starter",
  "description": "Full-stack AI dashboard with...",
  "price": 299.00,
  "currency": "USD",
  "category": "saas-starters",
  "tech_stack": ["Next.js", "FastAPI", "PostgreSQL"],
  "preview_images": [

```text

yaml

"<https://r2.mywork.ai/products/uuid/preview-1.png">

```text
text

  ],
  "demo_url": "<https://demo.mywork.ai/ai-dashboard>",
  "seller": {

```text

yaml

"id": "uuid",
"username": "devmaster",
"display_name": "Dev Master",
"avatar_url": "...",
"verified": true,
"rating": 4.8,
"total_sales": 142

```text
text

  },
  "stats": {

```text

yaml

"views": 1523,
"sales": 47,
"rating_average": 4.7,
"rating_count": 32

```text
text

  },
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-20T15:30:00Z"
}

```text

text

**POST /api/orders**

```text
json
// Request
{
  "product_id": "uuid",
  "license_type": "standard"
}

// Response
{
  "order_id": "uuid",
  "order_number": "MW-2026-00047",
  "amount": 299.00,
  "stripe_client_secret": "pi_xxx_secret_xxx",
  "status": "pending"
}

```text

text

---

## 4. Payment Integration

### Stripe Connect Flow

```text
text

1. SELLER ONBOARDING

   +----------------+     +----------------+     +----------------+

   | Seller clicks  | --> | Stripe Connect | --> | Account ready  |
   | "Become Seller"|     | Onboarding     |     | to receive $   |

   +----------------+     +----------------+     +----------------+

2. PURCHASE FLOW

   +----------------+     +----------------+     +----------------+

   | Buyer clicks   | --> | Stripe Payment | --> | Payment Intent |
   | "Buy Now"      |     | Intent created |     | confirmed      |

   +----------------+     +----------------+     +----------------+

```text

text

```text
text

   |

   v

```text

text

```text
text

   +----------------+     +----------------+     +----------------+

   | Webhook:       | --> | Order marked   | --> | Download URL   |
   | payment_intent |     | completed      |     | generated      |
   | .succeeded     |     |                |     |                |

   +----------------+     +----------------+     +----------------+

3. PAYOUT FLOW (Weekly)

   +----------------+     +----------------+     +----------------+

   | Calculate      | --> | Create Stripe  | --> | Transfer to    |
   | seller balance |     | Transfer       |     | seller bank    |

   +----------------+     +----------------+     +----------------+

```text

text

### Stripe Integration Code

```text
python

# services/stripe_service.py

import stripe
from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:

```text

javascript

@staticmethod
async def create_connect_account(user_id: str, email: str) -> str:

```text
text

"""Create Stripe Connect Express account for seller."""
account = stripe.Account.create(

```text

text
type="express",
email=email,
capabilities={

```text"card_payments": {"requested": True},
"transfers": {"requested": True},

```text},
metadata={"user_id": user_id}

```text
text
)
return account.id

```text

text

@staticmethod
async def create_onboarding_link(account_id: str) -> str:

```text
text

"""Generate Stripe Connect onboarding URL."""
link = stripe.AccountLink.create(

```text

text
account=account_id,
refresh_url=f"{settings.APP_URL}/seller/onboarding/refresh",
return_url=f"{settings.APP_URL}/seller/onboarding/complete",
type="account_onboarding",

```text
text
)
return link.url

```text

text

@staticmethod
async def create_payment_intent(

```text
text

amount: int,  # cents
seller_connect_id: str,
platform_fee: int,  # cents (10%)
metadata: dict

```text

text

) -> stripe.PaymentIntent:

```text
text

"""Create payment with automatic split to seller."""
return stripe.PaymentIntent.create(

```text

text
amount=amount,
currency="usd",
automatic_payment_methods={"enabled": True},
application_fee_amount=platform_fee,
transfer_data={"destination": seller_connect_id},
metadata=metadata

```text
text
)

```text

text

@staticmethod
async def process_payout(seller_id: str, amount: int) -> stripe.Transfer:

```text
text

"""Transfer funds to seller's connected account."""

# Get seller's connect account

seller = await get_seller(seller_id)

return stripe.Transfer.create(

```text

text
amount=amount,
currency="usd",
destination=seller.stripe_connect_id,
metadata={"seller_id": seller_id}

```text
text
)

```text

text

```text
text

```text

text

### Webhook Handler

```text
python

# api/webhooks/stripe.py

from fastapi import APIRouter, Request, HTTPException
import stripe

router = APIRouter()

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):

```text

yaml

payload = await request.body()
sig_header = request.headers.get("stripe-signature")

try:

```text
text

event = stripe.Webhook.construct_event(

```text

text
payload, sig_header, settings.STRIPE_WEBHOOK_SECRET

```text
text
)

```text

text

except ValueError:

```text
text

raise HTTPException(400, "Invalid payload")

```text

text

except stripe.error.SignatureVerificationError:

```text
text

raise HTTPException(400, "Invalid signature")

```text

text

# Handle events

if event.type == "payment_intent.succeeded":

```text
text

await handle_payment_success(event.data.object)

```text

text

elif event.type == "payment_intent.payment_failed":

```text
text

await handle_payment_failed(event.data.object)

```text

text

elif event.type == "account.updated":

```text
text

await handle_account_updated(event.data.object)

```text

text

elif event.type == "payout.paid":

```text
text

await handle_payout_completed(event.data.object)

```text

text

return {"status": "success"}


```text
text

async def handle_payment_success(payment_intent):

```text

markdown

"""Process successful payment."""
order_id = payment_intent.metadata.get("order_id")

# Update order status

order = await update_order(

```text
text

order_id,
status="completed",
payment_status="completed",
stripe_charge_id=payment_intent.latest_charge

```text

text

)

# Generate download URL

download_url = await generate_download_url(order.product_id)
await update_order(order_id, download_url=download_url)

# Update product sales count

await increment_product_sales(order.product_id)

# Update seller stats

await update_seller_stats(order.seller_id, order.seller_amount)

# Send confirmation emails

await send_purchase_confirmation(order)
await send_sale_notification(order)

```text
text

```text

text

---

## 5. Brain API Architecture

### Embedding & Search Flow

```text
yaml
KNOWLEDGE INGESTION
+------------------------------------------------------------------+

|                                                                    |
|  1. User contributes knowledge                                     |
|     POST /api/brain/learn                                          |
|     {                                                              |
|       "type": "pattern",                                           |
|       "title": "FastAPI + SQLAlchemy setup",                       |
|       "content": "Best practice for...",                           |
|       "tags": ["python", "fastapi", "database"]                    |
|     }                                                              |
|                                                                    |
|  2. Generate embedding via Claude                                  |
|     embedding = claude.embed(title + content)                      |
|                                                                    |
|  3. Store in Pinecone                                              |
|     pinecone.upsert(id, embedding, metadata)                       |
|                                                                    |
|  4. Store in PostgreSQL                                            |
|     INSERT INTO brain_entries (...)                                |
|                                                                    |

+------------------------------------------------------------------+

KNOWLEDGE QUERY
+------------------------------------------------------------------+

|                                                                    |
|  1. User queries brain                                             |
|     POST /api/brain/query                                          |
|     { "question": "How do I set up auth with FastAPI?" }           |
|                                                                    |
|  2. Generate query embedding                                       |
|     query_embedding = claude.embed(question)                       |
|                                                                    |
|  3. Vector search in Pinecone                                      |
|     matches = pinecone.query(query_embedding, top_k=10)            |
|                                                                    |
|  4. Fetch full entries from PostgreSQL                             |
|     entries = SELECT * FROM brain_entries WHERE id IN (...)        |
|                                                                    |
|  5. Generate response with Claude                                  |
|     response = claude.generate(question, context=entries)          |
|                                                                    |
|  6. Return response                                                |
|     { "answer": "...", "sources": [...] }                          |
|                                                                    |

+------------------------------------------------------------------+

```text

text

### Brain Service Implementation

```text
python

# services/brain_service.py

from anthropic import Anthropic
from pinecone import Pinecone
from config import settings

anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
pinecone = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pinecone.Index("mywork-brain")


class BrainService:

```text

text

@staticmethod
async def learn(entry: BrainEntry, user_id: str) -> BrainEntry:

```text
text
"""Add knowledge to the brain."""

# Generate embedding

text = f"{entry.title}\n{entry.content}"
embedding = await generate_embedding(text)

# Store in Pinecone

pinecone_id = f"brain_{entry.id}"
index.upsert(vectors=[{

```text

text
"id": pinecone_id,
"values": embedding,
"metadata": {

```text"type": entry.type,
"title": entry.title,
"tags": entry.tags,
"contributor_id": user_id

```text}

```text
text
}])

# Store in PostgreSQL

entry.embedding_id = pinecone_id
entry.contributor_id = user_id
await db.brain_entries.insert(entry)

return entry

```text

text

@staticmethod
async def query(question: str, user_id: str) -> BrainResponse:

```text
text
"""Query the brain for answers."""

# Generate query embedding

query_embedding = await generate_embedding(question)

# Search Pinecone

results = index.query(

```text

text
vector=query_embedding,
top_k=10,
include_metadata=True

```text
text
)

# Fetch full entries

entry_ids = [r.id.replace("brain_", "") for r in results.matches]
entries = await db.brain_entries.fetch_many(entry_ids)

# Generate response with Claude

context = "\n\n".join([

```text

text
f"[{e.type}] {e.title}:\n{e.content}"
for e in entries

```text
text
])

response = anthropic.messages.create(

```text

text
model="claude-sonnet-4-20250514",
max_tokens=1024,
messages=[{

```text"role": "user",
"content": f"""Based on the following knowledge base entries, answer
the question.

```text
```text
text

```text

text

```text
yaml
KNOWLEDGE BASE:
{context}

QUESTION: {question}

Provide a helpful, practical answer. Reference specific entries when relevant."""

```text

text

```text
text

```text

text
}]

```text
text
)

# Track usage

for entry in entries:

```text

text
await db.brain_entries.increment_usage(entry.id)

```text
text
return BrainResponse(

```text

text
answer=response.content[0].text,
sources=[{

```text"id": e.id,
"title": e.title,
"type": e.type

```text} for e in entries[:5]]

```text
text
)

```text

text

@staticmethod
async def suggest(context: str, user_id: str) -> List[Suggestion]:

```text
text
"""Get contextual suggestions based on current work."""

# Generate embedding from context

embedding = await generate_embedding(context)

# Find similar patterns

results = index.query(

```text

text
vector=embedding,
top_k=5,
filter={"type": {"$in": ["pattern", "tip"]}},
include_metadata=True

```text
text
)

# Format suggestions

suggestions = []
for r in results.matches:

```text

text
if r.score > 0.7:  # Only high-relevance suggestions

```textentry = await db.brain_entries.fetch(r.id.replace("brain_", ""))
suggestions.append(Suggestion(
```text
title=entry.title,
```text
content=entry.content[:200] + "...",
```text
relevance=r.score,
```text
type=entry.type
))

```text
```text
text
return suggestions


```text

text

```text
javascript
async def generate_embedding(text: str) -> List[float]:

```text

text

"""Generate embedding using Claude."""

# Using Claude's embedding capability

# In production, might use dedicated embedding model

response = anthropic.messages.create(

```text
text
model="claude-sonnet-4-20250514",
max_tokens=1,
messages=[{

```text

text
"role": "user",
"content": f"Generate a semantic embedding for: {text[:1000]}"

```text
text
}]

```text

text

)

# Parse embedding from response

# (This is simplified - actual implementation would use proper embedding API)

return [0.0] * 1536  # Placeholder

```text
markdown

```text

text

---

## 6. Infrastructure Setup

### Vercel Configuration

```text
json
// vercel.json
{
  "framework": "nextjs",
  "regions": ["iad1", "sfo1", "cdg1"],
  "functions": {

```text

text

"api/**/*.ts": {
  "maxDuration": 30
}

```text
yaml
  },
  "crons": [

```text

text

{
  "path": "/api/cron/process-payouts",
  "schedule": "0 0 ** 1"
},
{
  "path": "/api/cron/update-analytics",
  "schedule": "0 ** **"
}

```text
markdown

  ]
}

```text

text

### Railway Configuration

```text
toml

# railway.toml

[build]
builder = "DOCKERFILE"
dockerfilePath = "./Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[[services]]
name = "marketplace-api"
type = "web"
internalPort = 8000

[[services]]
name = "brain-api"
type = "web"
internalPort = 8001

[[services]]
name = "worker"
type = "worker"

```text

text

### Docker Configuration

```text
dockerfile

# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application

COPY . .

# Run

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```text

text

### Environment Variables

```text
bash

# .env.production (example - never commit real values)

# Database

DATABASE_URL=postgresql://user:pass@host:5432/mywork
REDIS_URL=redis://user:pass@host:6379

# Auth

CLERK_SECRET_KEY=sk_live_xxx
CLERK_PUBLISHABLE_KEY=pk_live_xxx

# Stripe

STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# AI

ANTHROPIC_API_KEY=sk-ant-xxx
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=us-east-1

# Storage

R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET=mywork-files
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com

# Email

RESEND_API_KEY=re_xxx

# Analytics

POSTHOG_API_KEY=phc_xxx

```text

text

---

## 7. Security Implementation

### Input Validation

```text
python

# schemas/product.py

from pydantic import BaseModel, validator, Field
from typing import List, Optional
import re

class ProductCreate(BaseModel):

```text

text

title: str = Field(..., min_length=10, max_length=200)
description: str = Field(..., min_length=100, max_length=10000)
price: float = Field(..., ge=0, le=10000)
category: str
tech_stack: List[str] = Field(..., max_items=10)

@validator('title')
def sanitize_title(cls, v):

```text
text

# Remove potentially dangerous characters

return re.sub(r'[<>\"\';&]', '', v)

```text

text

@validator('category')
def validate_category(cls, v):

```text
text
allowed = ['saas-starters', 'api-services', 'automation',

```text

text

```text   'mobile-apps', 'full-applications', 'components']

```text
```text
text
if v not in allowed:

```text

text
raise ValueError(f'Category must be one of: {allowed}')

```text
text
return v

```text

text

```text
markdown

```text

text

### Rate Limiting

```text
python

# middleware/rate_limit.py

from fastapi import Request, HTTPException
from redis import Redis
import time

redis = Redis.from_url(settings.REDIS_URL)

async def rate_limit(request: Request, limit: int = 100, window: int = 60):

```text

text

"""Rate limit by IP address."""

ip = request.client.host
key = f"rate_limit:{ip}"

current = redis.get(key)

if current is None:

```text
text
redis.setex(key, window, 1)

```text

text

elif int(current) >= limit:

```text
text
raise HTTPException(429, "Rate limit exceeded")

```text

text

else:

```text
text
redis.incr(key)

```text

text

```text
markdown

```text

text

### Code Scanning

```text
python

# services/security_service.py

import subprocess
import tempfile
import zipfile

class SecurityService:

```text

text

DANGEROUS_PATTERNS = [

```text
text
r'eval\s*\(',
r'exec\s*\(',
r'__import__\s*\(',
r'subprocess\.',
r'os\.system\s*\(',
r'os\.popen\s*\(',

```text

text

]

@staticmethod
async def scan_package(package_path: str) -> ScanResult:

```text
text
"""Scan uploaded package for security issues."""

issues = []

with tempfile.TemporaryDirectory() as tmpdir:

```text

text

# Extract package

with zipfile.ZipFile(package_path, 'r') as zip_ref:

```textzip_ref.extractall(tmpdir)

```text# Scan for dangerous patterns

for root, dirs, files in os.walk(tmpdir):

```textfor file in files:
```text
if file.endswith(('.py', '.js', '.ts')):
        filepath = os.path.join(root, file)
        file_issues = await scan_file(filepath)
        issues.extend(file_issues)

```text# Run bandit for Python

result = subprocess.run(

```text['bandit', '-r', tmpdir, '-f', 'json'],
capture_output=True

```text)
if result.returncode != 0:

```textbandit_issues = json.loads(result.stdout)
issues.extend(bandit_issues.get('results', []))

```text
```text
text
return ScanResult(

```text

text
passed=len(issues) == 0,
issues=issues

```text
text
)

```text

text

```text
markdown

```text

text

---

## 8. Monitoring & Analytics

### Logging

```text
python

# utils/logging.py

import structlog
from config import settings

structlog.configure(

```text

text

processors=[

```text
text
structlog.processors.TimeStamper(fmt="iso"),
structlog.processors.JSONRenderer()

```text

text

]

```text
markdown

)

logger = structlog.get_logger()

# Usage

logger.info("order_created",

```text

text

order_id=order.id,
amount=order.amount,
seller_id=order.seller_id

```text
markdown

)

```text

text

### Metrics

```text
python

# utils/metrics.py

from prometheus_client import Counter, Histogram

# Counters

orders_total = Counter(

```text

text

'orders_total',
'Total orders',
['status']

```text
markdown

)

# Histograms

order_amount = Histogram(

```text

text

'order_amount_dollars',
'Order amounts',
buckets=[10, 50, 100, 250, 500, 1000, 5000]

```text
markdown

)

# Usage

orders_total.labels(status='completed').inc()
order_amount.observe(order.amount)

```text

text

### Health Checks

```text
python

# api/health.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():

```text

text

checks = {

```text
text
"database": await check_database(),
"redis": await check_redis(),
"stripe": await check_stripe(),

```text

text

}

healthy = all(checks.values())

return {

```text
text
"status": "healthy" if healthy else "unhealthy",
"checks": checks

```text

text

}

```text
markdown

```text

text

---

## 9. Deployment Checklist

### Pre-Launch

- [ ] Database migrations applied
- [ ] Environment variables set
- [ ] Stripe webhooks configured
- [ ] SSL certificates valid
- [ ] Rate limiting enabled
- [ ] Error tracking enabled (Sentry)
- [ ] Backups configured
- [ ] Monitoring dashboards set up

### Security

- [ ] All secrets in environment variables
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection
- [ ] Rate limiting on sensitive endpoints
- [ ] Security headers configured

### Performance

- [ ] Database indexes created
- [ ] Redis caching enabled
- [ ] CDN configured
- [ ] Images optimized
- [ ] API response compression

---

*This technical specification is a living document and will be updated as the
platform evolves.*
