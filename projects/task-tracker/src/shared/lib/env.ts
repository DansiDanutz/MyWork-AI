import { z } from 'zod'

/**
 * Environment variables schema for production validation
 *
 * This schema validates required environment variables at startup.
 * Validation fails fast if env is misconfigured.
 *
 * Note: NEXTAUTH_URL is NOT included - Auth.js v5 infers it automatically.
 */
const envSchema = z.object({
  // Database
  DATABASE_URL: z.string().url().startsWith('postgresql://'),

  // App URL (client-exposed)
  NEXT_PUBLIC_APP_URL: z.string().url().default('http://localhost:3000'),

  // Auth.js (required for authentication)
  AUTH_SECRET: z
    .string()
    .min(32, 'AUTH_SECRET must be at least 32 characters for security'),
  AUTH_GITHUB_ID: z.string().min(1, 'AUTH_GITHUB_ID is required for GitHub OAuth'),
  AUTH_GITHUB_SECRET: z.string().min(1, 'AUTH_GITHUB_SECRET is required for GitHub OAuth'),

  // Upstash Redis (optional - for rate limiting)
  // When not provided, rate limiting is gracefully skipped
  UPSTASH_REDIS_REST_URL: z.string().url().optional(),
  UPSTASH_REDIS_REST_TOKEN: z.string().optional(),
})

// Validate at import time - fails fast if env is misconfigured
const parsed = envSchema.safeParse(process.env)

if (!parsed.success) {
  console.error('Invalid environment variables:')
  console.error(parsed.error.flatten().fieldErrors)
  throw new Error('Invalid environment configuration')
}

export const env = parsed.data

// NODE_ENV is managed by Next.js, access via process.env.NODE_ENV directly
// - 'development' during `npm run dev`
// - 'production' during `npm run build` and `npm run start`
export const isDev = process.env.NODE_ENV === 'development'
export const isProd = process.env.NODE_ENV === 'production'
