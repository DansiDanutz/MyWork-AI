# Marketplace Template Example

Build a complete peer-to-peer marketplace with buyer/seller profiles, payments, and review system.

## Quick Start

```bash
# Create a marketplace project
mw create marketplace service-hub

# Navigate to project
cd projects/service-hub

# Start development
docker-compose up
```

## What Gets Generated

### Multi-sided Platform
- **Buyer Interface**: Browse, search, purchase services
- **Seller Dashboard**: List services, manage orders, analytics
- **Admin Panel**: User moderation, dispute resolution
- **Messaging System**: In-app communication between users

### Core Features
- **Service Listings**: Categories, pricing, descriptions, images
- **User Profiles**: Reviews, ratings, verification badges
- **Payment Processing**: Stripe Connect for marketplace payments
- **Order Management**: Status tracking, delivery confirmation
- **Review System**: Two-way reviews, dispute handling

## Example Use Case: Freelance Services Platform

Let's build a platform for freelance services like design, writing, and consulting:

```bash
mw create marketplace freelance-hub
```

### Generated Structure
```
freelance-hub/
├── frontend/                 # Next.js marketplace UI
│   ├── pages/
│   │   ├── services/        # Service listings
│   │   ├── dashboard/       # Seller dashboard
│   │   ├── orders/          # Order management
│   │   ├── messages/        # Chat system
│   │   └── profile/         # User profiles
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── services/        # Service CRUD
│   │   ├── orders/          # Order processing
│   │   ├── payments/        # Stripe integration
│   │   ├── messaging/       # Chat API
│   │   └── reviews/         # Review system
├── database/                # PostgreSQL schemas
├── uploads/                 # File storage
└── websocket/               # Real-time messaging
```

### Key Features

#### 1. Service Management
```python
# backend/app/services/models.py
class Service(Base):
    __tablename__ = "services"
    
    id = Column(UUID, primary_key=True)
    seller_id = Column(UUID, ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(UUID, ForeignKey("categories.id"))
    price = Column(Numeric(10, 2))
    delivery_time = Column(Integer)  # days
    images = Column(JSON)  # array of image URLs
    status = Column(Enum(ServiceStatus))
    created_at = Column(DateTime)
    
    # Relationships
    seller = relationship("User", back_populates="services")
    orders = relationship("Order", back_populates="service")
    reviews = relationship("Review", back_populates="service")
```

```tsx
// frontend/components/services/ServiceCard.tsx
export default function ServiceCard({ service }: { service: Service }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <img src={service.images[0]} alt={service.title} />
      <h3 className="text-xl font-semibold">{service.title}</h3>
      <p className="text-gray-600">{service.description}</p>
      <div className="flex justify-between items-center mt-4">
        <span className="text-2xl font-bold">${service.price}</span>
        <button className="bg-blue-600 text-white px-4 py-2 rounded">
          Order Now
        </button>
      </div>
    </div>
  )
}
```

#### 2. Order Processing
```python
# backend/app/orders/service.py
class OrderService:
    def create_order(self, buyer_id: UUID, service_id: UUID, 
                    requirements: str) -> Order:
        # Create order with PENDING status
        # Hold payment with Stripe
        # Notify seller
        # Start delivery countdown
        
    def complete_order(self, order_id: UUID, deliverable_url: str):
        # Upload deliverable
        # Release payment to seller
        # Trigger review request
        # Update order status
```

```tsx
// frontend/pages/orders/[id].tsx
export default function OrderDetails({ order }: { order: Order }) {
  const [status, setStatus] = useState(order.status)
  
  const handleStatusUpdate = async (newStatus: OrderStatus) => {
    // Update order status
    // Send notifications
    // Handle payments
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <OrderHeader order={order} />
      <OrderTimeline status={status} />
      <DeliverableUpload orderId={order.id} />
      <MessageThread orderId={order.id} />
    </div>
  )
}
```

#### 3. Payment System (Stripe Connect)
```python
# backend/app/payments/stripe_service.py
class MarketplacePayments:
    def create_connected_account(self, user_id: UUID) -> str:
        """Create Stripe Connect account for sellers"""
        account = stripe.Account.create(
            type="standard",
            country="US",
            metadata={"user_id": str(user_id)}
        )
        return account.id
    
    def create_payment_intent(self, order: Order) -> str:
        """Hold payment until order completion"""
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # cents
            currency="usd",
            transfer_data={
                "destination": order.service.seller.stripe_account_id,
            },
            application_fee_amount=int(order.total * 0.05 * 100),  # 5% fee
        )
        return intent.client_secret
```

#### 4. Real-time Messaging
```python
# backend/app/messaging/websocket.py
from fastapi import WebSocket

class MessageManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def send_message(self, message: Message):
        # Store in database
        # Send to active connections
        # Push notification if offline
```

