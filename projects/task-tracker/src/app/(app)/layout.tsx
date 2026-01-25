import Link from 'next/link'
import { redirect } from 'next/navigation'
import { auth, signOut } from '@/shared/lib/auth'
import { UserMenu } from '@/shared/components/UserMenu'

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth()

  // Protect all routes in (app) group
  if (!session?.user) {
    redirect('/login')
  }

  // Server Action for sign out (passed to client component)
  async function handleSignOut() {
    'use server'
    await signOut({ redirectTo: '/' })
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="text-xl font-bold text-gray-900 dark:text-white">
              Task Tracker
            </Link>
            <nav className="hidden md:flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              >
                Dashboard
              </Link>
              <Link
                href="/tasks"
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              >
                Tasks
              </Link>
            </nav>
          </div>

          <UserMenu user={session.user} signOutAction={handleSignOut} />
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
