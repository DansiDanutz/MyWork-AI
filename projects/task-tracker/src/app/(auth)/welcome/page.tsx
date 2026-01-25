import { redirect } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { getUser } from '@/shared/lib/dal'

export default async function WelcomePage() {
  // This page requires authentication
  const user = await getUser()

  // If somehow not authenticated, redirect to login
  if (!user) {
    redirect('/login')
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        {/* User avatar */}
        {user.image && (
          <Image
            src={user.image}
            alt={user.name || 'User avatar'}
            width={80}
            height={80}
            className="w-20 h-20 rounded-full mx-auto mb-4 border-4 border-blue-100 dark:border-blue-900"
          />
        )}

        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome, {user.name || 'there'}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Your account is all set up. Let&apos;s get you started.
        </p>
      </div>

      {/* Quick tour / onboarding steps */}
      <div className="space-y-4 mb-8">
        <div className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-blue-600 dark:text-blue-400 font-semibold">1</span>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white">Create your first task</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Click the &quot;New Task&quot; button to add your first item
            </p>
          </div>
        </div>

        <div className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-blue-600 dark:text-blue-400 font-semibold">2</span>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white">Organize with categories</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Group related tasks together for better organization
            </p>
          </div>
        </div>

        <div className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-blue-600 dark:text-blue-400 font-semibold">3</span>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white">Track your progress</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Mark tasks as done and watch your productivity soar
            </p>
          </div>
        </div>
      </div>

      {/* CTA to continue */}
      <div className="space-y-3">
        <Link
          href="/dashboard"
          className="block w-full text-center px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Go to Dashboard
        </Link>
        <Link
          href="/settings/profile"
          className="block w-full text-center px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Set up your profile
        </Link>
      </div>
    </div>
  )
}
