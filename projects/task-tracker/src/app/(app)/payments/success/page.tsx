'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function PaymentSuccess() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In real app, verify session_id and show actual purchase details
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Processing your purchase...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-green-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
        <div className="text-green-600 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold mb-4">Payment Successful!</h1>
        <p className="text-gray-600 mb-6">
          Your credits have been added to your account. You can now use them in the marketplace.
        </p>
        <div className="space-y-3">
          <Link
            href="/dashboard"
            className="block w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/marketplace"
            className="block w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700"
          >
            Browse Marketplace
          </Link>
        </div>
      </div>
    </div>
  );
}
