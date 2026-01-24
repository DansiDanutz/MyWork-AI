"use client"

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
    sellerId: "seller1",
    sellerUsername: "dansi",
    name: "SaaS Starter Kit",
    slug: "saas-starter-kit",
    shortDescription: "Full-stack SaaS boilerplate with auth, payments, and dashboard",
    description: "Complete SaaS starter kit with Next.js, Stripe, and PostgreSQL",
    category: "saas",
    tags: ["nextjs", "stripe", "tailwind"],
    price: 299,
    thumbnailUrl: null,
    previewImages: [],
    techStack: ["Next.js", "TypeScript", "PostgreSQL", "Stripe"],
    status: "published",
    isFeatured: true,
    averageRating: 4.8,
    reviewCount: 42,
    salesCount: 156,
    viewCount: 2340,
    createdAt: "2024-01-15",
    publishedAt: "2024-01-15",
  },
  {
    id: "2",
    sellerId: "seller2",
    sellerUsername: "devpro",
    name: "AI Chat Interface",
    slug: "ai-chat-interface",
    shortDescription: "Beautiful chat UI with streaming, markdown, and code highlighting",
    description: "Production-ready chat interface for AI applications",
    category: "ui",
    tags: ["react", "ai", "chat"],
    price: 149,
    thumbnailUrl: null,
    previewImages: [],
    techStack: ["React", "TypeScript", "Tailwind CSS"],
    status: "published",
    isFeatured: false,
    averageRating: 4.9,
    reviewCount: 28,
    salesCount: 89,
    viewCount: 1520,
    createdAt: "2024-02-01",
    publishedAt: "2024-02-01",
  },
  {
    id: "3",
    sellerId: "seller3",
    sellerUsername: "automation_guru",
    name: "n8n Workflow Bundle",
    slug: "n8n-workflow-bundle",
    shortDescription: "50+ production n8n workflows for common automation tasks",
    description: "Save hours with these ready-to-use n8n workflows",
    category: "automation",
    tags: ["n8n", "automation", "workflows"],
    price: 79,
    thumbnailUrl: null,
    previewImages: [],
    techStack: ["n8n", "JavaScript"],
    status: "published",
    isFeatured: true,
    averageRating: 4.7,
    reviewCount: 65,
    salesCount: 234,
    viewCount: 3890,
    createdAt: "2024-01-20",
    publishedAt: "2024-01-20",
  },
  {
    id: "4",
    sellerId: "seller4",
    sellerUsername: "apicrafters",
    name: "REST API Boilerplate",
    slug: "rest-api-boilerplate",
    shortDescription: "Production-ready FastAPI template with auth, docs, and tests",
    description: "Complete FastAPI boilerplate for building APIs",
    category: "api",
    tags: ["fastapi", "python", "api"],
    price: 199,
    thumbnailUrl: null,
    previewImages: [],
    techStack: ["FastAPI", "Python", "PostgreSQL", "Redis"],
    status: "published",
    isFeatured: false,
    averageRating: 4.6,
    reviewCount: 19,
    salesCount: 67,
    viewCount: 980,
    createdAt: "2024-02-10",
    publishedAt: "2024-02-10",
  },
]
