'use client'

import { useState, useCallback } from 'react'
import Image from 'next/image'
import { useDebounce } from '@/shared/hooks/useDebounce'
import { updateProfileField, type ProfileUpdateResult } from '@/app/actions/profile'

interface ProfileFormProps {
  user: {
    id: string
    name?: string | null
    email?: string | null
    image?: string | null
    bio?: string | null
    customAvatar?: string | null
  }
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

export function ProfileForm({ user }: ProfileFormProps) {
  const [status, setStatus] = useState<SaveStatus>('idle')
  const [error, setError] = useState<string | null>(null)

  // Save function for name field
  const saveName = useCallback<(value: string) => Promise<void>>(async (value: string) => {
    setStatus('saving')
    setError(null)

    const result: ProfileUpdateResult = await updateProfileField('name', value)

    if (result.success) {
      setStatus('saved')
      setTimeout(() => setStatus('idle'), 2000)
    } else {
      setStatus('error')
      setError(result.error || 'Failed to save')
    }
  }, [])

  // Save function for bio field
  const saveBio = useCallback<(value: string) => Promise<void>>(async (value: string) => {
    setStatus('saving')
    setError(null)

    const result: ProfileUpdateResult = await updateProfileField('bio', value)

    if (result.success) {
      setStatus('saved')
      setTimeout(() => setStatus('idle'), 2000)
    } else {
      setStatus('error')
      setError(result.error || 'Failed to save')
    }
  }, [])

  const debouncedSaveName = useDebounce<(value: string) => Promise<void>>(saveName, 3000)
  const debouncedSaveBio = useDebounce<(value: string) => Promise<void>>(saveBio, 3000)

  const handleChange = (field: 'name' | 'bio') => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    if (field === 'name') {
      debouncedSaveName(e.target.value)
    } else {
      debouncedSaveBio(e.target.value)
    }
  }

  return (
    <div className="space-y-6">
      {/* Status indicator */}
      <div className="flex items-center gap-2 text-sm">
        {status === 'saving' && (
          <>
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
            <span className="text-gray-500 dark:text-gray-400">Saving...</span>
          </>
        )}
        {status === 'saved' && (
          <>
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-green-600 dark:text-green-400">Saved</span>
          </>
        )}
        {status === 'error' && (
          <>
            <div className="w-2 h-2 bg-red-500 rounded-full" />
            <span className="text-red-600 dark:text-red-400">{error}</span>
          </>
        )}
      </div>

      {/* GitHub Profile Info (read-only) */}
      <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center gap-4">
          {user.image && (
            <Image
              src={user.image}
              alt={user.name || 'GitHub avatar'}
              width={64}
              height={64}
              className="w-16 h-16 rounded-full"
            />
          )}
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Connected GitHub account
            </p>
            <p className="font-medium text-gray-900 dark:text-white">
              {user.email}
            </p>
          </div>
        </div>
      </div>

      {/* Editable fields */}
      <div className="space-y-4">
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Display Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            defaultValue={user.name || ''}
            onChange={handleChange('name')}
            placeholder="Your display name"
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            maxLength={100}
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            This is how your name appears across the app
          </p>
        </div>

        <div>
          <label
            htmlFor="bio"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            Bio
          </label>
          <textarea
            id="bio"
            name="bio"
            defaultValue={user.bio || ''}
            onChange={handleChange('bio')}
            placeholder="Tell us about yourself"
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            maxLength={500}
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            A short description (max 500 characters)
          </p>
        </div>
      </div>

      {/* Note about auto-save */}
      <p className="text-xs text-gray-500 dark:text-gray-400 italic">
        Changes are saved automatically
      </p>
    </div>
  )
}
