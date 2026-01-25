'use client'

import { useEffect } from 'react'
import Link from 'next/link'

type ErrorPageProps = {
  error: Error & { digest?: string }
  reset: () => void
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    console.error('App error:', error)
  }, [error])

  return (
    <main className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">⚠️</div>
        <h1 className="text-3xl font-bold mb-2">Something went wrong</h1>
        <p className="text-gray-400 mb-8">
          We hit an unexpected error. Please try again, or go back home.
        </p>
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={reset}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition"
          >
            Try again
          </button>
          <Link
            href="/"
            className="px-4 py-2 rounded-lg border border-gray-700 text-gray-200 hover:text-white hover:border-gray-500 transition"
          >
            Go home
          </Link>
        </div>
      </div>
    </main>
  )
}
