import Link from 'next/link'

type EmptyStateProps = {
  title: string
  description: string
  icon?: React.ReactNode
  action?: {
    label: string
    href: string
  }
}

/**
 * EmptyState: Reusable empty state component
 *
 * Features:
 * - Customizable icon, title, description
 * - Optional call-to-action button
 * - Responsive centered layout
 * - Dark mode support
 *
 * Usage:
 * <EmptyState
 *   title="No tasks yet!"
 *   description="Create your first task to get started."
 *   action={{ label: "Create task", href: "/tasks/new" }}
 * />
 */
export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  // Default icon (clipboard)
  const defaultIcon = (
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
  )

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="text-center max-w-md">
        {/* Icon */}
        {icon || defaultIcon}

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          {title}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
          {description}
        </p>

        {/* Action button */}
        {action && (
          <Link
            href={action.href}
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
            {action.label}
          </Link>
        )}
      </div>
    </div>
  )
}
