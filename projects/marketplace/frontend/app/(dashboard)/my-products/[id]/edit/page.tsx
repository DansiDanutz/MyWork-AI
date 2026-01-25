"use client"

import { useMemo, useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { useAuth } from "@clerk/nextjs"
import { ChevronLeft, ChevronRight, Upload, X, Plus, AlertCircle, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { productsApi, setAuthToken } from "@/lib/api"
import { uploadFileWithPresign } from "@/lib/uploads"

const PRODUCT_CATEGORIES = [
  { value: "saas-starters", label: "SaaS Starters" },
  { value: "api-services", label: "API Services" },
  { value: "automation", label: "Automation" },
  { value: "mobile-apps", label: "Mobile Apps" },
  { value: "full-applications", label: "Full Applications" },
  { value: "components", label: "Components" },
  { value: "templates", label: "Templates" },
  { value: "tools", label: "Tools" },
]

const LICENSE_TYPES = [
  { value: "standard", label: "Standard License", description: "Single project use" },
  { value: "extended", label: "Extended License", description: "Multiple projects, can modify" },
  { value: "enterprise", label: "Enterprise License", description: "Unlimited use, white-label allowed" },
]

const COMMON_TECH_STACK = [
  "React", "Next.js", "Vue", "Nuxt", "Svelte", "Angular",
  "Node.js", "Python", "Go", "Rust", "Java",
  "PostgreSQL", "MySQL", "MongoDB", "Redis",
  "Tailwind CSS", "shadcn/ui", "Material-UI", "Chakra UI",
  "TypeScript", "JavaScript", "Prisma", "Sequelize",
  "Docker", "Kubernetes", "AWS", "Vercel", "Stripe"
]

const MAX_IMAGE_BYTES = 5 * 1024 * 1024
const MAX_PACKAGE_BYTES = 500 * 1024 * 1024

const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
const ALLOWED_PACKAGE_TYPES = [
  "application/zip",
  "application/x-zip-compressed",
  "application/x-tar",
  "application/gzip",
  "application/x-gzip",
  "application/octet-stream",
]

interface FormData {
  // Step 1: Basic Info
  title: string
  short_description: string
  description: string
  category: string
  subcategory: string
  tags: string[]

  // Step 2: Pricing & License
  price: string
  license_type: string

  // Step 3: Technical Details
  tech_stack: string[]
  framework: string
  requirements: string
  demo_url: string
  documentation_url: string

  // Step 4: Files & Media
  preview_images: string[]
  package_url: string
  package_size_bytes: number | null
}

interface Product {
  id: string
  title: string
  slug: string
  short_description: string | null
  description: string | null
  price: number
  category: string
  subcategory: string | null
  tags: string[]
  license_type: string
  tech_stack: string[]
  framework: string | null
  requirements: string | null
  demo_url: string | null
  documentation_url: string | null
  preview_images: string[]
  package_url: string | null
  package_size_bytes?: number | null
  version: string
  status: string
}

const STEP_TITLES = [
  "Basic Information",
  "Pricing & License",
  "Technical Details",
  "Files & Media",
]

type UploadStatus = "idle" | "uploading" | "done" | "error"

interface ImageUpload {
  id: string
  name: string
  size: number
  progress: number
  status: UploadStatus
  url?: string
  error?: string
}

interface PackageUpload {
  name: string
  size: number
  progress: number
  status: UploadStatus
  fileKey?: string
  error?: string
}

export default function EditProductPage() {
  const router = useRouter()
  const params = useParams()
  const { getToken } = useAuth()
  const productId = params.id as string

  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [fetchLoading, setFetchLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const [formData, setFormData] = useState<FormData>({
    // Step 1
    title: "",
    short_description: "",
    description: "",
    category: "",
    subcategory: "",
    tags: [],

    // Step 2
    price: "",
    license_type: "standard",

    // Step 3
    tech_stack: [],
    framework: "",
    requirements: "",
    demo_url: "",
    documentation_url: "",

    // Step 4
    preview_images: [],
    package_url: "",
    package_size_bytes: null,
  })

  const [tagInput, setTagInput] = useState("")
  const [techStackInput, setTechStackInput] = useState("")
  const [imageUploads, setImageUploads] = useState<ImageUpload[]>([])
  const [packageUpload, setPackageUpload] = useState<PackageUpload | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  // Fetch product data on mount
  useEffect(() => {
    loadProduct()
  }, [productId])

  async function loadProduct() {
    try {
      setFetchLoading(true)
      setFetchError(null)

      const token = await getToken()
      if (!token) {
        setFetchError("Authentication required")
        return
      }

      setAuthToken(token)
      const response = await productsApi.getById(productId)
      const product = response.data as Product

      // Populate form with product data
      setFormData({
        title: product.title || "",
        short_description: product.short_description || "",
        description: product.description || "",
        category: product.category || "",
        subcategory: product.subcategory || "",
        tags: product.tags || [],
        price: product.price ? product.price.toString() : "",
        license_type: product.license_type || "standard",
        tech_stack: product.tech_stack || [],
        framework: product.framework || "",
        requirements: product.requirements || "",
        demo_url: product.demo_url || "",
        documentation_url: product.documentation_url || "",
        preview_images: product.preview_images || [],
        package_url: product.package_url || "",
        package_size_bytes: product.package_size_bytes || null,
      })
    } catch (err: any) {
      console.error("Failed to load product:", err)
      setFetchError(err.response?.data?.detail || "Failed to load product")
    } finally {
      setFetchLoading(false)
    }
  }

  async function handleSubmit(publish: boolean = false) {
    try {
      setLoading(true)
      setError(null)
      setSaveSuccess(false)

      if (hasActiveUploads) {
        setError("Please wait for uploads to finish")
        return
      }

      const token = await getToken()
      if (!token) {
        setError("Authentication required")
        return
      }

      setAuthToken(token)

      // Validate required fields for current step
      if (currentStep === 0 && !formData.title.trim()) {
        setError("Title is required")
        return
      }
      if (currentStep === 0 && !formData.short_description.trim()) {
        setError("Short description is required")
        return
      }
      if (currentStep === 0 && !formData.category) {
        setError("Category is required")
        return
      }
      if (currentStep === 1 && !formData.price) {
        setError("Price is required")
        return
      }

      // Prepare update data
      const updateData: any = {
        title: formData.title,
        short_description: formData.short_description,
        description: formData.description,
        category: formData.category,
        subcategory: formData.subcategory || null,
        tags: formData.tags,
        price: parseFloat(formData.price) || 0,
        license_type: formData.license_type,
        tech_stack: formData.tech_stack,
        framework: formData.framework || null,
        requirements: formData.requirements || null,
        demo_url: formData.demo_url || null,
        documentation_url: formData.documentation_url || null,
        preview_images: formData.preview_images,
        package_url: formData.package_url || null,
        package_size_bytes: formData.package_size_bytes || null,
      }

      // If publishing, set status to active, otherwise keep draft
      if (publish) {
        updateData.status = "active"
      }

      await productsApi.update(productId, updateData)

      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)

      if (publish) {
        // If published, go back to list
        router.push("/dashboard/my-products")
      }
    } catch (err: any) {
      console.error("Failed to update product:", err)
      setError(err.response?.data?.detail || "Failed to update product")
    } finally {
      setLoading(false)
    }
  }

  function addTag() {
    const tag = tagInput.trim()
    if (tag && !formData.tags.includes(tag)) {
      setFormData({ ...formData, tags: [...formData.tags, tag] })
      setTagInput("")
    }
  }

  function removeTag(tag: string) {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) })
  }

  function addTechStack() {
    const tech = techStackInput.trim()
    if (tech && !formData.tech_stack.includes(tech)) {
      setFormData({ ...formData, tech_stack: [...formData.tech_stack, tech] })
      setTechStackInput("")
    }
  }

  function removeTechStack(tech: string) {
    setFormData({ ...formData, tech_stack: formData.tech_stack.filter(t => t !== tech) })
  }

  const hasActiveUploads = useMemo(() => {
    const imagesUploading = imageUploads.some((upload) => upload.status === "uploading")
    const packageUploading = packageUpload?.status === "uploading"
    return imagesUploading || packageUploading
  }, [imageUploads, packageUpload])

  const formatBytes = (bytes: number) => {
    if (!bytes) return "0 B"
    const sizes = ["B", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    const value = bytes / Math.pow(1024, i)
    return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${sizes[i]}`
  }

  const createUploadId = () => {
    if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
      return crypto.randomUUID()
    }
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`
  }

  function addPreviewImageUrl() {
    const url = prompt("Enter image URL:")
    if (url && !formData.preview_images.includes(url)) {
      setFormData({ ...formData, preview_images: [...formData.preview_images, url] })
    }
  }

  function removePreviewImage(url: string) {
    setFormData({ ...formData, preview_images: formData.preview_images.filter(i => i !== url) })
  }

  const handleImageFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setUploadError(null)

    const token = await getToken()
    if (!token) {
      setUploadError("Authentication required for uploads")
      return
    }
    setAuthToken(token)

    const fileList = Array.from(files)
    for (const file of fileList) {
      if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
        setUploadError("Only JPG, PNG, or WebP images are allowed")
        continue
      }
      if (file.size > MAX_IMAGE_BYTES) {
        setUploadError("Image exceeds 5MB limit")
        continue
      }

      const id = createUploadId()
      setImageUploads((prev) => [
        ...prev,
        { id, name: file.name, size: file.size, progress: 0, status: "uploading" },
      ])

      try {
        const result = await uploadFileWithPresign(file, "preview_image", (progress) => {
          setImageUploads((prev) =>
            prev.map((upload) =>
              upload.id === id ? { ...upload, progress } : upload
            )
          )
        })

        if (!result.publicUrl) {
          throw new Error("Public URL not configured for image uploads")
        }

        setImageUploads((prev) =>
          prev.map((upload) =>
            upload.id === id
              ? { ...upload, status: "done", progress: 100, url: result.publicUrl }
              : upload
          )
        )
        setFormData((prev) => ({
          ...prev,
          preview_images: [...prev.preview_images, result.publicUrl as string],
        }))
      } catch (err: any) {
        console.error("Image upload failed:", err)
        setImageUploads((prev) =>
          prev.map((upload) =>
            upload.id === id
              ? { ...upload, status: "error", error: err?.message || "Upload failed" }
              : upload
          )
        )
        setUploadError(err?.message || "Failed to upload image")
      }
    }
  }

  const handlePackageFile = async (file: File | null) => {
    if (!file) return
    setUploadError(null)

    const isAllowedType =
      ALLOWED_PACKAGE_TYPES.includes(file.type) ||
      file.name.toLowerCase().endsWith(".zip") ||
      file.name.toLowerCase().endsWith(".tar") ||
      file.name.toLowerCase().endsWith(".tar.gz") ||
      file.name.toLowerCase().endsWith(".tgz")

    if (!isAllowedType) {
      setUploadError("Package must be a .zip or .tar archive")
      return
    }

    if (file.size > MAX_PACKAGE_BYTES) {
      setUploadError("Package exceeds 500MB limit")
      return
    }

    const token = await getToken()
    if (!token) {
      setUploadError("Authentication required for uploads")
      return
    }
    setAuthToken(token)

    setPackageUpload({
      name: file.name,
      size: file.size,
      progress: 0,
      status: "uploading",
    })

    try {
      const result = await uploadFileWithPresign(file, "package", (progress) => {
        setPackageUpload((prev) =>
          prev ? { ...prev, progress } : prev
        )
      })

      setPackageUpload((prev) =>
        prev
          ? { ...prev, status: "done", progress: 100, fileKey: result.fileKey }
          : prev
      )
      setFormData((prev) => ({
        ...prev,
        package_url: result.fileKey,
        package_size_bytes: file.size,
      }))
    } catch (err: any) {
      console.error("Package upload failed:", err)
      setPackageUpload((prev) =>
        prev
          ? { ...prev, status: "error", error: err?.message || "Upload failed" }
          : prev
      )
      setUploadError(err?.message || "Failed to upload package")
    }
  }

  function nextStep() {
    // Validate current step before proceeding
    if (currentStep === 0 && (!formData.title.trim() || !formData.short_description.trim() || !formData.category)) {
      setError("Please fill in all required fields")
      return
    }
    if (currentStep === 1 && !formData.price) {
      setError("Price is required")
      return
    }
    setError(null)
    setCurrentStep(Math.min(currentStep + 1, 3))
  }

  function prevStep() {
    setError(null)
    setCurrentStep(Math.max(currentStep - 1, 0))
  }

  if (fetchLoading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading product...</div>
        </div>
      </div>
    )
  }

  if (fetchError) {
    return (
      <div className="p-6 lg:p-8">
        <Card className="border-red-900 bg-red-950/20">
          <CardContent className="p-6">
            <p className="text-red-400 mb-4">{fetchError}</p>
            <Button
              variant="outline"
              onClick={() => router.push("/dashboard/my-products")}
            >
              Go Back to Products
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Edit Product</h1>
          <p className="text-gray-400">
            Step {currentStep + 1} of 4: {STEP_TITLES[currentStep]}
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => router.push("/dashboard/my-products")}
        >
          Cancel
        </Button>
      </div>

      {/* Progress Bar */}
      <div className="flex items-center gap-2">
        {[0, 1, 2, 3].map((step) => (
          <div
            key={step}
            className={`flex-1 h-2 rounded-full transition ${
              step <= currentStep ? "bg-blue-600" : "bg-gray-700"
            }`}
          />
        ))}
      </div>

      {/* Error Message */}
      {error && (
        <Card className="border-red-900 bg-red-950/20">
          <CardContent className="p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
            <p className="text-red-400">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Success Message */}
      {saveSuccess && (
        <Card className="border-green-900 bg-green-950/20">
          <CardContent className="p-4">
            <p className="text-green-400">Product updated successfully!</p>
          </CardContent>
        </Card>
      )}

      {/* Step 1: Basic Information */}
      {currentStep === 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Title <span className="text-red-400">*</span>
              </label>
              <Input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., AI SaaS Starter Kit"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Short Description <span className="text-red-400">*</span>
              </label>
              <Input
                type="text"
                value={formData.short_description}
                onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                placeholder="Brief one-line description (max 150 chars)"
                maxLength={150}
                className="bg-gray-800 border-gray-700 text-white"
              />
              <p className="text-xs text-gray-500 mt-1">
                {formData.short_description.length}/150 characters
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Full Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Detailed description of your product..."
                rows={6}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Category <span className="text-red-400">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a category</option>
                {PRODUCT_CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Subcategory
              </label>
              <Input
                type="text"
                value={formData.subcategory}
                onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
                placeholder="e.g., E-commerce, Blog, Dashboard"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Tags
              </label>
              <div className="flex gap-2 mb-2">
                <Input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                  placeholder="Add a tag..."
                  className="bg-gray-800 border-gray-700 text-white"
                />
                <Button type="button" onClick={addTag} variant="outline">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-blue-900/30 text-blue-400 text-sm rounded"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="hover:text-blue-300"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Pricing & License */}
      {currentStep === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Pricing & License</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Price (USD) <span className="text-red-400">*</span>
              </label>
              <div className="flex items-center gap-4">
                <div className="relative flex-1">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                  <Input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    placeholder="49.00"
                    min="0"
                    step="0.01"
                    className="bg-gray-800 border-gray-700 text-white pl-7"
                  />
                </div>
                <div className="text-sm text-gray-400">
                  You'll receive ${(parseFloat(formData.price || "0") * 0.9).toFixed(2)} (90%)
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-4">
                License Type <span className="text-red-400">*</span>
              </label>
              <div className="space-y-3">
                {LICENSE_TYPES.map((license) => (
                  <label
                    key={license.value}
                    className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition ${
                      formData.license_type === license.value
                        ? "border-blue-600 bg-blue-950/20"
                        : "border-gray-700 hover:border-gray-600"
                    }`}
                  >
                    <input
                      type="radio"
                      name="license_type"
                      value={license.value}
                      checked={formData.license_type === license.value}
                      onChange={(e) => setFormData({ ...formData, license_type: e.target.value })}
                      className="mt-1"
                    />
                    <div>
                      <div className="font-medium text-white">{license.label}</div>
                      <div className="text-sm text-gray-400">{license.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <Card className="bg-blue-950/20 border-blue-900">
              <CardContent className="p-4">
                <p className="text-sm text-blue-300">
                  <strong>Payout Structure:</strong> You keep 90% of each sale. The platform fee is 10%.
                </p>
              </CardContent>
            </Card>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Technical Details */}
      {currentStep === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Technical Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Tech Stack
              </label>
              <div className="flex gap-2 mb-2">
                <Input
                  type="text"
                  value={techStackInput}
                  onChange={(e) => setTechStackInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTechStack())}
                  placeholder="Add technology..."
                  className="bg-gray-800 border-gray-700 text-white"
                />
                <Button type="button" onClick={addTechStack} variant="outline">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.tech_stack.map((tech) => (
                  <span
                    key={tech}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-gray-700 text-gray-300 text-sm rounded"
                  >
                    {tech}
                    <button
                      type="button"
                      onClick={() => removeTechStack(tech)}
                      className="hover:text-white"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-500">Common suggestions:</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {COMMON_TECH_STACK.slice(0, 10).map((tech) => (
                  <button
                    key={tech}
                    type="button"
                    onClick={() => {
                      if (!formData.tech_stack.includes(tech)) {
                        setFormData({ ...formData, tech_stack: [...formData.tech_stack, tech] })
                      }
                    }}
                    className={`px-2 py-1 text-xs rounded transition ${
                      formData.tech_stack.includes(tech)
                        ? "bg-blue-600 text-white"
                        : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                    }`}
                  >
                    + {tech}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Framework
              </label>
              <Input
                type="text"
                value={formData.framework}
                onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
                placeholder="e.g., Next.js 14, React 18"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Requirements
              </label>
              <textarea
                value={formData.requirements}
                onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                placeholder="e.g., Node.js 18+, Python 3.11, PostgreSQL 14+"
                rows={3}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Demo URL
              </label>
              <Input
                type="url"
                value={formData.demo_url}
                onChange={(e) => setFormData({ ...formData, demo_url: e.target.value })}
                placeholder="https://demo.example.com"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Documentation URL
              </label>
              <Input
                type="url"
                value={formData.documentation_url}
                onChange={(e) => setFormData({ ...formData, documentation_url: e.target.value })}
                placeholder="https://docs.example.com"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Files & Media */}
      {currentStep === 3 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Files & Media</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Preview Images
              </label>
              <p className="text-xs text-gray-500 mb-3">
                Upload JPG/PNG/WebP files up to 5MB each.
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  id="preview-image-upload"
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  multiple
                  onChange={(event) => {
                    handleImageFiles(event.target.files)
                    event.currentTarget.value = ""
                  }}
                  className="hidden"
                />
                <Button asChild type="button" variant="outline" className="gap-2 border-dashed">
                  <label htmlFor="preview-image-upload" className="cursor-pointer">
                    <Upload className="h-4 w-4" />
                    Upload Images
                  </label>
                </Button>
                <Button onClick={addPreviewImageUrl} type="button" variant="ghost">
                  Add by URL
                </Button>
              </div>

              {imageUploads.length > 0 && (
                <div className="mt-4 space-y-3">
                  {imageUploads.map((upload) => (
                    <div key={upload.id} className="rounded-lg border border-gray-800 bg-gray-900/60 p-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-200">{upload.name}</span>
                        <span className="text-gray-500">
                          {upload.status === "uploading" ? `${upload.progress}%` : upload.status}
                        </span>
                      </div>
                      <div className="mt-2 h-1.5 rounded-full bg-gray-800">
                        <div
                          className={`h-1.5 rounded-full ${
                            upload.status === "error" ? "bg-red-600" : "bg-blue-600"
                          }`}
                          style={{ width: `${upload.progress}%` }}
                        />
                      </div>
                      {upload.error && (
                        <p className="mt-2 text-xs text-red-400">{upload.error}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {formData.preview_images.filter(Boolean).length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                  {formData.preview_images.filter(Boolean).map((url, idx) => (
                    <div key={idx} className="relative group">
                      <img
                        src={url}
                        alt={`Preview ${idx + 1}`}
                        className="w-full h-32 object-cover rounded border border-gray-700"
                      />
                      <button
                        type="button"
                        onClick={() => removePreviewImage(url)}
                        className="absolute top-2 right-2 p-1 bg-red-600 rounded-full opacity-0 group-hover:opacity-100 transition"
                      >
                        <X className="h-4 w-4 text-white" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Package File
              </label>
              <p className="text-xs text-gray-500 mb-3">
                Upload a .zip or .tar archive (up to 500MB).
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  id="package-upload"
                  type="file"
                  accept=".zip,.tar,.tar.gz,.tgz"
                  onChange={(event) => {
                    const file = event.target.files?.[0] || null
                    handlePackageFile(file)
                    event.currentTarget.value = ""
                  }}
                  className="hidden"
                />
                <Button asChild type="button" variant="outline" className="gap-2 border-dashed">
                  <label htmlFor="package-upload" className="cursor-pointer">
                    <Upload className="h-4 w-4" />
                    Upload Package
                  </label>
                </Button>
                {packageUpload?.status === "done" && (
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      setPackageUpload(null)
                      setFormData((prev) => ({
                        ...prev,
                        package_url: "",
                        package_size_bytes: null,
                      }))
                    }}
                  >
                    Remove
                  </Button>
                )}
              </div>

              {packageUpload && (
                <div className="mt-4 rounded-lg border border-gray-800 bg-gray-900/60 p-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-200">{packageUpload.name}</span>
                    <span className="text-gray-500">
                      {packageUpload.status === "uploading"
                        ? `${packageUpload.progress}%`
                        : packageUpload.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                    <span>{formatBytes(packageUpload.size)}</span>
                    {packageUpload.status === "done" && <span>Ready for download</span>}
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-gray-800">
                    <div
                      className={`h-1.5 rounded-full ${
                        packageUpload.status === "error" ? "bg-red-600" : "bg-green-600"
                      }`}
                      style={{ width: `${packageUpload.progress}%` }}
                    />
                  </div>
                  {packageUpload.error && (
                    <p className="mt-2 text-xs text-red-400">{packageUpload.error}</p>
                  )}
                </div>
              )}

                <div className="mt-4">
                  <label className="block text-xs text-gray-500 mb-2">
                    Or paste a hosted URL
                  </label>
                  <Input
                  type="url"
                  value={formData.package_url && formData.package_url.startsWith("http") ? formData.package_url : ""}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,
                      package_url: e.target.value,
                      package_size_bytes: null,
                    }))
                    if (e.target.value) {
                      setPackageUpload(null)
                    }
                  }}
                  placeholder="https://storage.example.com/product.zip"
                  className="bg-gray-800 border-gray-700 text-white"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    This link is used for downloads if you provide a hosted URL.
                  </p>
                </div>
                {!packageUpload && formData.package_url && !formData.package_url.startsWith("http") && (
                  <p className="mt-2 text-xs text-gray-500">
                    Stored package: {formData.package_url.split("/").slice(-1)[0]}
                  </p>
                )}
            </div>

            {uploadError && (
              <Card className="border-red-900 bg-red-950/20">
                <CardContent className="p-4">
                  <p className="text-sm text-red-400">{uploadError}</p>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
      )}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0 || loading}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>

        <div className="flex gap-2">
          <Button
            onClick={() => handleSubmit(false)}
            disabled={loading || hasActiveUploads}
            variant="outline"
            className="gap-2"
          >
            <Save className="h-4 w-4" />
            Save Draft
          </Button>

          {currentStep < 3 ? (
            <Button onClick={nextStep} disabled={loading} className="gap-2">
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={() => handleSubmit(true)}
              disabled={loading || hasActiveUploads}
              className="gap-2"
            >
              Publish Product
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
