/**
 * Profile settings page loading skeleton
 *
 * Matches ProfilePage structure:
 * - Section title
 * - Profile form fields (avatar, name, bio)
 */
export default function Loading() {
  return (
    <div>
      {/* Section title skeleton */}
      <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-4" />

      {/* Profile form skeleton */}
      <div className="space-y-6">
        {/* Avatar field skeleton */}
        <div>
          <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
          <div className="flex items-center gap-4">
            <div className="h-20 w-20 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
            <div className="h-10 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </div>

        {/* Name field skeleton */}
        <div>
          <div className="h-5 w-12 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
          <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>

        {/* Bio field skeleton */}
        <div>
          <div className="h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
          <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>

        {/* Status indicators skeleton */}
        <div className="h-5 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    </div>
  );
}
