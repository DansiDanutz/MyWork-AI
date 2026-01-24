// User types
export interface User {
  id: string
  email: string
  username: string
  displayName?: string
  avatarUrl?: string
  role: 'user' | 'seller' | 'admin'
  subscriptionTier: 'free' | 'pro' | 'team' | 'enterprise'
  isSeller: boolean
}

export interface SellerProfile {
  id: string
  userId: string
  bio?: string
  website?: string
  githubUsername?: string
  twitterHandle?: string
  totalSales: number
  totalRevenue: number
  averageRating: number
  verificationLevel: 'unverified' | 'verified' | 'trusted'
  payoutsEnabled: boolean
}

// Product types
export interface Product {
  id: string
  sellerId: string
  sellerUsername?: string
  name: string
  slug: string
  shortDescription?: string
  description?: string
  category: string
  subcategory?: string
  tags: string[]
  price: number
  extendedLicensePrice?: number
  unlimitedLicensePrice?: number
  thumbnailUrl?: string
  previewImages: string[]
  previewUrl?: string
  demoUrl?: string
  techStack: string[]
  requirements?: string
  status: 'draft' | 'pending' | 'published' | 'rejected'
  isFeatured: boolean
  averageRating: number
  reviewCount: number
  salesCount: number
  viewCount: number
  createdAt: string
  publishedAt?: string
}

export interface ProductListResponse {
  products: Product[]
  total: number
  page: number
  pageSize: number
}

// Order types
export interface Order {
  id: string
  buyerId: string
  sellerId: string
  productId: string
  productName: string
  amount: number
  platformFee: number
  sellerAmount: number
  licenseType: 'standard' | 'extended' | 'unlimited'
  status: 'pending' | 'completed' | 'refunded' | 'refund_requested' | 'failed'
  paymentIntentId?: string
  downloadCount: number
  maxDownloads: number
  escrowReleaseDate?: string
  createdAt: string
}

// Review types
export interface Review {
  id: string
  productId: string
  buyerId: string
  buyerUsername: string
  buyerAvatar?: string
  rating: number
  title: string
  content: string
  isVerifiedPurchase: boolean
  helpfulCount: number
  sellerResponse?: string
  sellerResponseAt?: string
  createdAt: string
  updatedAt?: string
}

export interface ReviewListResponse {
  reviews: Review[]
  total: number
  averageRating: number
  ratingDistribution: Record<number, number>
  page: number
  pageSize: number
}

// Brain types
export interface BrainEntry {
  id: string
  contributorId: string
  contributorUsername?: string
  title: string
  content: string
  entryType: 'pattern' | 'snippet' | 'tutorial' | 'solution' | 'documentation'
  category: string
  tags: string[]
  language?: string
  framework?: string
  qualityScore: number
  usageCount: number
  upvotes: number
  downvotes: number
  isVerified: boolean
  isPublic: boolean
}

export interface BrainSearchResponse {
  entries: BrainEntry[]
  total: number
  page: number
  pageSize: number
}

export interface BrainQueryResponse {
  query: string
  results: BrainEntry[]
  aiSummary?: string
}

// Subscription types
export interface Subscription {
  id: string
  userId: string
  tier: 'free' | 'pro' | 'team' | 'enterprise'
  status: 'active' | 'cancelled' | 'past_due'
  currentPeriodEnd?: string
  brainQueriesUsed: number
  brainQueriesLimit: number
  productsListed: number
  productsLimit: number
}

// Category types
export const CATEGORIES = [
  { value: 'saas', label: 'SaaS Templates' },
  { value: 'api', label: 'API Services' },
  { value: 'ui', label: 'UI Components' },
  { value: 'fullstack', label: 'Full-Stack Apps' },
  { value: 'mobile', label: 'Mobile Apps' },
  { value: 'ai', label: 'AI/ML Projects' },
  { value: 'automation', label: 'Automation' },
  { value: 'devtools', label: 'Developer Tools' },
  { value: 'other', label: 'Other' },
] as const

export type Category = typeof CATEGORIES[number]['value']
