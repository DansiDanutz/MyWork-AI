'use client';

import { useState } from 'react';

const PACKAGES = [
  { id: 'starter', credits: 100, price: 10, name: 'Starter Pack', desc: 'Perfect for trying out' },
  { id: 'pro', credits: 500, price: 45, name: 'Pro Pack', desc: 'Best value for regular users' },
  { id: 'business', credits: 1000, price: 80, name: 'Business Pack', desc: 'For power users & teams' },
];

export function PurchaseCredits({ userId }: { userId: string }) {
  const [loading, setLoading] = useState<string | null>(null);

  const purchase = async (packageId: string) => {
    setLoading(packageId);
    try {
      const res = await fetch('/api/payments/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, packageId }),
      });

      const { url } = await res.json();
      if (url) {
        window.location.href = url;
      } else {
        alert('Failed to create checkout session');
      }
    } catch (error) {
      console.error(error);
      alert('Something went wrong');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mt-8">
      {PACKAGES.map((pkg) => (
        <div key={pkg.id} className="border rounded-lg p-6 flex flex-col">
          <h3 className="text-xl font-bold mb-2">{pkg.name}</h3>
          <p className="text-gray-600 mb-4">{pkg.desc}</p>
          <div className="text-3xl font-bold mb-2">{pkg.credits} Credits</div>
          <div className="text-2xl font-semibold text-green-600 mb-6">${pkg.price}</div>
          <button
            onClick={() => purchase(pkg.id)}
            disabled={loading === pkg.id}
            className="mt-auto bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === pkg.id ? 'Processing...' : 'Purchase'}
          </button>
        </div>
      ))}
    </div>
  );
}
