import 'server-only'
import { prisma } from '@/shared/lib/db'

// Default retention period per research - GDPR safe
const DEFAULT_RETENTION_DAYS = 90

/**
 * Purge analytics events older than the retention period.
 * Should be run as a scheduled job (e.g., daily cron).
 *
 * @param retentionDays - Number of days to retain (default 90)
 * @returns Number of events deleted
 */
export async function purgeExpiredEvents(
  retentionDays: number = DEFAULT_RETENTION_DAYS
): Promise<{ deleted: number; cutoffDate: Date }> {
  const cutoffDate = new Date(
    Date.now() - retentionDays * 24 * 60 * 60 * 1000
  )

  const result = await prisma.analyticsEvent.deleteMany({
    where: {
      createdAt: {
        lt: cutoffDate,
      },
    },
  })

  console.log(
    `[Analytics] Purged ${result.count} events older than ${retentionDays} days ` +
    `(before ${cutoffDate.toISOString()})`
  )

  return {
    deleted: result.count,
    cutoffDate,
  }
}

/**
 * Get retention statistics for monitoring.
 * Shows event distribution by age to plan retention policies.
 */
export async function getRetentionStats() {
  const now = new Date()

  // Count events in different age buckets
  const [last7Days, last30Days, last90Days, total] = await Promise.all([
    prisma.analyticsEvent.count({
      where: {
        createdAt: { gte: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000) },
      },
    }),
    prisma.analyticsEvent.count({
      where: {
        createdAt: { gte: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000) },
      },
    }),
    prisma.analyticsEvent.count({
      where: {
        createdAt: { gte: new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000) },
      },
    }),
    prisma.analyticsEvent.count(),
  ])

  // Get oldest and newest events
  const [oldest, newest] = await Promise.all([
    prisma.analyticsEvent.findFirst({
      orderBy: { createdAt: 'asc' },
      select: { createdAt: true },
    }),
    prisma.analyticsEvent.findFirst({
      orderBy: { createdAt: 'desc' },
      select: { createdAt: true },
    }),
  ])

  return {
    total,
    byAge: {
      last7Days,
      last30Days,
      last90Days,
      older: total - last90Days,
    },
    dateRange: {
      oldest: oldest?.createdAt || null,
      newest: newest?.createdAt || null,
    },
    retentionDays: DEFAULT_RETENTION_DAYS,
  }
}

/**
 * Purge all analytics data for a specific user.
 * Required for GDPR "right to be forgotten" requests.
 *
 * @param userId - User ID to delete data for
 * @returns Number of events deleted
 */
export async function purgeUserData(
  userId: string
): Promise<{ deleted: number }> {
  const result = await prisma.analyticsEvent.deleteMany({
    where: { userId },
  })

  console.log(`[Analytics] Purged ${result.count} events for user ${userId}`)

  return { deleted: result.count }
}
