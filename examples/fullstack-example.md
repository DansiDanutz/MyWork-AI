# Fullstack Template Example

Build a complete full-stack application combining FastAPI backend with Next.js frontend, including authentication, database, and deployment.

## Quick Start

```bash
# Create a fullstack project
mw create fullstack task-management

# Navigate to project
cd projects/task-management

# Start development (both frontend and backend)
docker-compose up
```

## What Gets Generated

### Complete Application Stack
- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Authentication**: Unified JWT auth across frontend/backend
- **Database**: PostgreSQL with migrations and seeding
- **DevOps**: Docker, CI/CD, environment management
- **Testing**: Full test suites for both frontend and backend

### Integrated Features
- **Shared TypeScript Types**: Type safety across the stack
- **Real-time Updates**: WebSocket integration
- **File Uploads**: Image/document handling
- **Email System**: Transactional email with templates
- **Admin Dashboard**: User and content management
- **API Documentation**: Auto-generated and interactive

## Example Use Case: Task Management Platform

Let's build a collaborative task management platform with teams, projects, and real-time updates:

```bash
mw create fullstack task-platform
```

### Generated Structure
```
task-platform/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration & utilities
│   │   ├── services/       # Business logic
│   │   └── tests/          # Backend tests
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/               # Next.js application
│   ├── app/                # App router pages
│   ├── components/         # React components
│   ├── lib/                # Utilities & configurations
│   ├── hooks/              # Custom hooks
│   ├── types/              # Shared TypeScript types
│   └── __tests__/          # Frontend tests
├── shared/                 # Shared utilities
│   ├── types/              # Common TypeScript interfaces
│   └── constants/          # Shared constants
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
└── docs/                   # Project documentation
```

### Key Features

#### 1. Shared Type Definitions
```ts
// shared/types/index.ts
export interface User {
  id: string
  email: string
  username: string
  full_name: string
  avatar_url?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  name: string
  description?: string
  owner_id: string
  team_id?: string
  status: ProjectStatus
  created_at: string
  updated_at: string
  
  // Relations
  owner?: User
  team?: Team
  tasks?: Task[]
  members?: ProjectMember[]
}

export interface Task {
  id: string
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  project_id: string
  assignee_id?: string
  created_by_id: string
  due_date?: string
  completed_at?: string
  created_at: string
  updated_at: string
  
  // Relations
  project?: Project
  assignee?: User
  created_by?: User
  comments?: TaskComment[]
  attachments?: TaskAttachment[]
}

export enum TaskStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  REVIEW = 'review',
  DONE = 'done'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}
```

#### 2. Backend API with Comprehensive Routes
```python
# backend/app/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.task import Task as TaskModel
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services.notification import NotificationService
from app.services.websocket import WebSocketManager

router = APIRouter()
notification_service = NotificationService()
websocket_manager = WebSocketManager()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new task with notifications and real-time updates."""
    
    # Verify project access
    project = await verify_project_access(task_data.project_id, current_user, db)
    
    # Create task
    task = TaskModel(
        **task_data.dict(),
        created_by_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Background tasks for notifications
    background_tasks.add_task(
        notification_service.send_task_created_notification,
        task.id,
        current_user.id
    )
    
    # Real-time update via WebSocket
    await websocket_manager.broadcast_to_project(
        project.id,
        {
            "type": "task_created",
            "task": task.dict(),
            "created_by": current_user.dict()
        }
    )
    
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update task with change tracking and notifications."""
    
    task = await get_task_or_404(task_id, db)
    await verify_task_access(task, current_user)
    
    # Track changes for notifications
    changes = track_task_changes(task, task_update)
    
    # Update task
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    # Send notifications for significant changes
    if changes:
        background_tasks.add_task(
            notification_service.send_task_updated_notification,
            task.id,
            changes,
            current_user.id
        )
    
    # Real-time update
    await websocket_manager.broadcast_to_project(
        task.project_id,
        {
            "type": "task_updated",
            "task": task.dict(),
            "changes": changes,
            "updated_by": current_user.dict()
        }
    )
    
    return task

# Real-time WebSocket endpoint
@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await websocket_manager.connect(websocket, project_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time updates, typing indicators, etc.
            await websocket_manager.broadcast_to_project(
                project_id,
                json.loads(data)
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, project_id)
```

