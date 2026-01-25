import 'server-only'
import { prisma } from '@/shared/lib/db'
import type { EventType } from './types'

/**
 * Get event timeline for a specific user.
 * Useful for user activity debugging and pattern analysis.
 *
 * @param userId - User ID to query
 * @param days - Number of days to look back (default 30)
 * @returns Array of events sorted by date descending
 */
export async function getUserEventTimeline(
  userId: string,
  days: number = 30
) {
  const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)

  return prisma.analyticsEvent.findMany({
    where: {
      userId,
      createdAt: {
        gte: cutoffDate,
      },
    },
    orderBy: { createdAt: 'desc' },
    select: {
      id: true,
      eventType: true,
      properties: true,
      createdAt: true,
    },
  })
}

/**
 * Get events by type with optional time range.
 * Useful for feature-specific analysis.
 *
 * @param eventType - Type of event to query
 * @param startDate - Start of date range (optional)
 * @param endDate - End of date range (optional)
 * @param limit - Maximum number of results (default 1000)
 */
export async function getEventsByType(
  eventType: EventType,
  startDate?: Date,
  endDate?: Date,
  limit: number = 1000
) {
  return prisma.analyticsEvent.findMany({
    where: {
      eventType,
      createdAt: {
        ...(startDate ? { gte: startDate } : {}),
        ...(endDate ? { lte: endDate } : {}),
      },
    },
    orderBy: { createdAt: 'desc' },
    take: limit,
    select: {
      id: true,
      userId: true,
      properties: true,
      createdAt: true,
    },
  })
}

/**
 * Get aggregated feature usage statistics.
 * Uses raw SQL for efficient aggregation.
 *
 * @param eventType - Type of event to aggregate
 * @param days - Number of days to look back (default 30)
 */
export async function getFeatureUsageStats(eventType: EventType, days: number = 30) {
  const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)

  // Use Prisma's groupBy for aggregation
  const stats = await prisma.analyticsEvent.groupBy({
    by: ['eventType'],
    where: {
      eventType,
      createdAt: { gte: cutoffDate },
    },
    _count: { id: true },
  })

  // Also get unique users
  const uniqueUsers = await prisma.analyticsEvent.findMany({
    where: {
      eventType,
      createdAt: { gte: cutoffDate },
    },
    distinct: ['userId'],
    select: { userId: true },
  })

  return {
    eventType,
    totalEvents: stats[0]?._count.id || 0,
    uniqueUsers: uniqueUsers.length,
    period: { start: cutoffDate, end: new Date() },
  }
}

/**
 * Export events for brain analysis.
 * Optimized format for external analysis scripts.
 * Only includes user ID (not PII) for GDPR compliance.
 *
 * @param startDate - Start of export range
 * @param endDate - End of export range
 * @param eventTypes - Optional filter for specific event types
 */
export async function exportEventsForBrain(
  startDate: Date,
  endDate: Date,
  eventTypes?: EventType[]
) {
  return prisma.analyticsEvent.findMany({
    where: {
      createdAt: {
        gte: startDate,
        lte: endDate,
      },
      ...(eventTypes ? { eventType: { in: eventTypes } } : {}),
    },
    select: {
      eventType: true,
      properties: true,
      createdAt: true,
      userId: true,  // Only ID, no PII
    },
    orderBy: { createdAt: 'asc' },
  })
}

/**
 * Get analytics summary for dashboard/overview.
 *
 * @param days - Number of days to summarize (default 7)
 */
export async function getAnalyticsSummary(days: number = 7) {
  const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000)

  const [totalEvents, uniqueUsers, eventsByType] = await Promise.all([
    // Total events
    prisma.analyticsEvent.count({
      where: { createdAt: { gte: cutoffDate } },
    }),

    // Unique users
    prisma.analyticsEvent.findMany({
      where: { createdAt: { gte: cutoffDate } },
      distinct: ['userId'],
      select: { userId: true },
    }),

    // Events by type
    prisma.analyticsEvent.groupBy({
      by: ['eventType'],
      where: { createdAt: { gte: cutoffDate } },
      _count: { id: true },
      orderBy: { _count: { id: 'desc' } },
    }),
  ])

  return {
    period: { start: cutoffDate, end: new Date(), days },
    totalEvents,
    uniqueUsers: uniqueUsers.length,
    eventsByType: eventsByType.map((e) => ({
      type: e.eventType,
      count: e._count.id,
    })),
  }
}
