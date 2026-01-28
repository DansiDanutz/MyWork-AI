import { getUser, getTaskCounts } from "@/shared/lib/dal";
import Link from "next/link";

export default async function DashboardPage() {
  // Get user first (cached via React cache())
  const user = await getUser();

  // Then get task counts for that user
  const taskCounts = await getTaskCounts(user?.id || "");

  return (
    <div>
      {/* Header with quick-add button */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Welcome back, {user?.name || "there"}!
          </p>
        </div>

        {/* Quick-add button */}
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

      {/* Task statistics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Tasks
          </h2>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
            {taskCounts.total}
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
            {taskCounts.inProgress}
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
            {taskCounts.done}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Tasks completed
          </p>
        </div>
      </div>

      {/* Getting started / Quick actions section */}
      <div className="mt-8 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        {taskCounts.total === 0 ? (
          <>
            <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
              Getting Started
            </h2>
            <p className="text-blue-700 dark:text-blue-300 mb-4">
              You&apos;re all set up! Create your first task to start tracking
              your work.
            </p>
            <div className="flex gap-4">
              <Link
                href="/tasks/new"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Create your first task
              </Link>
              <Link
                href="/settings/profile"
                className="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-700 rounded-lg text-sm font-medium hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
              >
                Complete your profile
              </Link>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
              Quick Actions
            </h2>
            <p className="text-blue-700 dark:text-blue-300 mb-4">
              You have {taskCounts.total} task
              {taskCounts.total !== 1 ? "s" : ""} in your list.
            </p>
            <div className="flex gap-4">
              <Link
                href="/tasks"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                View all tasks
              </Link>
              <Link
                href="/settings/profile"
                className="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-700 rounded-lg text-sm font-medium hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
              >
                Edit profile
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
