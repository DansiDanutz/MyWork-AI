'use client'

import { useState, useTransition } from 'react'
import { FileAttachment } from '@prisma/client'
import { FileThumbnail } from './FileThumbnail'
import { FilePreview } from './FilePreview'
import { formatFileSize } from '@/shared/lib/file-validation'
import { deleteFileAction } from '@/app/actions/files'

interface FileListProps {
  files: FileAttachment[]
  onFileDeleted?: (fileId: string) => void
  editable?: boolean
  compact?: boolean
}

export function FileList({
  files,
  onFileDeleted,
  editable = false,
  compact = false,
}: FileListProps) {
  const [previewFile, setPreviewFile] = useState<FileAttachment | null>(null)
  const [isPending, startTransition] = useTransition()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  if (files.length === 0) {
    return null
  }

  const handleDownload = (file: FileAttachment) => {
    window.open(`/api/files/download/${file.id}`, '_blank')
  }

  const handleDelete = async (file: FileAttachment) => {
    if (!confirm(`Delete "${file.filename}"? This cannot be undone.`)) {
      return
    }

    setDeletingId(file.id)
    startTransition(async () => {
      const result = await deleteFileAction(file.id)
      if (result.success) {
        onFileDeleted?.(file.id)
        if (previewFile?.id === file.id) {
          setPreviewFile(null)
        }
      } else {
        alert(result.error || 'Failed to delete file')
      }
      setDeletingId(null)
    })
  }

  // Compact grid view (for task cards)
  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {files.slice(0, 4).map((file) => (
          <FileThumbnail
            key={file.id}
            filename={file.filename}
            mimeType={file.mimeType}
            thumbnailPath={file.thumbnailPath}
            size="sm"
            onClick={() => setPreviewFile(file)}
          />
        ))}
        {files.length > 4 && (
          <div className="w-10 h-10 flex items-center justify-center rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-400 text-xs">
            +{files.length - 4}
          </div>
        )}

        {/* Preview modal */}
        {previewFile && (
          <FilePreview
            fileId={previewFile.id}
            filename={previewFile.filename}
            mimeType={previewFile.mimeType}
            size={previewFile.size}
            onClose={() => setPreviewFile(null)}
            onDownload={() => handleDownload(previewFile)}
          />
        )}
      </div>
    )
  }

  // Full list view (for edit page)
  return (
    <div className="space-y-2">
      {files.map((file) => (
        <div
          key={file.id}
          className={`flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700 ${
            deletingId === file.id ? 'opacity-50' : ''
          }`}
        >
          <FileThumbnail
            filename={file.filename}
            mimeType={file.mimeType}
            thumbnailPath={file.thumbnailPath}
            size="md"
            onClick={() => setPreviewFile(file)}
          />

          <div className="flex-1 min-w-0">
            <p className="text-sm text-zinc-200 truncate">{file.filename}</p>
            <p className="text-xs text-zinc-500">
              {formatFileSize(file.size)}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleDownload(file)}
              className="p-1.5 text-zinc-400 hover:text-zinc-200 transition-colors"
              title="Download"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>

            {editable && (
              <button
                onClick={() => handleDelete(file)}
                disabled={isPending}
                className="p-1.5 text-red-400 hover:text-red-300 transition-colors disabled:opacity-50"
                title="Delete"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        </div>
      ))}

      {/* Preview modal */}
      {previewFile && (
        <FilePreview
          fileId={previewFile.id}
          filename={previewFile.filename}
          mimeType={previewFile.mimeType}
          size={previewFile.size}
          onClose={() => setPreviewFile(null)}
          onDownload={() => handleDownload(previewFile)}
          onDelete={editable ? () => handleDelete(previewFile) : undefined}
        />
      )}
    </div>
  )
}

// File count badge for task cards
export function FileCountBadge({ count }: { count: number }) {
  if (count === 0) return null

  return (
    <div className="flex items-center gap-1 text-xs text-zinc-400">
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
      </svg>
      <span>{count}</span>
    </div>
  )
}