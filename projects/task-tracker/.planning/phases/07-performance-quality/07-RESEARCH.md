# Phase 7: Performance & Quality - Research

**Researched:** 2026-01-26
**Domain:** Next.js 15 performance optimization, Core Web Vitals, responsive
design
**Confidence:** HIGH

## Summary

Phase 7 focuses on optimizing the existing Next.js 15 task tracker to meet
production performance standards: 2-second load times, responsive UI across
devices, smooth page transitions, and zero layout shifts. The research covers
Next.js built-in optimization features, Core Web Vitals measurement (LCP, INP,
CLS), code splitting strategies, mobile-first responsive design, and progressive
loading patterns.

**Key findings:**

- Next.js 15 provides automatic optimizations (Server Components, route-based
  code splitting, prefetching) that are already active
- Core Web Vitals now measure LCP (<2.5s), INP (<200ms), and CLS (<0.1) — note
  FID was replaced by INP in March 2024
- The standard stack uses `next/dynamic` for lazy loading, `react-swipeable` for
  mobile gestures, and built-in `loading.js` for skeleton screens
- Bundle analysis with `@next/bundle-analyzer` identifies optimization
  opportunities; the project should target <100KB initial JavaScript for fast
  loads

**Primary recommendation:** Use Next.js built-in features first (Server
Components, loading.js, Image component), then add progressive enhancements
(react-swipeable for mobile, bundle splitting for heavy features like file
management). Monitor with Lighthouse CI and real user monitoring.

## Standard Stack

The established libraries/tools for Next.js performance optimization:

### Core

