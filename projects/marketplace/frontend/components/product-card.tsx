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
          {product.preview_images && product.preview_images[0] ? (
            <img
              src={product.preview_images[0]}
              alt={product.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
              <span className="text-4xl">📦</span>
            </div>
          )}

          {/* Featured badge */}
          {product.featured && (
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
            {product.title}
          </h3>
        </Link>

        {/* Description */}
        <p className="text-sm text-gray-400 mt-1 line-clamp-2">
          {product.short_description || product.description || "No description"}
        </p>

        {/* Stats */}
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
            <span>{product.rating_average.toFixed(1)}</span>
            <span className="text-gray-600">({product.rating_count})</span>
          </div>
          <div className="flex items-center gap-1">
            <ShoppingCart className="h-4 w-4" />
            <span>{product.sales}</span>
          </div>
          <div className="flex items-center gap-1">
            <Eye className="h-4 w-4" />
            <span>{product.views}</span>
          </div>
        </div>

        {/* Tech stack */}
        {product.tech_stack && product.tech_stack.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {product.tech_stack.slice(0, 3).map((tech) => (
              <Badge key={tech} variant="outline" className="text-xs">
                {tech}
              </Badge>
            ))}
            {product.tech_stack.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{product.tech_stack.length - 3}
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
            fallback="S"
          />
          <span className="text-sm text-gray-400">
            Seller
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
