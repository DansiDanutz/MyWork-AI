// Event tracking
export { trackEvent, trackEventAsync, trackSessionEvent } from './tracker'
export { AnalyticsEventSchema, type AnalyticsEvent, type EventType } from './types'

// GitHub API integration
export {
  enrichUserWithGitHubData,
  enrichUser,
  checkRateLimitStatus,
  getGitHubAccessToken,
} from './github'

// Query functions
export {
  getUserEventTimeline,
  getEventsByType,
  getFeatureUsageStats,
  exportEventsForBrain,
  getAnalyticsSummary,
} from './queries'

// Data retention
export {
  purgeExpiredEvents,
  getRetentionStats,
  purgeUserData,
} from './retention'
