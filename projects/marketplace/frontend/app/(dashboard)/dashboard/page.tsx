"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useUser } from "@clerk/nextjs"
import { useSearchParams } from "next/navigation"
import {
  DollarSign,
  Package,
  ShoppingBag,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Brain,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatPrice, formatDate } from "@/lib/utils"

export default function DashboardPage() {
  const { user } = useUser()
  const searchParams = useSearchParams()
  const [showTopupNotice, setShowTopupNotice] = useState(false)
  const [stats, setStats] = useState({
    totalRevenue: 2456.80,
    totalSales: 23,
    totalProducts: 4,
    brainContributions: 12,
    revenueChange: 12.5,
    salesChange: 8.3,
  })

  const [recentOrders, setRecentOrders] = useState([
    {
      id: "1",
      productName: "SaaS Starter Kit",
      buyer: "john_dev",
      amount: 299,
      date: "2024-01-24",
    },
    {
      id: "2",
      productName: "AI Chat Interface",
      buyer: "startup_ceo",
      amount: 149,
      date: "2024-01-23",
    },
    {
      id: "3",
      productName: "SaaS Starter Kit",
      buyer: "product_builder",
      amount: 299,
      date: "2024-01-22",
    },
  ])

  useEffect(() => {
    if (searchParams?.get("credit_topup") === "success") {
      setShowTopupNotice(true)
    }
  }, [searchParams])

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {showTopupNotice && (
        <div className="rounded-lg border border-green-700/50 bg-green-900/20 px-4 py-3 text-green-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <p className="font-medium">Credits top-up successful</p>
            <p className="text-sm text-green-200/80">
              Your balance has been updated and is ready to use.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/dashboard/credits">
              <Button size="sm" variant="secondary">View Credits</Button>
            </Link>
            <Button size="sm" variant="ghost" onClick={() => setShowTopupNotice(false)}>
              Dismiss
            </Button>
          </div>
        </div>
      )}
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.firstName || "Creator"}!
          </h1>
          <p className="text-gray-400">
            Here's what's happening with your products.
          </p>
        </div>
        <Link href="/dashboard/products/new">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Product
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Total Revenue
            </CardTitle>
            <DollarSign className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {formatPrice(stats.totalRevenue)}
            </div>
            <div className="flex items-center text-xs text-green-500 mt-1">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              {stats.revenueChange}% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Total Sales
            </CardTitle>
            <ShoppingBag className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats.totalSales}
            </div>
            <div className="flex items-center text-xs text-green-500 mt-1">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              {stats.salesChange}% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Products Listed
            </CardTitle>
            <Package className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats.totalProducts}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              2 featured
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Brain Contributions
            </CardTitle>
            <Brain className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats.brainContributions}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              847 total uses
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Two column layout */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Sales */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Sales</CardTitle>
            <Link href="/dashboard/analytics">
              <Button variant="ghost" size="sm">
                View all
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentOrders.map((order) => (
                <div
                  key={order.id}
                  className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0"
                >
                  <div>
                    <p className="font-medium text-white">{order.productName}</p>
                    <p className="text-sm text-gray-400">
                      Purchased by {order.buyer}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-green-400">
                      +{formatPrice(order.amount * 0.9)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDate(order.date)}
                    </p>
                  </div>
                </div>
              ))}

              {recentOrders.length === 0 && (
                <p className="text-gray-400 text-center py-8">
                  No sales yet. List your first product!
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/dashboard/products/new" className="block">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-700 hover:border-gray-600 hover:bg-gray-800/50 transition">
                <div className="p-2 rounded-lg bg-blue-600">
                  <Package className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-medium text-white">List a Product</p>
                  <p className="text-sm text-gray-400">
                    Upload and sell your project
                  </p>
                </div>
              </div>
            </Link>

            <Link href="/dashboard/brain" className="block">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-700 hover:border-gray-600 hover:bg-gray-800/50 transition">
                <div className="p-2 rounded-lg bg-purple-600">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-medium text-white">Contribute to Brain</p>
                  <p className="text-sm text-gray-400">
                    Share your knowledge and patterns
                  </p>
                </div>
              </div>
            </Link>

            <Link href="/dashboard/payouts" className="block">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-700 hover:border-gray-600 hover:bg-gray-800/50 transition">
                <div className="p-2 rounded-lg bg-green-600">
                  <DollarSign className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-medium text-white">View Payouts</p>
                  <p className="text-sm text-gray-400">
                    Track your earnings and withdrawals
                  </p>
                </div>
              </div>
            </Link>

            <Link href="/dashboard/analytics" className="block">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-700 hover:border-gray-600 hover:bg-gray-800/50 transition">
                <div className="p-2 rounded-lg bg-orange-600">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-medium text-white">View Analytics</p>
                  <p className="text-sm text-gray-400">
                    See detailed performance metrics
                  </p>
                </div>
              </div>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Seller status */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-green-600/20">
                <TrendingUp className="h-6 w-6 text-green-500" />
              </div>
              <div>
                <h3 className="font-semibold text-white">Seller Status: Active</h3>
                <p className="text-sm text-gray-400">
                  Your products are live on the marketplace
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="success">Pro Plan</Badge>
              <Badge variant="secondary">Verified</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
