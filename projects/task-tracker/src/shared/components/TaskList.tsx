'use client'

import { useEffect, useState } from 'react'
import { TaskCard } from './TaskCard'
import { SwipeableTaskCard } from './SwipeableTaskCard'
import { EmptyState } from './EmptyState'

type Task = {
  id: string
  title: string
  description: string | null
  status: 'TODO' | 'IN_PROGRESS' | 'DONE'
  createdAt: Date
  updatedAt: Date
  tags?: { id: string; name: string; color: string | null }[]
  attachments?: { id: string }[]
}

type TaskListProps = {
  tasks: Task[]
}

type TaskSectionProps = {
  title: string
  tasks: Task[]
  status: Task['status']
  isMobile: boolean
}

function TaskSection({ title, tasks, status, isMobile }: TaskSectionProps) {
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
          {sectionTasks.map((task) =>
            isMobile ? (
              <SwipeableTaskCard key={task.id} task={task} />
            ) : (
              <TaskCard key={task.id} task={task} />
            )
          )}
        </div>
      )}
    </div>
  )
}

export function TaskList({ tasks }: TaskListProps) {
  const [isMobile, setIsMobile] = useState(false)

  // Detect mobile/touch device
  useEffect(() => {
    const checkMobile = () => {
      // Check for touch support and screen width
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0
      const isNarrow = window.innerWidth < 768
      setIsMobile(hasTouch && isNarrow)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

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
      {/* Swipe hint on mobile */}
      {isMobile && (
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
          Swipe right to complete, left to delete
        </p>
      )}
      <TaskSection title="To Do" tasks={tasks} status="TODO" isMobile={isMobile} />
      <TaskSection title="In Progress" tasks={tasks} status="IN_PROGRESS" isMobile={isMobile} />
      <TaskSection title="Done" tasks={tasks} status="DONE" isMobile={isMobile} />
    </div>
  )
}
