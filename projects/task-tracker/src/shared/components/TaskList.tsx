'use client'

import { TaskCard } from './TaskCard'
import { EmptyState } from './EmptyState'

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
      <EmptyState
        title="No tasks yet!"
        description="Create your first task to get started organizing your work."
        action={{ label: 'Create your first task', href: '/tasks/new' }}
      />
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
