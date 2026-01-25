import { notFound } from 'next/navigation'
import Link from 'next/link'
import { getTask, verifySession } from '@/shared/lib/dal'
import { TaskEditForm } from '@/shared/components/TaskEditForm'

type Props = {
  params: Promise<{ id: string }>
}

export default async function EditTaskPage({ params }: Props) {
  // Verify authentication and get user ID
  const { userId } = await verifySession()

  // Await params (Next.js 15 requirement)
  const { id } = await params

  // Fetch task with ownership verification
  const task = await getTask(id, userId)

  // If task doesn't exist or user doesn't own it, show 404
  if (!task) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
            <Link
              href="/tasks"
              className="hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
            >
              Tasks
            </Link>
            <span>/</span>
            <span className="text-gray-900 dark:text-gray-200">Edit</span>
          </div>

          {/* Page title */}
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Edit Task
          </h1>
        </div>

        {/* Edit form */}
        <TaskEditForm task={task} />
      </div>
    </div>
  )
}
