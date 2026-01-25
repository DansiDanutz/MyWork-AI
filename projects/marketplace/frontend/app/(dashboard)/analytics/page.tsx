"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
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
  Loader2,
  AlertCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatPrice, formatDate } from "@/lib/utils"
import { analyticsApi } from "@/lib/api"

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

interface AnalyticsStats {
  totalRevenue: number
  revenueChange: number
  totalSales: number
  salesChange: number
  totalViews: number
  viewsChange: number
  conversionRate: number
  conversionChange: number
  avgOrderValue: number
  avgOrderChange: number
}

export default function AnalyticsPage() {
  const { user } = useUser()
  const [timeRange, setTimeRange] = useState<TimeRange>("30d")
  const [chartType, setChartType] = useState<ChartType>("revenue")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // State for API data
  const [stats, setStats] = useState<AnalyticsStats>({
    totalRevenue: 0,
    revenueChange: 0,
    totalSales: 0,
    salesChange: 0,
    totalViews: 0,
    viewsChange: 0,
    conversionRate: 0,
    conversionChange: 0,
    avgOrderValue: 0,
    avgOrderChange: 0,
  })
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [topProducts, setTopProducts] = useState<ProductPerformance[]>([])
  const [trafficSources, setTrafficSources] = useState<TrafficSource[]>([])

  // Load analytics data
  useEffect(() => {
    loadAnalyticsData()
    loadTrafficSources()
  }, [timeRange])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      setError(null)

      const daysMap = { "7d": 7, "30d": 30, "90d": 90 }
      const days = daysMap[timeRange]

      const response = await analyticsApi.getAnalytics({ days })

      setStats(response.data.stats)
      setChartData(response.data.chartData)
      setTopProducts(response.data.topProducts)
    } catch (err: any) {
      console.error("Failed to load analytics:", err)
      setError(err.response?.data?.detail || "Failed to load analytics data")
    } finally {
      setLoading(false)
    }
  }

  const loadTrafficSources = async () => {
    try {
      const daysMap = { "7d": 7, "30d": 30, "90d": 90 }
      const days = daysMap[timeRange]

      const response = await analyticsApi.getTrafficSources({ days })
      setTrafficSources(response.data)
    } catch (err: any) {
      console.error("Failed to load traffic sources:", err)
      // Use empty array as fallback
      setTrafficSources([])
    }
  }

  const maxValue = chartData.length > 0
    ? Math.max(...chartData.map((d) => (chartType === "revenue" ? d.revenue : d.sales)))
    : 1

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

      {/* Error State */}
      {error && (
        <Card className="border-red-900 bg-red-950/20">
          <CardContent className="flex items-center gap-3 p-4">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-white font-medium">Failed to load analytics</p>
              <p className="text-gray-400 text-sm">{error}</p>
            </div>
            <Button size="sm" onClick={loadAnalyticsData}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      )}

      {!loading && !error && (
        <>
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
                {chartData.length > 0 ? (
                  <div className="h-64 flex items-end gap-2">
                    {chartData.map((data, index) => {
                      const value = chartType === "revenue" ? data.revenue : data.sales
                      const height = maxValue > 0 ? (value / maxValue) * 100 : 0
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
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    No data available for this time range
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Traffic Sources */}
            <Card>
              <CardHeader>
                <CardTitle>Traffic Sources</CardTitle>
              </CardHeader>
              <CardContent>
                {trafficSources.length > 0 ? (
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
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    No traffic data available
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Top Products */}
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Products</CardTitle>
            </CardHeader>
            <CardContent>
              {topProducts.length > 0 ? (
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
              ) : (
                <div className="text-center text-gray-500 py-8">
                  No product data available
                </div>
              )}
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
        </>
      )}
    </div>
  )
}