| Library | Version | Purpose | Why Standard |
| --------- | --------- | --------- | -------------- |
  | `next` | 15.5.9 | Framework w... | Automatic c... |  
  | `@next/bund... | Latest | Webpack bun... | Official Ne... |  
| `react-swip... | 7.0.2 | Mobile touc... | Minimal (us... |
  | `sharp` | 0.34.5 (alr... | Image optim... | Required by... |  

### Supporting

| Library | Version | Purpose | When to Use |
| --------- | --------- | --------- | ------------- |
  | `lighthouse` | Latest | Performance... | CI/CD integ... |  
| `web-vitals` | Latest | Core Web Vi... | Real user m... |
| `@use-gestu... | Latest | Advanced ge... | If react-sw... |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
| ------------ | ----------- | ---------- |
| `react-swipeable` | Custom `onTouchSta... | Custom = 50 lines ... |
| `@next/bundle-anal... | `webpack-bundle-an... | Same tool undernea... |
| Built-in Image com... | `react-lazy-load-i... | Image component is... |

**Installation:**

```bash
npm install react-swipeable @next/bundle-analyzer
npm install --save-dev lighthouse web-vitals

```markdown

## Architecture Patterns

### Recommended Project Structure

```
src/app/
├── (routes)/
│   ├── loading.tsx         # Route-level skeleton screens
│   ├── error.tsx           # Error boundaries per route
│   └── not-found.tsx       # 404 handling
├── components/
│   ├── ui/
│   │   ├── skeletons/      # Reusable skeleton components
│   │   └── error-states/   # Error feedback components
│   └── features/
│       └── [feature]/
│           ├── index.tsx   # Main export (Server Component)
│           └── client.tsx  # Dynamic client parts (use next/dynamic)
└── lib/

```
└── analytics/
    └── web-vitals.ts   # Core Web Vitals reporting

```
```markdown

### Pattern 1: Progressive Loading with loading.js

**What:** Next.js convention file that shows instant loading state while route
content streams
**When to use:** Every major route that fetches data
**Example:**

```tsx

// Source: https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming
// app/tasks/loading.tsx
export default function Loading() {
  return (

```
<div className="space-y-4">
  <div className="h-8 w-64 bg-gray-200 rounded animate-pulse" />
  <div className="h-32 bg-gray-200 rounded animate-pulse" />
  <div className="h-32 bg-gray-200 rounded animate-pulse" />
</div>

```
  )
}

```

**Key points:**

- Automatically wraps `page.tsx` in Suspense boundary
- Shows immediately on navigation (instant feedback)
- Works with streaming Server Components

### Pattern 2: Lazy Load Heavy Client Components

**What:** Use `next/dynamic` to defer loading non-critical Client Components
**When to use:** File upload UI, charts, modals, rich text editors
**Example:**

```tsx

// Source: https://nextjs.org/docs/app/guides/lazy-loading
import dynamic from 'next/dynamic'

// Lazy load file upload with loading fallback
const FileDropzone = dynamic(
  () => import('./FileDropzone'),
  {

```
loading: () => <div className="animate-pulse bg-gray-100 h-64 rounded" />,
ssr: false // Client-only (uses browser APIs)

```
  }
)

export default function TaskEditPage() {
  return (

```
<div>
  <h1>Edit Task</h1>
  {/* FileDropzone loads only when component mounts */}
  <FileDropzone />
</div>

```
  )
}

```yaml

**Critical rules:**

- Use `next/dynamic`, NOT `React.lazy()` (SSR compatibility)
- Set `ssr: false` for browser-dependent code (file APIs, localStorage)
- Always provide `loading` fallback to prevent blank screens

### Pattern 3: Mobile Swipe Gestures

**What:** Touch-friendly interactions using react-swipeable hook
**When to use:** Mobile task management (swipe to complete, swipe to delete)
**Example:**

```tsx

// Source: https://www.npmjs.com/package/react-swipeable
'use client'
import { useSwipeable } from 'react-swipeable'

export function TaskCard({ task, onComplete, onDelete }) {
  const handlers = useSwipeable({

```
onSwipedLeft: () => onDelete(task.id),
onSwipedRight: () => onComplete(task.id),
delta: 50, // Minimum swipe distance (px)
preventScrollOnSwipe: true,
trackMouse: false // Disable on desktop

```
  })

  return (

```
<div {...handlers} className="touch-pan-y">
  {/* Task content */}
</div>

```
  )
}

```

**Configuration options:**

- `delta`: Minimum swipe distance (default 10px, recommend 50px for intentional
  swipes)
- `preventScrollOnSwipe`: Prevents page scroll during swipe
- `trackMouse`: Enable mouse swipes (useful for testing, disable in production)

### Pattern 4: Responsive Image Optimization

**What:** Next.js Image component with automatic WebP/AVIF and responsive srcset
**When to use:** All images (file thumbnails, user avatars, any visual content)
**Example:**

```tsx

// Source: https://nextjs.org/docs/app/api-reference/components/image
import Image from 'next/image'

export function TaskThumbnail({ file }) {
  return (

```
<Image
  src={file.url}
  alt={file.name}
  width={200}
  height={150}
  sizes="(max-width: 768px) 100vw, 200px"
  placeholder="blur"
  blurDataURL={file.blurHash}
  className="object-cover rounded"
/>

```
  )
}

```yaml

**For LCP images (hero, first visible content):**

```tsx

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  preload={true} // New in Next.js 16 (replaces priority)
  sizes="100vw"
/>

```

### Pattern 5: Bundle Analysis and Code Splitting

**What:** Identify large dependencies and split them into separate chunks
**When to use:** When initial bundle exceeds 100KB or specific features are
rarely used
**Example:**

```js

// Source: https://nextjs.org/docs/app/guides/package-bundling
// next.config.js
module.exports = {
  experimental: {

```
// Optimize heavy icon/utility libraries
optimizePackageImports: ['@heroicons/react', 'date-fns']

```
  },
  serverExternalPackages: ['sharp'] // Don't bundle server-only packages
}

```yaml

**Running bundle analyzer:**

```bash

# Install

npm install @next/bundle-analyzer

# Analyze

ANALYZE=true npm run build

```

### Pattern 6: Core Web Vitals Monitoring

**What:** Report real user performance metrics to analytics
**When to use:** Production monitoring (optional in development)
**Example:**

```tsx

// Source: https://nextjs.org/docs/app/api-reference/functions/use-report-web-vitals
// app/layout.tsx
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {

```
// Send to analytics endpoint
fetch('/api/analytics/vitals', {
  method: 'POST',
  body: JSON.stringify(metric)
})

```
  })

  return null
}

