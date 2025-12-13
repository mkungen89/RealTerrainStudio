import { NextRequest, NextResponse } from 'next/server'
import { createCheckoutSession, type PlanType, type BillingInterval } from '@/lib/stripe'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { planType, billingInterval, userId, userEmail } = body

    // Validate request
    if (!planType || !billingInterval || !userId || !userEmail) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Create checkout session
    const session = await createCheckoutSession(
      planType as PlanType,
      billingInterval as BillingInterval,
      userId,
      userEmail
    )

    return NextResponse.json({ url: session.url })
  } catch (error: any) {
    console.error('Error creating checkout session:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to create checkout session' },
      { status: 500 }
    )
  }
}
