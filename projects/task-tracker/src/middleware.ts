import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

type RateLimitResult = { success: boolean; remaining: number; reset: number }
type RatelimitInstance = { limit: (identifier: string) => Promise<RateLimitResult> }

// Rate limiting (optional - only when Upstash is configured)
// Note: Middleware must not use top-level await, so we handle this at runtime
let ratelimit: RatelimitInstance | null = null
let ratelimitInitialized = false

async function initRatelimit() {
  if (ratelimitInitialized) return
  ratelimitInitialized = true

  if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    try {
      const { Ratelimit } = await import('@upstash/ratelimit')
      const { Redis } = await import('@upstash/redis')

      ratelimit = new Ratelimit({
        redis: Redis.fromEnv(),
        limiter: Ratelimit.slidingWindow(60, '1 m'), // 60 requests per minute
        analytics: true,
      })
    } catch {
      console.warn('Rate limiting disabled: Upstash dependencies not available')
    }
  }
}

// Routes that require authentication
const protectedRoutes = ['/settings', '/dashboard', '/tasks']

// Routes that authenticated users should be redirected away from
const authRoutes = ['/login']

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Initialize rate limiting on first request (if Upstash is configured)
  if (!ratelimitInitialized && pathname.startsWith('/api')) {
    await initRatelimit()
  }

  // Rate limit API routes (if Upstash is configured)
  if (ratelimit && pathname.startsWith('/api')) {
    const ip = request.headers.get('x-forwarded-for') ?? 'anonymous'
    const { success, remaining, reset } = await ratelimit.limit(ip)

    if (!success) {
      return new NextResponse('Too Many Requests', {
        status: 429,
        headers: {
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString(),
        },
      })
    }
  }

  // Lightweight session check via cookie only (Edge Runtime compatible)
  const sessionToken = request.cookies.get('authjs.session-token')?.value ||
                      request.cookies.get('__Secure-authjs.session-token')?.value
  const isAuthenticated = !!sessionToken

  // Check if current path is protected
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  )

  // Check if current path is auth-only (login page)
  const isAuthRoute = authRoutes.some(route =>
    pathname === route || pathname.startsWith(route)
  )

  // Redirect unauthenticated users away from protected routes
  if (isProtectedRoute && !isAuthenticated) {
    const loginUrl = new URL('/login', request.url)
    // Preserve the original URL for redirect after login
    loginUrl.searchParams.set('callbackUrl', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Redirect authenticated users away from login page
  if (isAuthRoute && isAuthenticated) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api/auth (Auth.js routes - let them handle their own auth)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc.)
     */
    '/((?!api/auth|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
