'use client'

import { useOptimistic, useTransition } from 'react'
import { updateTaskStatus, deleteTask } from '@/app/actions/tasks'
import Link from 'next/link'

type Task = {
  id: string
  title: string
  description: string | null
  status: 'TODO' | 'IN_PROGRESS' | 'DONE'
  createdAt: Date
  updatedAt: Date
}

type TaskCardProps = {
  task: Task
}

const statusLabels = {
  TODO: 'To Do',
  IN_PROGRESS: 'In Progress',
  DONE: 'Done',
}

const statusColors = {
  TODO: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  DONE: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
}

export function TaskCard({ task }: TaskCardProps) {
  const [isPending, startTransition] = useTransition()
  const [optimisticTask, setOptimisticTask] = useOptimistic(task)

  const handleStatusChange = async (newStatus: Task['status']) => {
    // Optimistic update
    startTransition(() => {
      setOptimisticTask({ ...optimisticTask, status: newStatus })
    })

    // Server update
    const result = await updateTaskStatus(task.id, newStatus)
    if (!result.success) {
      alert(`Failed to update status: ${result.error}`)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return
    }

    const result = await deleteTask(task.id)
    if (!result.success) {
      alert(`Failed to delete task: ${result.error}`)
    }
  }

  // Format date
  const formattedDate = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(optimisticTask.createdAt))

  return (
    <div
      className={`
        bg-white dark:bg-gray-800
        shadow rounded-lg p-4
        transition-opacity
        ${optimisticTask.status === 'DONE' ? 'opacity-75' : 'opacity-100'}
        ${isPending ? 'pointer-events-none' : ''}
      `}
    >
      {/* Status badge */}
      <div className="flex items-center justify-between mb-3">
        <span
          className={`
            px-2 py-1 text-xs font-medium rounded-full
            ${statusColors[optimisticTask.status]}
          `}
        >
          {statusLabels[optimisticTask.status]}
        </span>
        {isPending && (
          <span className="text-xs text-gray-500 dark:text-gray-400">Saving...</span>
        )}
      </div>

      {/* Task content */}
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
        {optimisticTask.title}
      </h3>
      {optimisticTask.description && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {optimisticTask.description}
        </p>
      )}

      {/* Date */}
      <p className="text-xs text-gray-500 dark:text-gray-500 mb-4">
        Created {formattedDate}
      </p>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {/* Status dropdown */}
        <select
          value={optimisticTask.status}
          onChange={(e) => handleStatusChange(e.target.value as Task['status'])}
          disabled={isPending}
          className="
            text-sm border border-gray-300 dark:border-gray-600
            rounded px-2 py-1
            bg-white dark:bg-gray-700
            text-gray-900 dark:text-gray-100
            focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        >
          <option value="TODO">To Do</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="DONE">Done</option>
        </select>

        <div className="flex-1" />

        {/* Edit button */}
        <Link
          href={`/tasks/${task.id}/edit`}
          className="
            text-sm text-blue-600 dark:text-blue-400
            hover:text-blue-700 dark:hover:text-blue-300
            font-medium
          "
        >
          Edit
        </Link>

        {/* Delete button */}
        <button
          onClick={handleDelete}
          disabled={isPending}
          className="
            text-sm text-red-600 dark:text-red-400
            hover:text-red-700 dark:hover:text-red-300
            font-medium
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        >
          Delete
        </button>
      </div>
    </div>
  )
}
