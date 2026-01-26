/**
 * Task edit page loading skeleton
 *
 * Matches EditTaskPage structure:
 * - Breadcrumb navigation
 * - Page title
 * - Form fields (title, description, status, tags, files section)
 */
export default function Loading() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header skeleton */}
        <div className="mb-8">
          {/* Breadcrumb skeleton */}
          <div className="flex items-center gap-2 mb-3">
            <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-4 w-1 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          {/* Page title skeleton */}
          <div className="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>

        {/* Form skeleton */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 space-y-6">
          {/* Title field skeleton */}
          <div>
            <div className="h-5 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
            <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          {/* Description field skeleton */}
          <div>
            <div className="h-5 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
            <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          {/* Status field skeleton */}
          <div>
            <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
            <div className="h-10 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          {/* Tags field skeleton */}
          <div>
            <div className="h-5 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
            <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          {/* Files section skeleton */}
          <div>
            <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
            <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          {/* Action buttons skeleton */}
          <div className="flex gap-3">
            <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-10 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  )
}
