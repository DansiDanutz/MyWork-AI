'use client'

import { useState } from 'react'
import Image from 'next/image'

interface FileThumbnailProps {
  filename: string
  mimeType: string
  thumbnailPath?: string | null
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
}

export function FileThumbnail({
  filename,
  mimeType,
  thumbnailPath,
  size = 'md',
  onClick,
}: FileThumbnailProps) {
  const [imageError, setImageError] = useState(false)

  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
  }

  const iconSizes = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  const isImage = mimeType.startsWith('image/')
  const hasThumbnail = thumbnailPath && !imageError

  // Show image thumbnail
  if (isImage && hasThumbnail) {
    return (
      <button
        onClick={onClick}
        className={`${sizeClasses[size]} relative rounded-lg overflow-hidden bg-zinc-800 border border-zinc-700 hover:border-zinc-500 transition-colors`}
      >
        <Image
          src={`/api/files/thumbnail/${thumbnailPath}`}
          alt={filename}
          fill
          className="object-cover"
          onError={() => setImageError(true)}
          sizes={size === 'lg' ? '96px' : size === 'md' ? '64px' : '40px'}
        />
      </button>
    )
  }

  // Show file type icon
  return (
    <button
      onClick={onClick}
      className={`${sizeClasses[size]} flex items-center justify-center rounded-lg bg-zinc-800 border border-zinc-700 hover:border-zinc-500 transition-colors`}
    >
      <FileTypeIcon mimeType={mimeType} className={iconSizes[size]} />
    </button>
  )
}

// File type icon based on MIME type
function FileTypeIcon({ mimeType, className }: { mimeType: string; className?: string }) {
  const isPdf = mimeType === 'application/pdf'
  const isDoc = mimeType.includes('word') || mimeType.includes('document')
  const isSpreadsheet = mimeType.includes('excel') || mimeType.includes('spreadsheet')
  const isPresentation = mimeType.includes('powerpoint') || mimeType.includes('presentation')
  const isArchive = mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('gzip')
  const isImage = mimeType.startsWith('image/')
  const isText = mimeType.startsWith('text/')

  // Choose color based on type
  let color = 'text-zinc-400'
  if (isPdf) color = 'text-red-400'
  else if (isDoc) color = 'text-blue-400'
  else if (isSpreadsheet) color = 'text-green-400'
  else if (isPresentation) color = 'text-orange-400'
  else if (isArchive) color = 'text-yellow-400'
  else if (isImage) color = 'text-purple-400'
  else if (isText) color = 'text-zinc-300'

  return (
    <svg className={`${className} ${color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      {isPdf ? (
        // PDF icon
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      ) : isImage ? (
        // Image icon
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      ) : isArchive ? (
        // Archive icon
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
      ) : (
        // Generic document icon
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      )}
    </svg>
  )
}

// Export FileTypeIcon for use elsewhere
export { FileTypeIcon }