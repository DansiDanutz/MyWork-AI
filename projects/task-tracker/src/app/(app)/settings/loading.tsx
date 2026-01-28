/**
 * Settings root loading skeleton
 *
 * Matches SettingsLayout structure:
 * - Settings title
 * - Two-column layout: navigation sidebar + content area
 */
export default function Loading() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Title skeleton */}
      <div className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-6" />

      <div className="flex flex-col md:flex-row gap-8">
        {/* Settings navigation skeleton */}
        <nav className="w-full md:w-48 flex-shrink-0">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-2">
            <div className="h-9 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
          </div>
        </nav>

        {/* Settings content skeleton */}
        <div className="flex-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <div className="space-y-6">
              {/* Generic form fields skeleton */}
              <div>
                <div className="h-5 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
                <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              </div>
              <div>
                <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
                <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              </div>
              <div className="h-10 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