#### 3. Frontend with Real-time Updates
```tsx
// frontend/components/tasks/TaskBoard.tsx
'use client'

import { useState, useEffect } from 'react'
import { Task, TaskStatus, Project } from '@/shared/types'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useTasks } from '@/hooks/useTasks'
import TaskColumn from './TaskColumn'
import TaskModal from './TaskModal'

interface TaskBoardProps {
  project: Project
}

export default function TaskBoard({ project }: TaskBoardProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false)
  
  const { tasks, createTask, updateTask, deleteTask, isLoading } = useTasks(project.id)
  
  // Real-time WebSocket connection
  const { sendMessage } = useWebSocket(`/api/tasks/ws/${project.id}`, {
    onMessage: (data) => {
      switch (data.type) {
        case 'task_created':
          // Optimistically update local state
          mutate(prev => prev ? [...prev, data.task] : [data.task])
          showNotification(`${data.created_by.full_name} created a new task: ${data.task.title}`)
          break
        case 'task_updated':
          // Update specific task in local state
          mutate(prev => prev?.map(task => 
            task.id === data.task.id ? data.task : task
          ))
          if (data.changes.status) {
            showNotification(`Task "${data.task.title}" moved to ${data.task.status}`)
          }
          break
        case 'task_deleted':
          mutate(prev => prev?.filter(task => task.id !== data.task_id))
          break
      }
    }
  })

  const groupedTasks = tasks?.reduce((acc, task) => {
    if (!acc[task.status]) acc[task.status] = []
    acc[task.status].push(task)
    return acc
  }, {} as Record<TaskStatus, Task[]>) || {}

  const handleTaskMove = async (taskId: string, newStatus: TaskStatus) => {
    // Optimistic update
    const updatedTasks = tasks?.map(task => 
      task.id === taskId ? { ...task, status: newStatus } : task
    )
    mutate(updatedTasks, false) // Don't revalidate immediately
    
    try {
      await updateTask(taskId, { status: newStatus })
    } catch (error) {
      // Revert on error
      mutate()
      showError('Failed to update task')
    }
  }

  if (isLoading) {
    return <TaskBoardSkeleton />
  }

  return (
    <div className="h-full flex flex-col">
      {/* Board Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{project.name}</h1>
        <button
          onClick={() => setIsTaskModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add Task
        </button>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto">
        <div className="flex space-x-6 min-w-max pb-6">
          {Object.values(TaskStatus).map((status) => (
            <TaskColumn
              key={status}
              status={status}
              tasks={groupedTasks[status] || []}
              onTaskClick={setSelectedTask}
              onTaskMove={handleTaskMove}
            />
          ))}
        </div>
      </div>

      {/* Task Modal */}
      <TaskModal
        task={selectedTask}
        isOpen={isTaskModalOpen || selectedTask !== null}
        onClose={() => {
          setIsTaskModalOpen(false)
          setSelectedTask(null)
        }}
        onSave={(taskData) => {
          if (selectedTask) {
            updateTask(selectedTask.id, taskData)
          } else {
            createTask({ ...taskData, project_id: project.id })
          }
        }}
        onDelete={selectedTask ? () => deleteTask(selectedTask.id) : undefined}
      />
    </div>
  )
}
```

