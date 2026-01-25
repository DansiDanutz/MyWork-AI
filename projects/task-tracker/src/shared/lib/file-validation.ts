import { fileTypeFromBuffer } from 'file-type'

// Allowed MIME types - whitelist approach for security
export const ALLOWED_MIME_TYPES = [
  // Images
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'image/svg+xml',

  // Documents
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',

  // Text
  'text/plain',
  'text/csv',
  'text/markdown',

  // Archives
  'application/zip',
  'application/x-rar-compressed',
  'application/gzip',
] as const

export type AllowedMimeType = typeof ALLOWED_MIME_TYPES[number]

// 25MB per file (from CONTEXT.md)
export const MAX_FILE_SIZE = 25 * 1024 * 1024

// 5MB threshold for Server Actions vs TUS protocol
export const SERVER_ACTION_SIZE_LIMIT = 5 * 1024 * 1024

export interface FileValidationResult {
  isValid: boolean
  error?: string
  mime?: string
  ext?: string
}

/**
 * Validate file type by reading magic bytes (binary signature).
 * This is security-critical - NEVER trust client-provided MIME types or extensions.
 */
export async function validateFileType(buffer: Buffer): Promise<FileValidationResult> {
  try {
    const type = await fileTypeFromBuffer(buffer)

    if (!type) {
      // Could be a text file (no magic bytes)
      // Try to detect if it's valid text
      const isText = isValidTextFile(buffer)
      if (isText) {
        return {
          isValid: true,
          mime: 'text/plain',
          ext: 'txt',
        }
      }
      return {
        isValid: false,
        error: 'Unable to detect file type. File may be corrupted.',
      }
    }

    if (!ALLOWED_MIME_TYPES.includes(type.mime as AllowedMimeType)) {
      return {
        isValid: false,
        error: `File type "${type.mime}" is not allowed. Supported types: images, documents, text files, and archives.`,
        mime: type.mime,
      }
    }

    return {
      isValid: true,
      mime: type.mime,
      ext: type.ext,
    }
  } catch (error) {
    console.error('File type validation error:', error)
    return {
      isValid: false,
      error: 'Failed to validate file type.',
    }
  }
}

/**
 * Validate file size against limit.
 */
export function validateFileSize(size: number): FileValidationResult {
  if (size > MAX_FILE_SIZE) {
    const sizeMB = (size / 1024 / 1024).toFixed(2)
    const limitMB = MAX_FILE_SIZE / 1024 / 1024
    return {
      isValid: false,
      error: `File size (${sizeMB}MB) exceeds the ${limitMB}MB limit.`,
    }
  }

  if (size === 0) {
    return {
      isValid: false,
      error: 'File is empty.',
    }
  }

  return { isValid: true }
}

/**
 * Check if buffer appears to be valid UTF-8 text.
 * Used for text files that don't have magic bytes.
 */
function isValidTextFile(buffer: Buffer): boolean {
  // Check first 1KB for valid UTF-8
  const sample = buffer.slice(0, 1024)

  try {
    const text = sample.toString('utf-8')
    // Check for null bytes (binary indicator)
    if (text.includes('\0')) {
      return false
    }
    // Check if it decodes back to same bytes (valid UTF-8)
    const reencoded = Buffer.from(text, 'utf-8')
    return sample.equals(reencoded)
  } catch {
    return false
  }
}

/**
 * Get human-readable file size string.
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Check if file should use TUS protocol (large file).
 */
export function shouldUseTusProtocol(size: number): boolean {
  return size > SERVER_ACTION_SIZE_LIMIT
}

/**
 * Get file extension from MIME type.
 */
export function getExtensionFromMime(mime: string): string {
  const mimeToExt: Record<string, string> = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'text/plain': 'txt',
    'text/csv': 'csv',
    'text/markdown': 'md',
    'application/zip': 'zip',
    'application/x-rar-compressed': 'rar',
    'application/gzip': 'gz',
  }

  return mimeToExt[mime] || 'bin'
}

/**
 * Check if MIME type is an image (for thumbnail generation).
 */
export function isImageMime(mime: string): boolean {
  return mime.startsWith('image/') && mime !== 'image/svg+xml'
}
