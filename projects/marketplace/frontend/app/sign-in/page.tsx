'use client'

import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome Back
          </h1>
          <p className="text-gray-400">
            Sign in to access your dashboard
          </p>
        </div>
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-8">
          <SignIn
            appearance={{
              elements: {
                rootBox: "mx-auto",
                card: "bg-transparent shadow-none",
                headerTitle: "text-white text-2xl font-bold",
                headerSubtitle: "text-gray-400",
                socialButtonsBlockButton: "bg-gray-700 hover:bg-gray-600 text-white border-gray-600",
                formButtonPrimary: "bg-blue-600 hover:bg-blue-700 text-white normal-case",
                formFieldLabel: "text-gray-300",
                formFieldInput: "bg-gray-700 border-gray-600 text-white focus:border-blue-500",
                footerActionLink: "text-blue-400 hover:text-blue-300",
                dividerText: "text-gray-500",
                identityPreviewText: "text-gray-400",
                identityPreviewTextContainer: "bg-gray-700/50",
                alert: "bg-gray-700 border-gray-600 text-gray-200",
                alertText: "text-gray-200",
              }
            }}
          />
        </div>
      </div>
    </div>
  )
}