```yaml

**Metric types:**

- `LCP`: Largest Contentful Paint (target: <2.5s)
- `INP`: Interaction to Next Paint (target: <200ms)
- `CLS`: Cumulative Layout Shift (target: <0.1)
- `FCP`: First Contentful Paint
- `TTFB`: Time to First Byte

### Anti-Patterns to Avoid

- **Don't lazy load entire pages** — Only lazy load specific heavy components,
  not whole page modules
- **Don't use `React.lazy()` in Next.js** — Use `next/dynamic` for SSR
  compatibility
- **Don't set `priority` on multiple images** — Only mark true LCP element (or
  use `preload` in v16)
- **Don't skip width/height on images** — Causes layout shift (CLS penalty)
- **Don't lazy load above-the-fold content** — Hurts LCP; only lazy load below
  the fold
- **Don't use custom loading without testing** — Over-lazy loading increases
  latency

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
| --------- | ------------- | ------------- | ----- |
| Mobile swip... | Custom touc... | `react-swip... | Handles edg... |
  | Image optim... | Manual WebP... | Next.js `<I... | Automatic f... |  
| Bundle anal... | Manual webp... | `@next/bund... | Pre-configu... |
| Lazy loading | Custom inte... | `next/dynamic` | SSR-compati... |
| Skeleton sc... | Loading spi... | Next.js `lo... | Route-level... |
| Core Web Vi... | Custom perf... | `web-vitals... | Google's of... |

**Key insight:** Next.js has already solved most performance problems through
built-in features. The framework's defaults (Server Components, automatic code
splitting, Image component) handle 80% of optimization work. Custom solutions
introduce bugs and maintenance burden.

## Common Pitfalls

### Pitfall 1: Using React.lazy() Instead of next/dynamic

**What goes wrong:** Components only render on client-side, breaking SSR and
harming SEO
**Why it happens:** React.lazy() is standard React pattern, but doesn't support
SSR
**How to avoid:** Always use `next/dynamic` in Next.js projects
**Warning signs:** "Hydration mismatch" errors, blank server-rendered pages,
missing content in page source

### Pitfall 2: Not Setting Image Dimensions

**What goes wrong:** Layout shifts as images load, CLS score increases, poor
user experience
**Why it happens:** Developers forget width/height props or use fill without
aspect ratio
**How to avoid:** Always set `width` and `height` props, or use `fill` with
aspect-ratio CSS
**Warning signs:** Content jumping during page load, CLS > 0.1 in Lighthouse

### Pitfall 3: Over-Lazy Loading Critical Content

**What goes wrong:** Above-the-fold content loads late, LCP score increases
dramatically
**Why it happens:** Blanket lazy loading strategy without considering viewport
**How to avoid:** Only lazy load below-the-fold content; mark LCP elements with
`preload`
**Warning signs:** LCP > 2.5s despite small page size, visible "popping in" of
hero content

### Pitfall 4: Lazy Loading Entire Pages

**What goes wrong:** Increases bundle size instead of reducing it, delays
rendering
**Why it happens:** Misunderstanding of code splitting granularity
**How to avoid:** Lazy load specific heavy components (file upload, charts), not
entire routes
**Warning signs:** Delayed page rendering after navigation, larger bundles than
expected

### Pitfall 5: Missing Loading Fallbacks

**What goes wrong:** Blank screens during component load, poor UX, potential
crashes if load fails
**Why it happens:** Using `next/dynamic` without `loading` option
**How to avoid:** Always provide `loading` component matching the final UI
structure
**Warning signs:** White flashes during navigation, "Loading..." text appearing
unexpectedly

### Pitfall 6: Ignoring Mobile Touch Targets

**What goes wrong:** Buttons too small on mobile (accessibility issue), hard to
tap accurately
**Why it happens:** Desktop-first design without mobile testing
**How to avoid:** Minimum 44x44px touch targets (WCAG 2.1), test on real devices
**Warning signs:** Users struggling to tap buttons, accessibility audits failing

### Pitfall 7: Not Testing on Real Mobile Devices

**What goes wrong:** Responsive CSS works in DevTools but fails on real phones
**Why it happens:** Browser DevTools don't simulate touch perfectly, different
rendering engines
**How to avoid:** Test on at least one iOS and one Android device (or
BrowserStack)
**Warning signs:** Swipe gestures not working, layout breaking on certain
devices

