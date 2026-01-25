"use client"

export const dynamic = "force-dynamic"

import { useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@clerk/nextjs"
import { ChevronLeft, ChevronRight, Upload, X, Plus, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
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
  fileKey?: string
  previewUrl?: string
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

export default function NewProductPage() {
  const router = useRouter()
  const { getToken } = useAuth()

  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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

  // Validation
  const validateStep = (step: number): boolean => {
    switch (step) {
      case 0:
        if (!formData.title.trim() || formData.title.length < 10) {
          setError("Title must be at least 10 characters")
          return false
        }
        if (!formData.short_description.trim() || formData.short_description.length > 500) {
          setError("Short description is required (max 500 characters)")
          return false
        }
        if (!formData.description.trim() || formData.description.length < 100) {
          setError("Description must be at least 100 characters")
          return false
        }
        if (!formData.category) {
          setError("Please select a category")
          return false
        }
        break

      case 1:
        const price = parseFloat(formData.price)
        if (isNaN(price) || price < 0 || price > 10000) {
          setError("Price must be between $0 and $10,000")
          return false
        }
        break

      case 2:
        if (formData.tech_stack.length === 0) {
          setError("Please add at least one technology")
          return false
        }
        break

      case 3:
        // Files are optional for draft
        break
    }

    setError(null)
    return true
  }

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(Math.min(currentStep + 1, STEP_TITLES.length - 1))
    }
  }

  const handleBack = () => {
    setCurrentStep(Math.max(currentStep - 1, 0))
    setError(null)
  }

  const handleSubmit = async (saveAsDraft: boolean = true) => {
    if (!validateStep(currentStep)) return
    if (hasActiveUploads) {
      setError("Please wait for uploads to finish")
      return
    }

    // For non-draft, validate all steps
    if (!saveAsDraft) {
      for (let i = 0; i < STEP_TITLES.length; i++) {
        if (!validateStep(i)) {
          setCurrentStep(i)
          return
        }
      }
    }

    setLoading(true)
    setError(null)

    try {
      const token = await getToken()
      if (!token) {
        setError("Authentication required")
        return
      }

      setAuthToken(token)

      const productData = {
        title: formData.title,
        description: formData.description,
        category: formData.category,
        price: parseFloat(formData.price),
        license_type: formData.license_type,
        ...(formData.short_description && { short_description: formData.short_description }),
        ...(formData.subcategory && { subcategory: formData.subcategory }),
        ...(formData.tags.length > 0 && { tags: formData.tags }),
        ...(formData.tech_stack.length > 0 && { tech_stack: formData.tech_stack }),
        ...(formData.framework && { framework: formData.framework }),
        ...(formData.requirements && { requirements: formData.requirements }),
        ...(formData.demo_url && { demo_url: formData.demo_url }),
        ...(formData.documentation_url && { documentation_url: formData.documentation_url }),
        ...(formData.preview_images.length > 0 && { preview_images: formData.preview_images }),
        ...(formData.package_url && { package_url: formData.package_url }),
        ...(formData.package_size_bytes && { package_size_bytes: formData.package_size_bytes }),
      }

      await productsApi.create(productData)

      // Redirect to product list
      router.push("/dashboard/my-products")
    } catch (err: any) {
      console.error("Failed to create product:", err)
      setError(err.response?.data?.detail || "Failed to create product")
    } finally {
      setLoading(false)
    }
  }

  const addTag = () => {
    const tag = tagInput.trim()
    if (tag && !formData.tags.includes(tag)) {
      setFormData({ ...formData, tags: [...formData.tags, tag] })
      setTagInput("")
    }
  }

  const removeTag = (tag: string) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) })
  }

  const addTechStack = () => {
    const tech = techStackInput.trim()
    if (tech && !formData.tech_stack.includes(tech)) {
      setFormData({ ...formData, tech_stack: [...formData.tech_stack, tech] })
      setTechStackInput("")
    }
  }

  const removeTechStack = (tech: string) => {
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

  const addPreviewImageUrl = () => {
    const url = prompt("Enter image URL:")
    if (url && !formData.preview_images.includes(url)) {
      setFormData({ ...formData, preview_images: [...formData.preview_images, url] })
    }
  }

  const removePreviewImage = (url: string) => {
    const uploadMatch = imageUploads.find((upload) => upload.fileKey === url)
    if (uploadMatch?.previewUrl) {
      URL.revokeObjectURL(uploadMatch.previewUrl)
    }
    setImageUploads((prev) =>
      prev.filter((upload) => upload.fileKey !== url)
    )
    setFormData({ ...formData, preview_images: formData.preview_images.filter(u => u !== url) })
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
      const previewUrl = URL.createObjectURL(file)
      setImageUploads((prev) => [
        ...prev,
        { id, name: file.name, size: file.size, progress: 0, status: "uploading", previewUrl },
      ])

      try {
        const result = await uploadFileWithPresign(file, "preview_image", (progress) => {
          setImageUploads((prev) =>
            prev.map((upload) =>
              upload.id === id ? { ...upload, progress } : upload
            )
          )
        })

        setImageUploads((prev) =>
          prev.map((upload) =>
            upload.id === id
              ? {
                  ...upload,
                  status: "done",
                  progress: 100,
                  fileKey: result.fileKey,
                }
              : upload
          )
        )
        setFormData((prev) => ({
          ...prev,
          preview_images: [...prev.preview_images, result.fileKey],
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

  const displayPreviewImages = useMemo(() => {
    return formData.preview_images
      .map((value) => {
        if (value.startsWith("http://") || value.startsWith("https://")) {
          return { key: value, url: value }
        }
        const match = imageUploads.find((upload) => upload.fileKey === value)
        return { key: value, url: match?.previewUrl }
      })
      .filter((item) => item.url)
  }, [formData.preview_images, imageUploads])

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

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">Create New Product</h1>
        <p className="text-gray-400">Fill in the details to list your product on the marketplace</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {STEP_TITLES.map((title, index) => (
            <div key={index} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition ${
                    index <= currentStep
                      ? "bg-blue-600 text-white"
                      : "bg-gray-800 text-gray-500"
                  }`}
                >
                  {index + 1}
                </div>
                <div className={`text-xs mt-2 text-center ${index <= currentStep ? "text-white" : "text-gray-500"}`}>
                  {title}
                </div>
              </div>
              {index < STEP_TITLES.length - 1 && (
                <div
                  className={`h-0.5 flex-1 mx-2 transition ${
                    index < currentStep ? "bg-blue-600" : "bg-gray-800"
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <Card className="mb-6 border-red-900 bg-red-950/20">
          <CardContent className="p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-400 text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Form */}
      <Card>
        <CardContent className="p-6">
          {/* Step 1: Basic Info */}
          {currentStep === 0 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Product Title <span className="text-red-400">*</span>
                </label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., Production-Ready SaaS Starter Kit"
                  className="bg-gray-800 border-gray-700 text-white"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.title.length}/200 characters (min 10)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Short Description <span className="text-red-400">*</span>
                </label>
                <Input
                  value={formData.short_description}
                  onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                  placeholder="A brief one-line description for the product card"
                  className="bg-gray-800 border-gray-700 text-white"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.short_description.length}/500 characters
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Full Description <span className="text-red-400">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe your product in detail. What does it do? What problem does it solve? What features are included?"
                  rows={8}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.description.length} characters (min 100)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Category <span className="text-red-400">*</span>
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-600"
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
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                    placeholder="Add a tag"
                    className="bg-gray-800 border-gray-700 text-white flex-1"
                  />
                  <Button onClick={addTag} type="button" variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                {formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 bg-blue-600/20 text-blue-400 px-2 py-1 rounded text-sm"
                      >
                        {tag}
                        <button
                          onClick={() => removeTag(tag)}
                          className="hover:text-red-400 transition"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Pricing & License */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Price (USD) <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                  <Input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    placeholder="49.00"
                    min="0"
                    max="10000"
                    step="0.01"
                    className="bg-gray-800 border-gray-700 text-white pl-7"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  You keep 90% of each sale (${!formData.price ? "0.00" : (parseFloat(formData.price || "0") * 0.9).toFixed(2)} per sale)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  License Type <span className="text-red-400">*</span>
                </label>
                <div className="space-y-3">
                  {LICENSE_TYPES.map((license) => (
                    <label
                      key={license.value}
                      className={`flex items-start p-4 rounded-lg border cursor-pointer transition ${
                        formData.license_type === license.value
                          ? "border-blue-600 bg-blue-600/10"
                          : "border-gray-700 bg-gray-800/50 hover:border-gray-600"
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
                      <div className="ml-3">
                        <div className="font-medium text-white">{license.label}</div>
                        <div className="text-sm text-gray-400">{license.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Technical Details */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tech Stack <span className="text-red-400">*</span>
                </label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={techStackInput}
                    onChange={(e) => setTechStackInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTechStack())}
                    placeholder="Add technology"
                    className="bg-gray-800 border-gray-700 text-white flex-1"
                  />
                  <Button onClick={addTechStack} type="button" variant="secondary">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="mb-3">
                  <p className="text-xs text-gray-500 mb-2">Quick add:</p>
                  <div className="flex flex-wrap gap-2">
                    {COMMON_TECH_STACK.map((tech) => (
                      <button
                        key={tech}
                        type="button"
                        onClick={() => {
                          if (!formData.tech_stack.includes(tech)) {
                            setFormData({ ...formData, tech_stack: [...formData.tech_stack, tech] })
                          }
                        }}
                        disabled={formData.tech_stack.includes(tech)}
                        className={`text-xs px-2 py-1 rounded transition ${
                          formData.tech_stack.includes(tech)
                            ? "bg-blue-600 text-white cursor-not-allowed"
                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                        }`}
                      >
                        {tech}
                      </button>
                    ))}
                  </div>
                </div>
                {formData.tech_stack.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.tech_stack.map((tech) => (
                      <span
                        key={tech}
                        className="inline-flex items-center gap-1 bg-green-600/20 text-green-400 px-2 py-1 rounded text-sm"
                      >
                        {tech}
                        <button
                          onClick={() => removeTechStack(tech)}
                          className="hover:text-red-400 transition"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Framework
                </label>
                <Input
                  value={formData.framework}
                  onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
                  placeholder="e.g., Next.js 14, React 18, Vue 3"
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
                  placeholder="e.g., Node.js 18+, Python 3.11, PostgreSQL 14"
                  rows={4}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Demo URL
                </label>
                <Input
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
                  value={formData.documentation_url}
                  onChange={(e) => setFormData({ ...formData, documentation_url: e.target.value })}
                  placeholder="https://docs.example.com"
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>
            </div>
          )}

          {/* Step 4: Files & Media */}
          {currentStep === 3 && (
            <div className="space-y-6">
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

                {displayPreviewImages.length > 0 && (
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
                    {displayPreviewImages.map((image, index) => (
                      <div key={image.key} className="relative group">
                        <img
                          src={image.url as string}
                          alt={`Preview ${index + 1}`}
                          className="w-full h-24 object-cover rounded border border-gray-700"
                        />
                        <button
                          onClick={() => removePreviewImage(image.key)}
                          className="absolute top-1 right-1 bg-red-600 text-white p-1 rounded opacity-0 group-hover:opacity-100 transition"
                        >
                          <X className="h-4 w-4" />
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
                    placeholder="https://storage.example.com/product-package.zip"
                    className="bg-gray-800 border-gray-700 text-white"
                  />
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
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-800">
            <Button
              onClick={handleBack}
              disabled={currentStep === 0 || loading}
              variant="ghost"
              className="gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Back
            </Button>

            <div className="flex gap-2">
              {currentStep === STEP_TITLES.length - 1 ? (
                <>
                  <Button
                    onClick={() => handleSubmit(true)}
                    disabled={loading || hasActiveUploads}
                    variant="outline"
                    className="gap-2"
                  >
                    Save as Draft
                  </Button>
                  <Button
                    onClick={() => handleSubmit(false)}
                    disabled={loading || hasActiveUploads}
                    className="gap-2"
                  >
                    {loading ? "Creating..." : "Publish Product"}
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </>
              ) : (
                <Button onClick={handleNext} disabled={loading} className="gap-2">
                  Next Step
                  <ChevronRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
