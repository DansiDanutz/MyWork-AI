import 'server-only'
import { after } from 'next/server'
import { prisma } from '@/shared/lib/db'
import { auth } from '@/shared/lib/auth'
import { AnalyticsEventSchema, type AnalyticsEvent } from './types'

/**
 * Track an analytics event asynchronously.
 * Validates the event and stores in database.
 * Called by trackEvent() after response is sent.
 */
export async function trackEventAsync(event: AnalyticsEvent): Promise<void> {
  try {
    // Validate event structure (will throw if invalid)
    const validatedEvent = AnalyticsEventSchema.parse(event)

    await prisma.analyticsEvent.create({
      data: {
        userId: validatedEvent.userId,
        eventType: validatedEvent.type,
        properties: validatedEvent.properties as any,
      }
    })
  } catch (error) {
    // Log but don't throw - analytics should never break the app
    console.error('[Analytics] Failed to track event:', error)
  }
}

/**
 * Track an analytics event without blocking the response.
 * Uses Next.js 15's after() API to defer database writes.
 *
 * @param event - The analytics event to track
 *
 * Usage in Server Actions:
 * ```
 * import { trackEvent } from '@/shared/lib/analytics'
 *
 * export async function createTask(data: FormData) {
 *   const task = await prisma.task.create(...)
 *
 *   trackEvent({
 *     type: 'task_created',
 *     userId: session.user.id,
 *     properties: { taskId: task.id, hasDescription: !!data.description }
 *   })
 *
 *   return { success: true }
 * }
 * ```
 */
export function trackEvent(event: AnalyticsEvent): void {
  after(async () => {
    await trackEventAsync(event)
  })
}

/**
 * Track event for current session user.
 * Convenience wrapper that auto-injects userId from session.
 *
 * @param type - Event type
 * @param properties - Event-specific properties
 */
export async function trackSessionEvent<T extends AnalyticsEvent['type']>(
  type: T,
  properties: Extract<AnalyticsEvent, { type: T }>['properties']
): Promise<void> {
  const session = await auth()
  if (!session?.user?.id) {
    console.warn('[Analytics] Cannot track event: no session')
    return
  }

  trackEvent({
    type,
    userId: session.user.id,
    properties,
  } as AnalyticsEvent)
}
