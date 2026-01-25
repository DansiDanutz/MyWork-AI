"use client"

export const dynamic = "force-dynamic"

import { useEffect, useState } from "react"
import { ShoppingBag, Download, ExternalLink, Calendar, Package } from "lucide-react"
import Link from "next/link"

// Types
interface Order {
  id: string
  order_number: string
  product_id: string
  product_name: string
  amount: number
  license_type: string
  status: string
  payment_status: string
  download_url: string | null
  download_count: number
  created_at: string
}

export default function PurchasesPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/orders?role=buyer`)

      if (!response.ok) {
        throw new Error("Failed to fetch orders")
      }

      const data = await response.json()
      setOrders(data.orders || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load orders")
      console.error("Error fetching orders:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (orderId: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/orders/${orderId}/download`,
        { method: "POST" }
      )

      if (!response.ok) {
        throw new Error("Failed to get download link")
      }

      const data = await response.json()

      // Open download URL in new tab
      if (data.download_url) {
        window.open(data.download_url, "_blank")
        // Refresh orders to update download count
        fetchOrders()
      }
    } catch (err) {
      console.error("Error downloading:", err)
      alert("Failed to download product. Please try again.")
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount)
  }

  const getStatusBadge = (status: string, paymentStatus: string) => {
    if (paymentStatus === "completed") {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900/30 text-green-400 border border-green-700/50">
          Completed
        </span>
      )
    }

    if (paymentStatus === "pending") {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-900/30 text-yellow-400 border border-yellow-700/50">
          Pending
        </span>
      )
    }

    if (paymentStatus === "failed") {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-900/30 text-red-400 border border-red-700/50">
          Failed
        </span>
      )
    }

    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-700/30 text-gray-400 border border-gray-600/50">
        {status}
      </span>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <ShoppingBag className="w-8 h-8 text-blue-400" />
          <h1 className="text-3xl font-bold text-white">My Purchases</h1>
        </div>
        <p className="text-gray-400">
          View and download your purchased products
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-6 text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchOrders}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && orders.length === 0 && (
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-12 text-center">
          <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No purchases yet</h3>
          <p className="text-gray-400 mb-6">
            Start browsing our marketplace to find amazing projects
          </p>
          <Link
            href="/products"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <ExternalLink className="w-4 h-4" />
            Browse Products
          </Link>
        </div>
      )}

      {/* Orders List */}
      {!loading && !error && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div
              key={order.id}
              className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                {/* Product Info */}
                <div className="flex-1">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Package className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-white mb-1 truncate">
                        {order.product_name}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {formatDate(order.created_at)}
                        </span>
                        <span>•</span>
                        <span className="uppercase">{order.license_type} License</span>
                        <span>•</span>
                        <span className="font-mono text-xs">{order.order_number}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Status & Actions */}
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white mb-1">
                      {formatPrice(Number(order.amount))}
                    </div>
                    {getStatusBadge(order.status, order.payment_status)}
                  </div>

                  {order.payment_status === "completed" && order.download_url && (
                    <button
                      onClick={() => handleDownload(order.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition flex-shrink-0"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  )}

                  {order.payment_status === "pending" && (
                    <div className="text-sm text-gray-400">
                      Processing...
                    </div>
                  )}
                </div>
              </div>

              {/* Download Count */}
              {order.payment_status === "completed" && (
                <div className="mt-4 pt-4 border-t border-gray-700">
                  <p className="text-sm text-gray-400">
                    Downloads used: <span className="text-white">{order.download_count}</span>
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
