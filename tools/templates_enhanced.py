#!/usr/bin/env python3
"""
Enhanced Templates for MyWork-AI
=================================
Working, runnable templates for different project types.
"""

def get_fastapi_template(name):
    """Generate a complete, runnable FastAPI template."""
    return {
        "structure": {
            "main.py": f'''"""
{name} - FastAPI Application
===========================
A production-ready FastAPI application with database, CORS, and health checks.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Database setup
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={{"check_same_thread": False}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class ItemDB(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="{name} API",
    description="A production-ready FastAPI application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {{"status": "healthy", "timestamp": datetime.utcnow()}}

# Root endpoint
@app.get("/")
async def root():
    return {{
        "message": "Welcome to {name} API",
        "docs": "/docs",
        "health": "/health"
    }}

# CRUD endpoints
@app.post("/items/", response_model=Item)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    return items

@app.get("/items/{{item_id}}", response_model=Item)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
            "requirements.txt": '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
pydantic>=2.5.0
''',
            "tests/": {
                "__init__.py": "",
                "test_main.py": f'''"""
Tests for {name} API
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_and_get_item():
    # Create an item
    item_data = {{"name": "Test Item", "description": "A test item"}}
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    created_item = response.json()
    
    # Get the item
    response = client.get(f"/items/{{created_item['id']}}")
    assert response.status_code == 200
    item = response.json()
    assert item["name"] == "Test Item"

def test_get_items():
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
''',
            },
            ".env.example": f'''# {name} Environment Variables
DATABASE_URL=sqlite:///./database.db
DEBUG=true
''',
            "README.md": f'''# {name}

A production-ready FastAPI application with database, CORS, and health checks.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Open your browser to http://localhost:8000/docs to see the API documentation.

## Features

- ✅ FastAPI with automatic OpenAPI docs
- ✅ SQLite database with SQLAlchemy ORM
- ✅ CORS support
- ✅ Health check endpoint
- ✅ Basic CRUD operations
- ✅ Request/response validation with Pydantic
- ✅ Test suite

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /items/` - Create an item
- `GET /items/` - List items
- `GET /items/{{id}}` - Get specific item

## Testing

```bash
pip install pytest httpx
python -m pytest tests/
```

## Deployment

This app is ready to deploy to:
- Vercel: `mw deploy --platform vercel`
- Railway: `mw deploy --platform railway`
- Docker: See Dockerfile

## Development

- Run with auto-reload: `python main.py`
- Format code: `mw lint fix`
- Run tests: `mw test`
''',
            ".gitignore": '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

.env
.env.local
.env.*.local

database.db
*.sqlite
*.db

.vscode/
.idea/
*.swp
*.swo

.pytest_cache/
.coverage
htmlcov/
''',
        }
    }

def get_express_template(name):
    """Generate a complete, runnable Express.js template.""" 
    return {
        "structure": {
            "index.js": f'''/**
 * {name} - Express.js Application
 * ===============================
 * A production-ready Express.js application with CORS, error handling, and health checks.
 */
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // CORS support
app.use(morgan('combined')); // Logging
app.use(express.json()); // JSON body parser
app.use(express.urlencoded({{ extended: true }})); // URL-encoded body parser

// In-memory data store (replace with database in production)
let items = [
    {{ id: 1, name: 'Sample Item', description: 'This is a sample item', createdAt: new Date() }}
];
let nextId = 2;

// Health check endpoint
app.get('/health', (req, res) => {{
    res.json({{
        status: 'healthy',
        timestamp: new Date(),
        uptime: process.uptime()
    }});
}});

// Root endpoint
app.get('/', (req, res) => {{
    res.json({{
        message: 'Welcome to {name} API',
        version: '1.0.0',
        endpoints: {{
            health: '/health',
            items: '/api/items'
        }}
    }});
}});

// Get all items
app.get('/api/items', (req, res) => {{
    const {{ limit = 10, offset = 0 }} = req.query;
    const start = parseInt(offset);
    const end = start + parseInt(limit);
    const paginatedItems = items.slice(start, end);
    
    res.json({{
        data: paginatedItems,
        total: items.length,
        limit: parseInt(limit),
        offset: parseInt(offset)
    }});
}});

// Get single item
app.get('/api/items/:id', (req, res) => {{
    const id = parseInt(req.params.id);
    const item = items.find(i => i.id === id);
    
    if (!item) {{
        return res.status(404).json({{ error: 'Item not found' }});
    }}
    
    res.json(item);
}});

// Create new item
app.post('/api/items', (req, res) => {{
    const {{ name, description }} = req.body;
    
    if (!name) {{
        return res.status(400).json({{ error: 'Name is required' }});
    }}
    
    const newItem = {{
        id: nextId++,
        name,
        description: description || '',
        createdAt: new Date()
    }};
    
    items.push(newItem);
    res.status(201).json(newItem);
}});

// Update item
app.put('/api/items/:id', (req, res) => {{
    const id = parseInt(req.params.id);
    const itemIndex = items.findIndex(i => i.id === id);
    
    if (itemIndex === -1) {{
        return res.status(404).json({{ error: 'Item not found' }});
    }}
    
    const {{ name, description }} = req.body;
    items[itemIndex] = {{
        ...items[itemIndex],
        name: name || items[itemIndex].name,
        description: description || items[itemIndex].description,
        updatedAt: new Date()
    }};
    
    res.json(items[itemIndex]);
}});

// Delete item
app.delete('/api/items/:id', (req, res) => {{
    const id = parseInt(req.params.id);
    const itemIndex = items.findIndex(i => i.id === id);
    
    if (itemIndex === -1) {{
        return res.status(404).json({{ error: 'Item not found' }});
    }}
    
    const deletedItem = items.splice(itemIndex, 1)[0];
    res.json({{ message: 'Item deleted', item: deletedItem }});
}});

// Error handling middleware
app.use((err, req, res, next) => {{
    console.error(err.stack);
    res.status(500).json({{ error: 'Something went wrong!' }});
}});

// 404 handler
app.use((req, res) => {{
    res.status(404).json({{ error: 'Route not found' }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(`🚀 {name} server running on http://localhost:${{PORT}}`);
    console.log(`📚 Health check: http://localhost:${{PORT}}/health`);
    console.log(`🔍 API endpoints: http://localhost:${{PORT}}/api/items`);
}});

module.exports = app;
''',
            "package.json": f'''{{
  "name": "{name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "description": "A production-ready Express.js application",
  "main": "index.js",
  "scripts": {{
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest",
    "test:watch": "jest --watch"
  }},
  "dependencies": {{
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "morgan": "^1.10.0",
    "helmet": "^7.1.0",
    "dotenv": "^16.3.1"
  }},
  "devDependencies": {{
    "nodemon": "^3.0.2",
    "jest": "^29.7.0",
    "supertest": "^6.3.3"
  }},
  "keywords": ["express", "api", "rest"],
  "author": "MyWork-AI",
  "license": "MIT"
}}
''',
            "tests/": {
                "app.test.js": f'''/**
 * Tests for {name} API
 */
const request = require('supertest');
const app = require('../index');

describe('{name} API', () => {{
    test('GET / should return welcome message', async () => {{
        const response = await request(app).get('/');
        expect(response.status).toBe(200);
        expect(response.body.message).toContain('Welcome');
    }});

    test('GET /health should return health status', async () => {{
        const response = await request(app).get('/health');
        expect(response.status).toBe(200);
        expect(response.body.status).toBe('healthy');
    }});

    test('GET /api/items should return items list', async () => {{
        const response = await request(app).get('/api/items');
        expect(response.status).toBe(200);
        expect(Array.isArray(response.body.data)).toBe(true);
    }});

    test('POST /api/items should create new item', async () => {{
        const newItem = {{ name: 'Test Item', description: 'Test Description' }};
        const response = await request(app)
            .post('/api/items')
            .send(newItem);
        expect(response.status).toBe(201);
        expect(response.body.name).toBe(newItem.name);
    }});

    test('POST /api/items without name should return error', async () => {{
        const response = await request(app)
            .post('/api/items')
            .send({{ description: 'No name' }});
        expect(response.status).toBe(400);
        expect(response.body.error).toContain('Name is required');
    }});
}});
''',
            },
            ".env.example": f'''# {name} Environment Variables
PORT=3000
NODE_ENV=development
''',
            "README.md": f'''# {name}

A production-ready Express.js application with CORS, error handling, and health checks.

## Quick Start

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the application:
   ```bash
   npm start
   ```

3. For development with auto-reload:
   ```bash
   npm run dev
   ```

4. Open your browser to http://localhost:3000 to see the API.

## Features

- ✅ Express.js with production middleware
- ✅ CORS support
- ✅ Security headers with Helmet
- ✅ Request logging with Morgan
- ✅ Health check endpoint
- ✅ RESTful CRUD API
- ✅ Error handling
- ✅ Test suite with Jest

## API Endpoints

- `GET /` - Welcome message and API info
- `GET /health` - Health check with uptime
- `GET /api/items` - List all items (with pagination)
- `GET /api/items/:id` - Get specific item
- `POST /api/items` - Create new item
- `PUT /api/items/:id` - Update existing item
- `DELETE /api/items/:id` - Delete item

## Testing

```bash
npm test
npm run test:watch  # Watch mode
```

## Deployment

This app is ready to deploy to:
- Vercel: `mw deploy --platform vercel`
- Railway: `mw deploy --platform railway`
- Heroku: Standard Node.js deployment

## Development

- Development server: `npm run dev`
- Format code: `mw lint fix`
- Run tests: `mw test`

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (development/production)
''',
            ".gitignore": '''node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
coverage/
.nyc_output
.cache
dist/
build/
.DS_Store
*.log
''',
        }
    }