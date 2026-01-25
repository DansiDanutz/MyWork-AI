import { createSearchParamsCache, parseAsString, parseAsArrayOf } from 'nuqs/server'

/**
 * URL query parameter parsers for task page filters.
 * Uses nuqs for type-safe URL state management.
 *
 * Example URL: /tasks?q=meeting&status=TODO,IN_PROGRESS&tags=work,urgent
 */
export const taskSearchParams = {
  // Search query string
  q: parseAsString.withDefault(''),

  // Status filter (multiple allowed)
  status: parseAsArrayOf(parseAsString).withDefault([]),

  // Tag IDs filter (multiple allowed)
  tags: parseAsArrayOf(parseAsString).withDefault([]),
}

/**
 * Server-side search params cache for Server Components.
 * Enables reading URL params in async Server Components.
 */
export const searchParamsCache = createSearchParamsCache(taskSearchParams)
