'use client'

import { useState, useEffect } from 'react'
import { ChatBubbleOvalLeftIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { submitFeedback } from '@/shared/actions/feedback'

type FeedbackType = 'bug' | 'idea' | 'other'

export function FeedbackWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [type, setType] = useState<FeedbackType>('idea')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const characterCount = feedback.length
  const maxCharacters = 500

  // Reset status after 3 seconds
  useEffect(() => {
    if (status !== 'idle') {
      const timer = setTimeout(() => {
        setStatus('idle')
        setErrorMessage('')
        if (status === 'success') {
          setIsOpen(false)
          setFeedback('')
          setType('idea')
        }
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [status])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!feedback.trim()) {
      setStatus('error')
      setErrorMessage('Please enter your feedback')
      return
    }

    if (characterCount > maxCharacters) {
      setStatus('error')
      setErrorMessage(`Feedback must be ${maxCharacters} characters or less`)
      return
    }

    setIsSubmitting(true)
    setStatus('idle')
    setErrorMessage('')

    try {
      const result = await submitFeedback({
        feedback: feedback.trim(),
        type,
        page: window.location.pathname,
      })

      if (result.success) {
        setStatus('success')
      } else {
        setStatus('error')
        setErrorMessage(result.error || 'Failed to submit feedback')
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      setStatus('error')
      setErrorMessage('Failed to submit feedback. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setIsOpen(false)
    setFeedback('')
    setType('idea')
    setStatus('idle')
    setErrorMessage('')
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen ? (
        // Floating button
        <button
          onClick={() => setIsOpen(true)}
          className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          aria-label="Send feedback"
        >
          <ChatBubbleOvalLeftIcon className="h-6 w-6" />
        </button>
      ) : (
        // Feedback form
        <div className="w-80 rounded-lg border border-gray-200 bg-white shadow-xl">
          <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
            <h3 className="text-lg font-semibold text-gray-900">Send Feedback</h3>
            <button
              onClick={handleCancel}
              className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
              aria-label="Close feedback form"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-4">
            {/* Feedback type selector */}
            <div className="mb-4">
              <label htmlFor="feedback-type" className="mb-2 block text-sm font-medium text-gray-700">
                Type
              </label>
              <select
                id="feedback-type"
                value={type}
                onChange={(e) => setType(e.target.value as FeedbackType)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
              >
                <option value="idea">Feature Idea</option>
                <option value="bug">Bug Report</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Feedback textarea */}
            <div className="mb-2">
              <label htmlFor="feedback-text" className="mb-2 block text-sm font-medium text-gray-700">
                What's on your mind?
              </label>
              <textarea
                id="feedback-text"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Share your thoughts, ideas, or report a bug..."
                rows={4}
                maxLength={maxCharacters}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
              />
            </div>

            {/* Character count */}
            <div className="mb-4 text-right">
              <span
                className={`text-xs ${
                  characterCount > maxCharacters ? 'text-red-600' : 'text-gray-500'
                }`}
              >
                {characterCount}/{maxCharacters}
              </span>
            </div>

            {/* Status messages */}
            {status === 'success' && (
              <div className="mb-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-800">
                Thanks for your feedback!
              </div>
            )}

            {status === 'error' && (
              <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
                {errorMessage}
              </div>
            )}

            {/* Action buttons */}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleCancel}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                disabled={isSubmitting || characterCount > maxCharacters}
              >
                {isSubmitting ? 'Sending...' : 'Submit'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