### Pitfall 8: Blocking Main Thread with Heavy JavaScript

**What goes wrong:** INP > 200ms, interactions feel sluggish, poor
responsiveness
**Why it happens:** Large bundles, synchronous operations, not using code
splitting
**How to avoid:** Use Server Components for heavy logic, split client bundles,
defer non-critical JS
**Warning signs:** Lighthouse INP warnings, slow button clicks, janky scrolling

## Code Examples

Verified patterns from official sources:

### Complete Loading.js Pattern

```tsx

// Source: https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming
// app/tasks/loading.tsx
export default function TasksLoading() {
  return (

```
<div className="container mx-auto p-4">
  {/* Header skeleton */}
  <div className="flex justify-between items-center mb-6">
    <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
    <div className="h-10 w-32 bg-gray-200 rounded animate-pulse" />
  </div>

  {/* Task list skeletons */}
  <div className="space-y-4">
    {[1, 2, 3, 4, 5].map((i) => (
      <div key={i} className="border rounded-lg p-4">
        <div className="h-6 w-3/4 bg-gray-200 rounded animate-pulse mb-2" />
        <div className="h-4 w-1/2 bg-gray-200 rounded animate-pulse" />
      </div>
    ))}
  </div>
</div>

```
  )
}

```

### Error Boundary Pattern

```tsx

// Source: https://nextjs.org/docs/app/getting-started/error-handling
// app/tasks/error.tsx
'use client'

import { useEffect } from 'react'

export default function TasksError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {

```
// Log to error monitoring service
console.error('Tasks error:', error)

```
  }, [error])

  return (

```
<div className="container mx-auto p-4">
  <div className="bg-red-50 border border-red-200 rounded-lg p-6">
    <h2 className="text-xl font-semibold text-red-900 mb-2">
      Failed to load tasks
    </h2>
    <p className="text-red-700 mb-4">
      {error.message || 'An unexpected error occurred'}
    </p>
    <button
      onClick={reset}
      className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
    >
      Try again
    </button>
  </div>
</div>

```
  )
}

```markdown

### Dynamic Import with Loading State

```tsx

// Source: https://nextjs.org/docs/app/guides/lazy-loading
import dynamic from 'next/dynamic'

// Lazy load file dropzone component
const FileDropzone = dynamic(
  () => import('@/components/features/files/FileDropzone'),
  {

```
loading: () => (
  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
    <div className="animate-pulse text-center">
      <div className="h-12 w-12 bg-gray-200 rounded-full mx-auto mb-4" />
      <div className="h-4 w-32 bg-gray-200 rounded mx-auto" />
    </div>
  </div>
),
ssr: false // File APIs are browser-only

```
  }
)

// Usage in page/component
export default function TaskEditPage() {
  return (

```
<div>
  <FileDropzone onUpload={handleUpload} />
</div>

```
  )
}

```

### Mobile-First Responsive Design

```tsx

// Source: https://tailwindcss.com/docs/responsive-design
// Mobile-first task card with collapsing actions
export function TaskCard({ task }) {
  return (

```
<div className="border rounded-lg p-4
                sm:p-6
                md:flex md:items-center md:justify-between">
  {/* Content: Full width on mobile, flex on desktop */}
  <div className="mb-4 md:mb-0 md:flex-1">
    <h3 className="text-lg font-semibold
                   sm:text-xl
                   lg:text-2xl">
      {task.title}
    </h3>
    <p className="text-sm text-gray-600
                  sm:text-base">
      {task.description}
    </p>
  </div>

  {/* Actions: Stacked on mobile, inline on desktop */}
  <div className="flex flex-col gap-2
                  sm:flex-row
                  md:flex-shrink-0 md:ml-4">
    <button className="px-4 py-2 bg-blue-600 text-white rounded
                       min-w-[44px] min-h-[44px]">
      Edit
    </button>
    <button className="px-4 py-2 bg-red-600 text-white rounded
                       min-w-[44px] min-h-[44px]">
      Delete
    </button>
  </div>
</div>

```
  )
}

```markdown

### Swipe Gesture Integration

