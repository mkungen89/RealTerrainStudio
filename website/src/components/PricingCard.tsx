'use client'

import { Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { cn, formatCurrency } from '@/lib/utils'
import { PlanType, BillingInterval } from '@/lib/stripe'

interface PricingCardProps {
  planType: PlanType
  name: string
  description?: string
  priceMonthly: number | null
  priceYearly: number | null
  features: string[]
  highlighted?: boolean
  billingInterval: BillingInterval
  onSelectPlan: (planType: PlanType) => void
  ctaText?: string
}

export function PricingCard({
  planType,
  name,
  description,
  priceMonthly,
  priceYearly,
  features,
  highlighted = false,
  billingInterval,
  onSelectPlan,
  ctaText = 'Get Started',
}: PricingCardProps) {
  const price = billingInterval === 'monthly' ? priceMonthly : priceYearly
  const isEnterprise = planType === 'enterprise'

  return (
    <Card
      className={cn(
        "relative flex flex-col",
        highlighted && "border-primary-500 shadow-lg ring-2 ring-primary-500"
      )}
    >
      {highlighted && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="inline-flex rounded-full bg-primary-500 px-4 py-1 text-sm font-semibold text-white">
            Most Popular
          </span>
        </div>
      )}

      <CardHeader>
        <CardTitle className="text-2xl">{name}</CardTitle>
        {description && (
          <CardDescription className="mt-2">{description}</CardDescription>
        )}
        <div className="mt-4">
          {isEnterprise ? (
            <div className="text-3xl font-bold">Custom</div>
          ) : (
            <>
              <div className="text-4xl font-bold">
                {formatCurrency(price!)}
              </div>
              <div className="text-sm text-slate-600">
                per {billingInterval === 'monthly' ? 'month' : 'year'}
              </div>
              {billingInterval === 'yearly' && priceYearly && priceMonthly && (
                <div className="mt-1 text-sm text-green-600">
                  Save {formatCurrency((priceMonthly * 12) - priceYearly)} per year
                </div>
              )}
            </>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1">
        <ul className="space-y-3">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="mr-3 h-5 w-5 flex-shrink-0 text-primary-500" />
              <span className="text-sm text-slate-700">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>

      <CardFooter>
        <Button
          variant={highlighted ? "primary" : "outline"}
          className="w-full"
          size="lg"
          onClick={() => onSelectPlan(planType)}
        >
          {isEnterprise ? 'Contact Sales' : ctaText}
        </Button>
      </CardFooter>
    </Card>
  )
}
