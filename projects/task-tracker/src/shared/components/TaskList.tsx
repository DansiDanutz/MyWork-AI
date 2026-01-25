'use client'

import { TaskCard } from './TaskCard'
import Link from 'next/link'

type Task = {
  id: string
  title: string
  description: string | null
  status: 'TODO' | 'IN_PROGRESS' | 'DONE'
  createdAt: Date
  updatedAt: Date
  tags?: { id: string; name: string; color: string | null }[]
}

type TaskListProps = {
  tasks: Task[]
}

type TaskSectionProps = {
  title: string
  tasks: Task[]
  status: Task['status']
}

function TaskSection({ title, tasks, status }: TaskSectionProps) {
  const sectionTasks = tasks.filter((task) => task.status === status)

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {title} ({sectionTasks.length})
      </h2>
      {sectionTasks.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400 italic">
          No tasks
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sectionTasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  )
}

export function TaskList({ tasks }: TaskListProps) {
  // Check if all sections are empty
  const isEmpty = tasks.length === 0

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="text-center max-w-md">
          <svg
            className="mx-auto h-24 w-24 text-gray-400 dark:text-gray-600 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            No tasks yet!
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Create your first task to get started organizing your work.
          </p>
          <Link
            href="/tasks/new"
            className="
              inline-flex items-center justify-center
              px-4 py-2
              border border-transparent
              text-sm font-medium rounded-md
              text-white bg-blue-600
              hover:bg-blue-700
              focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
              dark:bg-blue-500 dark:hover:bg-blue-600
              transition-colors
            "
          >
            Create your first task
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <TaskSection title="To Do" tasks={tasks} status="TODO" />
      <TaskSection title="In Progress" tasks={tasks} status="IN_PROGRESS" />
      <TaskSection title="Done" tasks={tasks} status="DONE" />
    </div>
  )
}
