export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Plan {
  name: string;
  price: number;
  features: string[];
}

export interface PlansResponse {
  plans: Record<string, Plan>;
  stripe_enabled: boolean;
}

export interface CheckoutResponse {
  session_id: string;
  url: string;
}

export async function getPlans(): Promise<PlansResponse> {
  const res = await fetch(API_BASE + '/api/billing/plans');
  if (!res.ok) throw new Error('Failed to fetch plans');
  return res.json();
}

export async function createCheckout(
  email: string,
  plan: string,
  successUrl: string,
  cancelUrl: string,
): Promise<CheckoutResponse> {
  const res = await fetch(API_BASE + '/api/billing/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, plan, success_url: successUrl, cancel_url: cancelUrl }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Checkout failed');
  }
  return res.json();
}

export async function openCustomerPortal(customerId: string, returnUrl: string) {
  const res = await fetch(API_BASE + '/api/billing/portal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customer_id: customerId, return_url: returnUrl }),
  });
  if (!res.ok) throw new Error('Portal failed');
  return res.json();
}
