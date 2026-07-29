"""Stripe Billing Service for MyWork AI."""

import logging
import os

logger = logging.getLogger(__name__)

try:
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_ENABLED = bool(stripe.api_key)
except ImportError:
    STRIPE_ENABLED = False
    logger.warning('stripe package not installed. Billing disabled.')

PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'features': ['5 projects', 'Basic AI suggestions', 'Community support'],
        'stripe_price_id': os.getenv('STRIPE_FREE_PRICE_ID'),
    },
    'pro': {
        'name': 'Pro',
        'price': 19,
        'features': ['Unlimited projects', 'Advanced AI', 'Priority support', 'Custom templates'],
        'stripe_price_id': os.getenv('STRIPE_PRO_PRICE_ID'),
    },
    'team': {
        'name': 'Team',
        'price': 49,
        'features': ['Everything in Pro', 'Team collaboration', 'Admin dashboard', 'API access', 'SLA'],
        'stripe_price_id': os.getenv('STRIPE_TEAM_PRICE_ID'),
    },
}


def get_plans():
    return {k: {'name': v['name'], 'price': v['price'], 'features': v['features']} for k, v in PLANS.items()}


def create_checkout_session(user_email, plan_key, success_url, cancel_url):
    if not STRIPE_ENABLED:
        raise RuntimeError('Stripe is not configured. Set STRIPE_SECRET_KEY.')
    plan = PLANS.get(plan_key)
    if not plan or not plan.get('stripe_price_id'):
        raise ValueError(f'Invalid plan: {plan_key}')
    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            payment_method_types=['card'],
            customer_email=user_email,
            line_items=[{'price': plan['stripe_price_id'], 'quantity': 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'plan': plan_key},
        )
        logger.info(f'Checkout session created for {user_email} plan={plan_key}')
        return {'session_id': session.id, 'url': session.url}
    except stripe.error.StripeError as e:
        logger.error(f'Stripe checkout error: {e}')
        raise


def create_customer_portal_session(user_email, return_url):
    if not STRIPE_ENABLED:
        raise RuntimeError('Stripe is not configured.')
    try:
        customers = stripe.Customer.list(email=user_email, limit=2).data
        if (
            len(customers) != 1
            or not customers[0].email
            or customers[0].email.casefold() != user_email.casefold()
        ):
            raise ValueError('Configured billing identity must resolve to exactly one customer.')
        session = stripe.billing_portal.Session.create(
            customer=customers[0].id,
            return_url=return_url,
        )
        return {'url': session.url}
    except stripe.error.StripeError as e:
        logger.error(f'Stripe portal error: {e}')
        raise


def handle_webhook(payload, sig_header):
    if not STRIPE_ENABLED:
        raise RuntimeError('Stripe is not configured.')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        raise RuntimeError('STRIPE_WEBHOOK_SECRET not set.')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        logger.warning('Invalid webhook signature')
        raise ValueError('Invalid signature') from None
    event_type = event['type']
    data = event['data']['object']
    if event_type == 'checkout.session.completed':
        logger.info(f"Checkout completed: {data.get('customer_email')} plan={data.get('metadata', {}).get('plan')}")
    elif event_type == 'customer.subscription.updated':
        logger.info(f"Subscription updated: {data.get('customer')}")
    elif event_type == 'customer.subscription.deleted':
        logger.info(f"Subscription cancelled: {data.get('customer')}")
    elif event_type == 'invoice.payment_failed':
        logger.warning(f"Payment failed: {data.get('customer')}")
    else:
        logger.info(f'Webhook event: {event_type}')
    return {'handled': True, 'event_type': event_type}