```tsx

// Source: https://www.npmjs.com/package/react-swipeable
'use client'
import { useSwipeable } from 'react-swipeable'
import { useState } from 'react'

export function SwipeableTaskCard({ task, onComplete, onDelete }) {
  const [swipeOffset, setSwipeOffset] = useState(0)

  const handlers = useSwipeable({

```
onSwiping: (eventData) => {
  // Visual feedback during swipe
  setSwipeOffset(eventData.deltaX)
},
onSwipedRight: () => {
  if (Math.abs(swipeOffset) > 100) {
    onComplete(task.id)
  }
  setSwipeOffset(0)
},
onSwipedLeft: () => {
  if (Math.abs(swipeOffset) > 100) {
    onDelete(task.id)
  }
  setSwipeOffset(0)
},
delta: 50, // Minimum distance for swipe
preventScrollOnSwipe: true,
trackMouse: false // Desktop uses buttons

```
  })

  return (

```
<div {...handlers}
     style={{ transform: `translateX(${swipeOffset}px)` }}
     className="touch-pan-y transition-transform">
  {/* Task content */}
</div>

```
  )
}

```

### Image Optimization Pattern

```tsx

// Source: https://nextjs.org/docs/app/api-reference/components/image
import Image from 'next/image'

export function FileThumbnail({ file }) {
  // For uploaded files
  if (file.type.startsWith('image/')) {

```
return (
  <Image
    src={`/api/files/thumbnail/${file.id}`}
    alt={file.name}
    width={200}
    height={150}
    sizes="(max-width: 768px) 100vw, 200px"
    className="object-cover rounded"
    loading="lazy" // Below-the-fold images
  />
)

```
  }

  // Fallback for non-images
  return <FileIcon type={file.type} />
}

// For hero/LCP images
export function HeroImage() {
  return (

```
<Image
  src="/hero.jpg"
  alt="Hero banner"
  width={1200}
  height={600}
  preload={true} // Prioritize loading
  sizes="100vw"
  className="w-full h-auto"
/>

```
  )
}

```markdown

### Core Web Vitals Reporting

```tsx

// Source: https://nextjs.org/docs/app/api-reference/functions/use-report-web-vitals
// app/components/WebVitalsReporter.tsx
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {

```
const body = JSON.stringify(metric)
const url = '/api/analytics/vitals'

// Use `navigator.sendBeacon()` if available, fall back to `fetch()`
if (navigator.sendBeacon) {
  navigator.sendBeacon(url, body)
} else {
  fetch(url, { body, method: 'POST', keepalive: true })
}

```
  })

  return null
}

// app/layout.tsx
import { WebVitalsReporter } from './components/WebVitalsReporter'

export default function RootLayout({ children }) {
  return (

```
<html>
  <body>
    <WebVitalsReporter />
    {children}
  </body>
</html>

