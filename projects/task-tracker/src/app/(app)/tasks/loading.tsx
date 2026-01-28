/**
 * Tasks page loading skeleton
 *
 * Matches TasksPage structure with TasksLoadingSkeleton:
 * - Page header with title and button
 * - Search bar
 * - Two-column layout: filter sidebar + task list
 * - Task list with 3 sections (To Do, In Progress, Done)
 */
export default function Loading() {
  return (
    <div>
      {/* Page header skeleton */}
      <div className="flex items-center justify-between mb-6">
        <div className="h-9 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div className="h-10 w-32 bg-gray-200 dark:bg-gray-700 rounded-md animate-pulse" />
      </div>

      {/* Search bar skeleton */}
      <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse mb-6" />

      {/* Two-column layout skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter sidebar skeleton */}
        <aside className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-4 animate-pulse" />
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
          </div>
        </aside>

        {/* Task list skeleton */}
        <main className="lg:col-span-3">
          <div className="space-y-8">
            {[1, 2, 3].map((section) => (
              <div key={section}>
                <div className="h-7 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4 animate-pulse" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3].map((card) => (
                    <div
                      key={card}
                      className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-3 animate-pulse" />
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2 animate-pulse" />
                      <div className="flex gap-1 mb-2">
                        <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-14 animate-pulse" />
                        <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse" />
                      </div>
                      <div className="space-y-2 mb-4">
                        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full animate-pulse" />
                        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6 animate-pulse" />
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-24 animate-pulse" />
                        <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
