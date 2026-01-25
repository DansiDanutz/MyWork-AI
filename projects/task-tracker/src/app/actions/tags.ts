'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'

import { prisma } from '@/shared/lib/db'
import { getUser } from '@/shared/lib/dal'
import { trackEvent } from '@/shared/lib/analytics'

// Validation schemas
const CreateTagSchema = z.object({
  name: z.string().min(1, 'Tag name is required').max(50, 'Tag name too long'),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, 'Invalid color format').optional(),
})

const UpdateTaskTagsSchema = z.object({
  taskId: z.string().min(1),
  tagIds: z.array(z.string()),
})

type ActionResult<T = void> =
  | { success: true; data?: T }
  | { success: false; error: string }

/**
 * Create a new tag for the authenticated user
 */
export async function createTag(formData: FormData): Promise<ActionResult<{ tagId: string }>> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to create tags' }
    }

    const result = CreateTagSchema.safeParse({
      name: formData.get('name'),
      color: formData.get('color') || undefined,
    })

    if (!result.success) {
      return { success: false, error: result.error.issues[0].message }
    }

    const { name, color } = result.data

    // Check for duplicate tag name for this user
    const existing = await prisma.tag.findFirst({
      where: { userId: user.id, name: { equals: name, mode: 'insensitive' } }
    })

    if (existing) {
      return { success: false, error: 'A tag with this name already exists' }
    }

    const tag = await prisma.tag.create({
      data: {
        name,
        color: color || '#6b7280', // Default gray
        userId: user.id,
      },
    })

    trackEvent({
      type: 'tag_created',
      userId: user.id,
      properties: { tagId: tag.id, tagName: tag.name },
    })

    revalidatePath('/tasks')
    return { success: true, data: { tagId: tag.id } }
  } catch (error) {
    console.error('Create tag error:', error)
    return { success: false, error: 'Failed to create tag' }
  }
}

/**
 * Delete a tag (removes from all tasks automatically via cascade)
 */
export async function deleteTag(tagId: string): Promise<ActionResult> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to delete tags' }
    }

    const tag = await prisma.tag.findFirst({
      where: { id: tagId, userId: user.id }
    })

    if (!tag) {
      return { success: false, error: 'Tag not found or access denied' }
    }

    await prisma.tag.delete({ where: { id: tagId } })

    trackEvent({
      type: 'tag_deleted',
      userId: user.id,
      properties: { tagId, tagName: tag.name },
    })

    revalidatePath('/tasks')
    return { success: true }
  } catch (error) {
    console.error('Delete tag error:', error)
    return { success: false, error: 'Failed to delete tag' }
  }
}

/**
 * Update tags for a task (set operation - replaces all existing tags)
 */
export async function updateTaskTags(
  taskId: string,
  tagIds: string[]
): Promise<ActionResult> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in to update task tags' }
    }

    // Verify task ownership
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId: user.id }
    })

    if (!task) {
      return { success: false, error: 'Task not found or access denied' }
    }

    // Verify all tags belong to user
    if (tagIds.length > 0) {
      const userTagCount = await prisma.tag.count({
        where: { id: { in: tagIds }, userId: user.id }
      })
      if (userTagCount !== tagIds.length) {
        return { success: false, error: 'One or more tags not found' }
      }
    }

    // Update task tags (set operation)
    await prisma.task.update({
      where: { id: taskId },
      data: {
        tags: {
          set: tagIds.map(id => ({ id }))
        }
      }
    })

    trackEvent({
      type: 'task_tags_updated',
      userId: user.id,
      properties: { taskId, tagCount: tagIds.length },
    })

    revalidatePath('/tasks')
    revalidatePath(`/tasks/${taskId}/edit`)
    return { success: true }
  } catch (error) {
    console.error('Update task tags error:', error)
    return { success: false, error: 'Failed to update task tags' }
  }
}

/**
 * Add tag to task during task creation (creates tag if doesn't exist)
 */
export async function addTagToTask(
  taskId: string,
  tagName: string
): Promise<ActionResult<{ tagId: string }>> {
  try {
    const user = await getUser()
    if (!user) {
      return { success: false, error: 'You must be logged in' }
    }

    // Verify task ownership
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId: user.id }
    })

    if (!task) {
      return { success: false, error: 'Task not found or access denied' }
    }

    // Connect or create tag
    const updatedTask = await prisma.task.update({
      where: { id: taskId },
      data: {
        tags: {
          connectOrCreate: {
            where: { userId_name: { userId: user.id, name: tagName } },
            create: { name: tagName, color: '#6b7280', userId: user.id }
          }
        }
      },
      include: { tags: true }
    })

    const addedTag = updatedTask.tags.find(t => t.name === tagName)

    trackEvent({
      type: 'tag_added_to_task',
      userId: user.id,
      properties: { taskId, tagName },
    })

    revalidatePath('/tasks')
    return { success: true, data: { tagId: addedTag?.id || '' } }
  } catch (error) {
    console.error('Add tag to task error:', error)
    return { success: false, error: 'Failed to add tag to task' }
  }
}
