'use client'

import { formatFileSize } from '@/shared/lib/file-validation'

export type UploadStatus = 'pending' | 'uploading' | 'complete' | 'error'

export interface UploadState {
  id: string
  filename: string
  size: number
  progress: number
  status: UploadStatus
  error?: string
}

interface FileUploadProgressProps {
  uploads: UploadState[]
  onCancel: (id: string) => void
  onRetry?: (id: string) => void
  onDismiss?: (id: string) => void
}

export function FileUploadProgress({
  uploads,
  onCancel,
  onRetry,
  onDismiss,
}: FileUploadProgressProps) {
  if (uploads.length === 0) return null

  return (
    <div className="space-y-2 mt-4">
      {uploads.map((upload) => (
        <div
          key={upload.id}
          className="border border-zinc-700 rounded-lg p-3 bg-zinc-800/50"
        >
          {/* File info row */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <FileIcon mimeType={getMimeFromFilename(upload.filename)} />
              <span className="text-sm text-zinc-200 truncate">
                {upload.filename}
              </span>
              <span className="text-xs text-zinc-500 flex-shrink-0">
                {formatFileSize(upload.size)}
              </span>
            </div>

            {/* Action button */}
            <div className="flex-shrink-0 ml-2">
              {upload.status === 'uploading' && (
                <button
                  onClick={() => onCancel(upload.id)}
                  className="text-xs text-red-400 hover:text-red-300 px-2 py-1"
                  title="Cancel upload"
                >
                  Cancel
                </button>
              )}
              {upload.status === 'error' && onRetry && (
                <button
                  onClick={() => onRetry(upload.id)}
                  className="text-xs text-blue-400 hover:text-blue-300 px-2 py-1"
                  title="Retry upload"
                >
                  Retry
                </button>
              )}
              {(upload.status === 'complete' || upload.status === 'error') && onDismiss && (
                <button
                  onClick={() => onDismiss(upload.id)}
                  className="text-xs text-zinc-400 hover:text-zinc-300 px-2 py-1"
                  title="Dismiss"
                >
                  Dismiss
                </button>
              )}
            </div>
          </div>

          {/* Progress bar */}
          {upload.status === 'uploading' && (
            <div className="mb-1">
              <div className="w-full bg-zinc-700 rounded-full h-1.5">
                <div
                  className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${upload.progress}%` }}
                />
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-zinc-400">Uploading...</span>
                <span className="text-xs text-zinc-400">{upload.progress.toFixed(0)}%</span>
              </div>
            </div>
          )}

          {/* Status messages */}
          {upload.status === 'complete' && (
            <div className="flex items-center gap-1.5">
              <CheckIcon className="w-4 h-4 text-green-500" />
              <span className="text-xs text-green-500">Upload complete</span>
            </div>
          )}

          {upload.status === 'error' && (
            <div className="flex items-center gap-1.5">
              <ErrorIcon className="w-4 h-4 text-red-500" />
              <span className="text-xs text-red-500">
                {upload.error || 'Upload failed'}
              </span>
            </div>
          )}

          {upload.status === 'pending' && (
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-zinc-400">Waiting...</span>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// Helper function to guess MIME type from filename
function getMimeFromFilename(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const mimeMap: Record<string, string> = {
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    webp: 'image/webp',
    pdf: 'application/pdf',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    txt: 'text/plain',
    csv: 'text/csv',
    zip: 'application/zip',
  }
  return mimeMap[ext] || 'application/octet-stream'
}

// File type icon component
function FileIcon({ mimeType }: { mimeType: string }) {
  const isImage = mimeType.startsWith('image/')
  const isPdf = mimeType === 'application/pdf'
  const isDoc = mimeType.includes('word') || mimeType.includes('document')
  const isSpreadsheet = mimeType.includes('excel') || mimeType.includes('spreadsheet')

  let color = 'text-zinc-400'
  let icon = 'M4 4h16v16H4V4z' // Generic file

  if (isImage) {
    color = 'text-purple-400'
    icon = 'M4 5a2 2 0 012-2h12a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm4 4a2 2 0 100 4 2 2 0 000-4zm8 8l-3-3-2 2-1-1-4 4h10z'
  } else if (isPdf) {
    color = 'text-red-400'
  } else if (isDoc) {
    color = 'text-blue-400'
  } else if (isSpreadsheet) {
    color = 'text-green-400'
  }

  return (
    <svg className={`w-5 h-5 ${color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={icon} />
    </svg>
  )
}

// Check icon for success
function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  )
}

// Error icon
function ErrorIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  )
}