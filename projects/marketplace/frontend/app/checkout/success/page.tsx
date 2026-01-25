"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import {
  Loader2,
  CheckCircle,
  Download,
  Home,
  Package,
  AlertCircle,
  FileText,
  ExternalLink,
  Check,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatPrice } from "@/lib/utils"
import { checkoutApi, ordersApi } from "@/lib/api"

interface OrderData {
  order_id: string
  status: string
  product_name: string
  amount: number
  license_type: string
  download_url: string
}

export default function CheckoutSuccessPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const sessionId = searchParams.get("session_id")

  const [loading, setLoading] = useState(true)
  const [verifying, setVerifying] = useState(false)
  const [order, setOrder] = useState<OrderData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function verifyOrder() {
      if (!sessionId) {
        setError("No session ID found. Please contact support if you believe this is an error.")
        setLoading(false)
        return
      }

      setVerifying(true)
      setError(null)

      try {
        // Verify the session and create the order
        const response = await checkoutApi.verifyAndCreateOrder(sessionId)
        setOrder(response.data)
      } catch (err: any) {
        console.error("Order verification failed:", err)
        setError(
          err.response?.data?.detail ||
            "Failed to verify your order. Please contact support with your session ID: " + sessionId
        )
      } finally {
        setVerifying(false)
        setLoading(false)
      }
    }

    verifyOrder()
  }, [sessionId])

  const handleDownload = async () => {
    if (!order) return

    try {
      const response = await ordersApi.download(order.order_id)
      const { download_url: downloadUrl } = response.data

      // Open download URL in new tab
      window.open(downloadUrl, "_blank")
    } catch (err: any) {
      console.error("Download failed:", err)
      alert("Failed to generate download link. Please try again or contact support.")
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-950">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-2xl mx-auto text-center">
            <Loader2 className="w-16 h-16 animate-spin text-blue-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-white mb-2">Verifying Your Order</h1>
            <p className="text-gray-400">Please wait while we confirm your payment...</p>
          </div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gray-950">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-2xl mx-auto text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-white mb-2">Order Verification Failed</h1>
            <p className="text-gray-400 mb-6">{error}</p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => router.push("/dashboard")}>Go to Dashboard</Button>
              <Button variant="outline" asChild>
                <Link href="/products">Browse Products</Link>
              </Button>
            </div>
          </div>
        </div>
      </main>
    )
  }

  if (!order) {
    return null
  }

  return (
    <main className="min-h-screen bg-gray-950">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Success Message */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-10 h-10 text-green-500" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Payment Successful!</h1>
            <p className="text-gray-400">Thank you for your purchase. Your order is confirmed.</p>
          </div>

          {/* Order Details */}
          <Card className="bg-gray-900 border-gray-800 mb-6">
            <CardHeader>
              <CardTitle className="text-white">Order Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center pb-4 border-b border-gray-800">
                <div>
                  <p className="text-sm text-gray-400">Order ID</p>
                  <p className="text-white font-mono">{order.order_id}</p>
                </div>
                <Badge className="bg-green-900/30 text-green-400 border-green-800">
                  {order.status}
                </Badge>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Product</span>
                  <span className="text-white font-medium">{order.product_name}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-400">License Type</span>
                  <span className="text-white capitalize">{order.license_type}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-400">Amount Paid</span>
                  <span className="text-white font-semibold">{formatPrice(order.amount)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Download Card */}
          <Card className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border-blue-700 mb-6">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Download className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-1">
                    Ready to Download
                  </h3>
                  <p className="text-sm text-gray-300 mb-4">
                    You can download your purchase now. You'll have up to 10 download attempts.
                  </p>
                  <Button onClick={handleDownload} size="lg" className="bg-blue-600 hover:bg-blue-700">
                    <Download className="w-4 h-4 mr-2" />
                    Download Now
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* What's Next */}
          <Card className="bg-gray-900 border-gray-800 mb-6">
            <CardHeader>
              <CardTitle className="text-white">What's Next?</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Download your files</p>
                    <p className="text-sm text-gray-400">
                      Access your purchase instantly from the download button above
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Find it in your dashboard</p>
                    <p className="text-sm text-gray-400">
                      All your purchases are stored in your dashboard for easy access
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">Get lifetime updates</p>
                    <p className="text-sm text-gray-400">
                      Receive free updates as the seller improves the product
                    </p>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button onClick={() => router.push("/dashboard")} className="flex-1" variant="outline">
              <Home className="w-4 h-4 mr-2" />
              Go to Dashboard
            </Button>
            <Button onClick={() => router.push("/dashboard/purchases")} className="flex-1">
              <Package className="w-4 h-4 mr-2" />
              View My Purchases
            </Button>
          </div>

          {/* Support Link */}
          <div className="text-center mt-6 text-sm text-gray-400">
            Need help?{" "}
            <Link href="/support" className="text-blue-400 hover:text-blue-300">
              Contact Support
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
