"use client";

// Note: global-error.tsx must include <html> and <body> tags per Next.js App Router requirements
// This is because it replaces the root layout when an error occurs
// See: https://nextjs.org/docs/app/building-your-application/routing/error-handling#global-errorjs
/* eslint-disable @next/next/no-html-link-for-pages */

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to console for debugging
    console.error("Global error:", error);
  }, [error]);

  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">
          <div className="max-w-md w-full text-center">
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-red-600 mb-4">
                Something went wrong!
              </h1>
              <p className="text-gray-600 mb-4">
                A critical error occurred. Please try again.
              </p>
              {error.digest && (
                <p className="text-sm text-gray-500">
                  Error ID: {error.digest}
                </p>
              )}
            </div>

            <div className="space-y-4">
              <button
                onClick={() => reset()}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Try Again
              </button>

              <a
                href="/"
                className="block w-full border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Go Home
              </a>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
