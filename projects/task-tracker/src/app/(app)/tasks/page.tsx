import { Suspense } from 'react'
import Link from 'next/link'
import { getTasksByUser, verifySession } from '@/shared/lib/dal'
import { TaskList } from '@/shared/components/TaskList'

// Loading skeleton that matches TaskList layout
function TaskListSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Three sections (TODO, IN_PROGRESS, DONE) */}
      {[1, 2, 3].map((section) => (
        <div key={section}>
          {/* Section title skeleton */}
          <div className="h-7 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4" />

          {/* Three card skeletons */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((card) => (
              <div
                key={card}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                {/* Title skeleton */}
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3" />

                {/* Description skeleton */}
                <div className="space-y-2 mb-4">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
                </div>

                {/* Footer skeleton */}
                <div className="flex items-center justify-between">
                  <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-24" />
                  <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// Async component that loads tasks
async function TaskListContent() {
  const { userId } = await verifySession()
  const tasks = await getTasksByUser(userId)

  return <TaskList tasks={tasks} />
}

export default function TasksPage() {
  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          My Tasks
        </h1>

        {/* New Task button */}
        <Link
          href="/tasks/new"
          className="
            inline-flex items-center justify-center
            px-4 py-2
            bg-blue-600 text-white
            rounded-md font-medium
            hover:bg-blue-700
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            dark:bg-blue-500 dark:hover:bg-blue-600
            transition-colors
          "
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Task
        </Link>
      </div>

      {/* Task list with Suspense for streaming */}
      <Suspense fallback={<TaskListSkeleton />}>
        <TaskListContent />
      </Suspense>
    </div>
  )
}
