'use client'

import { useState, useCallback } from 'react'
import { useSwipeable } from 'react-swipeable'
import { TaskCard } from './TaskCard'
import { updateTaskStatus, deleteTask } from '@/app/actions/tasks'

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

type SwipeableTaskCardProps = {
  task: Task
}

export function SwipeableTaskCard({ task }: SwipeableTaskCardProps) {
  const [swipeOffset, setSwipeOffset] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null)

  const handleComplete = useCallback(async () => {
    if (task.status === 'DONE' || isProcessing) return
    setIsProcessing(true)
    const result = await updateTaskStatus(task.id, 'DONE')
    if (!result.success) {
      alert(`Failed to complete task: ${result.error}`)
    }
    setIsProcessing(false)
    setSwipeOffset(0)
  }, [task.id, task.status, isProcessing])

  const handleDelete = useCallback(async () => {
    if (isProcessing) return
    if (!confirm('Delete this task?')) {
      setSwipeOffset(0)
      return
    }
    setIsProcessing(true)
    const result = await deleteTask(task.id)
    if (!result.success) {
      alert(`Failed to delete task: ${result.error}`)
      setIsProcessing(false)
      setSwipeOffset(0)
    }
  }, [task.id, isProcessing])

  const handlers = useSwipeable({
    onSwiping: (eventData) => {
      // Only track horizontal swipes
      if (Math.abs(eventData.deltaX) > Math.abs(eventData.deltaY)) {
        setSwipeOffset(eventData.deltaX)
        setSwipeDirection(eventData.deltaX > 0 ? 'right' : 'left')
      }
    },
    onSwipedRight: () => {
      if (Math.abs(swipeOffset) > 100) {
        handleComplete()
      } else {
        setSwipeOffset(0)
      }
      setSwipeDirection(null)
    },
    onSwipedLeft: () => {
      if (Math.abs(swipeOffset) > 100) {
        handleDelete()
      } else {
        setSwipeOffset(0)
      }
      setSwipeDirection(null)
    },
    onTouchEndOrOnMouseUp: () => {
      if (Math.abs(swipeOffset) < 100) {
        setSwipeOffset(0)
        setSwipeDirection(null)
      }
    },
    delta: 30, // Minimum swipe distance to register
    preventScrollOnSwipe: true,
    trackMouse: false, // Desktop uses buttons, not swipe
  })

  // Background color based on swipe direction
  const getBgColor = () => {
    if (!swipeDirection) return ''
    if (swipeDirection === 'right') return 'bg-green-500'
    return 'bg-red-500'
  }

  // Icon based on swipe direction
  const getSwipeIcon = () => {
    if (!swipeDirection) return null
    if (swipeDirection === 'right') {
      return (
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white">
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )
    }
    return (
      <div className="absolute right-4 top-1/2 -translate-y-1/2 text-white">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </div>
    )
  }

  return (
    <div className="relative overflow-hidden rounded-lg">
      {/* Background reveal */}
      <div className={`absolute inset-0 ${getBgColor()} transition-colors`}>
        {getSwipeIcon()}
      </div>

      {/* Card content */}
      <div
        {...handlers}
        style={{
          transform: `translateX(${swipeOffset}px)`,
          transition: swipeOffset === 0 ? 'transform 0.2s ease-out' : 'none',
        }}
        className={`relative touch-pan-y ${isProcessing ? 'opacity-50' : ''}`}
      >
        <TaskCard task={task} />
      </div>
    </div>
  )
}
