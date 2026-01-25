'use client'

import { useCallback, useState, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import * as tus from 'tus-js-client'
import { uploadFile } from '@/app/actions/files'
import {
  MAX_FILE_SIZE,
  SERVER_ACTION_SIZE_LIMIT,
  formatFileSize,
  validateFileSize,
} from '@/shared/lib/file-validation'
import { FileUploadProgress, UploadState } from './FileUploadProgress'

interface FileDropzoneProps {
  taskId: string
  onUploadComplete?: (fileId: string, filename: string) => void
  onUploadError?: (filename: string, error: string) => void
  maxFiles?: number
  disabled?: boolean
  compact?: boolean
}

export function FileDropzone({
  taskId,
  onUploadComplete,
  onUploadError,
  maxFiles = 10,
  disabled = false,
  compact = false,
}: FileDropzoneProps) {
  const [uploads, setUploads] = useState<UploadState[]>([])
  const tusUploadsRef = useRef<Map<string, tus.Upload>>(new Map())

  // Update upload state helper
  const updateUpload = useCallback((id: string, updates: Partial<UploadState>) => {
    setUploads((prev) =>
      prev.map((u) => (u.id === id ? { ...u, ...updates } : u))
    )
  }, [])

  // Remove upload from list
  const removeUpload = useCallback((id: string) => {
    setUploads((prev) => prev.filter((u) => u.id !== id))
    tusUploadsRef.current.delete(id)
  }, [])

  // Handle small file upload via Server Action
  const uploadSmallFile = useCallback(
    async (file: File, uploadId: string) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('taskId', taskId)

      const result = await uploadFile(formData)

      if (result.success) {
        updateUpload(uploadId, { status: 'complete', progress: 100 })
        onUploadComplete?.(result.fileId!, result.filename!)
      } else {
        updateUpload(uploadId, {
          status: 'error',
          error: result.error || 'Upload failed',
        })
        onUploadError?.(file.name, result.error || 'Upload failed')
      }
    },
    [taskId, onUploadComplete, onUploadError, updateUpload]
  )

  // Handle large file upload via TUS
  const uploadLargeFile = useCallback(
    (file: File, uploadId: string) => {
      const upload = new tus.Upload(file, {
        endpoint: '/api/files/upload',
        retryDelays: [0, 3000, 5000, 10000, 20000],
        chunkSize: 5 * 1024 * 1024, // 5MB chunks
        metadata: {
          filename: file.name,
          filetype: file.type,
          taskId,
        },
        onProgress: (bytesUploaded, bytesTotal) => {
          const progress = (bytesUploaded / bytesTotal) * 100
          updateUpload(uploadId, { progress, status: 'uploading' })
        },
        onSuccess: () => {
          updateUpload(uploadId, { status: 'complete', progress: 100 })
          // TUS creates DB record on server side, so we don't have fileId here
          // The UI should refresh to show the new file
          onUploadComplete?.('', file.name)
          tusUploadsRef.current.delete(uploadId)
        },
        onError: (error) => {
          const errorMessage = error.message || 'Upload failed'
          updateUpload(uploadId, { status: 'error', error: errorMessage })
          onUploadError?.(file.name, errorMessage)
          tusUploadsRef.current.delete(uploadId)
        },
      })

      tusUploadsRef.current.set(uploadId, upload)
      upload.start()
    },
    [taskId, onUploadComplete, onUploadError, updateUpload]
  )

  // Process dropped files
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Limit number of files
      const filesToUpload = acceptedFiles.slice(0, maxFiles)

      filesToUpload.forEach((file) => {
        // Generate unique ID for this upload
        const uploadId = `${file.name}-${Date.now()}-${Math.random()}`

        // Validate file size
        const sizeValidation = validateFileSize(file.size)
        if (!sizeValidation.isValid) {
          setUploads((prev) => [
            ...prev,
            {
              id: uploadId,
              filename: file.name,
              size: file.size,
              progress: 0,
              status: 'error',
              error: sizeValidation.error,
            },
          ])
          onUploadError?.(file.name, sizeValidation.error!)
          return
        }

        // Add to upload list
        setUploads((prev) => [
          ...prev,
          {
            id: uploadId,
            filename: file.name,
            size: file.size,
            progress: 0,
            status: 'uploading',
          },
        ])

        // Choose upload method based on file size
        if (file.size <= SERVER_ACTION_SIZE_LIMIT) {
          // Small file: use Server Action
          uploadSmallFile(file, uploadId)
        } else {
          // Large file: use TUS protocol
          uploadLargeFile(file, uploadId)
        }
      })
    },
    [maxFiles, uploadSmallFile, uploadLargeFile, onUploadError]
  )

  // Cancel an upload
  const handleCancel = useCallback((id: string) => {
    const tusUpload = tusUploadsRef.current.get(id)
    if (tusUpload) {
      tusUpload.abort()
    }
    removeUpload(id)
  }, [removeUpload])

  // Retry a failed upload
  const handleRetry = useCallback(
    (id: string) => {
      const upload = uploads.find((u) => u.id === id)
      if (upload) {
        // Reset status and re-trigger
        updateUpload(id, { status: 'uploading', progress: 0, error: undefined })

        // Find original file (we need to re-drop it)
        // For now, just remove and ask user to re-drop
        removeUpload(id)
      }
    },
    [uploads, updateUpload, removeUpload]
  )

  // Dismiss completed/errored upload
  const handleDismiss = useCallback(
    (id: string) => {
      removeUpload(id)
    },
    [removeUpload]
  )

  // Setup dropzone
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    disabled,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
  })

  // Active uploads count
  const activeUploads = uploads.filter((u) => u.status === 'uploading').length

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg transition-colors cursor-pointer
          ${compact ? 'p-4' : 'p-8'}
          ${isDragActive && !isDragReject ? 'border-blue-500 bg-blue-500/10' : ''}
          ${isDragReject ? 'border-red-500 bg-red-500/10' : ''}
          ${!isDragActive && !isDragReject ? 'border-zinc-600 hover:border-zinc-500' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className={`text-center ${compact ? '' : 'space-y-2'}`}>
          {/* Upload icon */}
          <svg
            className={`mx-auto text-zinc-400 ${compact ? 'w-6 h-6' : 'w-10 h-10'}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
            />
          </svg>

          {isDragActive ? (
            <p className={`text-blue-400 ${compact ? 'text-sm' : ''}`}>
              Drop files here...
            </p>
          ) : (
            <>
              <p className={`text-zinc-300 ${compact ? 'text-sm' : ''}`}>
                Drag & drop files here
              </p>
              {!compact && (
                <p className="text-zinc-500 text-sm">
                  or click to select files (max {formatFileSize(MAX_FILE_SIZE)} per file)
                </p>
              )}
            </>
          )}

          {activeUploads > 0 && (
            <p className="text-xs text-zinc-500 mt-1">
              {activeUploads} upload{activeUploads > 1 ? 's' : ''} in progress
            </p>
          )}
        </div>
      </div>

      {/* Upload progress list */}
      <FileUploadProgress
        uploads={uploads}
        onCancel={handleCancel}
        onRetry={handleRetry}
        onDismiss={handleDismiss}
      />
    </div>
  )
}