"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import {
  Loader2,
  Check,
  Shield,
  Download,
  RefreshCw,
  AlertCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatPrice } from "@/lib/utils"
import { productsApi, checkoutApi } from "@/lib/api"
import type { Product } from "@/types"

type LicenseType = "standard" | "extended"

interface LicenseOption {
  type: LicenseType
  name: string
  price: number
  description: string
  features: string[]
}

export default function CheckoutPage() {
  const params = useParams()
  const router = useRouter()
  const productId = params.productId as string

  const [product, setProduct] = useState<Product | null>(null)
  const [licenseOptions, setLicenseOptions] = useState<{
    standard_license: { price: number; description: string }
    extended_license: { price: number; description: string }
  } | null>(null)
  const [selectedLicense, setSelectedLicense] = useState<LicenseType>("standard")
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      setError(null)
      try {
        // Fetch product details
        const productRes = await productsApi.getById(productId)
        setProduct(productRes.data)

        // Fetch pricing options
        const pricesRes = await checkoutApi.getProductPrices(productId)
        setLicenseOptions(pricesRes.data)
      } catch (err: any) {
        console.error("Failed to fetch checkout data:", err)
        setError(err.response?.data?.detail || "Failed to load product information")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [productId])

  const handleCheckout = async () => {
    if (!product || processing) return

    setProcessing(true)
    setError(null)

    try {
      // Create Stripe checkout session
      const response = await checkoutApi.createSession({
        productId,
        licenseType: selectedLicense,
      })

      const { checkout_url } = response.data

      // Redirect to Stripe Checkout
      window.location.href = checkout_url
    } catch (err: any) {
      console.error("Checkout failed:", err)
      setError(err.response?.data?.detail || "Failed to initiate checkout. Please try again.")
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-950">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
            <p className="text-center text-gray-400">Loading checkout...</p>
          </div>
        </div>
      </main>
    )
  }

  if (error && !product) {
    return (
      <main className="min-h-screen bg-gray-950">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-2xl mx-auto text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-white mb-2">Checkout Error</h1>
            <p className="text-gray-400 mb-6">{error}</p>
            <Link href="/products">
              <Button>Browse Products</Button>
            </Link>
          </div>
        </div>
      </main>
    )
  }

  if (!product || !licenseOptions) {
    return null
  }

  const licenses: LicenseOption[] = [
    {
      type: "standard",
      name: "Standard License",
      price: licenseOptions.standard_license.price,
      description: licenseOptions.standard_license.description,
      features: [
        "Use in one single project",
        "Personal or commercial use",
        "Unlimited copies of the project",
        "Lifetime access to updates",
      ],
    },
    {
      type: "extended",
      name: "Extended License",
      price: licenseOptions.extended_license.price,
      description: licenseOptions.extended_license.description,
      features: [
        "Everything in Standard",
        "Unlimited projects",
        "Resell as part of your work",
        "SaaS usage allowed",
        "Priority support",
      ],
    },
  ]

  const currentPrice = licenses.find((l) => l.type === selectedLicense)?.price || 0

  return (
    <main className="min-h-screen bg-gray-950">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Link
              href={`/products/${product.slug}`}
              className="text-blue-400 hover:text-blue-300 text-sm mb-4 inline-block"
            >
              ← Back to product
            </Link>
            <h1 className="text-3xl font-bold text-white mb-2">Checkout</h1>
            <p className="text-gray-400">Complete your purchase securely with Stripe</p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Product & License Selection */}
            <div className="lg:col-span-2 space-y-6">
              {/* Product Summary */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-white">Product Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4">
                    {product.preview_images && product.preview_images[0] && (
                      <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-gray-800">
                        <img
                          src={product.preview_images[0]}
                          alt={product.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {product.title}
                      </h3>
                      <p className="text-sm text-gray-400 line-clamp-2">
                        {product.short_description || product.description}
                      </p>
                      <div className="flex gap-2 mt-2">
                        {product.category && (
                          <Badge variant="secondary" className="text-xs">
                            {product.category}
                          </Badge>
                        )}
                        {product.tech_stack && product.tech_stack.length > 0 && (
                          <Badge variant="outline" className="text-xs">
                            {product.tech_stack[0]}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* License Selection */}
              <div className="space-y-4">
                <h2 className="text-xl font-semibold text-white">Select License Type</h2>
                {licenses.map((license) => (
                  <Card
                    key={license.type}
                    className={`cursor-pointer transition-all ${
                      selectedLicense === license.type
                        ? "bg-blue-900/30 border-blue-500"
                        : "bg-gray-900 border-gray-800 hover:border-gray-700"
                    }`}
                    onClick={() => setSelectedLicense(license.type)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-white mb-1">
                            {license.name}
                          </h3>
                          <p className="text-sm text-gray-400">{license.description}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-white">
                            {formatPrice(license.price)}
                          </div>
                          <div className="text-xs text-gray-400">one-time payment</div>
                        </div>
                      </div>

                      <ul className="space-y-2">
                        {license.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                            <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>

                      {selectedLicense === license.type && (
                        <div className="mt-4 pt-4 border-t border-gray-700">
                          <Badge className="bg-blue-600 text-white">Selected</Badge>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Right Column - Order Summary */}
            <div className="lg:col-span-1">
              <Card className="bg-gray-900 border-gray-800 sticky top-8">
                <CardHeader>
                  <CardTitle className="text-white">Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Product */}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">{product.title}</span>
                    <span className="text-white font-medium">
                      {formatPrice(currentPrice)}
                    </span>
                  </div>

                  {/* License */}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">
                      {selectedLicense === "extended" ? "Extended License" : "Standard License"}
                    </span>
                    <span className="text-white">Included</span>
                  </div>

                  {/* Divider */}
                  <div className="border-t border-gray-700 pt-4">
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-400">Subtotal</span>
                      <span className="text-white">{formatPrice(currentPrice)}</span>
                    </div>
                    <div className="flex justify-between mb-2 text-sm text-gray-400">
                      <span>Platform fee (10%)</span>
                      <span>{formatPrice(currentPrice * 0.1)}</span>
                    </div>
                  </div>

                  {/* Total */}
                  <div className="border-t border-gray-700 pt-4">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold text-white">Total</span>
                      <span className="text-2xl font-bold text-white">
                        {formatPrice(currentPrice)}
                      </span>
                    </div>
                  </div>

                  {/* Checkout Button */}
                  {error && (
                    <div className="bg-red-900/20 border border-red-800 rounded-lg p-3">
                      <p className="text-sm text-red-400">{error}</p>
                    </div>
                  )}

                  <Button
                    onClick={handleCheckout}
                    disabled={processing}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    size="lg"
                  >
                    {processing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4 mr-2" />
                        Proceed to Payment
                      </>
                    )}
                  </Button>

                  {/* Security Note */}
                  <div className="text-center text-xs text-gray-500 space-y-1">
                    <p>Secure payment powered by Stripe</p>
                    <div className="flex items-center justify-center gap-2">
                      <Shield className="w-3 h-3" />
                      <span>SSL Encrypted</span>
                    </div>
                  </div>

                  {/* What happens next */}
                  <div className="bg-gray-800 rounded-lg p-4 space-y-2 text-sm">
                    <p className="font-semibold text-white mb-2">What happens next:</p>
                    <div className="flex items-start gap-2 text-gray-400">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>Complete payment securely with Stripe</span>
                    </div>
                    <div className="flex items-start gap-2 text-gray-400">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>Receive instant download access</span>
                    </div>
                    <div className="flex items-start gap-2 text-gray-400">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                      <span>Get lifetime updates</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
