'use server'

import { z } from 'zod'
import { getUser } from '@/shared/lib/dal'
import { searchTasks, filterTasks } from '@/shared/lib/dal'
import { TaskStatus } from '@prisma/client'
import { trackEvent } from '@/shared/lib/analytics'

// Validation schemas
const SearchTasksSchema = z.object({
  query: z.string().min(1).max(255),
})

const FilterTasksSchema = z.object({
  status: z.array(z.enum(['TODO', 'IN_PROGRESS', 'DONE'])).optional(),
  tagIds: z.array(z.string()).optional(),
  dateFrom: z.string().optional(), // ISO date string
  dateTo: z.string().optional(), // ISO date string
})

// Result type
type ActionResult<T = void> =
  | { success: true; data: T }
  | { success: false; error: string }

/**
 * Server Action: Search tasks by query string
 * Uses full-text search with fallback to fuzzy matching
 */
export async function searchTasksAction(
  query: string
): Promise<ActionResult<unknown[]>> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to search tasks' }
    }

    // Validate input
    const result = SearchTasksSchema.safeParse({ query })
    if (!result.success) {
      return { success: false, error: result.error.issues[0].message }
    }

    // Perform search
    const tasks = await searchTasks(user.id, result.data.query)

    // Track analytics
    trackEvent({
      type: 'search_performed',
      userId: user.id,
      properties: {
        query: result.data.query,
        resultCount: tasks.length,
        searchType: 'tasks',
      },
    })

    return { success: true, data: tasks }
  } catch (error) {
    console.error('Search tasks error:', error)
    return { success: false, error: 'Failed to search tasks' }
  }
}

/**
 * Server Action: Filter tasks by status, tags, and date range
 * All filters are optional and combined with AND logic
 */
export async function filterTasksAction(
  filters: {
    status?: string[]
    tagIds?: string[]
    dateFrom?: string
    dateTo?: string
  }
): Promise<ActionResult<unknown[]>> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to filter tasks' }
    }

    // Validate input
    const result = FilterTasksSchema.safeParse(filters)
    if (!result.success) {
      return { success: false, error: result.error.issues[0].message }
    }

    const { status, tagIds, dateFrom, dateTo } = result.data

    // Build filter object
    const filterObj: {
      status?: TaskStatus[]
      tagIds?: string[]
      dateFrom?: Date
      dateTo?: Date
    } = {}

    if (status && status.length > 0) {
      filterObj.status = status as TaskStatus[]
    }

    if (tagIds && tagIds.length > 0) {
      filterObj.tagIds = tagIds
    }

    if (dateFrom) {
      filterObj.dateFrom = new Date(dateFrom)
    }

    if (dateTo) {
      filterObj.dateTo = new Date(dateTo)
    }

    // Perform filter
    const tasks = await filterTasks(user.id, filterObj)

    // Track analytics
    trackEvent({
      type: 'filter_applied',
      userId: user.id,
      properties: {
        filters: {
          status: status?.length || 0,
          tags: tagIds?.length || 0,
          hasDateRange: !!(dateFrom || dateTo),
        },
        resultCount: tasks.length,
      },
    })

    return { success: true, data: tasks }
  } catch (error) {
    console.error('Filter tasks error:', error)
    return { success: false, error: 'Failed to filter tasks' }
  }
}

/**
 * Server Action: Get filtered tasks (combines search and filters)
 * Used by the tasks page to apply both search query and filters
 */
export async function getFilteredTasksAction(params: {
  q?: string
  status?: string[]
  tagIds?: string[]
}): Promise<ActionResult<unknown[]>> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in' }
    }

    // If there's a search query, use search (which returns ranked results)
    if (params.q && params.q.trim().length > 0) {
      const searchResults = await searchTasks(user.id, params.q.trim())

      // Apply additional filters to search results if needed
      let filtered = searchResults

      if (params.status && params.status.length > 0) {
        filtered = filtered.filter(task =>
          params.status!.includes(task.status)
        )
      }

      if (params.tagIds && params.tagIds.length > 0) {
        filtered = filtered.filter(task =>
          task.tags.some(tag => params.tagIds!.includes(tag.id))
        )
      }

      return { success: true, data: filtered }
    }

    // Otherwise use filter function
    const filterObj: {
      status?: TaskStatus[]
      tagIds?: string[]
    } = {}

    if (params.status && params.status.length > 0) {
      filterObj.status = params.status as TaskStatus[]
    }

    if (params.tagIds && params.tagIds.length > 0) {
      filterObj.tagIds = params.tagIds
    }

    const tasks = await filterTasks(user.id, filterObj)

    return { success: true, data: tasks }
  } catch (error) {
    console.error('Get filtered tasks error:', error)
    return { success: false, error: 'Failed to get tasks' }
  }
}
