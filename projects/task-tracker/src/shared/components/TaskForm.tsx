'use client'

import { useActionState } from 'react'
import { createTask } from '@/app/actions/tasks'
import Link from 'next/link'

type FormState = {
  success: boolean
  error?: string
  data?: { taskId: string }
} | null

export function TaskForm() {
  const [state, formAction, pending] = useActionState<FormState, FormData>(
    async (_prevState, formData) => {
      const result = await createTask(formData)
      return result
    },
    null
  )

  return (
    <form action={formAction} className="space-y-6 max-w-2xl">
      {/* Title field */}
      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          required
          maxLength={200}
          disabled={pending}
          className={`
            w-full px-3 py-2
            border rounded-md
            text-gray-900 dark:text-gray-100
            bg-white dark:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            ${state && !state.success ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}
          `}
          placeholder="e.g., Complete project proposal"
        />
        {state && !state.success && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">
            {state.error}
          </p>
        )}
      </div>

      {/* Description field */}
      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Description <span className="text-gray-500 text-xs">(optional)</span>
        </label>
        <textarea
          id="description"
          name="description"
          rows={4}
          maxLength={2000}
          disabled={pending}
          className="
            w-full px-3 py-2
            border border-gray-300 dark:border-gray-600 rounded-md
            text-gray-900 dark:text-gray-100
            bg-white dark:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            resize-vertical
          "
          placeholder="Add any additional details about this task..."
        />
      </div>

      {/* Button row */}
      <div className="flex items-center gap-3">
        {/* Submit button */}
        <button
          type="submit"
          disabled={pending}
          className="
            px-4 py-2
            bg-blue-600 text-white
            rounded-md font-medium
            hover:bg-blue-700
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors
          "
        >
          {pending ? 'Creating...' : 'Create Task'}
        </button>

        {/* Cancel button */}
        <Link
          href="/tasks"
          className="
            px-4 py-2
            border border-gray-300 dark:border-gray-600
            text-gray-700 dark:text-gray-300
            rounded-md font-medium
            hover:bg-gray-50 dark:hover:bg-gray-800
            focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500
            transition-colors
          "
        >
          Cancel
        </Link>
      </div>

      {/* Success message (shown after successful creation, before redirect) */}
      {state && state.success && (
        <div className="rounded-md bg-green-50 dark:bg-green-900/20 p-4">
          <p className="text-sm text-green-800 dark:text-green-200">
            Task created successfully! Redirecting...
          </p>
        </div>
      )}
    </form>
  )
}
