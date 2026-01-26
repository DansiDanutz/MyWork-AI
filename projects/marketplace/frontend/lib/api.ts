import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// Products API
export const productsApi = {
  list: (params?: {
    category?: string
    search?: string
    minPrice?: number
    maxPrice?: number
    sort?: string
    page?: number
    pageSize?: number
  }) =>
    api.get('/products', {
      params: {
        category: params?.category,
        search: params?.search,
        min_price: params?.minPrice,
        max_price: params?.maxPrice,
        sort: params?.sort,
        page: params?.page,
        page_size: params?.pageSize,
      },
    }),

  get: (id: string) => api.get(`/products/${id}`),

  getById: (id: string) => api.get(`/products/${id}`),

  getBySlug: (slug: string) => api.get(`/products/${slug}`),

  getMyProducts: (params?: {
    status?: string
    page?: number
    pageSize?: number
  }) =>
    api.get('/products/me', {
      params: {
        status: params?.status,
        page: params?.page,
        page_size: params?.pageSize,
      },
    }),

  create: (data: {
    title: string
    short_description?: string
    description: string
    category: string
    subcategory?: string
    tags?: string[]
    price: number
    license_type?: string
    tech_stack?: string[]
    framework?: string
    requirements?: string
    demo_url?: string
    documentation_url?: string
    preview_images?: string[]
    package_url?: string
    package_size_bytes?: number | null
  }) => api.post('/products', data),

  update: (id: string, data: any) => api.put(`/products/${id}`, data),

  delete: (id: string) => api.delete(`/products/${id}`),
}

// Users API
export const usersApi = {
  getMe: () => api.get('/users/me'),

  updateMe: (data: { displayName?: string; avatarUrl?: string }) =>
    api.put('/users/me', {
      ...(data.displayName !== undefined && { display_name: data.displayName }),
      ...(data.avatarUrl !== undefined && { avatar_url: data.avatarUrl }),
    }),

  getSellerProfile: () => api.get('/users/me/seller'),

  becomeSeller: (data?: {
    bio?: string
    website?: string
    githubUsername?: string
    twitterHandle?: string
  }) =>
    api.post('/users/become-seller', {
      ...(data?.bio !== undefined && { bio: data.bio }),
      ...(data?.website !== undefined && { website: data.website }),
      ...(data?.githubUsername !== undefined && { github_username: data.githubUsername }),
      ...(data?.twitterHandle !== undefined && { twitter_handle: data.twitterHandle }),
    }),

  getPublicProfile: (username: string) => api.get(`/users/${username}`),

  getPublicSellerProfile: (username: string) =>
    api.get(`/users/${username}/seller`),
}

// Orders API
export const ordersApi = {
  create: (data: { productId: string; licenseType?: string; useCredits?: boolean }) =>
    api.post('/orders', {
      product_id: data.productId,
      ...(data.licenseType && { license_type: data.licenseType }),
      ...(data.useCredits !== undefined && { use_credits: data.useCredits }),
    }),

  list: (params?: { role?: 'buyer' | 'seller'; status?: string }) =>
    api.get('/orders', { params }),

  get: (id: string) => api.get(`/orders/${id}`),

  download: (id: string) => api.post(`/orders/${id}/download`),

  requestRefund: (id: string, reason: string) =>
    api.post(`/orders/${id}/refund`, { reason }),
}

// Credits API
export const creditsApi = {
  getBalance: () => api.get('/credits/balance'),

  listLedger: (limit = 50) =>
    api.get('/credits/ledger', { params: { limit } }),

  createTopupSession: (amount: number) =>
    api.post('/credits/topup/session', { amount }),
}

