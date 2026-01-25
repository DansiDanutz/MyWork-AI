// User types
export interface User {
  id: string
  email: string
  username: string
  display_name?: string
  avatar_url?: string
  role: 'buyer' | 'seller' | 'admin'
  subscription_tier: 'free' | 'pro' | 'team' | 'enterprise'
  is_seller: boolean
}

export interface SellerProfile {
  id: string
  user_id: string
  bio?: string
  website?: string
  github_username?: string
  twitter_handle?: string
  total_sales: number
  total_revenue: number
  average_rating: number
  verification_level: 'basic' | 'verified' | 'premium'
  payouts_enabled: boolean
}

// Product types
export interface Product {
  id: string
  seller_id: string
  slug: string
  title: string
  short_description?: string
  description: string
  category: string
  subcategory?: string
  tags: string[]
  price: number
  license_type: 'standard' | 'extended' | 'enterprise'
  tech_stack: string[]
  framework?: string
  requirements?: string
  demo_url?: string
  documentation_url?: string
  preview_images: string[]
  package_url?: string
  package_size_bytes?: number
  status: 'draft' | 'pending' | 'active' | 'suspended' | 'archived'
  featured: boolean
  rating_average: number
  rating_count: number
  sales: number
  views: number
  version: string
  created_at: string
  updated_at: string
}

export interface ProductListResponse {
  products: Product[]
  total: number
  page: number
  page_size: number
}

// Order types
export interface Order {
  id: string
  buyer_id: string
  seller_id: string
  product_id: string
  product_name: string
  amount: number
  platform_fee: number
  seller_amount: number
  license_type: 'standard' | 'extended' | 'enterprise'
  status: 'pending' | 'completed' | 'refunded' | 'refund_requested' | 'failed'
  payment_intent_id?: string
  download_count: number
  max_downloads: number
  escrow_release_date?: string
  created_at: string
}

// Review types
export interface Review {
  id: string
  product_id: string
  buyer_id: string
  buyer_username: string
  buyer_avatar?: string
  rating: number
  title: string
  content: string
  is_verified_purchase: boolean
  helpful_count: number
  seller_response?: string
  seller_response_at?: string
  created_at: string
  updated_at?: string
}

export interface ReviewListResponse {
  reviews: Review[]
  total: number
  average_rating: number
  rating_distribution: Record<number, number>
  page: number
  page_size: number
}

// Brain types
export interface BrainEntry {
  id: string
  contributor_id: string
  contributor_username?: string
  title: string
  content: string
  type: 'pattern' | 'solution' | 'lesson' | 'tip' | 'antipattern'
  category: string
  tags: string[]
  language?: string
  framework?: string
  quality_score: number
  usage_count: number
  helpful_votes: number
  unhelpful_votes: number
  verified: boolean
}

export interface BrainSearchResponse {
  entries: BrainEntry[]
  total: number
  page: number
  page_size: number
}

export interface BrainQueryResponse {
  query: string
  results: BrainEntry[]
  ai_summary?: string
}

// Subscription types
export interface Subscription {
  id: string
  user_id: string
  tier: 'free' | 'pro' | 'team' | 'enterprise'
  status: 'active' | 'cancelled' | 'past_due'
  current_period_end?: string
  brain_queries_used: number
  brain_queries_limit: number
  products_listed: number
  products_limit: number
}

// Category types
export const CATEGORIES = [
  { value: 'saas-starters', label: 'SaaS Starters' },
  { value: 'api-services', label: 'API Services' },
  { value: 'automation', label: 'Automation' },
  { value: 'mobile-apps', label: 'Mobile Apps' },
  { value: 'full-applications', label: 'Full Applications' },
  { value: 'components', label: 'Components' },
  { value: 'templates', label: 'Templates' },
  { value: 'tools', label: 'Tools' },
] as const

export type Category = typeof CATEGORIES[number]['value']
