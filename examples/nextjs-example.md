# Next.js Template Example

Build a modern, production-ready frontend application with Next.js 14, TypeScript, and Tailwind CSS.

## Quick Start

```bash
# Create a Next.js project
mw create nextjs analytics-dashboard

# Navigate to project
cd projects/analytics-dashboard

# Start development server
npm run dev
```

## What Gets Generated

### Modern Frontend Stack
- **Next.js 14**: App Router, Server Components, Server Actions
- **TypeScript**: Full type safety and IntelliSense
- **Tailwind CSS**: Utility-first styling with custom components
- **Authentication**: NextAuth.js with multiple providers
- **State Management**: Zustand for client state
- **API Integration**: SWR for data fetching and caching

### Production Features
- **SEO Optimized**: Meta tags, Open Graph, structured data
- **Performance**: Image optimization, lazy loading, code splitting
- **PWA Ready**: Service worker, offline support, installable
- **Responsive**: Mobile-first design with dark mode
- **Testing**: Jest + Testing Library setup
- **CI/CD**: GitHub Actions for deployment

## Example Use Case: Analytics Dashboard

Let's build a business analytics dashboard with charts, metrics, and real-time data:

```bash
mw create nextjs analytics-dashboard
```

### Generated Structure
```
analytics-dashboard/
├── app/                     # Next.js 14 App Router
│   ├── (auth)/             # Auth route group
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/          # Protected dashboard
│   │   ├── analytics/
│   │   ├── reports/
│   │   └── settings/
│   ├── api/                # API routes
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/             # Reusable components
│   ├── ui/                 # Base UI components
│   ├── charts/             # Chart components
│   ├── forms/              # Form components
│   └── layout/             # Layout components
├── lib/                    # Utilities and configurations
│   ├── auth.ts             # Auth configuration
│   ├── api.ts              # API client
│   ├── utils.ts            # Helper functions
│   └── validations.ts      # Zod schemas
├── hooks/                  # Custom React hooks
├── stores/                 # Zustand stores
├── types/                  # TypeScript definitions
└── public/                 # Static assets
```

### Key Features

#### 1. Dashboard Layout
```tsx
// app/dashboard/layout.tsx
import { Metadata } from 'next'
import Sidebar from '@/components/layout/Sidebar'
import Header from '@/components/layout/Header'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { redirect } from 'next/navigation'

export const metadata: Metadata = {
  title: 'Dashboard | Analytics Platform',
  description: 'Comprehensive business analytics dashboard',
}

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await getServerSession(authOptions)
  
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar />
      <div className="lg:pl-64">
        <Header user={session.user} />
        <main className="py-6 px-4 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  )
}
```

#### 2. Data Fetching with SWR
```tsx
// hooks/useAnalytics.ts
import useSWR from 'swr'
import { fetcher } from '@/lib/api'

export interface AnalyticsData {
  revenue: number
  users: number
  conversions: number
  growth: number
}

export function useAnalytics(timeRange: string = '7d') {
  const { data, error, isLoading, mutate } = useSWR<AnalyticsData>(
    `/api/analytics?range=${timeRange}`,
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
    }
  )

  return {
    analytics: data,
    isLoading,
    error,
    refresh: mutate,
  }
}
```

```tsx
// app/dashboard/page.tsx
'use client'

import { useAnalytics } from '@/hooks/useAnalytics'
import MetricCard from '@/components/dashboard/MetricCard'
import Chart from '@/components/charts/Chart'
import { useState } from 'react'

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState('7d')
  const { analytics, isLoading, error } = useAnalytics(timeRange)

  if (error) {
    return <ErrorState error={error} />
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Revenue"
          value={analytics?.revenue ?? 0}
          format="currency"
          trend="up"
          loading={isLoading}
        />
        <MetricCard
          title="Users"
          value={analytics?.users ?? 0}
          format="number"
          trend="up"
          loading={isLoading}
        />
        <MetricCard
          title="Conversions"
          value={analytics?.conversions ?? 0}
          format="percentage"
          trend="down"
          loading={isLoading}
        />
        <MetricCard
          title="Growth"
          value={analytics?.growth ?? 0}
          format="percentage"
          trend="up"
          loading={isLoading}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart
          title="Revenue Trend"
          type="line"
          timeRange={timeRange}
          loading={isLoading}
        />
        <Chart
          title="User Acquisition"
          type="bar"
          timeRange={timeRange}
          loading={isLoading}
        />
      </div>
    </div>
  )
}
```

#### 3. Reusable UI Components
```tsx
// components/ui/MetricCard.tsx
import { TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: number | string
  format?: 'number' | 'currency' | 'percentage'
  trend?: 'up' | 'down' | 'neutral'
  loading?: boolean
  className?: string
}

export default function MetricCard({
  title,
  value,
  format = 'number',
  trend = 'neutral',
  loading = false,
  className,
}: MetricCardProps) {
  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(val)
      case 'percentage':
        return `${val}%`
      default:
        return new Intl.NumberFormat('en-US').format(val)
    }
  }

  if (loading) {
    return (
      <div className={cn('bg-white p-6 rounded-lg shadow', className)}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
          <div className="h-8 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('bg-white p-6 rounded-lg shadow', className)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatValue(value)}
          </p>
        </div>
        {trend !== 'neutral' && (
          <div
            className={cn(
              'flex items-center text-sm',
              trend === 'up' ? 'text-green-600' : 'text-red-600'
            )}
          >
            {trend === 'up' ? (
              <TrendingUp className="h-4 w-4 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 mr-1" />
            )}
            <span>{trend === 'up' ? '+' : '-'}12%</span>
          </div>
        )}
      </div>
    </div>
  )
}
```

