import { TaskFormWithTags } from '@/shared/components/TaskFormWithTags'
import { getTagsByUser, verifySession } from '@/shared/lib/dal'
import Link from 'next/link'

export default async function NewTaskPage() {
  // Verify authentication and get user ID
  const { userId } = await verifySession()

  // Fetch available tags for autocomplete
  const tags = await getTagsByUser(userId)

  return (
    <div className="max-w-2xl">
      {/* Page header */}
      <div className="mb-6">
        {/* Breadcrumb / back link */}
        <Link
          href="/tasks"
          className="
            inline-flex items-center
            text-sm text-gray-600 dark:text-gray-400
            hover:text-gray-900 dark:hover:text-gray-200
            mb-4
            transition-colors
          "
        >
          <svg
            className="w-4 h-4 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Tasks
        </Link>

        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Create New Task
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Add a new task to your list and start tracking your work.
        </p>
      </div>

      {/* Task form component */}
      <TaskFormWithTags availableTags={tags} />
    </div>
  )
}
