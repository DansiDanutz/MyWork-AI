'use client';

import { PurchaseCredits } from '@/components/PurchaseCredits';

export default function PricingPage() {
  // In real app, get userId from session
  const userId = 'user@example.com';

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Purchase Credits</h1>
          <p className="text-gray-600 text-lg">
            Buy credits to use in the MyWork-AI marketplace
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <p className="text-sm text-gray-500 mb-2">
              Current Balance: <span className="font-bold">0 credits</span>
            </p>
            <p className="text-xs text-gray-400">
              Payments processed securely via Stripe
            </p>
          </div>

          <PurchaseCredits userId={userId} />

          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-500">
            <p>All purchases are final. Credits are non-refundable unless required by law.</p>
            <p className="mt-2">
              Need help? <a href="/support" className="text-blue-600 hover:underline">Contact support</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
