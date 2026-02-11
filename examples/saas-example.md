# SaaS Template Example

Build a complete Software-as-a-Service application with user authentication, payments, and admin dashboard.

## Quick Start

```bash
# Create a SaaS project
mw create saas billing-platform

# Navigate to project
cd projects/billing-platform

# Start development
npm run dev
```

## What Gets Generated

### Frontend (Next.js)
- **User Authentication**: Login, register, password reset
- **Dashboard**: User portal with navigation
- **Billing**: Stripe integration for subscriptions
- **Admin Panel**: User management, analytics
- **Components**: Reusable UI components with Tailwind CSS

### Backend (FastAPI)
- **Authentication**: JWT tokens, password hashing
- **User Management**: CRUD operations, roles
- **Billing**: Stripe webhooks, subscription handling
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Auto-generated with FastAPI

### DevOps
- **Docker**: Development and production containers
- **CI/CD**: GitHub Actions workflow
- **Environment**: Multiple environment configs
- **Monitoring**: Health checks and logging

## Example Use Case: Billing Platform

Let's build a subscription billing platform for SaaS companies:

```bash
mw create saas billing-platform
```

### Generated Structure
```
billing-platform/
├── frontend/                 # Next.js app
│   ├── pages/
│   │   ├── auth/            # Login, register
│   │   ├── dashboard/       # User dashboard
│   │   ├── admin/           # Admin panel
│   │   └── billing/         # Payment pages
│   ├── components/          # Reusable components
│   └── styles/              # Tailwind CSS
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── auth/            # Authentication
│   │   ├── billing/         # Stripe integration
│   │   ├── users/           # User management
│   │   └── admin/           # Admin endpoints
│   ├── database/            # Models and migrations
│   └── tests/               # API tests
├── docker-compose.yml       # Development setup
├── .github/workflows/       # CI/CD
└── docs/                    # API documentation
```

### Key Features

#### 1. User Authentication
```python
# backend/app/auth/routes.py
@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Password hashing with bcrypt
    # Email verification
    # JWT token generation
```

```jsx
// frontend/pages/auth/login.tsx
export default function Login() {
  // Form validation with react-hook-form
  // JWT storage and management
  // Protected routes
}
```

#### 2. Stripe Integration
```python
# backend/app/billing/stripe_service.py
class StripeService:
    def create_subscription(self, user_id: str, price_id: str):
        # Create Stripe customer
        # Set up subscription
        # Handle webhooks
```

```jsx
// frontend/components/billing/SubscriptionForm.tsx
export default function SubscriptionForm() {
  // Stripe Elements integration
  // Payment method collection
  // Subscription management
}
```

#### 3. Admin Dashboard
```python
# backend/app/admin/routes.py
@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(require_admin)
):
    # User analytics
    # Revenue reporting
    # System health
```

### Deployment

#### Local Development
```bash
# Start all services
docker-compose up

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Database: PostgreSQL on port 5432
```

#### Production Deployment
```bash
# Deploy to Vercel (frontend) and Railway (backend)
mw deploy --platform vercel
mw deploy --platform railway

# Or use Docker
docker build -t billing-platform .
docker run -p 3000:3000 billing-platform
```

### Environment Configuration

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/billing_db
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
JWT_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```

## Customization

### Adding New Features
1. **New API Endpoint**: Add to `backend/app/` with proper structure
2. **New Page**: Add to `frontend/pages/` with authentication
3. **New Component**: Add to `frontend/components/` with TypeScript
4. **Database Changes**: Create migration in `backend/database/migrations/`

### Styling
- **Theme**: Modify `frontend/tailwind.config.js`
- **Components**: Update `frontend/components/ui/`
- **Branding**: Change colors in `frontend/styles/globals.css`

### Integrations
- **Email**: Configured for SendGrid/Resend
- **Analytics**: Google Analytics ready
- **Monitoring**: Sentry integration included
- **Search**: Algolia ready components

## Examples of Generated Files

### User Model (Backend)
```python
# backend/app/users/models.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    subscription_status = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Dashboard Page (Frontend)
```tsx
// frontend/pages/dashboard/index.tsx
import { useSession } from "next-auth/react"
import Layout from "../../components/Layout"
import StatsCards from "../../components/dashboard/StatsCards"
import RecentActivity from "../../components/dashboard/RecentActivity"

export default function Dashboard() {
  const { data: session } = useSession()
  
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome, {session?.user?.name}
        </h1>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCards />
          <RecentActivity />
        </div>
      </div>
    </Layout>
  )
}
```

### API Tests
```python
# backend/tests/test_auth.py
def test_user_registration(client, db):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()
```

## Best Practices Included

- **Security**: HTTPS, CSRF protection, input validation
- **Performance**: Database indexing, API caching, CDN ready
- **Testing**: Unit tests, integration tests, E2E tests
- **Documentation**: API docs, code comments, README
- **Monitoring**: Error tracking, performance metrics, health checks

## Time Saved

- **Authentication System**: 20+ hours
- **Payment Integration**: 15+ hours
- **Admin Dashboard**: 25+ hours
- **DevOps Setup**: 10+ hours
- **Testing Infrastructure**: 8+ hours

**Total: 78+ hours of development time saved**