#### 4. Custom Hooks for API Integration
```tsx
// frontend/hooks/useTasks.ts
import useSWR from 'swr'
import { Task, TaskCreate, TaskUpdate } from '@/shared/types'
import { api } from '@/lib/api'

export function useTasks(projectId: string) {
  const { data: tasks, error, mutate } = useSWR<Task[]>(
    projectId ? `/api/tasks?project_id=${projectId}` : null,
    api.get,
    {
      revalidateOnFocus: false,
      refreshInterval: 0, // Rely on WebSocket for updates
    }
  )

  const createTask = async (taskData: TaskCreate): Promise<Task> => {
    const newTask = await api.post('/api/tasks/', taskData)
    mutate(prev => prev ? [...prev, newTask] : [newTask], false)
    return newTask
  }

  const updateTask = async (taskId: string, update: TaskUpdate): Promise<Task> => {
    const updatedTask = await api.put(`/api/tasks/${taskId}`, update)
    mutate(prev => prev?.map(task => 
      task.id === taskId ? updatedTask : task
    ), false)
    return updatedTask
  }

  const deleteTask = async (taskId: string): Promise<void> => {
    await api.delete(`/api/tasks/${taskId}`)
    mutate(prev => prev?.filter(task => task.id !== taskId), false)
  }

  return {
    tasks,
    isLoading: !error && !tasks,
    error,
    createTask,
    updateTask,
    deleteTask,
    mutate,
  }
}
```

```tsx
// frontend/hooks/useWebSocket.ts
import { useEffect, useRef } from 'react'
import { useSession } from 'next-auth/react'

interface UseWebSocketOptions {
  onMessage?: (data: any) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const { data: session } = useSession()
  const websocket = useRef<WebSocket | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = () => {
    if (!session?.accessToken) return

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}${url}`
    const ws = new WebSocket(`${wsUrl}?token=${session.accessToken}`)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      reconnectAttempts.current = 0
      options.onConnect?.()
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        options.onMessage?.(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      options.onDisconnect?.()
      
      // Attempt reconnection
      if (reconnectAttempts.current < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.current++
          connect()
        }, Math.pow(2, reconnectAttempts.current) * 1000) // Exponential backoff
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    websocket.current = ws
  }

  const sendMessage = (data: any) => {
    if (websocket.current?.readyState === WebSocket.OPEN) {
      websocket.current.send(JSON.stringify(data))
    }
  }

  const disconnect = () => {
    websocket.current?.close()
  }

  useEffect(() => {
    if (session?.accessToken) {
      connect()
    }
    
    return () => disconnect()
  }, [session?.accessToken, url])

  return { sendMessage, disconnect }
}
```

#### 5. Integrated Authentication
```python
# backend/app/core/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

```ts
// frontend/lib/auth.ts
import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null

        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (!response.ok) return null

          const data = await response.json()
          
          return {
            id: data.user.id,
            email: data.user.email,
            name: data.user.full_name,
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
          }
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    jwt: async ({ token, user, account }) => {
      if (user) {
        token.accessToken = user.accessToken
        token.refreshToken = user.refreshToken
      }
      
      // Refresh token if needed
      if (token.accessToken && isTokenExpired(token.accessToken)) {
        const newTokens = await refreshAccessToken(token.refreshToken)
        if (newTokens) {
          token.accessToken = newTokens.accessToken
          token.refreshToken = newTokens.refreshToken
        }
      }
      
      return token
    },
    session: async ({ session, token }) => {
      session.accessToken = token.accessToken
      return session
    },
  },
  pages: {
    signIn: '/auth/signin',
    signUp: '/auth/signup',
  },
}
```

### Production Deployment

#### Docker Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/taskplatform
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
      - NEXTAUTH_URL=https://yourdomain.com
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: taskplatform
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy Full Stack

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      
      - name: Test Frontend
        run: |
          cd frontend
          npm ci
          npm run test
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          # Deploy backend to Railway/Heroku
          # Deploy frontend to Vercel
          # Update database migrations
```

## Time Saved

- **Full Stack Setup & Configuration**: 15+ hours
- **Authentication Integration**: 20+ hours
- **Real-time WebSocket Implementation**: 25+ hours
- **Database Design & Migrations**: 15+ hours
- **API Development & Testing**: 30+ hours
- **Frontend Components & State Management**: 35+ hours
- **DevOps & Deployment Setup**: 18+ hours
- **Integration & E2E Testing**: 12+ hours

**Total: 170+ hours of development time saved**

This fullstack template provides a complete, production-ready foundation for modern web applications with real-time features, comprehensive testing, and scalable architecture.