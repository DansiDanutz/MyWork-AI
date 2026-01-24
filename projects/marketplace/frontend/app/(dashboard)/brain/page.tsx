"use client"

import { useState, useEffect } from "react"
import { useUser } from "@clerk/nextjs"
import { brainApi } from "@/lib/api"
import {
  Brain,
  Plus,
  Search,
  Filter,
  TrendingUp,
  Eye,
  ThumbsUp,
  ThumbsDown,
  Edit,
  Trash2,
  Tag,
  Code,
  BookOpen,
  Lightbulb,
  Wrench,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react"
import Link from "next/link"

// Types
interface BrainEntry {
  id: string
  contributor_id: string
  contributor_username: string | null
  title: string
  content: string
  entry_type: string
  category: string
  tags: string[]
  language: string | null
  framework: string | null
  quality_score: number
  usage_count: number
  upvotes: number
  downvotes: number
  is_verified: boolean
  is_public: boolean
}

interface BrainStats {
  total_entries: number
  verified_entries: number
  total_queries: number
  entries_by_type: Record<string, number>
  top_categories: Record<string, number>
}

const ENTRY_TYPES = [
  { value: "pattern", label: "Design Pattern", icon: Lightbulb },
  { value: "snippet", label: "Code Snippet", icon: Code },
  { value: "tutorial", label: "Tutorial", icon: BookOpen },
  { value: "solution", label: "Solution", icon: Wrench },
  { value: "documentation", label: "Documentation", icon: FileText },
]

const ENTRY_TYPE_COLORS: Record<string, string> = {
  pattern: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  snippet: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  tutorial: "bg-green-500/20 text-green-300 border-green-500/30",
  solution: "bg-purple-500/20 text-purple-300 border-purple-500/30",
  documentation: "bg-orange-500/20 text-orange-300 border-orange-500/30",
}

export default function BrainContributionsPage() {
  const { isLoaded, isSignedIn } = useUser()
  const [entries, setEntries] = useState<BrainEntry[]>([])
  const [stats, setStats] = useState<BrainStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [selectedType, setSelectedType] = useState<string>("")
  const [sortBy, setSortBy] = useState<"relevance" | "newest" | "popular" | "quality">("relevance")
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set())

  // Form state
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    entry_type: "pattern",
    category: "",
    tags: "",
    language: "",
    framework: "",
    is_public: true,
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      loadEntries()
      loadStats()
    }
  }, [isLoaded, isSignedIn, sortBy, selectedCategory, selectedType])

  const loadEntries = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await brainApi.search({
        q: searchQuery || undefined,
        category: selectedCategory || undefined,
        entryType: selectedType || undefined,
        sort: sortBy,
        pageSize: 50,
      })

      setEntries(response.data.entries)
    } catch (err: any) {
      console.error("Error loading brain entries:", err)
      setError(err.response?.data?.detail || "Failed to load entries")
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await brainApi.stats()
      setStats(response.data)
    } catch (err: any) {
      console.error("Error loading brain stats:", err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setSubmitting(true)

    try {
      await brainApi.contribute({
        title: formData.title,
        content: formData.content,
        entryType: formData.entry_type,
        category: formData.category,
        tags: formData.tags.split(",").map(t => t.trim()).filter(t => t),
        language: formData.language || undefined,
        framework: formData.framework || undefined,
        isPublic: formData.is_public,
      })

      // Reset form and reload
      setFormData({
        title: "",
        content: "",
        entry_type: "pattern",
        category: "",
        tags: "",
        language: "",
        framework: "",
        is_public: true,
      })
      setShowCreateForm(false)
      loadEntries()
      loadStats()
    } catch (err: any) {
      console.error("Error creating entry:", err)
      setFormError(err.response?.data?.detail || "Failed to create entry")
    } finally {
      setSubmitting(false)
    }
  }

  const handleVote = async (entryId: string, vote: 1 | -1) => {
    try {
      await brainApi.vote(entryId, vote)
      loadEntries()
    } catch (err: any) {
      console.error("Error voting:", err)
    }
  }

  const handleDelete = async (entryId: string) => {
    if (!confirm("Are you sure you want to delete this entry?")) return

    try {
      // Note: Delete endpoint not in API client yet, would need to add
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/brain/${entryId}`, {
        method: 'DELETE',
      })
      loadEntries()
      loadStats()
    } catch (err: any) {
      console.error("Error deleting entry:", err)
      alert("Failed to delete entry")
    }
  }

  const toggleExpand = (entryId: string) => {
    setExpandedEntries(prev => {
      const newSet = new Set(prev)
      if (newSet.has(entryId)) {
        newSet.delete(entryId)
      } else {
        newSet.add(entryId)
      }
      return newSet
    })
  }

  if (!isLoaded || !isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                <Brain className="w-8 h-8 text-blue-500" />
                Brain Contributions
              </h1>
              <p className="text-gray-400">
                Share your knowledge with the community. Contribute patterns, snippets, tutorials, and solutions.
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5" />
              Contribute Knowledge
            </button>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Entries</p>
                    <p className="text-2xl font-bold text-white">{stats.total_entries}</p>
                  </div>
                  <Brain className="w-8 h-8 text-blue-500" />
                </div>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Verified</p>
                    <p className="text-2xl font-bold text-green-400">{stats.verified_entries}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Queries</p>
                    <p className="text-2xl font-bold text-white">{stats.total_queries}</p>
                  </div>
                  <Search className="w-8 h-8 text-purple-500" />
                </div>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Your Contributions</p>
                    <p className="text-2xl font-bold text-blue-400">{entries.filter(e => e.contributor_id === "temp-user-id").length}</p>
                  </div>
                  <Plus className="w-8 h-8 text-blue-500" />
                </div>
              </div>
            </div>
          )}

          {/* Create Form */}
          {showCreateForm && (
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Contribute to the Brain</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Title *</label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., React Hook Pattern for Data Fetching"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Entry Type *</label>
                    <select
                      value={formData.entry_type}
                      onChange={(e) => setFormData({ ...formData, entry_type: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      {ENTRY_TYPES.map(type => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Content *</label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    rows={8}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Share your knowledge in detail..."
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Category *</label>
                    <input
                      type="text"
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., React, Testing, DevOps"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Language</label>
                    <input
                      type="text"
                      value={formData.language}
                      onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., TypeScript, Python"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Framework</label>
                    <input
                      type="text"
                      value={formData.framework}
                      onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., React, FastAPI"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., hooks, api, async"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={formData.is_public}
                    onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                    className="w-4 h-4 bg-gray-800 border-gray-700 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <label htmlFor="is_public" className="text-sm text-gray-300">Make this entry public</label>
                </div>

                {formError && (
                  <div className="bg-red-500/20 border border-red-500/50 text-red-300 px-4 py-2 rounded-lg">
                    {formError}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? "Creating..." : "Contribute"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Filters */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && loadEntries()}
                    placeholder="Search knowledge base..."
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Categories</option>
                  {stats?.top_categories && Object.keys(stats.top_categories).map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  {ENTRY_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="relevance">Relevance</option>
                  <option value="newest">Newest</option>
                  <option value="popular">Most Popular</option>
                  <option value="quality">Highest Quality</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Entries List */}
        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500" />
            </div>
          ) : error ? (
            <div className="bg-red-500/20 border border-red-500/50 text-red-300 px-6 py-4 rounded-lg">
              {error}
            </div>
          ) : entries.length === 0 ? (
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-12 text-center">
              <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">No entries yet</h3>
              <p className="text-gray-400 mb-4">Be the first to contribute knowledge to the Brain!</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Create First Entry
              </button>
            </div>
          ) : (
            entries.map((entry) => {
              const entryType = ENTRY_TYPES.find(t => t.value === entry.entry_type)
              const EntryIcon = entryType?.icon || Lightbulb
              const isExpanded = expandedEntries.has(entry.id)
              const isOwner = entry.contributor_id === "temp-user-id"

              return (
                <div
                  key={entry.id}
                  className="bg-gray-900 border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-colors"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <EntryIcon className="w-5 h-5 text-blue-500" />
                        <h3 className="text-lg font-semibold text-white">{entry.title}</h3>
                        {entry.is_verified && (
                          <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full border border-green-500/30">
                            ✓ Verified
                          </span>
                        )}
                        {!entry.is_public && (
                          <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded-full">
                            Private
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span>{entry.contributor_username || "Anonymous"}</span>
                        <span className="px-2 py-1 text-xs rounded border {ENTRY_TYPE_COLORS[entry.entry_type]}">
                          {entryType?.label}
                        </span>
                        {entry.category && (
                          <span className="px-2 py-1 bg-gray-800 text-gray-300 text-xs rounded">
                            {entry.category}
                          </span>
                        )}
                        {(entry.language || entry.framework) && (
                          <span className="text-xs">
                            {entry.language && <span className="mr-2">{entry.language}</span>}
                            {entry.framework && <span>{entry.framework}</span>}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Content Preview */}
                  <div className="mb-4">
                    {isExpanded ? (
                      <div className="text-gray-300 whitespace-pre-wrap">{entry.content}</div>
                    ) : (
                      <div className="text-gray-400 line-clamp-3">{entry.content}</div>
                    )}
                    {entry.content.length > 200 && (
                      <button
                        onClick={() => toggleExpand(entry.id)}
                        className="text-blue-400 hover:text-blue-300 text-sm mt-2 flex items-center gap-1"
                      >
                        {isExpanded ? (
                          <>
                            Show less <ChevronUp className="w-4 h-4" />
                          </>
                        ) : (
                          <>
                            Show more <ChevronDown className="w-4 h-4" />
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Tags */}
                  {entry.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {entry.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-800 text-gray-400 text-xs rounded flex items-center gap-1"
                        >
                          <Tag className="w-3 h-3" />
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-800">
                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center gap-2 text-gray-400">
                        <Eye className="w-4 h-4" />
                        <span>{entry.usage_count}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => handleVote(entry.id, 1)}
                          className="flex items-center gap-1 text-gray-400 hover:text-green-400 transition-colors"
                        >
                          <ThumbsUp className="w-4 h-4" />
                          <span>{entry.upvotes}</span>
                        </button>
                        <button
                          onClick={() => handleVote(entry.id, -1)}
                          className="flex items-center gap-1 text-gray-400 hover:text-red-400 transition-colors"
                        >
                          <ThumbsDown className="w-4 h-4" />
                          <span>{entry.downvotes}</span>
                        </button>
                      </div>
                      <div className="text-gray-400">
                        Quality: <span className="text-blue-400">{(entry.quality_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    {isOwner && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {/* TODO: Implement edit */}}
                          className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-800 rounded transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(entry.id)}
                          className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
