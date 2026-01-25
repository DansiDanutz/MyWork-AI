"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { useUser } from "@clerk/nextjs"
import {
  Star,
  ShoppingCart,
  Eye,
  Download,
  ExternalLink,
  Github,
  Check,
  ChevronRight,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar } from "@/components/ui/avatar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPrice, formatDate } from "@/lib/utils"
import { productsApi, reviewsApi } from "@/lib/api"
import type { Product, Review, ReviewListResponse } from "@/types"

export default function ProductPage() {
  const params = useParams()
  const { isSignedIn } = useUser()
  const slug = params.slug as string

  const [product, setProduct] = useState<Product | null>(null)
  const [reviews, setReviews] = useState<ReviewListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedLicense, setSelectedLicense] = useState<"standard" | "extended" | "unlimited">("standard")

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      try {
        const productRes = await productsApi.getBySlug(slug)
        setProduct(productRes.data)
      } catch (error) {
        console.error("Failed to fetch product:", error)
        // Use mock data
        setProduct(MOCK_PRODUCT)
        setReviews(MOCK_REVIEWS)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [slug])

  if (loading) {
    return (
      <main className="min-h-screen">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-700 rounded w-1/4" />
            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-4">
                <div className="aspect-video bg-gray-700 rounded-xl" />
                <div className="h-4 bg-gray-700 rounded w-3/4" />
                <div className="h-4 bg-gray-700 rounded w-1/2" />
              </div>
              <div className="h-96 bg-gray-700 rounded-xl" />
            </div>
          </div>
        </div>
      </main>
    )
  }

  if (!product) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😕</div>
          <h1 className="text-2xl font-bold text-white mb-2">Product Not Found</h1>
          <p className="text-gray-400 mb-6">The product you're looking for doesn't exist.</p>
          <Link href="/products">
            <Button>Browse Marketplace</Button>
          </Link>
        </div>
      </main>
    )
  }

  const getPrice = () => {
    switch (selectedLicense) {
      case "extended":
        return product.price * 2.5
      case "unlimited":
        return product.price * 5
      default:
        return product.price
    }
  }

  return (
    <main className="min-h-screen">
      {/* Breadcrumb */}
      <div className="border-b border-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Link href="/products" className="hover:text-white">
              Marketplace
            </Link>
            <ChevronRight className="h-4 w-4" />
            <Link href={`/products?category=${product.category}`} className="hover:text-white capitalize">
              {product.category}
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-white">{product.title}</span>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Header */}
            <div>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2">{product.title}</h1>
                  <p className="text-gray-400">{product.short_description}</p>
                </div>
                {product.featured && (
                  <Badge variant="success">Featured</Badge>
                )}
              </div>

              {/* Stats */}
              <div className="flex flex-wrap items-center gap-6 text-sm text-gray-400">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                  <span className="font-medium text-white">{product.rating_average.toFixed(1)}</span>
                  <span>({product.rating_count} reviews)</span>
                </div>
                <div className="flex items-center gap-1">
                  <ShoppingCart className="h-4 w-4" />
                  <span>{product.sales} sales</span>
                </div>
                <div className="flex items-center gap-1">
                  <Eye className="h-4 w-4" />
                  <span>{product.views} views</span>
                </div>
              </div>
            </div>

            {/* Preview Image */}
            <div className="aspect-video rounded-xl overflow-hidden bg-gray-800 border border-gray-700">
              {product.preview_images && product.preview_images[0] ? (
                <img
                  src={product.preview_images[0]}
                  alt={product.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
                  <span className="text-8xl">📦</span>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex gap-4">
              {product.demo_url && (
                <a href={product.demo_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" className="gap-2">
                    <ExternalLink className="h-4 w-4" />
                    Live Demo
                  </Button>
                </a>
              )}
              {product.documentation_url && (
                <a href={product.documentation_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" className="gap-2">
                    <Github className="h-4 w-4" />
                    Documentation
                  </Button>
                </a>
              )}
            </div>

            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-invert max-w-none">
                  <p className="text-gray-300 whitespace-pre-wrap">
                    {product.description || "No description provided."}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Tech Stack */}
            {product.tech_stack && product.tech_stack.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Tech Stack</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {product.tech_stack.map((tech) => (
                      <Badge key={tech} variant="secondary" className="text-sm">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Requirements */}
            {product.requirements && (
              <Card>
                <CardHeader>
                  <CardTitle>Requirements</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-300 whitespace-pre-wrap">
                    {product.requirements}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Reviews */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Reviews</CardTitle>
                {reviews && (
                  <div className="flex items-center gap-2">
                    <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                    <span className="text-xl font-bold text-white">
                      {reviews.average_rating.toFixed(1)}
                    </span>
                    <span className="text-gray-400">
                      ({reviews.total} reviews)
                    </span>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {reviews && reviews.reviews.length > 0 ? (
                  <div className="space-y-6">
                    {reviews.reviews.map((review) => (
                      <div key={review.id} className="border-b border-gray-700 pb-6 last:border-0">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <Avatar
                              src={review.buyer_avatar}
                              fallback={review.buyer_username}
                              size="sm"
                            />
                            <div>
                              <p className="font-medium text-white">{review.buyer_username}</p>
                              <p className="text-sm text-gray-500">{formatDate(review.created_at)}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`h-4 w-4 ${
                                  i < review.rating
                                    ? "text-yellow-500 fill-yellow-500"
                                    : "text-gray-600"
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        <h4 className="font-medium text-white mb-1">{review.title}</h4>
                        <p className="text-gray-400">{review.content}</p>
                        {review.is_verified_purchase && (
                          <Badge variant="success" className="mt-2">
                            <Check className="h-3 w-3 mr-1" />
                            Verified Purchase
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-center py-8">
                    No reviews yet. Be the first to review!
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Purchase */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <Card>
                <CardContent className="p-6 space-y-6">
                  {/* Seller */}
                  <div className="flex items-center gap-3">
                    <Avatar
                      fallback="S"
                      size="lg"
                    />
                    <div>
                      <p className="font-medium text-white">Seller</p>
                    </div>
                  </div>

                  {/* License selection */}
                  <div className="space-y-3">
                    <p className="text-sm font-medium text-gray-300">Select License</p>

                    <button
                      onClick={() => setSelectedLicense("standard")}
                      className={`w-full p-4 rounded-lg border text-left transition ${
                        selectedLicense === "standard"
                          ? "border-blue-500 bg-blue-500/10"
                          : "border-gray-700 hover:border-gray-600"
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-white">Standard</span>
                        <span className="font-bold text-green-400">{formatPrice(product.price)}</span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">Single project use</p>
                    </button>

                    <button
                      onClick={() => setSelectedLicense("extended")}
                      className={`w-full p-4 rounded-lg border text-left transition ${
                        selectedLicense === "extended"
                          ? "border-blue-500 bg-blue-500/10"
                          : "border-gray-700 hover:border-gray-600"
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-white">Extended</span>
                        <span className="font-bold text-green-400">
                          {formatPrice(product.price * 2.5)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">Multiple projects + redistribution</p>
                    </button>

                    <button
                      onClick={() => setSelectedLicense("unlimited")}
                      className={`w-full p-4 rounded-lg border text-left transition ${
                        selectedLicense === "unlimited"
                          ? "border-blue-500 bg-blue-500/10"
                          : "border-gray-700 hover:border-gray-600"
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-white">Unlimited</span>
                        <span className="font-bold text-green-400">
                          {formatPrice(product.price * 5)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-400 mt-1">Unlimited use + SaaS allowed</p>
                    </button>
                  </div>

                  {/* Purchase button */}
                  <Button className="w-full" size="lg" variant="success" asChild>
                    <Link href={`/checkout/${product.id}`}>
                      <Download className="h-5 w-5 mr-2" />
                      Buy Now - {formatPrice(getPrice())}
                    </Link>
                  </Button>

                  {/* Info */}
                  <div className="space-y-2 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Instant download</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>Lifetime access to updates</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>6 months support included</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>7-day money back guarantee</span>
                    </div>
                  </div>

                  {/* Platform fee note */}
                  <p className="text-xs text-gray-500 text-center">
                    Seller receives {formatPrice(getPrice() * 0.9)} (90%)
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

// Mock data
const MOCK_PRODUCT: Product = {
  id: "1",
  seller_id: "seller1",
  title: "SaaS Starter Kit",
  slug: "saas-starter-kit",
  short_description: "Full-stack SaaS boilerplate with auth, payments, and dashboard",
  description: `A complete SaaS starter kit built with Next.js 14, TypeScript, and Tailwind CSS.

Features included:
- Authentication with Clerk
- Payments with Stripe (subscriptions + one-time)
- Dashboard with analytics
- User management
- Team/organization support
- Email notifications
- Dark/light mode
- Mobile responsive
- SEO optimized
- 50+ components

Perfect for launching your SaaS product in days, not months.`,
  category: "saas-starters",
  tags: ["nextjs", "stripe", "tailwind"],
  price: 299,
  license_type: "standard",
  preview_images: [],
  demo_url: "https://demo.example.com",
  tech_stack: ["Next.js 14", "TypeScript", "PostgreSQL", "Stripe", "Clerk", "Tailwind CSS"],
  requirements: "Node.js 18+\nPostgreSQL database\nStripe account\nClerk account",
  status: "active",
  featured: true,
  rating_average: 4.8,
  rating_count: 42,
  sales: 156,
  views: 2340,
  version: "1.0.0",
  created_at: "2024-01-15",
  updated_at: "2024-01-15",
}

const MOCK_REVIEWS: ReviewListResponse = {
  reviews: [
    {
      id: "r1",
      product_id: "1",
      buyer_id: "b1",
      buyer_username: "developer123",
      rating: 5,
      title: "Saved me weeks of work",
      content: "This starter kit is incredibly well organized. The code quality is top-notch and everything just works out of the box. Highly recommended!",
      is_verified_purchase: true,
      helpful_count: 12,
      created_at: "2024-02-01",
    },
    {
      id: "r2",
      product_id: "1",
      buyer_id: "b2",
      buyer_username: "saasbuilder",
      rating: 4,
      title: "Great foundation",
      content: "Very solid foundation for a SaaS. Would love to see more documentation, but overall excellent value for the price.",
      is_verified_purchase: true,
      helpful_count: 8,
      created_at: "2024-01-28",
    },
  ],
  total: 42,
  average_rating: 4.8,
  rating_distribution: { 5: 32, 4: 8, 3: 2, 2: 0, 1: 0 },
  page: 1,
  page_size: 20,
}
