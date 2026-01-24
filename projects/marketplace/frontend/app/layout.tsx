import type { Metadata } from 'next'
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MyWork Marketplace',
  description: 'You Build. You Share. You Sell. The AI-powered marketplace where developers keep 90%.',
  keywords: ['marketplace', 'developer', 'sell code', 'saas templates', 'developer tools'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en" className="dark">
        <body className={`${inter.className} bg-gray-900 text-gray-100 min-h-screen`}>
          <header className="border-b border-gray-800 bg-gray-900/95 backdrop-blur supports-[backdrop-filter]:bg-gray-900/60">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
              <div className="flex items-center gap-8">
                <Link href="/" className="text-xl font-bold text-white">
                  MyWork
                </Link>
                <nav className="hidden md:flex items-center gap-6">
                  <Link href="/products" className="text-gray-300 hover:text-white transition">
                    Browse
                  </Link>
                  <Link href="/pricing" className="text-gray-300 hover:text-white transition">
                    Pricing
                  </Link>
                </nav>
              </div>
              <div className="flex items-center gap-4">
                <SignedOut>
                  <SignInButton mode="modal">
                    <button className="text-gray-300 hover:text-white transition">
                      Sign In
                    </button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <button className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition">
                      Sign Up
                    </button>
                  </SignUpButton>
                </SignedOut>
                <SignedIn>
                  <button className="text-gray-300 hover:text-white transition relative p-2">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                  </button>
                  <Link href="/dashboard" className="text-gray-300 hover:text-white transition">
                    Dashboard
                  </Link>
                  <UserButton afterSignOutUrl="/" />
                </SignedIn>
              </div>
            </div>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
