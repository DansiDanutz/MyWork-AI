"use client"

import Link from "next/link"
import { Star, Eye, ShoppingCart } from "lucide-react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar } from "@/components/ui/avatar"
import { formatPrice } from "@/lib/utils"
import type { Product } from "@/types"

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Card className="group overflow-hidden hover:border-gray-600 transition-all">
      {/* Thumbnail */}
      <Link href={`/products/${product.slug}`}>
        <div className="relative aspect-video overflow-hidden bg-gray-900">
          {product.thumbnailUrl ? (
            <img
              src={product.thumbnailUrl}
              alt={product.name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
              <span className="text-4xl">📦</span>
            </div>
          )}

          {/* Featured badge */}
          {product.isFeatured && (
            <Badge className="absolute top-2 left-2" variant="success">
              Featured
            </Badge>
          )}

          {/* Category badge */}
          <Badge className="absolute top-2 right-2" variant="secondary">
            {product.category}
          </Badge>
        </div>
      </Link>

      <CardContent className="p-4">
        {/* Title */}
        <Link href={`/products/${product.slug}`}>
          <h3 className="font-semibold text-white hover:text-blue-400 transition-colors line-clamp-1">
            {product.name}
          </h3>
        </Link>

        {/* Description */}
        <p className="text-sm text-gray-400 mt-1 line-clamp-2">
          {product.shortDescription || product.description || "No description"}
        </p>

        {/* Stats */}
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
            <span>{product.averageRating.toFixed(1)}</span>
            <span className="text-gray-600">({product.reviewCount})</span>
          </div>
          <div className="flex items-center gap-1">
            <ShoppingCart className="h-4 w-4" />
            <span>{product.salesCount}</span>
          </div>
          <div className="flex items-center gap-1">
            <Eye className="h-4 w-4" />
            <span>{product.viewCount}</span>
          </div>
        </div>

        {/* Tech stack */}
        {product.techStack && product.techStack.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {product.techStack.slice(0, 3).map((tech) => (
              <Badge key={tech} variant="outline" className="text-xs">
                {tech}
              </Badge>
            ))}
            {product.techStack.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{product.techStack.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>

      <CardFooter className="p-4 pt-0 flex items-center justify-between">
        {/* Seller */}
        <div className="flex items-center gap-2">
          <Avatar
            size="sm"
            fallback={product.sellerUsername || "S"}
          />
          <span className="text-sm text-gray-400">
            {product.sellerUsername || "Seller"}
          </span>
        </div>

        {/* Price */}
        <div className="text-right">
          <span className="text-lg font-bold text-green-400">
            {formatPrice(product.price)}
          </span>
        </div>
      </CardFooter>
    </Card>
  )
}
