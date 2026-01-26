/**
 * TaskCardSkeleton: Loading placeholder for TaskCard component
 *
 * Matches TaskCard structure:
 * - Status badge
 * - Title
 * - Tags (2 visible)
 * - Description (2 lines)
 * - Date and file count indicator
 * - Actions (status dropdown, edit, delete)
 */
export function TaskCardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
      {/* Status badge skeleton */}
      <div className="flex items-center justify-between mb-3">
        <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
      </div>

      {/* Title skeleton */}
      <div className="h-6 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />

      {/* Tags skeleton (2 tags) */}
      <div className="flex gap-1 mb-2">
        <div className="h-5 w-14 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>

      {/* Description skeleton (2 lines) */}
      <div className="space-y-2 mb-3">
        <div className="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="h-4 w-5/6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>

      {/* Date and file indicator skeleton */}
      <div className="flex items-center justify-between mb-4">
        <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="h-5 w-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>

      {/* Actions skeleton */}
      <div className="flex items-center gap-3">
        {/* Status dropdown skeleton */}
        <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="flex-1" />
        {/* Edit button skeleton */}
        <div className="h-8 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        {/* Delete button skeleton */}
        <div className="h-8 w-14 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    </div>
  )
}
