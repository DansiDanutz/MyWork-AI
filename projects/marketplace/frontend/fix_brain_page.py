#!/usr/bin/env python3
"""Fix brain page field names to match backend."""

# Read the file
with open('app/(dashboard)/brain/page.tsx', 'r') as f:
    content = f.read()

# Remove isPublic from form data
content = content.replace(
    '''const [formData, setFormData] = useState({
    title: "",
    content: "",
    type: "pattern",
    category: "",
    tags: "",
    language: "",
    framework: "",
    isPublic: true,
  })''',
    '''const [formData, setFormData] = useState({
    title: "",
    content: "",
    type: "pattern",
    category: "",
    tags: "",
    language: "",
    framework: "",
  })'''
)

# Remove isPublic from contribute call
content = content.replace(
    '''await brainApi.contribute({
        title: formData.title,
        content: formData.content,
        type: formData.type,
        category: formData.category,
        tags: formData.tags.split(",").map(t => t.trim()).filter(t => t),
        language: formData.language || undefined,
        framework: formData.framework || undefined,
        isPublic: formData.isPublic,
      })''',
    '''await brainApi.contribute({
        title: formData.title,
        content: formData.content,
        type: formData.type,
        category: formData.category,
        tags: formData.tags.split(",").map(t => t.trim()).filter(t => t),
        language: formData.language || undefined,
        framework: formData.framework || undefined,
      })'''
)

# Remove isPublic from form reset
content = content.replace(
    '''setFormData({
        title: "",
        content: "",
        type: "pattern",
        category: "",
        tags: "",
        language: "",
        framework: "",
        isPublic: true,
      })''',
    '''setFormData({
        title: "",
        content: "",
        type: "pattern",
        category: "",
        tags: "",
        language: "",
        framework: "",
      })'''
)

# Fix field references in display
content = content.replace('entry.entry_type', 'entry.type')
content = content.replace('entry.is_verified', 'entry.verified')
content = content.replace('entry.is_public', 'entry.status !== "active"')
content = content.replace('entry.upvotes', 'entry.helpful_votes')
content = content.replace('entry.downvotes', 'entry.unhelpful_votes')

# Fix the is_public checkbox
content = content.replace(
    '''<div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="is_public"
                      checked={formData.is_public}
                      onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                    />
                    <label htmlFor="is_public" className="text-sm text-gray-300">Make this entry public</label>
                  </div>''',
    ''  # Remove this checkbox entirely
)

# Fix the ENTRY_TYPE_COLORS to include the new types
content = content.replace(
    '''const ENTRY_TYPE_COLORS: Record<string, string> = {
  pattern: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  snippet: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  tutorial: "bg-green-500/20 text-green-300 border-green-500/30",
  solution: "bg-purple-500/20 text-purple-300 border-purple-500/30",
  documentation: "bg-orange-500/20 text-orange-300 border-orange-500/30",
}''',
    '''const ENTRY_TYPE_COLORS: Record<string, string> = {
  pattern: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  solution: "bg-purple-500/20 text-purple-300 border-purple-500/30",
  lesson: "bg-green-500/20 text-green-300 border-green-500/30",
  tip: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  antipattern: "bg-red-500/20 text-red-300 border-red-500/30",
}'''
)

# Write back
with open('app/(dashboard)/brain/page.tsx', 'w') as f:
    f.write(content)

print("Fixed brain page field names")
