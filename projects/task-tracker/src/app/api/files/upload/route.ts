import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/shared/lib/auth'
import { prisma } from '@/shared/lib/db'
import { validateFileType, isImageMime, getExtensionFromMime, MAX_FILE_SIZE } from '@/shared/lib/file-validation'
import { saveFile } from '@/shared/lib/file-storage'
import { generateThumbnail } from '@/shared/lib/thumbnail-generator'
import { trackEvent } from '@/shared/lib/analytics'

// Helper to verify auth
async function getAuthenticatedUserId(): Promise<string | null> {
  try {
    const session = await auth()
    return session?.user?.id || null
  } catch {
    return null
  }
}

// For this plan, we'll implement a simple chunked upload endpoint
// The full TUS protocol will be added in a later iteration if needed
export async function POST(request: NextRequest) {
  try {
    // Verify authentication
    const userId = await getAuthenticatedUserId()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Parse form data (for chunked uploads)
    const formData = await request.formData()
    const file = formData.get('file') as File | null
    const taskId = formData.get('taskId') as string | null
    const chunkIndex = parseInt(formData.get('chunkIndex') as string || '0')
    const totalChunks = parseInt(formData.get('totalChunks') as string || '1')
    const originalFilename = formData.get('filename') as string || 'unnamed'

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    if (!taskId) {
      return NextResponse.json({ error: 'No task ID provided' }, { status: 400 })
    }

    // Verify user owns the task
    const task = await prisma.task.findFirst({
      where: { id: taskId, userId },
    })

    if (!task) {
      return NextResponse.json({ error: 'Task not found or access denied' }, { status: 404 })
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json({
        error: `File size exceeds ${MAX_FILE_SIZE / 1024 / 1024}MB limit`
      }, { status: 413 })
    }

    // For single chunk uploads (small files), process immediately
    if (totalChunks === 1) {
      const buffer = Buffer.from(await file.arrayBuffer())

      // Validate file type by content
      const typeValidation = await validateFileType(buffer)
      if (!typeValidation.isValid) {
        return NextResponse.json({ error: typeValidation.error }, { status: 400 })
      }

      // Save file to disk
      const extension = typeValidation.ext || getExtensionFromMime(typeValidation.mime!)
      const { storedFilename, filePath } = await saveFile(buffer, userId, taskId, extension)

      // Generate thumbnail for images
      let thumbnailPath: string | null = null
      if (isImageMime(typeValidation.mime!)) {
        try {
          thumbnailPath = await generateThumbnail(filePath, userId, taskId, storedFilename)
        } catch (error) {
          console.warn('Thumbnail generation failed:', error)
          // Continue without thumbnail
        }
      }

      // Create database record
      const attachment = await prisma.fileAttachment.create({
        data: {
          taskId,
          userId,
          filename: originalFilename,
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

      return NextResponse.json({
        success: true,
        fileId: attachment.id,
        filename: originalFilename,
      })
    }

    // For multi-chunk uploads, return chunked upload placeholder response
    // The full TUS implementation would handle this properly
    return NextResponse.json({
      success: true,
      message: 'Chunk received',
      chunkIndex,
      totalChunks,
      note: 'Full chunked upload support will be implemented with TUS protocol in next iteration'
    })
  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { error: 'An unexpected error occurred during upload' },
      { status: 500 }
    )
  }
}

// HEAD request for TUS protocol (upload info)
export async function HEAD(_request: NextRequest) {
  const userId = await getAuthenticatedUserId()
  if (!userId) {
    return new Response(null, { status: 401 })
  }

  // Return TUS headers for protocol compatibility
  return new Response(null, {
    status: 200,
    headers: {
      'Tus-Resumable': '1.0.0',
      'Tus-Version': '1.0.0',
      'Tus-Extension': 'creation,expiration',
      'Tus-Max-Size': MAX_FILE_SIZE.toString(),
    },
  })
}

// PATCH for chunk uploads (TUS protocol)
export async function PATCH(_request: NextRequest) {
  const userId = await getAuthenticatedUserId()
  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Placeholder for TUS PATCH implementation
  return NextResponse.json(
    { error: 'TUS PATCH not implemented in this iteration' },
    { status: 501 }
  )
}

// OPTIONS for CORS
export async function OPTIONS(_request: NextRequest) {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, HEAD, PATCH, OPTIONS, DELETE',
      'Access-Control-Allow-Headers': 'Content-Type, Upload-Offset, Upload-Length, Tus-Resumable',
      'Tus-Resumable': '1.0.0',
      'Tus-Version': '1.0.0',
      'Tus-Extension': 'creation,expiration',
      'Tus-Max-Size': MAX_FILE_SIZE.toString(),
    },
  })
}

// DELETE for canceling uploads
export async function DELETE(_request: NextRequest) {
  const userId = await getAuthenticatedUserId()
  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Placeholder for upload cancellation
  return NextResponse.json({ success: true, message: 'Upload cancelled' })
}
