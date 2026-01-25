import 'server-only'
import { cache } from 'react'
import { auth } from '@/shared/lib/auth'
import { prisma } from '@/shared/lib/db'
import { redirect } from 'next/navigation'
import { Task, TaskStatus } from '@prisma/client'

/**
 * Verify the current session and redirect to login if not authenticated.
 * Uses React cache() to prevent duplicate auth checks within the same request.
 *
 * @returns Object with isAuth flag and userId
 * @throws Redirects to /login if not authenticated
 */
export const verifySession = cache(async () => {
  const session = await auth()

  if (!session?.user?.id) {
    redirect('/login')
  }

  return { isAuth: true, userId: session.user.id }
})

/**
 * Get the current authenticated user with profile data.
 * Calls verifySession first to ensure authentication.
 * Uses React cache() to prevent duplicate database queries.
 *
 * @returns User object with profile fields, or null if not found
 */
export const getUser = cache(async () => {
  const { userId } = await verifySession()

  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: {
      id: true,
      name: true,
      email: true,
      image: true,
      bio: true,
      customAvatar: true,
      createdAt: true,
      updatedAt: true,
      // Exclude sensitive fields like accounts/sessions
    }
  })

  return user
})

/**
 * Get session without redirect - for checking auth status in UI.
 * Use this when you want to show different content for auth/unauth users
 * rather than forcing a redirect.
 */
export const getSession = cache(async () => {
  return await auth()
})

/**
 * Get all tasks for a user, grouped by status and sorted by creation date.
 * Uses React cache() for request deduplication.
 */
export const getTasksByUser = cache(async (userId: string): Promise<Task[]> => {
  try {
    const tasks = await prisma.task.findMany({
      where: { userId },
      orderBy: [
        { status: 'asc' }, // TODO first, then IN_PROGRESS, then DONE
        { createdAt: 'desc' } // Newest first within each status
      ]
    })

    return tasks
  } catch (error) {
    console.error('Error fetching user tasks:', error)
    return []
  }
})

/**
 * Get a single task by ID with ownership verification.
 * Returns null if task doesn't exist or user doesn't have access.
 */
export const getTask = cache(async (taskId: string, userId: string): Promise<Task | null> => {
  try {
    const task = await prisma.task.findFirst({
      where: {
        id: taskId,
        userId // Ensures user can only access their own tasks
      }
    })

    return task
  } catch (error) {
    console.error('Error fetching task:', error)
    return null
  }
})

/**
 * Get task counts by status for dashboard statistics.
 * Useful for dashboard widgets showing task summary.
 */
export const getTaskCounts = cache(async (userId: string): Promise<{
  todo: number
  inProgress: number
  done: number
  total: number
}> => {
  try {
    const [todo, inProgress, done] = await Promise.all([
      prisma.task.count({ where: { userId, status: 'TODO' } }),
      prisma.task.count({ where: { userId, status: 'IN_PROGRESS' } }),
      prisma.task.count({ where: { userId, status: 'DONE' } }),
    ])

    return {
      todo,
      inProgress,
      done,
      total: todo + inProgress + done,
    }
  } catch (error) {
    console.error('Error fetching task counts:', error)
    return { todo: 0, inProgress: 0, done: 0, total: 0 }
  }
})
