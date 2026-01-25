import { prisma } from '@/shared/lib/db'
import { NextResponse } from 'next/server'

export async function GET() {
  const checks = {
    timestamp: new Date().toISOString(),
    status: 'ok' as 'ok' | 'error',
    environment: process.env.NODE_ENV || 'unknown',
    checks: {
      database: { status: 'pending' as 'ok' | 'error', message: '' },
      environment: { status: 'ok' as 'ok' | 'error', message: 'Validated' },
    },
  }

  // Check database connection
  try {
    await prisma.$queryRaw`SELECT 1`
    checks.checks.database = { status: 'ok', message: 'Connected' }
  } catch (error) {
    checks.status = 'error'
    checks.checks.database = {
      status: 'error',
      message: error instanceof Error ? error.message : 'Connection failed',
    }
  }

  const statusCode = checks.status === 'ok' ? 200 : 503

  return NextResponse.json(checks, { status: statusCode })
}
