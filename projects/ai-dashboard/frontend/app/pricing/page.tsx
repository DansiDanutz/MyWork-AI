"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getPlans, createCheckout, type Plan, type PlansResponse } from "@/lib/billing";

const PLAN_COLORS: Record<string, string> = {
  free: "border-gray-300",
  pro: "border-blue-500 ring-2 ring-blue-100",
  team: "border-purple-500",
};

const PLAN_BADGES: Record<string, string> = {
  free: "",
  pro: "Most Popular",
  team: "Best Value",
};

export default function PricingPage() {
  const [plans, setPlans] = useState<Record<string, Plan>>({});
  const [stripeEnabled, setStripeEnabled] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPlans()
      .then((data: PlansResponse) => {
        setPlans(data.plans);
        setStripeEnabled(data.stripe_enabled);
      })
      .catch(() => setError("Failed to load pricing plans"));
  }, []);

  async function handleSubscribe(planKey: string) {
    if (planKey === "free") return;
    setLoading(planKey);
    setError(null);
    try {
      const origin = window.location.origin;
      const result = await createCheckout(
        "user@example.com",
        planKey,
        origin + "/pricing?success=true",
        origin + "/pricing?canceled=true",
      );
      window.location.href = result.url;
    } catch (error: unknown) {
      setError(error instanceof Error ? error.message : "Checkout failed");
      setLoading(null);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-gray-900">
            MyWork AI
          </Link>
          <div className="flex gap-4 text-sm">
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link href="/pricing" className="text-blue-600 font-medium">
              Pricing
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">Simple, transparent pricing</h1>
          <p className="mt-4 text-lg text-gray-600">
            Choose the plan that fits your workflow. Upgrade anytime.
          </p>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
            {error}
          </div>
        )}

        {!stripeEnabled && (
          <div className="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-center">
            Billing is being set up. Payment processing will be available soon.
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-8">
          {Object.entries(plans).map(([key, plan]) => (
            <div
              key={key}
              className={"bg-white rounded-xl border-2 p-8 flex flex-col " + (PLAN_COLORS[key] || "border-gray-300")}
            >
              {PLAN_BADGES[key] && (
                <span className="self-start bg-blue-100 text-blue-700 text-xs font-semibold px-3 py-1 rounded-full mb-4">
                  {PLAN_BADGES[key]}
                </span>
              )}
              <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
              <div className="mt-4">
                <span className="text-4xl font-bold">{"$" + plan.price}</span>
                {plan.price > 0 && <span className="text-gray-500">/month</span>}
              </div>
              <ul className="mt-8 space-y-3 flex-1">
                {plan.features.map((f: string) => (
                  <li key={f} className="flex items-start gap-2 text-gray-600">
                    <svg className="w-5 h-5 text-green-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSubscribe(key)}
                disabled={key === "free" || !stripeEnabled || loading !== null}
                className={
                  "mt-8 w-full py-3 px-6 rounded-lg font-medium transition-colors " +
                  (key === "pro"
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "bg-gray-100 text-gray-800 hover:bg-gray-200") +
                  (loading === key ? " opacity-50 cursor-wait" : "") +
                  (key === "free" || !stripeEnabled ? " opacity-50 cursor-not-allowed" : "")
                }
              >
                {loading === key ? "Redirecting..." : key === "free" ? "Current Plan" : "Subscribe"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
