import { z } from 'zod'

const envSchema = z.object({
  // Database
  DATABASE_URL: z.string().url().startsWith('postgresql://'),

  // App URL (client-exposed)
  NEXT_PUBLIC_APP_URL: z.string().url().default('http://localhost:3000'),
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
