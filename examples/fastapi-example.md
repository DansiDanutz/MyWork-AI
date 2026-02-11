# FastAPI Template Example

Build a modern, high-performance REST API with FastAPI, SQLAlchemy, and PostgreSQL.

## Quick Start

```bash
# Create a FastAPI project
mw create fastapi task-api

# Navigate to project
cd projects/task-api

# Start development server
uvicorn main:app --reload
```

## What Gets Generated

### Core API Features
- **SQLAlchemy ORM**: Database models and relationships
- **Pydantic Schemas**: Request/response validation
- **Authentication**: JWT token-based auth
- **CRUD Operations**: Create, Read, Update, Delete endpoints
- **Database Migrations**: Alembic for schema changes
- **API Documentation**: Auto-generated OpenAPI docs

### Production Ready
- **Docker Support**: Development and production containers
- **Testing**: Pytest with test database
- **Logging**: Structured logging with correlation IDs
- **Error Handling**: Global exception handlers
- **Rate Limiting**: Request throttling
- **Health Checks**: Endpoint monitoring

## Example Use Case: Task Management API

Let's build a REST API for task management with users, projects, and tasks:

```bash
mw create fastapi task-manager-api
```

### Generated Structure
```
task-manager-api/
├── app/
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── projects.py
│   │   └── tasks.py
│   ├── core/                # Core utilities
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── deps.py
│   ├── tests/               # Test suite
│   └── main.py              # FastAPI app
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container setup
└── docker-compose.yml      # Development environment
```

### Key Features

#### 1. Database Models
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", back_populates="assignee")
```

```python
# app/models/task.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

class TaskStatus(PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
```

#### 2. Pydantic Schemas
```python
# app/schemas/task.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

class Task(TaskBase):
    id: int
    status: TaskStatus
    project_id: int
    assignee_id: Optional[int]
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
```

#### 3. API Routes
```python
# app/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.task import Task as TaskModel, TaskStatus
from app.schemas.task import Task, TaskCreate, TaskUpdate

router = APIRouter()

@router.get("/", response_model=List[Task])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[TaskStatus] = None,
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List tasks with filtering and pagination."""
    query = db.query(TaskModel)
    
    # Apply filters
    if status:
        query = query.filter(TaskModel.status == status)
    if project_id:
        query = query.filter(TaskModel.project_id == project_id)
    if assignee_id:
        query = query.filter(TaskModel.assignee_id == assignee_id)
    
    # User can only see tasks from their projects or assigned to them
    if not current_user.is_superuser:
        query = query.filter(
            (TaskModel.assignee_id == current_user.id) |
            (TaskModel.project.has(owner_id=current_user.id))
        )
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task."""
    # Verify user has access to the project
    project = db.query(ProjectModel).filter(
        ProjectModel.id == task_data.project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create task
    task = TaskModel(
        **task_data.dict(),
        created_by_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific task."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if (task.assignee_id != current_user.id and 
        task.project.owner_id != current_user.id and 
        not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a task."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if (task.project.owner_id != current_user.id and 
        not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    
    # Handle status change to 'done'
    if update_data.get("status") == TaskStatus.DONE:
        update_data["completed_at"] = datetime.utcnow()
    elif update_data.get("status") != TaskStatus.DONE:
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions
    if (task.project.owner_id != current_user.id and 
        not current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(task)
    db.commit()
```

#### 4. Authentication & Security
```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)
```

```python
# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

#### 5. Configuration Management
```python
# app/core/config.py
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Task Manager API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/taskmanager"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Database Migrations

#### Alembic Setup
```python
# alembic/versions/001_initial_migration.py
"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

def downgrade():
    op.drop_table('users')
```

### Testing

#### Test Configuration
```python
# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/api/auth/register", json=user_data)
    return response.json()
```

#### API Tests
```python
# app/tests/test_tasks.py
def test_create_task(client, test_user, auth_headers):
    project_data = {"name": "Test Project", "description": "Test"}
    project_response = client.post("/api/projects/", json=project_data, headers=auth_headers)
    project_id = project_response.json()["id"]
    
    task_data = {
        "title": "Test Task",
        "description": "Test task description",
        "priority": "high",
        "project_id": project_id
    }
    
    response = client.post("/api/tasks/", json=task_data, headers=auth_headers)
    
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Test Task"
    assert task["priority"] == "high"
    assert task["status"] == "todo"

def test_update_task_status(client, test_user, auth_headers):
    # Create task first
    # ... setup code ...
    
    update_data = {"status": "done"}
    response = client.put(f"/api/tasks/{task_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    task = response.json()
    assert task["status"] == "done"
    assert task["completed_at"] is not None
```

### API Documentation

The FastAPI template includes automatic API documentation:

- **Swagger UI**: Available at `http://localhost:8000/docs`
- **ReDoc**: Available at `http://localhost:8000/redoc`
- **OpenAPI JSON**: Available at `http://localhost:8000/openapi.json`

### Performance Features

#### Database Optimization
```python
# Eager loading relationships
tasks = db.query(Task).options(
    joinedload(Task.project),
    joinedload(Task.assignee)
).all()

# Pagination with cursor
def paginate_tasks(cursor: Optional[int] = None, limit: int = 20):
    query = db.query(Task)
    if cursor:
        query = query.filter(Task.id > cursor)
    return query.order_by(Task.id).limit(limit).all()
```

#### Caching
```python
# app/core/cache.py
import redis
from typing import Optional
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_get(key: str) -> Optional[dict]:
    """Get value from cache."""
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None

def cache_set(key: str, value: dict, expire_seconds: int = 300):
    """Set value in cache."""
    redis_client.setex(key, expire_seconds, json.dumps(value, default=str))
```

### Deployment

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/taskmanager
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: taskmanager
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Time Saved

- **Project Setup & Configuration**: 8+ hours
- **Database Models & Migrations**: 12+ hours
- **Authentication System**: 15+ hours
- **CRUD Operations**: 20+ hours
- **API Documentation**: 5+ hours
- **Testing Infrastructure**: 10+ hours
- **Docker & Deployment**: 8+ hours

**Total: 78+ hours of development time saved**