```tsx
// frontend/hooks/useChat.ts
export function useChat(orderId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [socket, setSocket] = useState<WebSocket | null>(null)
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat/${orderId}`)
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      setMessages(prev => [...prev, message])
    }
    
    setSocket(ws)
    return () => ws.close()
  }, [orderId])
  
  const sendMessage = (content: string) => {
    socket?.send(JSON.stringify({ content, orderId }))
  }
  
  return { messages, sendMessage }
}
```

#### 5. Review & Rating System
```python
# backend/app/reviews/models.py
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID, primary_key=True)
    order_id = Column(UUID, ForeignKey("orders.id"))
    reviewer_id = Column(UUID, ForeignKey("users.id"))
    reviewee_id = Column(UUID, ForeignKey("users.id"))
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text)
    review_type = Column(Enum(ReviewType))  # buyer_to_seller, seller_to_buyer
    created_at = Column(DateTime)
```

### Search & Filtering

#### Advanced Search
```python
# backend/app/services/search.py
def search_services(
    query: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    delivery_time: int = None,
    seller_rating: float = None
):
    filters = []
    
    if query:
        filters.append(Service.title.ilike(f"%{query}%"))
    if category:
        filters.append(Service.category_id == category)
    if min_price:
        filters.append(Service.price >= min_price)
    # ... more filters
    
    return db.query(Service).filter(*filters).all()
```

```tsx
// frontend/components/search/SearchFilters.tsx
export default function SearchFilters({ onFilterChange }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <PriceRangeSlider onChange={onFilterChange} />
      <CategorySelect onChange={onFilterChange} />
      <DeliveryTimeFilter onChange={onFilterChange} />
      <SellerRatingFilter onChange={onFilterChange} />
    </div>
  )
}
```

### Seller Dashboard

#### Analytics & Insights
```tsx
// frontend/pages/dashboard/seller/analytics.tsx
export default function SellerAnalytics() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Total Revenue"
        value="$12,350"
        change="+15%"
        icon={DollarSign}
      />
      <MetricCard
        title="Active Orders"
        value="23"
        change="+8%"
        icon={ShoppingBag}
      />
      <MetricCard
        title="Average Rating"
        value="4.8"
        change="+0.2"
        icon={Star}
      />
      <MetricCard
        title="Response Time"
        value="2.5h"
        change="-30%"
        icon={Clock}
      />
    </div>
  )
}
```

## Admin Panel Features

### User Management
- **User Verification**: ID verification, business verification
- **Dispute Resolution**: Automated and manual dispute handling
- **Content Moderation**: Service listing approval, review moderation
- **Analytics Dashboard**: Platform metrics, revenue tracking

### Trust & Safety
```python
# backend/app/admin/moderation.py
class ModerationService:
    def flag_suspicious_activity(self, user_id: UUID):
        # Check for fraudulent patterns
        # Temporarily suspend account
        # Notify admin team
        
    def verify_seller(self, user_id: UUID, documents: List[str]):
        # Verify identity documents
        # Enable advanced seller features
        # Update trust score
```

## Mobile Responsiveness

All components are built with mobile-first design:

```tsx
// Responsive service grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {services.map(service => (
    <ServiceCard key={service.id} service={service} />
  ))}
</div>
```

## Deployment Configuration

### Development
```bash
# Start all services
docker-compose up

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: PostgreSQL on 5432
# Redis: Cache on 6379
# Websocket: ws://localhost:8001
```

### Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
  
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/marketplace
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - REDIS_URL=redis://redis:6379
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
```

## Testing Strategy

### Backend Tests
```python
# tests/test_orders.py
def test_create_order_with_payment_hold():
    # Test order creation
    # Verify payment hold
    # Check seller notification
    
def test_order_completion_releases_payment():
    # Complete order
    # Verify payment release
    # Check review trigger
```

### Frontend Tests
```tsx
// __tests__/ServiceCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import ServiceCard from '../components/ServiceCard'

test('displays service information correctly', () => {
  const service = createMockService()
  render(<ServiceCard service={service} />)
  
  expect(screen.getByText(service.title)).toBeInTheDocument()
  expect(screen.getByText(`$${service.price}`)).toBeInTheDocument()
})
```

## Security Features

- **Payment Security**: PCI DSS compliance through Stripe
- **Data Protection**: GDPR compliant, encrypted data
- **Fraud Prevention**: Machine learning fraud detection
- **Identity Verification**: Document verification for sellers
- **Secure Messaging**: Encrypted in-app messaging

## Time Saved

- **User Authentication & Profiles**: 25+ hours
- **Payment Processing (Stripe Connect)**: 30+ hours
- **Order Management System**: 35+ hours
- **Messaging System**: 20+ hours
- **Review & Rating System**: 15+ hours
- **Search & Filtering**: 18+ hours
- **Admin Panel**: 30+ hours

**Total: 173+ hours of development time saved**