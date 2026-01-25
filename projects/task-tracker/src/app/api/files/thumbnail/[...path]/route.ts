import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/shared/lib/auth'
import path from 'path'
import fs from 'fs/promises'

/**
 * Serve thumbnail files with authentication.
 * Path format: /api/files/thumbnail/userId/taskId/thumbs/filename.webp
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  try {
    // Authenticate
    const session = await auth()
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { path: pathSegments } = await params

    // Validate path segments
    if (!pathSegments || pathSegments.length < 4) {
      return NextResponse.json({ error: 'Invalid path' }, { status: 400 })
    }

    // Extract userId from path and verify ownership
    const [userId] = pathSegments
    if (userId !== session.user.id) {
      return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
    }

    // Construct full path
    const thumbnailPath = path.join(process.cwd(), 'uploads', ...pathSegments)

    // Security: Prevent path traversal
    const normalizedPath = path.normalize(thumbnailPath)
    const uploadsDir = path.join(process.cwd(), 'uploads')
    if (!normalizedPath.startsWith(uploadsDir)) {
      return NextResponse.json({ error: 'Invalid path' }, { status: 400 })
    }

    // Read thumbnail
    try {
      const buffer = await fs.readFile(normalizedPath)

      return new NextResponse(buffer, {
        status: 200,
        headers: {
          'Content-Type': 'image/webp',
          'Cache-Control': 'private, max-age=86400', // Cache for 24 hours
        },
      })
    } catch {
      return NextResponse.json({ error: 'Thumbnail not found' }, { status: 404 })
    }
  } catch (error) {
    console.error('Thumbnail serving error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}