// Reviews API
export const reviewsApi = {
  getProductReviews: (
    productId: string,
    params?: {
      rating?: number
      verifiedOnly?: boolean
      sort?: string
      page?: number
      pageSize?: number
    }
  ) =>
    api.get(`/reviews/product/${productId}`, {
      params: {
        rating: params?.rating,
        verified_only: params?.verifiedOnly,
        sort: params?.sort,
        page: params?.page,
        page_size: params?.pageSize,
      },
    }),

  create: (data: {
    productId: string
    rating: number
    title: string
    content: string
  }) =>
    api.post('/reviews', {
      product_id: data.productId,
      rating: data.rating,
      title: data.title,
      content: data.content,
    }),

  update: (id: string, data: any) => api.put(`/reviews/${id}`, data),

  delete: (id: string) => api.delete(`/reviews/${id}`),

  markHelpful: (id: string) => api.post(`/reviews/${id}/helpful`),

  respond: (id: string, response: string) =>
    api.post(`/reviews/${id}/respond`, { response }),
}

// Brain API
export const brainApi = {
  search: (params?: {
    q?: string
    category?: string
    type?: string
    language?: string
    framework?: string
    tag?: string
    verifiedOnly?: boolean
    sort?: string
    page?: number
    pageSize?: number
  }) =>
    api.get('/brain', {
      params: {
        q: params?.q,
        category: params?.category,
        entry_type: params?.type,
        language: params?.language,
        framework: params?.framework,
        tag: params?.tag,
        verified_only: params?.verifiedOnly,
        sort: params?.sort,
        page: params?.page,
        page_size: params?.pageSize,
      },
    }),

  query: (data: {
    query: string
    category?: string
    language?: string
    framework?: string
    limit?: number
  }) => api.post('/brain/query', data),

  contribute: (data: {
    title: string
    content: string
    type: string
    category: string
    tags?: string[]
    language?: string
    framework?: string
  }) => api.post('/brain', data),

  get: (id: string) => api.get(`/brain/${id}`),

  vote: (id: string, vote: 1 | -1) => api.post(`/brain/${id}/vote`, { vote }),

  stats: () => api.get('/brain/stats/overview'),
}

// Payouts API
export const payoutsApi = {
  getBalance: () => api.get('/payouts/me/balance'),

  getPayouts: (params?: {
    status?: string
    limit?: number
    offset?: number
  }) => api.get('/payouts/me', { params }),

  requestPayout: () => api.post('/payouts/me/request'),

  getSellerProfile: () => api.get('/payouts/me/seller-profile'),
}

// Analytics API
export const analyticsApi = {
  getAnalytics: (params?: { days?: number }) =>
    api.get('/analytics', { params }),

  getTrafficSources: (params?: { days?: number }) =>
    api.get('/analytics/traffic-sources', { params }),
}

// Uploads API
export const uploadsApi = {
  createPresignedUrl: (data: {
    kind: 'preview_image' | 'package'
    filename: string
    content_type: string
    size_bytes: number
  }) => api.post('/uploads/presign', data),
}

// Submissions API
export const submissionsApi = {
  create: (data: {
    title: string
    short_description?: string
    description: string
    category: string
    subcategory?: string
    tags?: string[]
    price: number
    license_type?: string
    tech_stack?: string[]
    framework?: string
    requirements?: string
    demo_url?: string
    documentation_url?: string
    preview_images?: string[]
    package_url?: string
    package_size_bytes?: number | null
  }) => api.post('/submissions', data),

  listMine: (params?: { status?: string; page?: number; pageSize?: number }) =>
    api.get('/submissions/me', {
      params: {
        status: params?.status,
        page: params?.page,
        page_size: params?.pageSize,
      },
    }),

  get: (id: string) => api.get(`/submissions/${id}`),

  retry: (id: string) => api.post(`/submissions/${id}/retry`),

  publish: (id: string) => api.post(`/submissions/${id}/publish`),
}

// Checkout API
export const checkoutApi = {
  createSession: (data: { productId: string; licenseType: 'standard' | 'extended' }) =>
    api.post('/checkout/create-session', {
      product_id: data.productId,
      license_type: data.licenseType,
    }),

  getSession: (sessionId: string) =>
    api.get(`/checkout/session/${sessionId}`),

  verifyAndCreateOrder: (sessionId: string) =>
    api.post('/checkout/verify-and-create-order', null, { params: { session_id: sessionId } }),

  getProductPrices: (productId: string) =>
    api.get(`/checkout/prices/${productId}`),
}

export default api
