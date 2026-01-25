import 'server-only'
import { cache } from 'react'
import { auth } from '@/shared/lib/auth'
import { prisma } from '@/shared/lib/db'
import { redirect } from 'next/navigation'

/**
 * Verify the current session and redirect to login if not authenticated.
 * Uses React cache() to prevent duplicate auth checks within the same request.
 *
 * @returns Object with isAuth flag and userId
 * @throws Redirects to /login if not authenticated
 */
export const verifySession = cache(async () => {
  const session = await auth()

  if (!session?.user?.id) {
    redirect('/login')
  }

  return { isAuth: true, userId: session.user.id }
})

/**
 * Get the current authenticated user with profile data.
 * Calls verifySession first to ensure authentication.
 * Uses React cache() to prevent duplicate database queries.
 *
 * @returns User object with profile fields, or null if not found
 */
export const getUser = cache(async () => {
  const { userId } = await verifySession()

  const user = await prisma.user.findUnique({
    where: { id: userId },
    select: {
      id: true,
      name: true,
      email: true,
      image: true,
      bio: true,
      customAvatar: true,
      createdAt: true,
      updatedAt: true,
      // Exclude sensitive fields like accounts/sessions
    }
  })

  return user
})

/**
 * Get session without redirect - for checking auth status in UI.
 * Use this when you want to show different content for auth/unauth users
 * rather than forcing a redirect.
 */
export const getSession = cache(async () => {
  return await auth()
})