#### 4. Authentication (NextAuth.js)
```ts
// lib/auth.ts
import { NextAuthOptions } from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import CredentialsProvider from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@auth/prisma-adapter'
import { prisma } from './prisma'
import { compare } from 'bcryptjs'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: 'jwt',
  },
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: {
            email: credentials.email,
          },
        })

        if (!user) {
          return null
        }

        const isPasswordValid = await compare(
          credentials.password,
          user.password
        )

        if (!isPasswordValid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
        }
      },
    }),
  ],
  callbacks: {
    session: ({ session, token }) => ({
      ...session,
      user: {
        ...session.user,
        id: token.id,
        role: token.role,
      },
    }),
    jwt: ({ user, token }) => {
      if (user) {
        return {
          ...token,
          id: user.id,
          role: user.role,
        }
      }
      return token
    },
  },
  pages: {
    signIn: '/login',
    signUp: '/register',
  },
}
```

#### 5. State Management (Zustand)
```ts
// stores/useUserStore.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string
  role: string
}

interface UserState {
  user: User | null
  preferences: {
    theme: 'light' | 'dark' | 'system'
    timezone: string
    language: string
  }
  setUser: (user: User | null) => void
  updatePreferences: (prefs: Partial<UserState['preferences']>) => void
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        preferences: {
          theme: 'system',
          timezone: 'UTC',
          language: 'en',
        },
        setUser: (user) => set({ user }),
        updatePreferences: (prefs) =>
          set((state) => ({
            preferences: { ...state.preferences, ...prefs },
          })),
      }),
      {
        name: 'user-storage',
      }
    )
  )
)
```

#### 6. Charts with Recharts
```tsx
// components/charts/LineChart.tsx
'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useTheme } from 'next-themes'

interface ChartData {
  date: string
  value: number
}

interface LineChartProps {
  data: ChartData[]
  title: string
  loading?: boolean
}

export default function CustomLineChart({ data, title, loading }: LineChartProps) {
  const { theme } = useTheme()
  
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-64 bg-gray-100 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            stroke={theme === 'dark' ? '#9CA3AF' : '#6B7280'}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            stroke={theme === 'dark' ? '#9CA3AF' : '#6B7280'}
          />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#3B82F6" 
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

### Advanced Features

#### 1. SEO Optimization
```tsx
// app/layout.tsx
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    template: '%s | Analytics Platform',
    default: 'Analytics Platform',
  },
  description: 'Comprehensive business analytics and insights platform',
  keywords: ['analytics', 'dashboard', 'business intelligence'],
  authors: [{ name: 'Your Company' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://yourapp.com',
    title: 'Analytics Platform',
    description: 'Comprehensive business analytics platform',
    siteName: 'Analytics Platform',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Analytics Platform',
    description: 'Comprehensive business analytics platform',
    creator: '@yourcompany',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}
```

#### 2. Error Boundaries
```tsx
// components/ErrorBoundary.tsx
'use client'

import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center text-red-500 mb-4">
              <AlertTriangle className="h-6 w-6 mr-2" />
              <h1 className="text-lg font-semibold">Something went wrong</h1>
            </div>
            <p className="text-gray-600 mb-4">
              An unexpected error occurred. Please try refreshing the page.
            </p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
            >
              Try again
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
```

#### 3. PWA Configuration
```ts
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
})

module.exports = withPWA({
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
})
```

### Testing

#### Component Tests
```tsx
// __tests__/components/MetricCard.test.tsx
import { render, screen } from '@testing-library/react'
import MetricCard from '@/components/ui/MetricCard'

describe('MetricCard', () => {
  it('renders metric card correctly', () => {
    render(
      <MetricCard
        title="Revenue"
        value={12500}
        format="currency"
        trend="up"
      />
    )

    expect(screen.getByText('Revenue')).toBeInTheDocument()
    expect(screen.getByText('$12,500')).toBeInTheDocument()
    expect(screen.getByText('+12%')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(<MetricCard title="Revenue" value={0} loading={true} />)
    
    expect(screen.getByText('Revenue')).not.toBeInTheDocument()
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument()
  })
})
```

### Deployment

#### Vercel Configuration
```json
// vercel.json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "devCommand": "next dev",
  "installCommand": "npm install",
  "env": {
    "NEXTAUTH_SECRET": "@nextauth-secret",
    "GOOGLE_CLIENT_ID": "@google-client-id",
    "GOOGLE_CLIENT_SECRET": "@google-client-secret",
    "DATABASE_URL": "@database-url"
  },
  "build": {
    "env": {
      "NODE_ENV": "production"
    }
  }
}
```

#### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build application
        run: npm run build
      
      - name: Deploy to Vercel
        uses: vercel/action@v24
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## Time Saved

- **Next.js 14 Setup & Configuration**: 6+ hours
- **TypeScript Configuration**: 4+ hours
- **Authentication System**: 12+ hours
- **UI Component Library**: 25+ hours
- **State Management Setup**: 5+ hours
- **Testing Infrastructure**: 8+ hours
- **PWA & SEO Setup**: 6+ hours
- **Deployment Configuration**: 4+ hours

**Total: 70+ hours of development time saved**