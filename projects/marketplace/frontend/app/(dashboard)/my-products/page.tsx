"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useAuth } from "@clerk/nextjs"
import { useUser } from "@clerk/nextjs"
import {
  Package,
  Plus,
  MoreVertical,
  Eye,
  ShoppingBag,
  Star,
  Edit,
  Trash2,
  ExternalLink,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { productsApi, setAuthToken } from "@/lib/api"
import { formatPrice, formatDate } from "@/lib/utils"

interface Product {
  id: string
  title: string
  slug: string
  short_description: string | null
  price: number
  category: string
  status: string
  views: number
  sales: number
  rating_average: number
  rating_count: number
  version: string
  created_at: string
  updated_at: string
}

interface ProductsResponse {
  products: Product[]
  total: number
  page: number
  page_size: number
}

const STATUS_COLORS: Record<string, { text: string; variant: "success" | "warning" | "destructive" | "secondary" | "default" }> = {
  draft: { text: "Draft", variant: "secondary" },
  active: { text: "Active", variant: "success" },
  archived: { text: "Archived", variant: "destructive" },
  pending: { text: "Pending Review", variant: "warning" },
}

export default function ProductsPage() {
  const { getToken } = useAuth()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>("all")

  useEffect(() => {
    loadProducts()
  }, [statusFilter])

  async function loadProducts() {
    try {
      setLoading(true)
      setError(null)

      const token = await getToken()
      if (!token) {
        setError("Authentication required")
        return
      }

      // Set auth token for this request
      setAuthToken(token)

      const params: any = {}
      if (statusFilter !== "all") {
        params.status = statusFilter
      }

      const response = await productsApi.getMyProducts(params)
      setProducts(response.data.products)
    } catch (err: any) {
      console.error("Failed to load products:", err)
      setError(err.response?.data?.detail || "Failed to load products")
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(productId: string) {
    if (!confirm("Are you sure you want to delete this product?")) {
      return
    }

    try {
      const token = await getToken()
      if (!token) return

      setAuthToken(token)
      await productsApi.delete(productId)
      setProducts(products.filter(p => p.id !== productId))
    } catch (err: any) {
      console.error("Failed to delete product:", err)
      alert(err.response?.data?.detail || "Failed to delete product")
    }
  }

  if (loading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading products...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">My Products</h1>
          <p className="text-gray-400">
            Manage your product listings
          </p>
        </div>
        <Link href="/dashboard/my-products/new">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Product
          </Button>
        </Link>
      </div>

      {/* Error State */}
      {error && (
        <Card className="border-red-900 bg-red-950/20">
          <CardContent className="p-6">
            <p className="text-red-400">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-400">Filter:</span>
        <Button
          variant={statusFilter === "all" ? "default" : "ghost"}
          size="sm"
          onClick={() => setStatusFilter("all")}
        >
          All ({products.length})
        </Button>
        <Button
          variant={statusFilter === "active" ? "default" : "ghost"}
          size="sm"
          onClick={() => setStatusFilter("active")}
        >
          Active
        </Button>
        <Button
          variant={statusFilter === "draft" ? "default" : "ghost"}
          size="sm"
          onClick={() => setStatusFilter("draft")}
        >
          Draft
        </Button>
        <Button
          variant={statusFilter === "pending" ? "default" : "ghost"}
          size="sm"
          onClick={() => setStatusFilter("pending")}
        >
          Pending
        </Button>
      </div>

      {/* Products List */}
      {products.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-12">
            <Package className="h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">
              No products yet
            </h3>
            <p className="text-gray-400 text-center mb-6">
              {statusFilter === "all"
                ? "Create your first product to start selling on the marketplace."
                : `No ${statusFilter} products found.`}
            </p>
            {statusFilter === "all" && (
              <Link href="/dashboard/my-products/new">
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  Create Product
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {products.map((product) => (
            <Card key={product.id} className="hover:bg-gray-800/30 transition">
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-white truncate">
                            {product.title}
                          </h3>
                          <Badge variant={STATUS_COLORS[product.status]?.variant || "secondary"}>
                            {STATUS_COLORS[product.status]?.text || product.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-400 line-clamp-2 mb-2">
                          {product.short_description || "No description"}
                        </p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span className="text-white font-medium">
                            {formatPrice(product.price)}
                          </span>
                          <span>{product.category}</span>
                          <span>v{product.version}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-6 text-sm">
                    <div className="flex items-center gap-1 text-gray-400">
                      <Eye className="h-4 w-4" />
                      <span>{product.views}</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-400">
                      <ShoppingBag className="h-4 w-4" />
                      <span>{product.sales}</span>
                    </div>
                    {product.rating_count > 0 && (
                      <div className="flex items-center gap-1 text-gray-400">
                        <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                        <span>{product.rating_average.toFixed(1)}</span>
                        <span className="text-gray-500">({product.rating_count})</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Link href={`/products/${product.slug}`} target="_blank">
                      <Button variant="ghost" size="icon" title="View on marketplace">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Link href={`/dashboard/my-products/${product.id}/edit`}>
                      <Button variant="ghost" size="icon" title="Edit">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Delete"
                      onClick={() => handleDelete(product.id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-950/20"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Footer */}
                <div className="mt-4 pt-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
                  <span>Created {formatDate(product.created_at)}</span>
                  <span>Updated {formatDate(product.updated_at)}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
