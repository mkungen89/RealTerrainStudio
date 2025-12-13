import { NextRequest, NextResponse } from 'next/server'
import { stripe } from '@/lib/stripe'
import { supabase } from '@/lib/supabase'
import Stripe from 'stripe'

export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

// Generate a random license key
function generateLicenseKey(): string {
  const segments = []
  for (let i = 0; i < 4; i++) {
    const segment = Math.random().toString(36).substring(2, 8).toUpperCase()
    segments.push(segment)
  }
  return segments.join('-')
}

export async function POST(request: NextRequest) {
  const body = await request.text()
  const signature = request.headers.get('stripe-signature')

  if (!signature) {
    return NextResponse.json(
      { error: 'Missing stripe signature' },
      { status: 400 }
    )
  }

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (error: any) {
    console.error('Webhook signature verification failed:', error)
    return NextResponse.json(
      { error: `Webhook Error: ${error.message}` },
      { status: 400 }
    )
  }

  // Handle the event
  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session

        // Get user ID and plan type from metadata
        const userId = session.metadata?.userId
        const planType = session.metadata?.planType as 'hobby' | 'professional' | 'enterprise'

        if (!userId || !planType) {
          console.error('Missing metadata in checkout session')
          break
        }

        // Generate license key
        const licenseKey = generateLicenseKey()

        // Calculate expiration (1 year from now)
        const expiresAt = new Date()
        expiresAt.setFullYear(expiresAt.getFullYear() + 1)

        // Create license in database
        const { error: licenseError } = await supabase
          .from('licenses')
          .insert({
            user_id: userId,
            license_key: licenseKey,
            plan_type: planType,
            status: 'active',
            expires_at: expiresAt.toISOString(),
            max_activations: 3,
            current_activations: 0,
          })

        if (licenseError) {
          console.error('Error creating license:', licenseError)
        } else {
          console.log(`License created for user ${userId}: ${licenseKey}`)
        }

        break
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription

        // Update license status based on subscription status
        const userId = subscription.metadata?.userId

        if (!userId) {
          console.error('Missing userId in subscription metadata')
          break
        }

        const status = subscription.status === 'active' ? 'active' : 'expired'

        const { error: updateError } = await supabase
          .from('licenses')
          .update({ status })
          .eq('user_id', userId)

        if (updateError) {
          console.error('Error updating license:', updateError)
        }

        break
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription

        const userId = subscription.metadata?.userId

        if (!userId) {
          console.error('Missing userId in subscription metadata')
          break
        }

        // Mark license as cancelled
        const { error: cancelError } = await supabase
          .from('licenses')
          .update({ status: 'cancelled' })
          .eq('user_id', userId)

        if (cancelError) {
          console.error('Error cancelling license:', cancelError)
        }

        break
      }

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return NextResponse.json({ received: true })
  } catch (error: any) {
    console.error('Error handling webhook:', error)
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    )
  }
}