```
  )
}

```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
| -------------- | ------------------ | -------------- | -------- |
  | FID (First ... | INP (Intera... | March 2024 | INP is stri... |  
  | `priority` ... | `preload` prop | Next.js 16 ... | Same functi... |  
| Client-side... | Server Comp... | Next.js 13 ... | Massive bun... |
  | Manual lazy... | next/dynami... | Always (Nex... | SSR compati... |  
  | Custom load... | loading.js ... | Next.js 13 ... | Automatic S... |  
  | Manual rout... | Automatic o... | Next.js 10+ | Instant nav... |  
| JPEG/PNG im... | Automatic W... | Next.js 10+ | 20-50% smal... |

**Deprecated/outdated:**

- `priority` prop on Image component: Use `preload` instead (Next.js 16+)
- `onLoadingComplete` callback: Use `onLoad` instead (Next.js 14+)
- FID (First Input Delay): Now INP (Interaction to Next Paint) in Core Web Vitals
- `React.lazy()` in Next.js: Use `next/dynamic` for SSR compatibility
- Manual image optimization: Built-in Image component handles it automatically

## Open Questions

Things that couldn't be fully resolved:

1. **Performance Budget Thresholds**
   - What we know: Lighthouse CI can enforce budgets, typical targets are <100KB

```
 JS for initial load

```
   - What's unclear: Specific bundle size limits for this project (depends on

```
 features)

```
   - Recommendation: Run bundle analyzer first, then set realistic budgets based

```
 on current state

```
2. **Real User Monitoring vs Synthetic Testing**
   - What we know: RUM (Real User Monitoring) tracks actual users, synthetic

```
 tests (Lighthouse) are lab-based

```
   - What's unclear: Best balance for this project phase (RUM requires user

```
 traffic)

```
   - Recommendation: Start with Lighthouse CI (synthetic), add RUM in Phase 8

```
 (Deployment) when users exist

```
3. **Mobile Browser Testing Coverage**
   - What we know: Should test iOS Safari and Android Chrome at minimum
   - What's unclear: Which specific device/OS versions to target
   - Recommendation: Test latest iOS + Android, use BrowserStack for older

```
 versions if needed

```
4. **Progressive Web App (PWA) Features**
   - What we know: PWA adds offline support, install prompts, service workers
   - What's unclear: Whether PWA is in scope for this phase (not mentioned in

```
 requirements)

```
   - Recommendation: Defer PWA to future phase; focus on core performance first

## Sources

### Primary (HIGH confidence)

- [Next.js Production
  Checklist](https://nextjs.org/docs/app/guides/production-checklist) -
  Performance optimization, Core Web Vitals, bundle analysis
- [Next.js Loading UI and
  Streaming](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming)
  - loading.js patterns, Suspense boundaries, streaming
- [Next.js Error
  Handling](https://nextjs.org/docs/app/getting-started/error-handling) - Error
  boundaries, recovery mechanisms, user feedback
- [Next.js Lazy Loading](https://nextjs.org/docs/app/guides/lazy-loading) -
  next/dynamic usage, SSR options, pitfalls
- [Next.js Image
  Component](https://nextjs.org/docs/app/api-reference/components/image) -
  Automatic optimization, lazy loading, responsive images
- [Next.js Package Bundling](https://nextjs.org/docs/app/guides/package-bundling)
  - optimizePackageImports, serverExternalPackages, bundle reduction
- [Google Core Web
  Vitals](https://developers.google.com/search/docs/appearance/core-web-vitals) -
  LCP, INP, CLS metrics and thresholds
- [Tailwind Responsive Design](https://tailwindcss.com/docs/responsive-design) -
  Mobile-first breakpoint system
- [react-swipeable npm](https://www.npmjs.com/package/react-swipeable) - API
  documentation, configuration options

### Secondary (MEDIUM confidence)

- [Mastering Lazy Loading in Next.js
  15](https://medium.com/@sureshdotariya/mastering-lazy-loading-in-next-js-15-advanced-patterns-for-peak-performance-75e0bd574c76)
  - Advanced patterns, performance impact (WebSearch verified with official docs)
- [Core Web Vitals 2026 Guide](https://senorit.de/en/blog/core-web-vitals-2026) -
  INP replacement of FID, current thresholds (WebSearch verified with Google
  docs)
- [Next.js Performance Optimization
  Guide](https://www.aniq-ui.com/en/blog/performance-optimization-nextjs) - Code
  splitting strategies (WebSearch verified with official docs)
- [Best Practices for Loading States in
  Next.js](https://www.getfishtank.com/insights/best-practices-for-loading-states-in-nextjs)
  - Skeleton patterns (WebSearch verified with official docs)

### Tertiary (LOW confidence)

- [47% of websites fail Core Web
  Vitals](https://nitropack.io/blog/most-important-core-web-vitals-metrics/) -
  Industry statistics (WebSearch only, not critical for implementation)
- [React Swipeable Tutorial](https://codingcops.com/react-swipeable/) - Community
  usage examples (WebSearch only, official docs preferred)

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All libraries verified via official documentation and
  npm registry
- Architecture: HIGH - Patterns from official Next.js documentation and
  established conventions
- Pitfalls: HIGH - Based on official docs warnings and verified community
  patterns
- Mobile gestures: MEDIUM - react-swipeable is well-documented but implementation
  details need testing
- Performance budgets: LOW - Project-specific thresholds require bundle analysis
  to determine

**Research date:** 2026-01-26
**Valid until:** 60 days (Next.js stable, stack mature, Core Web Vitals unlikely
to change)

**Note on INP vs FID:** Google officially replaced FID with INP in March 2024.
All references to Core Web Vitals should use INP (target <200ms), not FID.
