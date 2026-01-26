'use client'

// Note: global-error.tsx handles errors in the root layout
// We use <a> tags instead of <Link> because Next.js components may not be reliable here
/* eslint-disable @next/next/no-html-link-for-pages */

import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to console for debugging
    console.error('Global error:', error)
  }, [error])

  return (
    <html lang="en">
      <body className="bg-gray-900 text-gray-100">
        <main className="min-h-screen flex items-center justify-center px-6">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-4">💥</div>
            <h1 className="text-3xl font-bold mb-2">Critical Error</h1>
            <p className="text-gray-400 mb-4">
              Something went seriously wrong. Please try again.
            </p>
            {error.digest && (
              <p className="text-sm text-gray-500 mb-6">
                Error ID: {error.digest}
              </p>
            )}
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={reset}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition"
              >
                Try again
              </button>
              <a
                href="/"
                className="px-4 py-2 rounded-lg border border-gray-700 text-gray-200 hover:text-white hover:border-gray-500 transition"
              >
                Go home
              </a>
            </div>
          </div>
        </main>
      </body>
    </html>
  )
}
