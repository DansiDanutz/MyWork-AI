/**
 * New task page loading skeleton
 *
 * Matches NewTaskPage structure:
 * - Breadcrumb / back link
 * - Page title and description
 * - Form fields (title, description, status, tags)
 */
export default function Loading() {
  return (
    <div className="max-w-2xl">
      {/* Page header skeleton */}
      <div className="mb-6">
        {/* Breadcrumb / back link skeleton */}
        <div className="h-4 w-28 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-4" />

        {/* Title skeleton */}
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
        {/* Description skeleton */}
        <div className="h-5 w-96 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
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

        {/* Action buttons skeleton */}
        <div className="flex gap-3">
          <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div className="h-10 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>
      </div>
    </div>
  )
}
