'use client'

import dynamic from 'next/dynamic'

// Lazy load FileList with loading fallback
const FileList = dynamic(
  () => import('./FileList').then((mod) => mod.FileList),
  {
    loading: () => (
      <div className="space-y-2 animate-pulse">
        <div className="flex items-center gap-3 p-3 bg-gray-100 dark:bg-gray-800 rounded">
          <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="flex-1">
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-1" />
            <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    ),
    ssr: false,
  }
)

export { FileList as LazyFileList }
