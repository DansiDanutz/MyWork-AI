import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">😕</div>
        <h1 className="text-3xl font-bold mb-2">Page not found</h1>
        <p className="text-gray-400 mb-8">
          The page you are looking for doesn’t exist or has moved.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            href="/"
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition"
          >
            Go home
          </Link>
          <Link
            href="/products"
            className="px-4 py-2 rounded-lg border border-gray-700 text-gray-200 hover:text-white hover:border-gray-500 transition"
          >
            Browse marketplace
          </Link>
        </div>
      </div>
    </main>
  )
}
