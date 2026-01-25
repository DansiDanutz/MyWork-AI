'use server'

import { auth } from '@/shared/lib/auth'
import { prisma } from '@/shared/lib/db'
import { revalidatePath } from 'next/cache'
import {
  validateFileType,
  validateFileSize,
  getExtensionFromMime,
  SERVER_ACTION_SIZE_LIMIT,
} from '@/shared/lib/file-validation'
import { saveFile, deleteFile as deleteFileFromDisk } from '@/shared/lib/file-storage'
import { generateThumbnail, canGenerateThumbnail, deleteThumbnail } from '@/shared/lib/thumbnail-generator'
import { trackEvent } from '@/shared/lib/analytics'

interface UploadResult {
  success: boolean
  error?: string
  fileId?: string
  filename?: string
}

/**
 * Upload a file via Server Action (for files < 5MB).
 * Larger files should use the TUS endpoint.
 */
export async function uploadFile(formData: FormData): Promise<UploadResult> {
  try {
    // Authenticate
    const session = await auth()
    if (!session?.user?.id) {
      return { success: false, error: 'Unauthorized' }
    }

    const userId = session.user.id

    // Get file and taskId from form data
    const file = formData.get('file') as File | null
    const taskId = formData.get('taskId') as string | null

    if (!file) {
      return { success: false, error: 'No file provided' }
    }

    if (!taskId) {
      return { success: false, error: 'No task ID provided' }
    }

    // Check file size for Server Action limit
    if (file.size > SERVER_ACTION_SIZE_LIMIT) {
      return {
        success: false,
        error: `File too large for direct upload. Files over 5MB should use the upload endpoint.`,
      }
    }

    // Validate file size (overall limit)
    const sizeValidation = validateFileSize(file.size)
    if (!sizeValidation.isValid) {
      return { success: false, error: sizeValidation.error }
    }

    // Verify user owns the task
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId },
    })

    if (!task) {
      return { success: false, error: 'Task not found or access denied' }
    }

    // Read file content
    const buffer = Buffer.from(await file.arrayBuffer())

    // Validate file type by content (security-critical)
    const typeValidation = await validateFileType(buffer)
    if (!typeValidation.isValid) {
      return { success: false, error: typeValidation.error }
    }

    // Save file to disk
    const extension = typeValidation.ext || getExtensionFromMime(typeValidation.mime!)
    const { storedFilename, filePath } = await saveFile(buffer, userId, taskId, extension)

    // Generate thumbnail for images
    let thumbnailPath: string | null = null
    if (canGenerateThumbnail(typeValidation.mime!)) {
      thumbnailPath = await generateThumbnail(filePath, userId, taskId, storedFilename)
    }

    // Create database record
    const attachment = await prisma.fileAttachment.create({
      data: {
        taskId,
        userId,
        filename: file.name,
        storedFilename,
        mimeType: typeValidation.mime!,
        size: file.size,
        thumbnailPath,
      },
    })

    // Track analytics
    trackEvent({
      type: 'file_uploaded',
      userId,
      properties: {
        fileId: attachment.id,
        taskId,
        fileSize: file.size,
        mimeType: typeValidation.mime!,
      },
    })

    // Revalidate task page
    revalidatePath(`/tasks/${taskId}`)
    revalidatePath(`/tasks/${taskId}/edit`)

    return {
      success: true,
      fileId: attachment.id,
      filename: file.name,
    }
  } catch (error) {
    console.error('Upload error:', error)
    return {
      success: false,
      error: 'An unexpected error occurred during upload',
    }
  }
}

/**
 * Delete a file attachment.
 */
export async function deleteFileAction(fileId: string): Promise<{ success: boolean; error?: string }> {
  try {
    // Authenticate
    const session = await auth()
    if (!session?.user?.id) {
      return { success: false, error: 'Unauthorized' }
    }

    const userId = session.user.id

    // Find file and verify ownership
    const file = await prisma.fileAttachment.findFirst({
      where: { id: fileId, userId },
      include: { task: true },
    })

    if (!file) {
      return { success: false, error: 'File not found or access denied' }
    }

    // Delete from filesystem
    await deleteFileFromDisk(userId, file.taskId, file.storedFilename, file.thumbnailPath)

    // Delete thumbnail if exists
    if (file.thumbnailPath) {
      await deleteThumbnail(file.thumbnailPath)
    }

    // Delete from database
    await prisma.fileAttachment.delete({
      where: { id: fileId },
    })

    // Revalidate
    revalidatePath(`/tasks/${file.taskId}`)
    revalidatePath(`/tasks/${file.taskId}/edit`)

    return { success: true }
  } catch (error) {
    console.error('Delete file error:', error)
    return { success: false, error: 'Failed to delete file' }
  }
}

/**
 * Get file attachments for a task.
 */
export async function getTaskFiles(taskId: string) {
  const session = await auth()
  if (!session?.user?.id) {
    return []
  }

  const files = await prisma.fileAttachment.findMany({
    where: { taskId, userId: session.user.id },
    orderBy: { createdAt: 'desc' },
  })

  return files
}
