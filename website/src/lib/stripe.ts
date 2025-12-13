import Stripe from 'stripe'
import { loadStripe } from '@stripe/stripe-js'

// Server-side Stripe instance
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
  typescript: true,
})

// Client-side Stripe instance
let stripePromise: ReturnType<typeof loadStripe>
export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
  }
  return stripePromise
}

// Pricing configuration
export const PRICING_PLANS = {
  hobby: {
    name: 'Hobby',
    priceMonthly: 29,
    priceYearly: 249,
    stripePriceIdMonthly: process.env.STRIPE_HOBBY_MONTHLY_PRICE_ID,
    stripePriceIdYearly: process.env.STRIPE_HOBBY_YEARLY_PRICE_ID,
    features: [
      '10 exports per month',
      'Up to 25km² area',
      '30m elevation resolution',
      'Basic satellite imagery',
      'Standard materials',
      'Email support',
    ],
    limits: {
      exportsPerMonth: 10,
      maxAreaKm2: 25,
      elevationResolution: 30,
      satelliteResolution: 10,
    },
  },
  professional: {
    name: 'Professional',
    priceMonthly: 99,
    priceYearly: 849,
    stripePriceIdMonthly: process.env.STRIPE_PRO_MONTHLY_PRICE_ID,
    stripePriceIdYearly: process.env.STRIPE_PRO_YEARLY_PRICE_ID,
    features: [
      'Unlimited exports',
      'Up to 100km² area',
      '10m elevation (1m with LiDAR)',
      'High-res satellite imagery',
      'Advanced PBR materials',
      'OSM integration (roads, buildings)',
      'Priority support',
      'Commercial license',
    ],
    limits: {
      exportsPerMonth: -1, // unlimited
      maxAreaKm2: 100,
      elevationResolution: 10,
      satelliteResolution: 3,
      lidarSupport: true,
    },
  },
  enterprise: {
    name: 'Enterprise',
    priceMonthly: null, // Custom pricing
    priceYearly: null,
    stripePriceIdMonthly: null,
    stripePriceIdYearly: null,
    features: [
      'Everything in Professional',
      'Unlimited area size',
      '1m LiDAR elevation',
      'Custom processing pipeline',
      'Dedicated support',
      'Custom integrations',
      'Bulk licensing',
      'SLA guarantee',
    ],
    limits: {
      exportsPerMonth: -1,
      maxAreaKm2: -1, // unlimited
      elevationResolution: 1,
      satelliteResolution: 0.5,
      lidarSupport: true,
      customProcessing: true,
    },
  },
}

export type PlanType = keyof typeof PRICING_PLANS
export type BillingInterval = 'monthly' | 'yearly'

// Helper to create checkout session
export async function createCheckoutSession(
  planType: PlanType,
  billingInterval: BillingInterval,
  userId: string,
  userEmail: string
) {
  const plan = PRICING_PLANS[planType]

  if (!plan) {
    throw new Error('Invalid plan type')
  }

  const priceId = billingInterval === 'monthly'
    ? plan.stripePriceIdMonthly
    : plan.stripePriceIdYearly

  if (!priceId) {
    throw new Error('Price ID not configured for this plan')
  }

  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [
      {
        price: priceId,
        quantity: 1,
      },
    ],
    customer_email: userEmail,
    client_reference_id: userId,
    metadata: {
      userId,
      planType,
      billingInterval,
    },
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    subscription_data: {
      metadata: {
        userId,
        planType,
      },
    },
  })

  return session
}

// Helper to create customer portal session
export async function createPortalSession(customerId: string) {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard/billing`,
  })

  return session
}
