"use client"

import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const plans = [
  {
    name: "Free",
    price: 0,
    description: "Perfect for exploring and learning",
    features: [
      "Access to MyWork framework",
      "10 Brain queries/month",
      "Browse marketplace",
      "Purchase products",
      "Community support",
    ],
    cta: "Get Started",
    popular: false,
  },
  {
    name: "Pro",
    price: 49,
    description: "For developers who want to sell",
    features: [
      "Everything in Free",
      "Unlimited Brain queries",
      "Sell on marketplace",
      "Keep 90% of sales",
      "Analytics dashboard",
      "Priority support",
      "Verified seller badge",
    ],
    cta: "Start Selling",
    popular: true,
  },
  {
    name: "Team",
    price: 149,
    description: "For agencies and teams",
    features: [
      "Everything in Pro",
      "5 team seats",
      "Team analytics",
      "Shared product library",
      "Custom branding",
      "API access",
      "Dedicated support",
    ],
    cta: "Contact Sales",
    popular: false,
  },
]

export default function PricingPage() {
  return (
    <main className="min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-b from-gray-800 to-gray-900 border-b border-gray-800">
        <div className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Start free, upgrade when you're ready to sell.
            No hidden fees. Cancel anytime.
          </p>
        </div>
      </div>

      {/* Pricing cards */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative ${
                plan.popular
                  ? "border-blue-500 shadow-lg shadow-blue-500/20"
                  : ""
              }`}
            >
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                  Most Popular
                </Badge>
              )}

              <CardHeader className="text-center pb-2">
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Price */}
                <div className="text-center">
                  <span className="text-5xl font-bold text-white">
                    ${plan.price}
                  </span>
                  <span className="text-gray-400">/month</span>
                </div>

                {/* Features */}
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                      <span className="text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <Button
                  className="w-full"
                  variant={plan.popular ? "default" : "outline"}
                  size="lg"
                >
                  {plan.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ section */}
        <div className="max-w-3xl mx-auto mt-20">
          <h2 className="text-3xl font-bold text-white text-center mb-10">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div className="border-b border-gray-800 pb-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                Why do sellers keep 90%?
              </h3>
              <p className="text-gray-400">
                We believe creators deserve more. Most marketplaces take 30-37.5%.
                We take only 10% because we prioritize volume over margin.
                More sellers = more products = more buyers = everyone wins.
              </p>
            </div>

            <div className="border-b border-gray-800 pb-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                What's the Brain?
              </h3>
              <p className="text-gray-400">
                The Brain is our collective knowledge system. Every developer's solutions
                contribute to making everyone smarter. It's AI-powered search through
                patterns, snippets, and tutorials contributed by the community.
              </p>
            </div>

            <div className="border-b border-gray-800 pb-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                When do I get paid?
              </h3>
              <p className="text-gray-400">
                We have a 7-day escrow period for buyer protection.
                After that, funds are automatically transferred to your
                connected Stripe account. You can withdraw anytime.
              </p>
            </div>

            <div className="border-b border-gray-800 pb-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-gray-400">
                Yes! You can cancel your subscription at any time.
                You'll keep access until the end of your billing period.
                Your products will stay listed, but you won't be able to add new ones.
              </p>
            </div>

            <div className="pb-6">
              <h3 className="text-lg font-semibold text-white mb-2">
                Is the framework really free?
              </h3>
              <p className="text-gray-400">
                Yes! The MyWork framework is 100% free and open source.
                You only pay if you want to sell on the marketplace.
                Build as much as you want, forever free.
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-16">
          <h2 className="text-2xl font-bold text-white mb-4">
            Ready to start building?
          </h2>
          <p className="text-gray-400 mb-8">
            Join thousands of developers on MyWork.
          </p>
          <Button size="xl" variant="success">
            Get Started Free
          </Button>
        </div>
      </div>
    </main>
  )
}
