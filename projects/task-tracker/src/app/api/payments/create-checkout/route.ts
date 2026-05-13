import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';

function getStripe(): Stripe {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error('STRIPE_SECRET_KEY is not configured');
  }
  return new Stripe(process.env.STRIPE_SECRET_KEY, {
    apiVersion: '2026-04-22.dahlia',
  });
}

const CREDIT_PACKAGES = {
  'starter': { credits: 100, price: 1000, name: 'Starter Pack' },      // $10
  'pro': { credits: 500, price: 4500, name: 'Pro Pack' },             // $45
  'business': { credits: 1000, price: 8000, name: 'Business Pack' },  // $80
};

export async function POST(req: NextRequest) {
  try {
    const { userId, packageId } = await req.json();

    if (!userId || !packageId || !CREDIT_PACKAGES[packageId as keyof typeof CREDIT_PACKAGES]) {
      return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
    }

    const pkg = CREDIT_PACKAGES[packageId as keyof typeof CREDIT_PACKAGES];

    const session = await getStripe().checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{
        price_data: {
          currency: 'usd',
          product_data: {
            name: pkg.name,
            description: `${pkg.credits} credits for MyWork-AI marketplace`,
            metadata: { packageId, credits: pkg.credits.toString() },
          },
          unit_amount: pkg.price,
        },
        quantity: 1,
      }],
      mode: 'payment',
      success_url: `${process.env.NEXTAUTH_URL}/payments/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXTAUTH_URL}/pricing`,
      metadata: {
        userId,
        packageId,
        credits: pkg.credits.toString(),
      },
      customer_email: userId.includes('@') ? userId : undefined,
    });

    return NextResponse.json({ sessionId: session.id, url: session.url });
  } catch (error) {
    console.error('Stripe checkout error:', error);
    return NextResponse.json({ error: 'Payment failed' }, { status: 500 });
  }
}
