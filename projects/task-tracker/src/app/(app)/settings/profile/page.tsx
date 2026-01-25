import { getUser } from '@/shared/lib/dal'
import { ProfileForm } from '@/shared/components/ProfileForm'

export default async function ProfilePage() {
  const user = await getUser()

  if (!user) {
    // This shouldn't happen due to layout protection, but handle gracefully
    return (
      <div className="text-center py-8">
        <p className="text-gray-600 dark:text-gray-400">
          Unable to load profile. Please try again.
        </p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Profile Information
      </h2>
      <ProfileForm user={user} />
    </div>
  )
}
