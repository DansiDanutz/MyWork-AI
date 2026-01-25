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
  }) => api.get('/products', { params }),

  get: (id: string) => api.get(`/products/${id}`),

  getById: (id: string) => api.get(`/products/${id}`),

  getBySlug: (slug: string) => api.get(`/products/slug/${slug}`),

  getMyProducts: (params?: {
    status?: string
    page?: number
    pageSize?: number
  }) => api.get('/products/me', { params }),

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
    api.put('/users/me', data),

  getSellerProfile: () => api.get('/users/me/seller'),

  becomeSeller: (data?: {
    bio?: string
    website?: string
    githubUsername?: string
    twitterHandle?: string
  }) => api.post('/users/become-seller', data),

  getPublicProfile: (username: string) => api.get(`/users/${username}`),

  getPublicSellerProfile: (username: string) =>
    api.get(`/users/${username}/seller`),
}

// Orders API
export const ordersApi = {
  create: (data: { productId: string; licenseType?: string }) =>
    api.post('/orders', data),

  list: (params?: { role?: 'buyer' | 'seller'; status?: string }) =>
    api.get('/orders', { params }),

  get: (id: string) => api.get(`/orders/${id}`),

  download: (id: string) => api.post(`/orders/${id}/download`),

  requestRefund: (id: string, reason: string) =>
    api.post(`/orders/${id}/refund`, { reason }),
}

// Reviews API
export const reviewsApi = {
  getProductReviews: (productId: string, params?: any) =>
    api.get(`/reviews/product/${productId}`, { params }),

  create: (data: {
    productId: string
    rating: number
    title: string
    content: string
  }) => api.post('/reviews', data),

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
  }) => api.get('/brain', { params }),

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

// Checkout API
export const checkoutApi = {
  createSession: (data: { productId: string; licenseType: 'standard' | 'extended' }) =>
    api.post('/checkout/create-session', data),

  getSession: (sessionId: string) =>
    api.get(`/checkout/session/${sessionId}`),

  verifyAndCreateOrder: (sessionId: string) =>
    api.post('/checkout/verify-and-create-order', null, { params: { session_id: sessionId } }),

  getProductPrices: (productId: string) =>
    api.get(`/checkout/prices/${productId}`),
}

export default api
