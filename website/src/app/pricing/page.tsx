'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { PricingCard } from '@/components/PricingCard'
import { PRICING_PLANS, type BillingInterval, type PlanType } from '@/lib/stripe'
import { createSupabaseClient } from '@/lib/supabase'

export default function PricingPage() {
  const [billingInterval, setBillingInterval] = useState<BillingInterval>('yearly')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const supabase = createSupabaseClient()

  const handleSelectPlan = async (planType: PlanType) => {
    if (planType === 'enterprise') {
      // Redirect to contact page for enterprise
      router.push('/contact?plan=enterprise')
      return
    }

    setLoading(true)

    try {
      // Check if user is logged in
      const { data: { user } } = await supabase.auth.getUser()

      if (!user) {
        // Redirect to signup with plan selection
        router.push(`/signup?plan=${planType}&interval=${billingInterval}`)
        return
      }

      // Create checkout session
      const response = await fetch('/api/create-checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planType,
          billingInterval,
          userId: user.id,
          userEmail: user.email,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create checkout session')
      }

      const { url } = await response.json()

      // Redirect to Stripe Checkout
      window.location.href = url
    } catch (error) {
      console.error('Error creating checkout session:', error)
      alert('Failed to start checkout. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="py-20">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mx-auto mb-16 max-w-3xl text-center">
          <h1 className="mb-4 text-5xl font-bold text-slate-900">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-slate-600">
            Choose the plan that fits your needs. All plans include our core features.
          </p>
        </div>

        {/* Billing Toggle */}
        <div className="mb-12 flex justify-center">
          <div className="inline-flex rounded-lg bg-slate-100 p-1">
            <button
              onClick={() => setBillingInterval('monthly')}
              className={`rounded-md px-6 py-2 text-sm font-medium transition-colors ${
                billingInterval === 'monthly'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingInterval('yearly')}
              className={`rounded-md px-6 py-2 text-sm font-medium transition-colors ${
                billingInterval === 'yearly'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Yearly
              <span className="ml-2 text-xs text-green-600">Save 30%</span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid gap-8 lg:grid-cols-3">
          <PricingCard
            planType="hobby"
            name={PRICING_PLANS.hobby.name}
            description="Perfect for hobbyists and small projects"
            priceMonthly={PRICING_PLANS.hobby.priceMonthly}
            priceYearly={PRICING_PLANS.hobby.priceYearly}
            features={PRICING_PLANS.hobby.features}
            billingInterval={billingInterval}
            onSelectPlan={handleSelectPlan}
            ctaText={loading ? 'Loading...' : 'Get Started'}
          />

          <PricingCard
            planType="professional"
            name={PRICING_PLANS.professional.name}
            description="For professional developers and studios"
            priceMonthly={PRICING_PLANS.professional.priceMonthly}
            priceYearly={PRICING_PLANS.professional.priceYearly}
            features={PRICING_PLANS.professional.features}
            highlighted={true}
            billingInterval={billingInterval}
            onSelectPlan={handleSelectPlan}
            ctaText={loading ? 'Loading...' : 'Get Started'}
          />

          <PricingCard
            planType="enterprise"
            name={PRICING_PLANS.enterprise.name}
            description="Custom solutions for large organizations"
            priceMonthly={PRICING_PLANS.enterprise.priceMonthly}
            priceYearly={PRICING_PLANS.enterprise.priceYearly}
            features={PRICING_PLANS.enterprise.features}
            billingInterval={billingInterval}
            onSelectPlan={handleSelectPlan}
            ctaText="Contact Sales"
          />
        </div>

        {/* FAQ Section */}
        <div className="mx-auto mt-20 max-w-3xl">
          <h2 className="mb-8 text-center text-3xl font-bold text-slate-900">
            Frequently Asked Questions
          </h2>
          <div className="space-y-6">
            <div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">
                What happens after my trial ends?
              </h3>
              <p className="text-slate-600">
                After your 7-day free trial, you'll be automatically upgraded to the plan you selected.
                You can cancel anytime before the trial ends with no charge.
              </p>
            </div>
            <div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">
                Can I change plans later?
              </h3>
              <p className="text-slate-600">
                Yes! You can upgrade or downgrade your plan at any time from your dashboard.
                Changes take effect immediately, and we'll prorate the cost.
              </p>
            </div>
            <div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">
                How many machines can I activate?
              </h3>
              <p className="text-slate-600">
                Each license can be activated on up to 3 machines. You can deactivate machines
                from your dashboard to free up slots.
              </p>
            </div>
            <div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">
                What payment methods do you accept?
              </h3>
              <p className="text-slate-600">
                We accept all major credit cards (Visa, Mastercard, American Express) through Stripe.
                Enterprise customers can also pay via invoice.
              </p>
            </div>
            <div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900">
                Do you offer refunds?
              </h3>
              <p className="text-slate-600">
                Yes! We offer a 30-day money-back guarantee. If you're not satisfied, contact us
                for a full refund within 30 days of purchase.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
