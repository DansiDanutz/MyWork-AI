import { getUser } from '@/shared/lib/dal'

export default async function DashboardPage() {
  const user = await getUser()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Welcome back, {user?.name || 'there'}!
        </p>
      </div>

      {/* Placeholder content - will be replaced in Phase 3 */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Tasks
          </h2>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
            0
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Total tasks
          </p>
        </div>

        <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            In Progress
          </h2>
          <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
            0
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Tasks in progress
          </p>
        </div>

        <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Completed
          </h2>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400">
            0
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Tasks completed
          </p>
        </div>
      </div>

      {/* Getting started section */}
      <div className="mt-8 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
          Getting Started
        </h2>
        <p className="text-blue-700 dark:text-blue-300 mb-4">
          You&apos;re all set up! Task management features coming in Phase 3.
        </p>
        <div className="flex gap-4">
          <a
            href="/settings/profile"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Complete your profile
          </a>
        </div>
      </div>
    </div>
  )
}
