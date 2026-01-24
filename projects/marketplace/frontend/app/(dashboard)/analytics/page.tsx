"use client"

import { useState } from "react"
import { useUser } from "@clerk/nextjs"
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  ShoppingBag,
  Users,
  Package,
  ArrowUpRight,
  ArrowDownRight,
  Download,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatPrice, formatDate } from "@/lib/utils"

type TimeRange = "7d" | "30d" | "90d"
type ChartType = "revenue" | "sales"

interface ChartData {
  date: string
  revenue: number
  sales: number
}

interface ProductPerformance {
  id: string
  name: string
  sales: number
  revenue: number
  views: number
  conversionRate: number
}

interface TrafficSource {
  source: string
  visits: number
  percentage: number
  color: string
}

export default function AnalyticsPage() {
  const { user } = useUser()
  const [timeRange, setTimeRange] = useState<TimeRange>("30d")
  const [chartType, setChartType] = useState<ChartType>("revenue")

  // Mock data - will be replaced with API calls
  const stats = {
    totalRevenue: 12456.80,
    revenueChange: 23.5,
    totalSales: 156,
    salesChange: 18.2,
    totalViews: 8934,
    viewsChange: 32.1,
    conversionRate: 1.75,
    conversionChange: 0.3,
    avgOrderValue: 79.85,
    avgOrderChange: 5.4,
  }

  const chartData: ChartData[] = [
    { date: "Jan 1", revenue: 245, sales: 3 },
    { date: "Jan 5", revenue: 189, sales: 2 },
    { date: "Jan 10", revenue: 478, sales: 6 },
    { date: "Jan 15", revenue: 356, sales: 4 },
    { date: "Jan 20", revenue: 623, sales: 8 },
    { date: "Jan 25", revenue: 891, sales: 11 },
    { date: "Jan 30", revenue: 742, sales: 9 },
  ]

  const topProducts: ProductPerformance[] = [
    {
      id: "1",
      name: "SaaS Starter Kit",
      sales: 67,
      revenue: 5373,
      views: 2341,
      conversionRate: 2.86,
    },
    {
      id: "2",
      name: "AI Chat Interface",
      sales: 45,
      revenue: 2241,
      views: 1876,
      conversionRate: 2.4,
    },
    {
      id: "3",
      name: "Next.js E-commerce Template",
      sales: 28,
      revenue: 2788,
      views: 1456,
      conversionRate: 1.92,
    },
    {
      id: "4",
      name: "React Admin Dashboard",
      sales: 16,
      revenue: 2046,
      views: 987,
      conversionRate: 1.62,
    },
  ]

  const trafficSources: TrafficSource[] = [
    { source: "Direct", visits: 3421, percentage: 38.3, color: "bg-blue-500" },
    { source: "Google", visits: 2890, percentage: 32.3, color: "bg-green-500" },
    { source: "Twitter", visits: 1234, percentage: 13.8, color: "bg-sky-500" },
    { source: "GitHub", visits: 876, percentage: 9.8, color: "bg-gray-600" },
    { source: "Other", visits: 513, percentage: 5.8, color: "bg-gray-400" },
  ]

  const maxValue = Math.max(...chartData.map((d) => (chartType === "revenue" ? d.revenue : d.sales)))

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-gray-400">
            Track your performance and revenue metrics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="flex items-center gap-2">
        <Button
          variant={timeRange === "7d" ? "default" : "outline"}
          size="sm"
          onClick={() => setTimeRange("7d")}
        >
          Last 7 days
        </Button>
        <Button
          variant={timeRange === "30d" ? "default" : "outline"}
          size="sm"
          onClick={() => setTimeRange("30d")}
        >
          Last 30 days
        </Button>
        <Button
          variant={timeRange === "90d" ? "default" : "outline"}
          size="sm"
          onClick={() => setTimeRange("90d")}
        >
          Last 90 days
        </Button>
      </div>

      {/* Key Metrics */}
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
            <div className="flex items-center text-xs mt-1">
              {stats.revenueChange > 0 ? (
                <>
                  <ArrowUpRight className="h-3 w-3 mr-1 text-green-500" />
                  <span className="text-green-500">{stats.revenueChange}%</span>
                </>
              ) : (
                <>
                  <ArrowDownRight className="h-3 w-3 mr-1 text-red-500" />
                  <span className="text-red-500">{Math.abs(stats.revenueChange)}%</span>
                </>
              )}
              <span className="text-gray-500 ml-1">vs previous period</span>
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
            <div className="flex items-center text-xs mt-1">
              {stats.salesChange > 0 ? (
                <>
                  <ArrowUpRight className="h-3 w-3 mr-1 text-green-500" />
                  <span className="text-green-500">{stats.salesChange}%</span>
                </>
              ) : (
                <>
                  <ArrowDownRight className="h-3 w-3 mr-1 text-red-500" />
                  <span className="text-red-500">{Math.abs(stats.salesChange)}%</span>
                </>
              )}
              <span className="text-gray-500 ml-1">vs previous period</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Product Views
            </CardTitle>
            <Users className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats.totalViews.toLocaleString()}
            </div>
            <div className="flex items-center text-xs mt-1">
              {stats.viewsChange > 0 ? (
                <>
                  <ArrowUpRight className="h-3 w-3 mr-1 text-green-500" />
                  <span className="text-green-500">{stats.viewsChange}%</span>
                </>
              ) : (
                <>
                  <ArrowDownRight className="h-3 w-3 mr-1 text-red-500" />
                  <span className="text-red-500">{Math.abs(stats.viewsChange)}%</span>
                </>
              )}
              <span className="text-gray-500 ml-1">vs previous period</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Conversion Rate
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {stats.conversionRate}%
            </div>
            <div className="flex items-center text-xs mt-1">
              {stats.conversionChange > 0 ? (
                <>
                  <ArrowUpRight className="h-3 w-3 mr-1 text-green-500" />
                  <span className="text-green-500">+{stats.conversionChange}%</span>
                </>
              ) : (
                <>
                  <ArrowDownRight className="h-3 w-3 mr-1 text-red-500" />
                  <span className="text-red-500">{stats.conversionChange}%</span>
                </>
              )}
              <span className="text-gray-500 ml-1">vs previous period</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chart Section */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                {chartType === "revenue" ? "Revenue Over Time" : "Sales Over Time"}
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant={chartType === "revenue" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartType("revenue")}
                >
                  Revenue
                </Button>
                <Button
                  variant={chartType === "sales" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChartType("sales")}
                >
                  Sales
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Simple CSS-based chart */}
            <div className="h-64 flex items-end gap-2">
              {chartData.map((data, index) => {
                const value = chartType === "revenue" ? data.revenue : data.sales
                const height = (value / maxValue) * 100
                return (
                  <div key={index} className="flex-1 flex flex-col items-center gap-2">
                    <div className="w-full relative group">
                      <div
                        className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-md transition-all hover:from-blue-500 hover:to-blue-300"
                        style={{ height: `${height}%`, minHeight: "4px" }}
                      />
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {chartType === "revenue" ? formatPrice(value) : value}
                      </div>
                    </div>
                    <span className="text-xs text-gray-500">{data.date}</span>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Traffic Sources */}
        <Card>
          <CardHeader>
            <CardTitle>Traffic Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {trafficSources.map((source, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white">{source.source}</span>
                    <span className="text-gray-400">{source.visits.toLocaleString()}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full ${source.color} transition-all`}
                      style={{ width: `${source.percentage}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 text-right">
                    {source.percentage}% of total
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Products */}
      <Card>
        <CardHeader>
          <CardTitle>Top Performing Products</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">
                    Product
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                    Sales
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                    Revenue
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                    Views
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">
                    Conversion
                  </th>
                </tr>
              </thead>
              <tbody>
                {topProducts.map((product, index) => (
                  <tr key={product.id} className="border-b border-gray-800 last:border-0">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                          {index + 1}
                        </div>
                        <span className="text-white font-medium">{product.name}</span>
                      </div>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className="text-white">{product.sales}</span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className="text-green-400 font-medium">
                        {formatPrice(product.revenue)}
                      </span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className="text-gray-400">{product.views.toLocaleString()}</span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <Badge
                        variant={
                          product.conversionRate > 2
                            ? "success"
                            : product.conversionRate > 1
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {product.conversionRate}%
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Additional Metrics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Average Order Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold text-white">
                  {formatPrice(stats.avgOrderValue)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Per order</p>
              </div>
              <div
                className={`p-3 rounded-full ${
                  stats.avgOrderChange > 0 ? "bg-green-600/20" : "bg-red-600/20"
                }`}
              >
                {stats.avgOrderChange > 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-500" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-500" />
                )}
              </div>
            </div>
            <div className="mt-4 text-sm">
              {stats.avgOrderChange > 0 ? (
                <span className="text-green-500">+{stats.avgOrderChange}%</span>
              ) : (
                <span className="text-red-500">{stats.avgOrderChange}%</span>
              )}
              <span className="text-gray-500 ml-1">vs previous period</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Products</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold text-white">
                  {topProducts.length}
                </p>
                <p className="text-sm text-gray-400 mt-1">Active listings</p>
              </div>
              <div className="p-3 rounded-full bg-blue-600/20">
                <Package className="h-6 w-6 text-blue-500" />
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-500">
              Across all categories
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
