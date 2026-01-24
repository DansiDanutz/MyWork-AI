import type { Metadata } from 'next'
import { ClerkProvider } from '@clerk/nextjs'
import { Inter } from 'next/font/google'
import { Navbar } from '@/components/navbar'
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
          <Navbar />
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
