"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Search, Filter, ChevronDown } from "lucide-react"
import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { productsApi } from "@/lib/api"
import { CATEGORIES, type Product } from "@/types"

const SORT_OPTIONS = [
  { value: "newest", label: "Newest" },
  { value: "popular", label: "Most Popular" },
  { value: "price_low", label: "Price: Low to High" },
  { value: "price_high", label: "Price: High to Low" },
]

export default function ProductsPage() {
  const searchParams = useSearchParams()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  // Filters
  const [search, setSearch] = useState(searchParams.get("search") || "")
  const [category, setCategory] = useState(searchParams.get("category") || "")
  const [sort, setSort] = useState(searchParams.get("sort") || "newest")
  const [showFilters, setShowFilters] = useState(false)

  // Fetch products
  useEffect(() => {
    async function fetchProducts() {
      setLoading(true)
      try {
        const response = await productsApi.list({
          search: search || undefined,
          category: category || undefined,
          sort,
          page,
          pageSize: 20,
        })
        setProducts(response.data.products)
        setTotal(response.data.total)
      } catch (error) {
        console.error("Failed to fetch products:", error)
        // Use mock data for demo
        setProducts(MOCK_PRODUCTS)
        setTotal(MOCK_PRODUCTS.length)
      } finally {
        setLoading(false)
      }
    }

    fetchProducts()
  }, [search, category, sort, page])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
  }

  const clearFilters = () => {
    setSearch("")
    setCategory("")
    setSort("newest")
    setPage(1)
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-b from-gray-800 to-gray-900 border-b border-gray-800">
        <div className="container mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            Marketplace
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl">
            Discover production-ready projects built by developers.
            Every purchase directly supports creators - they keep 90%.
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar - Filters */}
          <aside className={`lg:w-64 shrink-0 ${showFilters ? 'block' : 'hidden lg:block'}`}>
            <div className="sticky top-24 space-y-6">
              {/* Search */}
              <div>
                <label className="text-sm font-medium text-gray-300 mb-2 block">
                  Search
                </label>
                <form onSubmit={handleSearch}>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      type="search"
                      placeholder="Search products..."
                      className="pl-10"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </div>
                </form>
              </div>

              {/* Categories */}
              <div>
                <label className="text-sm font-medium text-gray-300 mb-2 block">
                  Category
                </label>
                <div className="flex flex-wrap gap-2">
                  <Badge
                    variant={category === "" ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => setCategory("")}
                  >
                    All
                  </Badge>
                  {CATEGORIES.map((cat) => (
                    <Badge
                      key={cat.value}
                      variant={category === cat.value ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => setCategory(cat.value)}
                    >
                      {cat.label}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Sort */}
              <div>
                <label className="text-sm font-medium text-gray-300 mb-2 block">
                  Sort by
                </label>
                <select
                  value={sort}
                  onChange={(e) => setSort(e.target.value)}
                  className="w-full h-10 rounded-lg border border-gray-600 bg-gray-800 px-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {SORT_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Clear filters */}
              {(search || category || sort !== "newest") && (
                <Button variant="outline" onClick={clearFilters} className="w-full">
                  Clear Filters
                </Button>
              )}
            </div>
          </aside>

          {/* Main content */}
          <div className="flex-1">
            {/* Mobile filter toggle */}
            <div className="lg:hidden mb-4">
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="w-full justify-between"
              >
                <span className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  Filters
                </span>
                <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </Button>
            </div>

            {/* Results header */}
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-400">
                {loading ? "Loading..." : `${total} products found`}
              </p>
            </div>

            {/* Products grid */}
            {loading ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div
                    key={i}
                    className="rounded-xl border border-gray-700 bg-gray-800 animate-pulse"
                  >
                    <div className="aspect-video bg-gray-700" />
                    <div className="p-4 space-y-3">
                      <div className="h-5 bg-gray-700 rounded w-3/4" />
                      <div className="h-4 bg-gray-700 rounded w-full" />
                      <div className="h-4 bg-gray-700 rounded w-1/2" />
                    </div>
                  </div>
                ))}
              </div>
            ) : products.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  No products found
                </h3>
                <p className="text-gray-400 mb-6">
                  Try adjusting your filters or search query
                </p>
                <Button onClick={clearFilters}>Clear Filters</Button>
              </div>
            )}

            {/* Pagination */}
            {total > 20 && (
              <div className="flex justify-center gap-2 mt-8">
                <Button
                  variant="outline"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  disabled={page * 20 >= total}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

// Mock data for demo
const MOCK_PRODUCTS: Product[] = [
  {
    id: "1",
    seller_id: "seller1",
    title: "SaaS Starter Kit",
    slug: "saas-starter-kit",
    short_description: "Full-stack SaaS boilerplate with auth, payments, and dashboard",
    description: "Complete SaaS starter kit with Next.js, Stripe, and PostgreSQL",
    category: "saas-starters",
    tags: ["nextjs", "stripe", "tailwind"],
    price: 299,
    license_type: "standard",
    preview_images: [],
    tech_stack: ["Next.js", "TypeScript", "PostgreSQL", "Stripe"],
    status: "active",
    featured: true,
    rating_average: 4.8,
    rating_count: 42,
    sales: 156,
    views: 2340,
    version: "1.0.0",
    created_at: "2024-01-15",
    updated_at: "2024-01-15",
  },
  {
    id: "2",
    seller_id: "seller2",
    title: "AI Chat Interface",
    slug: "ai-chat-interface",
    short_description: "Beautiful chat UI with streaming, markdown, and code highlighting",
    description: "Production-ready chat interface for AI applications",
    category: "components",
    tags: ["react", "ai", "chat"],
    price: 149,
    license_type: "standard",
    preview_images: [],
    tech_stack: ["React", "TypeScript", "Tailwind CSS"],
    status: "active",
    featured: false,
    rating_average: 4.9,
    rating_count: 28,
    sales: 89,
    views: 1520,
    version: "1.0.0",
    created_at: "2024-02-01",
    updated_at: "2024-02-01",
  },
  {
    id: "3",
    seller_id: "seller3",
    title: "n8n Workflow Bundle",
    slug: "n8n-workflow-bundle",
    short_description: "50+ production n8n workflows for common automation tasks",
    description: "Save hours with these ready-to-use n8n workflows",
    category: "automation",
    tags: ["n8n", "automation", "workflows"],
    price: 79,
    license_type: "standard",
    preview_images: [],
    tech_stack: ["n8n", "JavaScript"],
    status: "active",
    featured: true,
    rating_average: 4.7,
    rating_count: 65,
    sales: 234,
    views: 3890,
    version: "1.0.0",
    created_at: "2024-01-20",
    updated_at: "2024-01-20",
  },
  {
    id: "4",
    seller_id: "seller4",
    title: "REST API Boilerplate",
    slug: "rest-api-boilerplate",
    short_description: "Production-ready FastAPI template with auth, docs, and tests",
    description: "Complete FastAPI boilerplate for building APIs",
    category: "api-services",
    tags: ["fastapi", "python", "api"],
    price: 199,
    license_type: "standard",
    preview_images: [],
    tech_stack: ["FastAPI", "Python", "PostgreSQL", "Redis"],
    status: "active",
    featured: false,
    rating_average: 4.6,
    rating_count: 19,
    sales: 67,
    views: 980,
    version: "1.0.0",
    created_at: "2024-02-10",
    updated_at: "2024-02-10",
  },
]
