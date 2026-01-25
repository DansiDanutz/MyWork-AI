'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'

import { prisma } from '@/shared/lib/db'
import { getUser } from '@/shared/lib/dal'
import { trackEvent } from '@/shared/lib/analytics'

// Validation schemas
const CreateTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255, 'Title too long'),
  description: z.string().optional(),
})

const UpdateTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255, 'Title too long'),
  description: z.string().optional(),
})

const TaskStatusSchema = z.enum(['TODO', 'IN_PROGRESS', 'DONE'])

// Action result types
type ActionResult<T = void> =
  | { success: true; data?: T }
  | { success: false; error: string }

/**
 * Create a new task for the authenticated user
 */
export async function createTask(formData: FormData): Promise<ActionResult<{ taskId: string }>> {
  try {
    // Verify authentication
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to create tasks' }
    }

    // Validate input
    const result = CreateTaskSchema.safeParse({
      title: formData.get('title'),
      description: formData.get('description'),
    })

    if (!result.success) {
      return { success: false, error: result.error.issues[0].message }
    }

    const { title, description } = result.data

    // Create task
    const task = await prisma.task.create({
      data: {
        title,
        description: description || null,
        userId: user.id,
      },
    })

    // Track analytics
    trackEvent({
      type: 'task_created',
      userId: user.id,
      properties: {
        taskId: task.id,
        hasDescription: !!description,
      },
    })

    // Revalidate relevant pages
    revalidatePath('/tasks')
    revalidatePath('/dashboard')

    return { success: true, data: { taskId: task.id } }
  } catch (error) {
    console.error('Create task error:', error)
    return { success: false, error: 'Failed to create task' }
  }
}

/**
 * Update an existing task (title/description only, not status)
 */
export async function updateTask(taskId: string, formData: FormData): Promise<ActionResult> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to update tasks' }
    }

    // Validate input
    const result = UpdateTaskSchema.safeParse({
      title: formData.get('title'),
      description: formData.get('description'),
    })

    if (!result.success) {
      return { success: false, error: result.error.issues[0].message }
    }

    const { title, description } = result.data

    // Verify task ownership and update
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId: user.id },
    })

    if (!task) {
      return { success: false, error: 'Task not found or access denied' }
    }

    await prisma.task.update({
      where: { id: taskId },
      data: {
        title,
        description: description || null,
      },
    })

    // Track analytics
    trackEvent({
      type: 'task_updated',
      userId: user.id,
      properties: {
        taskId,
        fieldsChanged: ['title', description ? 'description' : null].filter(Boolean) as string[],
      },
    })

    // Revalidate pages
    revalidatePath('/tasks')
    revalidatePath(`/tasks/${taskId}/edit`)

    return { success: true }
  } catch (error) {
    console.error('Update task error:', error)
    return { success: false, error: 'Failed to update task' }
  }
}

/**
 * Update task status (separate action for optimistic UI)
 */
export async function updateTaskStatus(taskId: string, status: string): Promise<ActionResult> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to update tasks' }
    }

    // Validate status
    const result = TaskStatusSchema.safeParse(status)
    if (!result.success) {
      return { success: false, error: 'Invalid task status' }
    }

    // Verify ownership and update
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId: user.id },
    })

    if (!task) {
      return { success: false, error: 'Task not found or access denied' }
    }

    await prisma.task.update({
      where: { id: taskId },
      data: { status: result.data },
    })

    // Track analytics
    trackEvent({
      type: 'task_updated',
      userId: user.id,
      properties: {
        taskId,
        fieldsChanged: ['status'],
        newStatus: result.data,
      },
    })

    // Revalidate pages
    revalidatePath('/tasks')

    return { success: true }
  } catch (error) {
    console.error('Update task status error:', error)
    return { success: false, error: 'Failed to update task status' }
  }
}

/**
 * Delete a task (with ownership verification)
 */
export async function deleteTask(taskId: string): Promise<ActionResult> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to delete tasks' }
    }

    // Verify ownership
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId: user.id },
    })

    if (!task) {
      return { success: false, error: 'Task not found or access denied' }
    }

    // Delete task
    await prisma.task.delete({
      where: { id: taskId },
    })

    // Track analytics
    trackEvent({
      type: 'task_deleted',
      userId: user.id,
      properties: {
        taskId,
      },
    })

    // Revalidate pages
    revalidatePath('/tasks')
    revalidatePath('/dashboard')

    return { success: true }
  } catch (error) {
    console.error('Delete task error:', error)
    return { success: false, error: 'Failed to delete task' }
  }
}
