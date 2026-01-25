'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-6">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-red-600 dark:text-red-400 mb-4">
            Something went wrong!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            An unexpected error occurred. Please try again.
          </p>
          {process.env.NODE_ENV === 'development' && (
            <details className="text-left bg-gray-100 dark:bg-gray-800 p-4 rounded-lg mb-4">
              <summary className="cursor-pointer font-medium mb-2">Error Details</summary>
              <pre className="text-sm text-red-600 dark:text-red-400 overflow-auto">
                {error.message}
              </pre>
            </details>
          )}
        </div>

        <div className="space-y-4">
          <button
            onClick={() => reset()}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Try Again
          </button>

          <a
            href="/dashboard"
            className="block w-full border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Back to Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}