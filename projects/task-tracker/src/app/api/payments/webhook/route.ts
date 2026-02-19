import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { CreditsLedger } from '../../../../../../../tools/credits_ledger';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-01-27.acacia',
});

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(req: NextRequest) {
  const body = await req.text();
  const sig = req.headers.get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, sig, webhookSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  const ledger = new CreditsLedger();

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        const { userId, packageId, credits } = session.metadata || {};

        if (userId && credits) {
          const amount = parseFloat(credits);
          const stripeId = session.payment_intent as string;

          const entry = ledger.add_credits(
            userId,
            amount,
            'stripe',
            stripeId,
            `Purchased ${packageId} pack via Stripe`,
          );

          console.log(`✅ Payment processed: ${userId} +${amount} credits (${entry.tx_id})`);
        }
        break;
      }

      case 'payment_intent.succeeded': {
        const intent = event.data.object as Stripe.PaymentIntent;
        console.log(`💰 Payment succeeded: ${intent.id} for ${intent.amount / 100} USD`);
        break;
      }

      case 'payment_intent.payment_failed': {
        const intent = event.data.object as Stripe.PaymentIntent;
        console.error(`❌ Payment failed: ${intent.id}`);
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('Webhook processing error:', error);
    return NextResponse.json({ error: 'Webhook failed' }, { status: 500 });
  }
}
