import sharp from 'sharp'
import path from 'path'
import fs from 'fs/promises'
import { getThumbnailDir } from '@/shared/lib/file-storage'

// Thumbnail configuration
const THUMBNAIL_SIZE = 200 // pixels (square)
const THUMBNAIL_QUALITY = 80

/**
 * Generate a WebP thumbnail for an image file.
 * Returns the relative thumbnail path (for storage in DB) or null if generation fails.
 */
export async function generateThumbnail(
  sourcePath: string,
  userId: string,
  taskId: string,
  storedFilename: string
): Promise<string | null> {
  try {
    // Get thumbnail directory
    const thumbDir = await getThumbnailDir(userId, taskId)

    // Generate thumbnail filename (same base name, .webp extension)
    const baseName = path.basename(storedFilename, path.extname(storedFilename))
    const thumbFilename = `${baseName}.webp`
    const thumbPath = path.join(thumbDir, thumbFilename)

    // Generate thumbnail with Sharp
    await sharp(sourcePath)
      .resize(THUMBNAIL_SIZE, THUMBNAIL_SIZE, {
        fit: 'cover',      // Crop to fill square
        position: 'center', // Center the crop
      })
      .webp({ quality: THUMBNAIL_QUALITY })
      .toFile(thumbPath)

    // Return relative path for DB storage
    // Format: userId/taskId/thumbs/filename.webp
    return path.join(userId, taskId, 'thumbs', thumbFilename)
  } catch (error) {
    console.error('Thumbnail generation failed:', error)
    return null
  }
}

/**
 * Delete a thumbnail file.
 */
export async function deleteThumbnail(relativePath: string): Promise<void> {
  const fullPath = path.join(process.cwd(), 'uploads', relativePath)

  try {
    await fs.unlink(fullPath)
  } catch {
    // Ignore if file doesn't exist
  }
}

/**
 * Check if a file is a supported image format for thumbnail generation.
 */
export function canGenerateThumbnail(mimeType: string): boolean {
  const supported = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    // Note: SVG excluded - Sharp can convert but may have security issues
  ]

  return supported.includes(mimeType)
}

/**
 * Get thumbnail URL for a file attachment.
 * Returns null if no thumbnail exists.
 */
export function getThumbnailUrl(thumbnailPath: string | null): string | null {
  if (!thumbnailPath) return null
  // Thumbnails are served via the download endpoint
  return `/api/files/thumbnail/${encodeURIComponent(thumbnailPath)}`
}
